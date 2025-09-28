import json
from litellm import completion
from sqlalchemy import create_engine, text
from backend.core.config import settings
from backend.services.document_processor import DocumentProcessor
from backend.services.cache_manager import QueryCache
from backend.services.schema_discovery import SchemaDiscovery

# SYSTEM_PROMPT remains the same...
SYSTEM_PROMPT = """
You are an expert analytical assistant. Your goal is to help users query an employee database.
Given a database schema and a user's question, you must perform the following tasks:
1.  **Classify the query**: Determine if the question can be answered by the SQL database, by searching unstructured documents, or requires both. The types are 'SQL', 'DOCUMENT', or 'HYBRID'.
2.  **Generate a SQL query**: If the question can be answered by the database, generate a syntactically correct SQL query for SQLite.

**Constraints**:
- Only use tables and columns present in the provided schema.
- If a query is for documents (e.g., "show me John's resume"), classify it as 'DOCUMENT' and return an empty string for the SQL query.
- If a query is vague or could involve both structured data and documents (e.g., "Find Python developers earning over 100k"), classify it as 'HYBRID'.
- ALWAYS respond with a single, valid JSON object in the following format. Do not add any text before or after the JSON object.

{
  "query_type": "...",
  "sql": "..."
}
"""

class QueryEngine:
    def __init__(self, document_processor: DocumentProcessor, cache: QueryCache):
        self.document_processor = document_processor
        self.cache = cache

    def _get_schema_representation(self, connection_string: str) -> str:
        # This function remains the same...
        schema_data = SchemaDiscovery().analyze_database(connection_string)
        if schema_data["status"] != "success":
            raise ValueError("Failed to retrieve database schema.")
        
        representation = ""
        for table, details in schema_data["schema"]["tables"].items():
            columns = ", ".join([f"{col['name']} ({col['type']})" for col in details["columns"]])
            representation += f"Table {table}: {columns}\n"
        return representation

    def process_query(self, user_query: str, connection_string: str):
        cache_key = f"{connection_string}::{user_query}"
        cached_result = self.cache.get(cache_key)
        if cached_result:
            cached_result["cache_hit"] = True
            return cached_result

        # --- ADDING ROBUST ERROR HANDLING AROUND THE AI LOGIC ---
        try:
            schema_rep = self._get_schema_representation(connection_string)
            prompt = f"Database Schema:\n{schema_rep}\n\nUser Question: \"{user_query}\""
            
            response = completion(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                format="json"
            )
            
            llm_output_str = response.choices[0].message.content
            
            # This is a common failure point. Let's make it safe.
            try:
                llm_output = json.loads(llm_output_str)
            except json.JSONDecodeError:
                print(f"DEBUG: LLM returned non-JSON response:\n{llm_output_str}")
                raise ValueError("The AI model returned an invalid format.")

            query_type = llm_output.get("query_type")
            generated_sql = llm_output.get("sql", "")
            
            results = {"query_type": query_type, "sql_result": None, "doc_result": None}
            
            if query_type in ["SQL", "HYBRID"] and generated_sql:
                # This is another common failure point.
                try:
                    engine = create_engine(connection_string)
                    with engine.connect() as connection:
                        sql_result = connection.execute(text(generated_sql)).mappings().all()
                        results["sql_result"] = [dict(row) for row in sql_result]
                except Exception as e:
                    print(f"DEBUG: Error executing generated SQL: {generated_sql}")
                    print(f"DEBUG: SQL Error: {e}")
                    # Return the error to the frontend instead of crashing
                    results["sql_result"] = {"error": f"Failed to execute SQL: {e}"}

            if query_type in ["DOCUMENT", "HYBRID"]:
                doc_search_results = self.document_processor.search_documents(user_query)
                results["doc_result"] = doc_search_results
                
            results["cache_hit"] = False
            self.cache.set(cache_key, results)

            return results
        
        # Catch any other unexpected errors during the process
        except Exception as e:
            print(f"An unexpected error occurred in QueryEngine: {e}")
            # Re-raise to be caught by the API route's error handler
            raise e
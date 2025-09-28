from sqlalchemy import create_engine, inspect, MetaData
from sqlalchemy.exc import SQLAlchemyError

class SchemaDiscovery:
    """A service to discover the schema of a SQL database."""

    def analyze_database(self, connection_string: str) -> dict:
        """
        [cite_start]Connects to a database and discovers its schema. [cite: 7]
        [cite_start]This method must handle variations in table and column names. [cite: 49]
        """
        try:
            # Create a database engine using the provided connection string
            engine = create_engine(connection_string)
            
            # Use inspector to get detailed info and MetaData to reflect the schema
            inspector = inspect(engine)
            meta = MetaData()
            meta.reflect(bind=engine)

            schema_info = {"tables": {}}

            # Iterate through all discovered tables
            for table_name in inspector.get_table_names():
                table_info = {
                    "columns": [],
                    "foreign_keys": []
                }
                
                # Get columns for the current table
                columns = inspector.get_columns(table_name)
                for column in columns:
                    table_info["columns"].append({
                        "name": column['name'],
                        "type": str(column['type'])
                    })
                
                # [cite_start]Get foreign keys for the current table to understand relationships [cite: 47]
                foreign_keys = inspector.get_foreign_keys(table_name)
                for fk in foreign_keys:
                    table_info["foreign_keys"].append({
                        "constrained_columns": fk['constrained_columns'],
                        "referred_table": fk['referred_table'],
                        "referred_columns": fk['referred_columns']
                    })
                
                schema_info["tables"][table_name] = table_info

            return {"status": "success", "schema": schema_info}

        except SQLAlchemyError as e:
            # [cite_start]Graceful error handling for database connection issues [cite: 99]
            return {"status": "error", "message": f"Database connection or inspection failed: {str(e)}"}
        except Exception as e:
            return {"status": "error", "message": f"An unexpected error occurred: {str(e)}"}
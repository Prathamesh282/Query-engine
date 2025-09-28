# backend/dependencies.py
from backend.services.document_processor import DocumentProcessor
from backend.services.query_engine import QueryEngine
from backend.services.cache_manager import QueryCache # Add this import

document_processor = DocumentProcessor()
query_cache = QueryCache() # Create a single cache instance

# Pass the cache to the QueryEngine
query_engine = QueryEngine(
    document_processor=document_processor,
    cache=query_cache
)

def get_document_processor():
    return document_processor

def get_query_engine():
    return query_engine
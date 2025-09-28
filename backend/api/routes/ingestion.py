import os
import shutil
from fastapi import APIRouter, HTTPException, Body, UploadFile, File, Depends
from typing import List
from backend.services.schema_discovery import SchemaDiscovery
from backend.services.document_processor import DocumentProcessor

# We'll create this file next to manage our service instances
from backend.dependencies import get_document_processor

router = APIRouter()
UPLOAD_DIR = "temp_uploads"

@router.post("/ingest/database")
async def connect_and_discover_schema(connection_string: str = Body(..., embed=True, description="Database connection string")):
    discovery_service = SchemaDiscovery()
    result = discovery_service.analyze_database(connection_string)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@router.post("/ingest/documents")
async def upload_documents(
    files: List[UploadFile] = File(...),
    processor: DocumentProcessor = Depends(get_document_processor)
):
    """
    API endpoint to upload and process documents. It saves the files,
    sends them to the DocumentProcessor, and then cleans up.
    """
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    saved_file_paths = []
    for file in files:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        saved_file_paths.append(file_path)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
    try:
        # Process the saved files
        processor.process_documents(saved_file_paths)
    except Exception as e:
        # Clean up files even if processing fails
        for file_path in saved_file_paths:
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Failed to process documents: {str(e)}")
    finally:
        # Ensure cleanup happens after processing
        for file_path in saved_file_paths:
            os.remove(file_path)

    return {
        "status": "success",
        "message": f"Successfully processed and indexed {len(saved_file_paths)} documents.",
        "total_chunks_in_store": processor.index.ntotal
    }
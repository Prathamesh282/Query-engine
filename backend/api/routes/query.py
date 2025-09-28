from fastapi import APIRouter, Depends, Body, HTTPException
from backend.services.query_engine import QueryEngine
from backend.dependencies import get_query_engine

router = APIRouter()

@router.post("/query")
async def process_user_query(
    query: str = Body(..., embed=True),
    connection_string: str = Body(..., embed=True),
    engine: QueryEngine = Depends(get_query_engine)
):
    """
    Processes a natural language query from the user.
    """
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    if not connection_string:
        raise HTTPException(status_code=400, detail="Connection string cannot be empty.")

    try:
        result = engine.process_query(user_query=query, connection_string=connection_string)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
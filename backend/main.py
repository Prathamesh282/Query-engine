from fastapi import FastAPI
# Add this import
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import ingestion, query

app = FastAPI(title="AI Query Engine")

# --- Add CORS Middleware ---
# This allows your frontend to communicate with the backend
origins = ["*"] # For development, allow all origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Include Routers ---
app.include_router(ingestion.router, prefix="/api", tags=["Ingestion"])
app.include_router(query.router, prefix="/api", tags=["Query"])

@app.get("/")
def read_root():
    """A simple endpoint to confirm the API is running."""
    return {"status": "ok", "message": "AI Query Engine API is running!"}
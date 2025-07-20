import uvicorn
from fastapi import FastAPI

from intelligent_backend.api import endpoints
from intelligent_backend.core.config import settings
from intelligent_backend.db.models import Base
from intelligent_backend.db.session import engine

# This function will create the database tables.
# It's useful for development to ensure the schema exists.
def create_tables():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)

# Create the main FastAPI application instance
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API layer for RAG and other LLM workflows powered by Apache Burr.",
    version="1.0.0",
)

# Include the API router from the endpoints module
app.include_router(endpoints.router, prefix=settings.API_V1_STR)

@app.on_event("startup")
def on_startup():
    """
    Actions to perform on application startup.
    """
    create_tables()


@app.get("/", tags=["Health Check"])
def read_root():
    """
    Root endpoint to check if the service is running.
    """
    return {"status": "ok", "message": f"Welcome to the {settings.PROJECT_NAME}!"}

# This block allows running the app directly with `python src/intelligent_backend/main.py`
# However, the recommended way is to use `uvicorn` from the command line for production.
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

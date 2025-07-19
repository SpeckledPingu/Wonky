import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import search, processing, reports, documents, projects # <-- IMPORTED
from app.core.config import settings
from app.database import Base, engine

# This line creates the database tables if they don't exist.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include the API routers
app.include_router(projects.router, prefix=settings.API_V1_STR, tags=["Projects"]) # <-- ADDED
app.include_router(search.router, prefix=settings.API_V1_STR, tags=["Search"])
app.include_router(processing.router, prefix=settings.API_V1_STR, tags=["Processing"])
app.include_router(reports.router, prefix=settings.API_V1_STR, tags=["Reports"])
app.include_router(documents.router, prefix=settings.API_V1_STR, tags=["Documents"])


@app.get("/", tags=["Root"])
async def read_root():
    """
    A simple root endpoint to confirm the API is running.
    """
    return {"message": "Welcome to the Research Analytics Platform API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

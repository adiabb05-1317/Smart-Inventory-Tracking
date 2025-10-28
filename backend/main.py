from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import aiohttp
import os
from dotenv import load_dotenv
from src.db.db_manager import DBManager
from src.routers import products, analytics, ai_chat
from src.services.cache_service import CacheService
from src.services.ai_agent import InventoryAgent

# Load environment variables from .env file
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    Handles startup and shutdown events for database and HTTP client.
    """
    # Startup: Initialize database manager and aiohttp session
    print("Starting up application...")
    
    # Initialize database manager (uses environment variables)
    db_manager = DBManager()
    db_manager.initialize_pool()
    app.state.db_manager = db_manager

    print("Database connection pool initialized")
    
    # Initialize aiohttp ClientSession
    app.state.http_client = aiohttp.ClientSession()
    print("HTTP client session initialized")
    
    # Initialize cache service for analytics
    cache_ttl = int(os.getenv("CACHE_TTL_SECONDS", "300"))
    app.state.cache = CacheService(default_ttl_seconds=cache_ttl)
    print(f"Cache service initialized (TTL: {cache_ttl}s)")
    
    # Note: AI agent is initialized lazily in ai_chat router
    print("AI agent will be initialized on first use")
    
    yield
    
    # Shutdown: Close database connections and aiohttp session
    print("Shutting down application...")
    db_manager.close_pool()
    await app.state.http_client.close()
    print("Cleanup completed")


# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Inventory Tracker API",
    description="Electronic Store Inventory Management System",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
cors_origins = os.getenv("CORS_ALLOW_ORIGINS", "*")
allow_origins = cors_origins.split(",") if cors_origins != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(products.router)
app.include_router(analytics.router)
app.include_router(ai_chat.router)


@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to Inventory Tracker API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    
    api_host = os.getenv("API_HOST", "0.0.0.0")
    api_port = int(os.getenv("API_PORT", "8000"))
    api_reload = os.getenv("API_RELOAD", "true").lower() == "true"
    
    uvicorn.run("main:app", host=api_host, port=api_port, reload=api_reload)


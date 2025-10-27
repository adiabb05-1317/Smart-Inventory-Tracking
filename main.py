from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import aiohttp
from src.db.db_manager import DBManager
from src.routers import products, analytics


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    Handles startup and shutdown events for database and HTTP client.
    """
    # Startup: Initialize database manager and aiohttp session
    print("Starting up application...")
    
    # Initialize database manager
    db_manager = DBManager(min_conn=2, max_conn=10)
    db_manager.initialize_pool(
        host="localhost",
        port=5432,
        database="inventory_db",
        user="kubo_user",
        password="password"
    )
    app.state.db_manager = db_manager
    print("Database connection pool initialized")
    
    # Initialize aiohttp ClientSession
    app.state.http_client = aiohttp.ClientSession()
    print("HTTP client session initialized")
    
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

# Configure CORS to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(products.router)
app.include_router(analytics.router)


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
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


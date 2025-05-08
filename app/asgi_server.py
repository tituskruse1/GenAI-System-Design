import os

from fastapi import FastAPI, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import psycopg
from utils import RedisABTestMiddleware, redis_client, create_session

# from psycopg.rows import dict_rows
from contextlib import asynccontextmanager

# Database connection configuration
DB_CONFIG = {
    "dbname": os.getenv("POSTGRES_DB", "vectordb"),
    "user": os.getenv("POSTGRES_USER", "root"),
    "password": os.getenv("POSTGRES_PASSWORD", "pass"),
    "host": os.getenv("POSTGRES_URL", "postgres"),
    "port": "5432",
}


def get_db_connection():
    """Create and return a database connection."""
    try:
        conn = psycopg.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    """This function handles the startup and shutdown events of the fastapi app."""
    app.state.session = create_session()
    app.state.db_conn = get_db_connection()
    redis_client.set("experiments", ["llama-3.3-70b", "mistral-31-24b"])

    yield

    app.state.session.close()
    redis_client.close()


# Initialize FastAPI app
app = FastAPI(
    title="GenAI System Design API",
    description="API for GenAI System Design",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.add_middleware(
    RedisABTestMiddleware,
)


@app.get("/")
async def root():
    """Root endpoint that returns a welcome message."""
    return {"message": "Welcome to GenAI System Design API"}


@app.post("/ingest_img")
async def ingest_img(file: UploadFile = File(...)):
    """
    Endpoint to handle image file uploads.
    The File(...) parameter means this is a required field.
    """
    # You can access the file contents using:
    # contents = await file.read()
    # And file metadata using:
    # filename = file.filename
    # content_type = file.content_type

    return {"filename": file.filename, "content_type": file.content_type}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# @contextmanager
def get_db():
    """Database connection dependency."""
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()


@app.get("/test-db")
async def test_db(db: psycopg.Connection = Depends(get_db)):
    """Test endpoint to verify database connection."""
    try:
        with db.cursor() as cur:
            cur.execute("SELECT version();")
            version = cur.fetchone()
        return {"status": "connected", "version": version}
    except Exception as e:
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    uvicorn.run(
        "asgi_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload during development
    )

import os

from fastapi import FastAPI, UploadFile, File, Depends, Request, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import psycopg2
from utils import RedisABTestMiddleware, redis_client, create_session, VeniceApiWrapper

import logging

logger = logging.Logger(__name__)

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
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        raise


# @contextmanager
def get_db():
    """Database connection dependency."""
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """This function handles the startup and shutdown events of the fastapi app."""
    app.state.session = create_session()
    app.state.db_conn = get_db_connection()
    redis_client.rpush(
        "experiments", "llama-3.3-70b", "mistral-31-24b"
    )  ### ONLY USED FOR DEV SEEDING

    app.state.model_api = VeniceApiWrapper(app.state.session)

    yield

    app.state.session.close()
    redis_client.close()


# Initialize FastAPI app
app = FastAPI(
    title="GenAI System Design API",
    description="API for GenAI System Design",
    version="1.0.0",
    lifespan=lifespan,
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


@app.post("/ask_question")
async def ask_question(request: Request, prompt: str = Form(...)):
    """
    Endpoint to handle question prompts.
    The Form(...) parameter means this is a required field.
    """
    response = app.state.model_api.get_answer(model=request.state.model, prompt=prompt)
    return {"response": response}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/")
async def root():
    """Root endpoint that returns a welcome message."""
    return {"message": "Welcome to GenAI System Design API"}


if __name__ == "__main__":
    uvicorn.run(
        "asgi_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload during development
    )

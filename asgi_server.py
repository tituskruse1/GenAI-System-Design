from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

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


if __name__ == "__main__":
    uvicorn.run(
        "asgi_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload during development
    )

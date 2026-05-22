from fastapi import FastAPI, UploadFile, File
from uuid import uuid4
from apps.api.routes.upload import router as upload_router

app = FastAPI(title="Construction RFI API")
app.include_router(upload_router)

# setting up logging

import logging

# logging at app startup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),  # File output
        logging.StreamHandler()                # Console output
    ]
)

# setting up basic routes 

# 1. check health
@app.get("/health")
def health_check():
    return {"status": "ok"}

# 2. check upload 
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    job_id = str(uuid4())
    return {"job_id": job_id, "filename": file.filename, "message": "File uploaded and job created"}

# 3. check job status (let job_id:str -> 'status' =/!= 'processing')
@app.get("/job/{job_id}")
def get_job_status(job_id: str):
    # Mocking job status retrieval
    return {"job_id": job_id, "status": "processing"}

if __name__ == "__main__":
    try:
        import uvicorn
    except ImportError:
        raise RuntimeError(
            "uvicorn is required to run the server. Install it with: pip install uvicorn"
        )
    uvicorn.run(app, host="0.0.0.0", port=8000)


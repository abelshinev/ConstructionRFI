from fastapi import FastAPI, UploadFile, File
from uuid import uuid4
import uvicorn

app = FastAPI(title="Construction RFI API")

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # Mocking file processing and job creation
    job_id = str(uuid4())
    return {"job_id": job_id, "filename": file.filename, "message": "File uploaded and job created"}

@app.get("/job/{job_id}")
def get_job_status(job_id: str):
    # Mocking job status retrieval
    return {"job_id": job_id, "status": "processing"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

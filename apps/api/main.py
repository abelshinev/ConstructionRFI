from fastapi import FastAPI, UploadFile, File
from uuid import uuid4
from apps.api.routes import upload


# setting up logging

import logging
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI(title="Construction RFI API")

# 1. Include your API routes FIRST
# app.include_router(observations.router)

# 2. Mount the "assets" folder containing your compiled JS/CSS
# Assuming your React build folder is at "../frontend/dist"
frontend_dist = os.path.join(os.path.dirname(__file__), "../frontend/dist")

# Serve the static assets (CSS, JS files)
app.mount("/assets", StaticFiles(directory=f"{frontend_dist}/assets"), name="assets")

# 3. Catch-all route to serve the React index.html
# This must be at the very bottom so it doesn't override your /api routes!
@app.get("/{catchall:path}")
async def serve_react_app(catchall: str):
    index_path = f"{frontend_dist}/index.html"
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": "Frontend build not found. Run 'npm run build' first."}

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

# 2. check upload (routes/upload.py)'
app.include_router(upload.router)

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


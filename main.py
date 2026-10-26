import os
import uuid
import shutil
import traceback

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from pipeline import run_pipeline
from automation import run_automation

app = FastAPI(title="AI Report Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "tmp/uploads"
OUTPUT_DIR = "tmp/outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory="static", html=True), name="static")


@app.get("/")
async def serve_ui():
    return FileResponse("static/index.html")


@app.post("/upload")
async def upload_csv(request: Request):
    job_id   = str(uuid.uuid4())[:8]
    csv_path = f"{UPLOAD_DIR}/{job_id}.csv"
    pdf_path = f"{OUTPUT_DIR}/{job_id}_report.pdf"

    content_type = request.headers.get("content-type", "")

    # Must be multipart form — file + user inputs
    if "multipart" not in content_type:
        # Raw binary fallback (curl testing)
        body = await request.body()
        if not body:
            raise HTTPException(status_code=400, detail="Empty request body.")
        with open(csv_path, "wb") as f:
            f.write(body)
        email        = ""
        drive_folder = ""
        sheets_id    = ""
    else:
        form         = await request.form()
        file         = form.get("file")
        email        = form.get("email", "")
        drive_folder = form.get("drive_folder", "")
        sheets_id    = form.get("sheets_id", "")

        if file is None:
            raise HTTPException(status_code=400, detail="No file uploaded.")
        with open(csv_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

    # Run pipeline
    try:
        summary = run_pipeline(csv_path, pdf_path)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")

    # Run automations — passes user-provided values
    automation_results = []
    try:
        automation_results = run_automation(
            pdf_path     = pdf_path,
            summary      = summary,
            job_id       = job_id,
            email        = email,
            drive_folder = drive_folder,
            sheets_id    = sheets_id,
        )
    except Exception as e:
        print(f"AUTOMATION ERROR: {e}")

    return JSONResponse({
        "job_id":       job_id,
        "status":       "complete",
        "download_url": f"/report/{job_id}",
        "summary":      summary,
        "automations":  automation_results,
    })


@app.get("/report/{job_id}")
async def download_report(job_id: str):
    pdf_path = f"{OUTPUT_DIR}/{job_id}_report.pdf"
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="Report not found.")
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename="student_performance_report.pdf"
    )


@app.get("/health")
async def health():
    return {"status": "ok"}
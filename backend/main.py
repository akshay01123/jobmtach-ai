"""FastAPI backend for JobMatch AI (placeholder)

This file provides a minimal FastAPI app with a health check and
an analyze endpoint stub. Real resume parsing and AI analysis will
be added later.
"""
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="JobMatch AI - Backend")

# Allow local frontend to call the API during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve the frontend static files so you can open the app at http://127.0.0.1:8000
# This keeps the frontend and backend separated but hosted from the same server
# during development (no edits to `frontend/script.js` required).


@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


class AnalyzeResponse(BaseModel):
    match_percentage: str
    overall_match: str
    skills_match: str
    experience_match: str
    education_match: str
    missing_skills: List[str]
    strengths: List[str]
    ai_recommendation: str


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze(
    resume: Optional[UploadFile] = File(None),
    job_file: Optional[UploadFile] = File(None),
    job_text: Optional[str] = Form(None),
):
    """
    Placeholder analyze endpoint.

    Accepts an uploaded resume and/or job description (file or text).
    Does NOT perform any AI analysis yet — returns a consistent placeholder
    response so the frontend can be wired up and tested.
    """

    # We intentionally do not parse or analyze files here yet.
    # In the future we'll add PDF/DOCX parsing, embedding generation,
    # semantic matching, and an LLM-based explanation.

    # Return a predictable placeholder response that the frontend can consume.
    return {
        "match_percentage": "--%",
        "overall_match": "--%",
        "skills_match": "--%",
        "experience_match": "--%",
        "education_match": "--%",
        "missing_skills": [],
        "strengths": [],
        "ai_recommendation": "AI analysis not implemented yet. Backend placeholder response."
    }


# Mount frontend static files after API routes so API paths (e.g. /api/health)
# are matched first. Serving at `/` allows opening the app at
# http://127.0.0.1:8000 without editing frontend paths.
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)

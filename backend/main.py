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

    # Basic match implementation (keyword overlap).
    # This is intentionally simple and meant as a lightweight proof-of-concept
    # until full resume parsing, embeddings, and LLM logic are added.
    import re

    def extract_text_from_upload(upload: Optional[UploadFile]):
        if not upload:
            return ""
        # Try to read text for plain text uploads. For binary formats (pdf/docx)
        # we do not parse them yet; return an empty string and rely on job_text.
        try:
            content = upload.file.read()
            # reset file pointer for later if needed
            upload.file.seek(0)
            # decode as utf-8 ignoring errors
            return content.decode('utf-8', errors='ignore')
        except Exception:
            return ""

    # Collect raw strings
    resume_text = extract_text_from_upload(resume)
    job_file_text = extract_text_from_upload(job_file)
    job_source = (job_text or "") + "\n" + job_file_text

    # Tokenize and sanitize
    def tokens(s: str):
        s = s.lower()
        # replace non-word characters with spaces
        parts = re.split(r"[^a-z0-9+#+\-]+", s)
        # small stoplist
        stop = {"the","and","with","for","a","an","to","of","in","on","is","as","by","at","be","or","from","that","this","we","you"}
        toks = [p for p in parts if p and len(p) > 2 and p not in stop]
        return toks

    job_tokens = set(tokens(job_source))
    resume_tokens = set(tokens(resume_text))

    # If no job tokens are provided, return placeholder response prompting user
    if not job_tokens:
        return {
            "match_percentage": "--%",
            "overall_match": "--%",
            "skills_match": "--%",
            "experience_match": "--%",
            "education_match": "--%",
            "missing_skills": [],
            "strengths": [],
            "ai_recommendation": "Please provide job description text or upload a text-based job file."
        }

    # Compute simple keyword overlap
    matched = sorted(list(job_tokens & resume_tokens))
    missing = sorted(list(job_tokens - resume_tokens))

    # Skills match is percent of job tokens present in resume
    skills_pct = round((len(matched) / len(job_tokens)) * 100) if job_tokens else 0

    # Experience match heuristic: check for presence of experience-related words
    exp_keywords = {"experience","years","year","senior","junior","mid-level","lead"}
    exp_in_job = any(k in job_tokens for k in exp_keywords)
    exp_in_resume = any(k in resume_tokens for k in exp_keywords)
    experience_pct = 100 if (exp_in_job and exp_in_resume) else (50 if (exp_in_job or exp_in_resume) else 0)

    # Education match heuristic: look for degree keywords
    edu_keywords = {"bachelor","master","phd","bs","ba","ms","degree"}
    edu_in_job = any(k in job_tokens for k in edu_keywords)
    edu_in_resume = any(k in resume_tokens for k in edu_keywords)
    education_pct = 100 if (edu_in_job and edu_in_resume) else (50 if (edu_in_job or edu_in_resume) else 0)

    # Combine into an overall score (weights chosen for demonstration)
    overall = round(0.65 * skills_pct + 0.25 * experience_pct + 0.10 * education_pct)

    ai_recommendation = (
        "This is a basic keyword-overlap match. For better results, upload a text resume or "
        "implement PDF/DOCX parsing, embeddings, and an LLM."
    )

    return {
        "match_percentage": f"{overall}%",
        "overall_match": f"{overall}%",
        "skills_match": f"{skills_pct}%",
        "experience_match": f"{experience_pct}%",
        "education_match": f"{education_pct}%",
        "missing_skills": missing[:20],
        "strengths": matched[:20],
        "ai_recommendation": ai_recommendation,
    }


# Mount frontend static files after API routes so API paths (e.g. /api/health)
# are matched first. Serving at `/` allows opening the app at
# http://127.0.0.1:8000 without editing frontend paths.
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)

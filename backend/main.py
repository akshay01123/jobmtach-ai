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
import requests
from bs4 import BeautifulSoup
import subprocess
import json

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



@app.post("/api/search_and_match")
async def search_and_match(job_text: str = Form(...), max_results: int = Form(3)):
    """
    Prototype: Search the web for similar job postings and compute simple
    keyword-overlap matches against the provided `job_text`.

    Notes:
    - Uses DuckDuckGo HTML search (no API key). Limited to a few pages.
    - This is a proof-of-concept. Respect site robots/usage when running at scale.
    """
    # Basic helpers (reuse tokenization logic)
    import re

    def tokens(s: str):
        s = (s or "").lower()
        parts = re.split(r"[^a-z0-9+#+\-]+", s)
        stop = {"the","and","with","for","a","an","to","of","in","on","is","as","by","at","be","or","from","that","this","we","you"}
        return [p for p in parts if p and len(p) > 2 and p not in stop]

    job_tokens = set(tokens(job_text))
    if not job_tokens:
        return {"error": "job_text is required and should contain searchable tokens."}

    # Perform a DuckDuckGo HTML search (lightweight, no JS)
    try:
        params = {"q": job_text + " job"}
        resp = requests.get("https://html.duckduckgo.com/html/", params=params, timeout=8, headers={"User-Agent": "jobmatch-ai-bot/1.0"})
        resp.raise_for_status()
    except Exception as e:
        return {"error": f"search failed: {e}"}

    soup = BeautifulSoup(resp.text, "html.parser")
    links = []
    # DuckDuckGo's HTML results put links in <a class="result__a"> often;
    for a in soup.select('a.result__a'):
        href = a.get('href')
        if href and href.startswith('http'):
            links.append(href)
    # Fallback: any external links
    if not links:
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith('http'):
                links.append(href)

    links = links[:max_results]

    results = []
    scores = []
    for url in links:
        try:
            r = requests.get(url, timeout=8, headers={"User-Agent": "jobmatch-ai-bot/1.0"})
            r.raise_for_status()
            page = BeautifulSoup(r.text, "html.parser")
            text = page.get_text(separator=' ')
        except Exception:
            text = ""

        page_tokens = set(tokens(text))
        matched = job_tokens & page_tokens
        score = round((len(matched) / len(job_tokens)) * 100) if job_tokens else 0
        scores.append(score)
        results.append({
            "url": url,
            "score": score,
            "matched_terms": sorted(list(matched))[:30],
            "snippet": (text or '')[:300]
        })

    avg = round(sum(scores) / len(scores)) if scores else 0

    return {"average_match": f"{avg}%", "results": results}



@app.post("/api/ollama_match")
async def ollama_match(
    job_text: str = Form(...),
    resume: Optional[UploadFile] = File(None),
    model: str = Form('gemma3:4b'),
    timeout: int = Form(20),
):
    """
    Use local Ollama (via CLI) to compare resume text and job_text.

    This endpoint constructs a prompt asking the model to produce a JSON
    object with fields: score (0-100), strengths (list), missing_skills (list),
    and recommendation (string). It calls the `ollama` CLI and returns the parsed JSON.

    Note: This uses the `ollama` CLI available on the host. If you prefer an
    HTTP-based integration, set `model` and we can adapt the code.
    """
    # Reuse the simple text extraction helper (best-effort)
    def extract_text_from_upload(upload: Optional[UploadFile]):
        if not upload:
            return ""
        try:
            content = upload.file.read()
            upload.file.seek(0)
            return content.decode('utf-8', errors='ignore')
        except Exception:
            return ""

    resume_text = extract_text_from_upload(resume)

    prompt = (
        "You are an assistant that compares a candidate resume to a job description.\n"
        "Input: a JSON object with keys 'job_text' and 'resume_text'.\n"
        "Output: ONLY a JSON object with the following keys:\n"
        "- score: integer from 0 to 100 representing overall match\n"
        "- strengths: array of short strings (skills the resume has)\n"
        "- missing_skills: array of short strings (skills in job but missing in resume)\n"
        "- recommendation: short action-oriented advice.\n"
        "Do not include any additional text.\n\n"
        "Now process the input and produce the JSON.\n\n"
        "INPUT_JSON: {\"job_text\": " + json.dumps(job_text) + ", \"resume_text\": " + json.dumps(resume_text) + "}"
    )

    # Use the Ollama CLI by default (more reliable local concatenated output).
    out = ""
    try:
        completed = subprocess.run(
            ["ollama", "run", model, prompt],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except FileNotFoundError:
        return {"error": "ollama CLI not found. Ensure ollama is installed and on PATH."}
    except subprocess.TimeoutExpired:
        return {"error": "ollama call timed out"}

    out = (completed.stdout or completed.stderr or "").strip()
    # Strip common ANSI/control sequences that may be present in model output
    try:
        import re as _re
        out = _re.sub(r"\x1B\[[0-9;]*[A-Za-z]", "", out)
    except Exception:
        pass

    # Try to find a JSON object in the output. Ollama's HTTP API may stream
    # many small JSON objects (one per chunk) where the model text appears
    # in a "response" field. The model's produced JSON may be embedded inside
    # that streamed text (possibly with code fences), so attempt several
    # extraction strategies and return the first valid JSON object found.
    def _extract_first_json(text: str):
        import re

        # Fast path: if the whole response is valid JSON, return it
        try:
            return json.loads(text)
        except Exception:
            pass

        # Search for balanced-brace substrings and try to parse them.
        # Iterate over all '{' positions and attempt to find a matching '}'
        starts = [m.start() for m in re.finditer(r"\\{", text)]
        ends = [m.start() for m in re.finditer(r"\\}", text)]
        for s in starts:
            for e in ends:
                if e <= s:
                    continue
                cand = text[s : e + 1]
                try:
                    return json.loads(cand)
                except Exception:
                    continue

        # As a last effort, try to find JSON inside triple-backtick fences
        # allow optional fence language like ```json
        code_fence = re.search(r"```(?:\w+)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if code_fence:
            try:
                return json.loads(code_fence.group(1))
            except Exception:
                pass

        return None

    # If the HTTP API returned a streaming sequence of small JSON objects
    # (one per chunk) that include a 'response' field, reconstruct the
    # model text by concatenating those 'response' values in order, then
    # attempt to extract JSON from that reconstructed text.
    reconstructed = None
    try:
        lines = [ln for ln in out.splitlines() if ln.strip()]
        parts = []
        for ln in lines:
            try:
                jln = json.loads(ln)
            except Exception:
                # not a JSON line — skip
                continue
            if isinstance(jln, dict) and 'response' in jln:
                parts.append(str(jln.get('response') or ''))
        if parts:
            reconstructed = ''.join(parts)
    except Exception:
        reconstructed = None

    if reconstructed:
        parsed_rec = _extract_first_json(reconstructed)
        if parsed_rec is not None:
            return parsed_rec

    # Final attempt: run the general extractor on the raw output
    parsed = _extract_first_json(out)
    if parsed is not None:
        return parsed

    # If the model placed JSON inside code-fence markers (```...```),
    # extract the fenced content and attempt to parse JSON from it.
    try:
        if '```' in out:
            first = out.find('```')
            last = out.rfind('```')
            if first != -1 and last != -1 and last > first:
                fenced = out[first+3:last]
                s = fenced.find('{')
                e = fenced.rfind('}')
                if s != -1 and e != -1 and e > s:
                    candidate = fenced[s:e+1]
                    try:
                        return json.loads(candidate)
                    except Exception:
                        pass
    except Exception:
        pass

    return {"error": "Failed to parse model output as JSON", "raw_output": out}


# Mount frontend static files after API routes so API paths (e.g. /api/health)
# are matched first. Serving at `/` allows opening the app at
# http://127.0.0.1:8000 without editing frontend paths.
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)

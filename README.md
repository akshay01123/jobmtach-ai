# JobMatch AI

JobMatch AI is a small portfolio project foundation for analyzing how well a resume matches a job description.

Current status
- Project scaffold and basic frontend + backend foundation.
- Frontend: landing/application page with drag-and-drop resume and job description inputs.
- Backend: FastAPI placeholder with health and analyze endpoints (no AI logic yet).

Planned AI features
- PDF / DOCX parsing for resumes and job descriptions
- Text normalization, skill extraction, and experience parsing
- Embeddings and semantic matching using vector search
- LLM-based explanation and tailored recommendations

Technology stack
- Frontend: HTML5, CSS3, vanilla JavaScript (no frameworks)
- Backend: Python, FastAPI, Uvicorn

Getting started

1. Frontend

	 - Open `frontend/index.html` in your browser for the static frontend. The UI is designed to call the backend at `/api/analyze`.

2. Backend

	 - Create and activate a Python virtual environment (recommended):

		 python -m venv .venv
		 source .venv/bin/activate

	 - Install dependencies:

		 pip install -r requirements.txt

	 - Run the development server:

		 uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000

	 - Health check: GET http://127.0.0.1:8000/api/health

Notes
- This initial commit intentionally does NOT implement any AI or parsing logic. The `/api/analyze` endpoint returns a placeholder JSON so the frontend can be wired up.
- Keep the frontend and backend clearly separated so AI components (parsers, embeddings, LLM clients) can be added later.

If you'd like, I can now run a quick verification to list the created files and start the backend server locally.

"""
Resume Screening & Job-Matching API
-------------------------------------
Run locally with:
    uvicorn app.main:app --reload

Then open http://127.0.0.1:8000/docs for interactive Swagger UI.
"""

import shutil
import tempfile
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.parser import parse_file, parse_document, ParsedDocument
from app.matcher import compute_match
from app.suggestions import generate_suggestions
from app.models import ParsedDocumentResponse, MatchResponse, SuggestionResponse

app = FastAPI(
    title="Resume Screening & Job-Matching API",
    description="Upload a resume and a job description to get a match score.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _to_response(doc: ParsedDocument) -> ParsedDocumentResponse:
    return ParsedDocumentResponse(
        email=doc.email,
        phone=doc.phone,
        skills=doc.skills,
        degrees=doc.degrees,
        years_experience=doc.years_experience,
    )


@app.get("/")
def health_check():
    return {"status": "ok", "message": "Resume matcher API is running"}


@app.post("/parse-resume", response_model=ParsedDocumentResponse)
async def parse_resume(file: UploadFile = File(...)):
    """Upload a PDF/DOCX/TXT resume and get back structured data."""
    suffix = Path(file.filename).suffix.lower()
    if suffix not in (".pdf", ".docx", ".txt"):
        raise HTTPException(status_code=400, detail="Only PDF, DOCX, or TXT files are supported.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        parsed = parse_file(tmp_path)
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    return _to_response(parsed)


@app.post("/match", response_model=MatchResponse)
async def match_resume_to_job(
    file: UploadFile = File(...),
    job_text: str = Form(...),
):
    """
    Upload a resume file + provide job description text as a form field.
    Returns overall match score plus a skill-level breakdown.
    """
    suffix = Path(file.filename).suffix.lower()
    if suffix not in (".pdf", ".docx", ".txt"):
        raise HTTPException(status_code=400, detail="Only PDF, DOCX, or TXT files are supported.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        resume_parsed = parse_file(tmp_path)
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    job_parsed = parse_document(job_text)
    result = compute_match(resume_parsed, job_parsed)
    suggestions = generate_suggestions(resume_parsed, job_parsed, result)

    return MatchResponse(
        overall_score=result.overall_score,
        text_similarity=result.text_similarity,
        skill_overlap_score=result.skill_overlap_score,
        matched_skills=result.matched_skills,
        missing_skills=result.missing_skills,
        suggestions=[
            SuggestionResponse(category=s.category, priority=s.priority, message=s.message)
            for s in suggestions
        ],
    )
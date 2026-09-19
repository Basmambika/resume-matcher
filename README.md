# Resume Screening & Job-Matching System

An NLP-based system that parses resumes and job descriptions, scores
how well they match, and generates actionable improvement suggestions —
built as a 7th-semester CSE project.

**Live demo flow:** upload a resume → paste a job description → get a
match score, a skill-level breakdown, and specific advice on what to
fix. Full-stack: FastAPI backend + browser-based frontend, no build
tools required to run either.

## Features

- **Resume & job description parsing** — extracts email, phone,
  skills, degree, and years of experience from PDF, DOCX, or TXT files
- **Match scoring** — combines TF-IDF text similarity with exact
  skill-overlap scoring (weighted 40/60)
- **Skill gap analysis** — shows exactly which required skills are
  present vs. missing
- **Improvement suggestions** — plain-English, prioritized advice
  (skills, experience, education, overall fit) generated from the
  match result
- **Evaluation suite** — a labeled test set with accuracy/precision
  reporting, so scoring quality is measured, not assumed

## Project Structure
resume-matcher/
├── app/
│ ├── main.py # FastAPI app (API endpoints)
│ ├── parser.py # Resume/JD text extraction + skill extraction
│ ├── matcher.py # TF-IDF + skill-overlap scoring engine
│ ├── suggestions.py # Turns match results into actionable advice
│ ├── evaluate.py # Labeled test set + accuracy/precision report
│ └── models.py # Pydantic request/response schemas
├── data/ # Place sample resumes/job postings here
├── requirements.txt
└── README.md


There's also a standalone frontend (`resume-matcher-frontend.html`) —
a single self-contained HTML file with no build step. Open it directly
in a browser once the API is running.

## Setup

```bash
python -m venv venv
venv\Scripts\activate       # Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
```

## Run the API

```bash
uvicorn app.main:app --reload
```

Open **http://127.0.0.1:8000/docs** for interactive Swagger UI, or
open `resume-matcher-frontend.html` directly in a browser for the full
visual experience (score, skill chips, suggestion cards).

## Run the evaluation

```bash
python -m app.evaluate
```

**Current results (15-pair labeled starter set):**
- Accuracy: 100%
- Precision (good-match predictions): 100%

⚠️ **Honesty note for your report:** this starter set uses clearly
distinct pairs (e.g. a Python job vs. a Python resume, a designer vs.
a backend role), which is why accuracy is this high. Real resumes have
much more overlap and ambiguity. Expand `TEST_PAIRS` in `evaluate.py`
to 50+ real resume/job pairs for a defensible, presentation-worthy
number — the methodology (labeled pairs → predicted label via
threshold → accuracy/precision) is already in place and will work the
same way with more/better data.

## How scoring works
overall_score = 0.4 × text_similarity + 0.6 × skill_overlap


- **text_similarity**: TF-IDF cosine similarity between full resume
  and job description text
- **skill_overlap**: % of the job's required skills found in the
  resume

Weights are tunable in `matcher.py` (`compute_match`). Once you have a
larger labeled set, sweep these weights and pick whichever maximizes
precision on your data — that sweep + resulting number is a strong
addition to a project report.

## Known limitations / next steps

- **Skill taxonomy is a fixed keyword list** (`SKILL_KEYWORDS` in
  `parser.py`). Skills phrased differently than the list, or not on it
  at all, won't be detected. Swapping to embeddings (see below) fixes
  this at the cost of needing a model download.
- **TF-IDF has no semantic understanding** — "Python developer" and
  "Software engineer skilled in Python" score lower than they should.
  `sentence-transformers` embeddings (commented out in
  `requirements.txt`) fix this — same `matcher.py` structure, swap
  cosine similarity to run on embeddings instead of TF-IDF vectors.
- **No database** — everything is stateless per-request. Add
  PostgreSQL/SQLite to store parsed resumes/postings and support a
  "rank all candidates for this job" recruiter view.
- **No authentication / no deployment** — this runs locally only.
  Deploying (e.g. Render, Railway) and adding basic auth would be a
  natural extension for a stronger portfolio piece.

## Resume bullet point (draft)

> Built a full-stack NLP resume-job matching system (FastAPI + vanilla
> JS) using TF-IDF similarity and rule-based skill extraction;
> generated prioritized improvement suggestions and evaluated
> accuracy/precision on a labeled test set.

## Project roadmap (completed)

- [x] Week 1-2: Project setup
- [x] Week 3-4: Resume parsing pipeline
- [x] Week 5: Job description parsing
- [x] Week 6-7: Matching engine (TF-IDF + skill overlap)
- [x] Week 8: Backend API
- [x] Week 9: Frontend (browser-based, no build tools)
- [x] Week 10: Evaluation on labeled test set
- [x] Week 11: Resume improvement suggestions
- [ ] Week 12: Demo video + final submission polish
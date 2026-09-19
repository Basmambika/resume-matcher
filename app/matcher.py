"""
Matching Engine
----------------
Scores how well a resume matches a job description using two signals:

1. TF-IDF cosine similarity on the full raw text (captures overall
   textual/contextual similarity).
2. Explicit skill-set overlap (captures exact must-have skill matches,
   which recruiters care about most).

Final score is a weighted combination. This is intentionally simple and
dependency-light (scikit-learn only) so it runs anywhere. Swap in
sentence-transformers embeddings later for semantic matching that
doesn't require exact keyword overlap — see README for the upgrade path.
"""

from dataclasses import dataclass
from typing import List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.parser import ParsedDocument


@dataclass
class MatchResult:
    overall_score: float          # 0-100
    text_similarity: float        # 0-100, TF-IDF cosine similarity
    skill_overlap_score: float    # 0-100, % of required skills present
    matched_skills: List[str]
    missing_skills: List[str]


def text_similarity_score(resume_text: str, job_text: str) -> float:
    """Cosine similarity between TF-IDF vectors of the two documents."""
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform([resume_text, job_text])
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return round(float(similarity) * 100, 2)


def skill_overlap_score(resume_skills: List[str], job_skills: List[str]) -> tuple:
    """Returns (score_0_to_100, matched_skills, missing_skills)."""
    if not job_skills:
        return 0.0, [], []

    resume_set = set(resume_skills)
    job_set = set(job_skills)

    matched = sorted(resume_set & job_set)
    missing = sorted(job_set - resume_set)

    score = round((len(matched) / len(job_set)) * 100, 2)
    return score, matched, missing


def compute_match(
    resume: ParsedDocument,
    job: ParsedDocument,
    text_weight: float = 0.4,
    skill_weight: float = 0.6,
) -> MatchResult:
    """
    Combines text similarity + skill overlap into one score.
    Default weighting favors exact skill match (0.6) over general
    textual similarity (0.4) — tune this based on what your evaluation
    shows works best on your labeled test set.
    """
    text_sim = text_similarity_score(resume.raw_text, job.raw_text)
    skill_score, matched, missing = skill_overlap_score(resume.skills, job.skills)

    overall = round(text_weight * text_sim + skill_weight * skill_score, 2)

    return MatchResult(
        overall_score=overall,
        text_similarity=text_sim,
        skill_overlap_score=skill_score,
        matched_skills=matched,
        missing_skills=missing,
    )


if __name__ == "__main__":
    from app.parser import parse_document

    resume_text = """
    Jane Doe. B.Tech Computer Science.
    Skills: Python, React, Node.js, SQL, Docker, AWS, Machine Learning.
    3 years of experience building REST APIs with Flask and FastAPI.
    """

    job_text = """
    Looking for a Backend Engineer with strong Python skills.
    Required: Python, FastAPI, SQL, Docker, AWS, REST API design.
    2+ years of experience preferred.
    """

    resume_parsed = parse_document(resume_text)
    job_parsed = parse_document(job_text)

    result = compute_match(resume_parsed, job_parsed)
    print(f"Overall Score: {result.overall_score}")
    print(f"Text Similarity: {result.text_similarity}")
    print(f"Skill Overlap: {result.skill_overlap_score}")
    print(f"Matched Skills: {result.matched_skills}")
    print(f"Missing Skills: {result.missing_skills}")

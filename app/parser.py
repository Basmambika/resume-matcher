"""
Resume & Job Description Parser
--------------------------------
Extracts structured data (skills, education, experience) from raw
resume/job-description text. Uses a keyword/regex based approach so it
works with zero external model downloads. You can swap in spaCy NER
later for more robust name/org extraction (see README).
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional

import pdfplumber
import docx


# --------------------------------------------------------------------
# Skill taxonomy — extend this list as needed for your dataset/domain
# --------------------------------------------------------------------
SKILL_KEYWORDS = [
    # Languages
    "python", "java", "c++", "c#", "c", "javascript", "typescript", "go",
    "golang", "rust", "kotlin", "swift", "php", "ruby", "r", "scala",
    "matlab", "dart",
    # Frontend
    "react", "angular", "vue", "next.js", "redux", "html", "css",
    "tailwind", "bootstrap", "jquery", "sass",
    # Backend / frameworks
    "node.js", "express", "django", "flask", "fastapi", "spring",
    "spring boot", ".net", "asp.net", "laravel", "graphql", "rest api",
    "microservices", "grpc",
    # Databases
    "sql", "mysql", "postgresql", "mongodb", "redis", "sqlite",
    "oracle", "cassandra", "firebase", "dynamodb", "elasticsearch",
    # Cloud / DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform",
    "jenkins", "ci/cd", "linux", "git", "github", "gitlab", "ansible",
    "nginx",
    # Data / ML / AI
    "machine learning", "deep learning", "nlp", "computer vision",
    "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "keras",
    "opencv", "spark", "hadoop", "tableau", "power bi", "excel",
    "data analysis", "data visualization", "statistics", "matplotlib",
    "seaborn", "etl", "airflow",
    # CS fundamentals
    "data structures", "algorithms", "object oriented programming",
    "oop", "system design", "operating systems", "computer networks",
    "dbms",
    # Practices / tools
    "agile", "scrum", "jira", "postman", "figma", "unit testing",
    "test driven development", "tdd",
]

DEGREE_KEYWORDS = [
    "b.tech", "btech", "b.e.", "b.e", "bachelor of engineering",
    "bachelor", "m.tech", "mtech", "m.e.", "m.e", "master of engineering",
    "master", "mca", "bca", "b.sc", "bsc", "m.sc", "msc", "phd", "ph.d",
    "diploma", "b.com", "bcom",
]

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3,4}\)?[-.\s]?\d{3}[-.\s]?\d{3,4}")
EXPERIENCE_RE = re.compile(r"(\d+)\+?\s*(?:years?|yrs?)", re.IGNORECASE)
# Catches date ranges like "2021 - 2023", "2021-2023", "2021 to Present"
DATE_RANGE_RE = re.compile(
    r"(19|20)\d{2}\s*(?:-|to|–|—)\s*((19|20)\d{2}|present|current)",
    re.IGNORECASE,
)


@dataclass
class ParsedDocument:
    raw_text: str
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: List[str] = field(default_factory=list)
    degrees: List[str] = field(default_factory=list)
    years_experience: Optional[int] = None


def extract_text_from_pdf(file_path: str) -> str:
    text_parts = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)


def extract_text_from_docx(file_path: str) -> str:
    doc = docx.Document(file_path)
    return "\n".join(p.text for p in doc.paragraphs)


def extract_text(file_path: str) -> str:
    """Dispatch based on file extension."""
    lower = file_path.lower()
    if lower.endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    elif lower.endswith(".docx"):
        return extract_text_from_docx(file_path)
    elif lower.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    else:
        raise ValueError(f"Unsupported file type: {file_path}")


def find_skills(text: str) -> List[str]:
    text_lower = text.lower()
    found = []
    # Sort longest-first so "node.js" is checked before the shorter "node"
    # substring skill, then dedupe on words already consumed by a longer match.
    for skill in sorted(SKILL_KEYWORDS, key=len, reverse=True):
        pattern = r"(?<![a-zA-Z0-9])" + re.escape(skill) + r"(?![a-zA-Z0-9])"
        if re.search(pattern, text_lower):
            # skip if this skill is a substring of one already found
            # (e.g. skip "node" if "node.js" already matched)
            if any(skill != f and skill in f for f in found):
                continue
            found.append(skill)
    return found


def find_degrees(text: str) -> List[str]:
    text_lower = text.lower()
    found = []
    for degree in DEGREE_KEYWORDS:
        pattern = r"(?<![a-zA-Z0-9])" + re.escape(degree) + r"(?![a-zA-Z0-9])"
        if re.search(pattern, text_lower):
            found.append(degree)
    return found


def find_years_experience(text: str) -> Optional[int]:
    # 1. Look for explicit "X years"/"X yrs" phrasing first — most reliable.
    matches = EXPERIENCE_RE.findall(text)
    if matches:
        return max(int(m) for m in matches)

    # 2. Fallback: infer from date ranges like "2021 - 2023" or "2021 to
    #    Present" in a work-experience section. This is approximate —
    #    it sums up all date-range durations found, which works for a
    #    single job but double-counts overlapping/multiple entries.
    #    Good enough as a rough signal; flag it as approximate in your
    #    project report if you rely on this path.
    ranges = DATE_RANGE_RE.findall(text)
    if not ranges:
        return None

    from datetime import datetime
    current_year = datetime.now().year
    total_years = 0
    for m in re.finditer(DATE_RANGE_RE, text):
        start_year = int(re.match(r"(19|20)\d{2}", m.group(0)).group(0))
        end_str = m.group(2).lower()
        end_year = current_year if end_str in ("present", "current") else int(end_str)
        if end_year >= start_year:
            total_years += end_year - start_year
    return total_years if total_years > 0 else None


def parse_document(text: str) -> ParsedDocument:
    email_match = EMAIL_RE.search(text)
    phone_match = PHONE_RE.search(text)

    return ParsedDocument(
        raw_text=text,
        email=email_match.group(0) if email_match else None,
        phone=phone_match.group(0) if phone_match else None,
        skills=find_skills(text),
        degrees=find_degrees(text),
        years_experience=find_years_experience(text),
    )


def parse_file(file_path: str) -> ParsedDocument:
    text = extract_text(file_path)
    return parse_document(text)


if __name__ == "__main__":
    # Quick manual test with a plain-text sample
    sample = """
    Jane Doe
    jane.doe@email.com | +1-555-123-4567

    Education: B.Tech in Computer Science

    Skills: Python, React, Node.js, SQL, Docker, AWS, Machine Learning

    Experience: 3 years of experience as a Software Engineer building
    REST APIs with Flask and FastAPI.
    """
    result = parse_document(sample)
    print(result)

"""
Suggestions Engine
-------------------
Turns a match result into plain-English, actionable advice for improving
a resume against a specific job description. This is the "why did I get
this score, and what should I do about it" layer on top of matcher.py.
"""

from dataclasses import dataclass
from typing import List

from app.parser import ParsedDocument
from app.matcher import MatchResult


@dataclass
class Suggestion:
    category: str      # "skills", "experience", "education", "overall"
    priority: str       # "high", "medium", "low"
    message: str


def generate_suggestions(
    resume: ParsedDocument,
    job: ParsedDocument,
    match: MatchResult,
) -> List[Suggestion]:
    suggestions: List[Suggestion] = []

    # --- Skills gaps: the highest-impact, most actionable advice ---
    if match.missing_skills:
        if len(match.missing_skills) <= 3:
            skill_list = ", ".join(match.missing_skills)
            suggestions.append(Suggestion(
                category="skills",
                priority="high",
                message=(
                    f"This job lists {skill_list} as required. If you have "
                    f"experience with these — even from coursework or personal "
                    f"projects — add them explicitly to your Skills section. "
                    f"ATS systems and recruiters often filter on exact keyword "
                    f"matches, not just related experience."
                ),
            ))
        else:
            shown = ", ".join(match.missing_skills[:5])
            remaining = len(match.missing_skills) - 5
            extra = f" and {remaining} more" if remaining > 0 else ""
            suggestions.append(Suggestion(
                category="skills",
                priority="high",
                message=(
                    f"You're missing several skills this job asks for, "
                    f"including {shown}{extra}. This is a significant gap — "
                    f"consider whether this role is a strong fit, or whether "
                    f"you can pick up 1-2 of the most important ones (check "
                    f"the job posting for which are 'required' vs 'nice to "
                    f"have') before applying."
                ),
            ))
    else:
        suggestions.append(Suggestion(
            category="skills",
            priority="low",
            message="Your resume covers every skill this job explicitly lists. Nice — skills won't be the bottleneck here.",
        ))

    # --- Experience gap ---
    if job.years_experience is not None and resume.years_experience is not None:
        gap = job.years_experience - resume.years_experience
        if gap > 0:
            suggestions.append(Suggestion(
                category="experience",
                priority="medium" if gap <= 2 else "high",
                message=(
                    f"This job appears to expect around {job.years_experience} "
                    f"years of experience; your resume shows {resume.years_experience}. "
                    f"If you're short on years, lean on project depth, internships, "
                    f"or specific outcomes in your experience section to show "
                    f"impact rather than tenure."
                ),
            ))
    elif job.years_experience is not None and resume.years_experience is None:
        suggestions.append(Suggestion(
            category="experience",
            priority="medium",
            message=(
                "This job mentions a specific experience requirement, but we "
                "couldn't detect a clear years-of-experience figure on your "
                "resume. Consider stating it explicitly (e.g. '2 years of "
                "experience in...') near the top of your experience section "
                "— vague phrasing can get missed by both ATS filters and quick "
                "human scans."
            ),
        ))

    # --- Education check ---
    if job.degrees and not (set(resume.degrees) & set(job.degrees)):
        job_degrees = ", ".join(job.degrees)
        suggestions.append(Suggestion(
            category="education",
            priority="low",
            message=(
                f"This posting mentions {job_degrees} — double check your "
                f"resume clearly states your degree if it satisfies this "
                f"requirement (sometimes it's a strict formatting/keyword "
                f"match issue, not an actual mismatch)."
            ),
        ))

    # --- Overall framing based on score ---
    if match.overall_score >= 75:
        suggestions.append(Suggestion(
            category="overall",
            priority="low",
            message="Strong overall match. This is a good role to apply to as-is.",
        ))
    elif match.overall_score >= 45:
        suggestions.append(Suggestion(
            category="overall",
            priority="medium",
            message="Moderate match. Worth applying, but the suggestions above will meaningfully strengthen your chances.",
        ))
    else:
        suggestions.append(Suggestion(
            category="overall",
            priority="high",
            message="Low match. This role may not be the best fit right now — consider it a stretch application, or focus effort on roles closer to your current skill set.",
        ))

    return suggestions


if __name__ == "__main__":
    from app.parser import parse_document
    from app.matcher import compute_match

    resume_text = """
    B.Com graduate. Skills: Excel, Tally, Data Entry.
    1 year of experience.
    """
    job_text = """
    Accounts Assistant role. B.Com required.
    Skills needed: Excel, Tally, GST, Bookkeeping.
    2+ years of experience preferred.
    """

    resume = parse_document(resume_text)
    job = parse_document(job_text)
    match = compute_match(resume, job)
    suggestions = generate_suggestions(resume, job, match)

    print(f"Overall score: {match.overall_score}\n")
    for s in suggestions:
        print(f"[{s.priority.upper()}] ({s.category}) {s.message}\n")
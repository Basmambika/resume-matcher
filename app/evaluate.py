"""
Evaluation Script
-------------------
Runs the matcher against a small hand-labeled set of (resume, job
description, expected_label) triples and reports precision.

expected_label is "good_match" or "poor_match" — a human judgment call
based on whether the resume's skills genuinely fit the job's core
requirements.

This is a STARTER set (15 pairs) meant to establish the evaluation
methodology. For your project report, ideally expand this to 50+ pairs
using real resumes/postings — see README for where to find datasets.
Treat threshold=50 as a first cut; tune it against your own labeled
set once you have more data.
"""

from app.parser import parse_document
from app.matcher import compute_match

# Each row: (label, resume_text, job_text)
# label: "good_match" or "poor_match" (human judgment)
TEST_PAIRS = [
    # --- Clear good matches ---
    ("good_match",
     "Python developer. Skills: Python, Django, SQL, Docker, AWS, REST API. 3 years experience.",
     "Backend Engineer needed. Required: Python, Django, SQL, Docker, REST API."),

    ("good_match",
     "Frontend developer. Skills: React, JavaScript, HTML, CSS, Git. 2 years experience building UIs.",
     "Looking for a Frontend Developer with React, JavaScript, HTML, CSS skills."),

    ("good_match",
     "Data analyst. Skills: Python, Pandas, NumPy, SQL, Tableau, Excel, Data Analysis.",
     "Data Analyst role requiring Python, SQL, Tableau, and strong Excel skills."),

    ("good_match",
     "DevOps engineer. Skills: Docker, Kubernetes, AWS, Jenkins, CI/CD, Linux, Terraform.",
     "DevOps role: need Docker, Kubernetes, AWS, CI/CD, and Linux experience."),

    ("good_match",
     "Machine learning engineer. Skills: Python, TensorFlow, PyTorch, Scikit-learn, NLP, Machine Learning.",
     "ML Engineer position requiring Python, TensorFlow, Machine Learning, NLP expertise."),

    ("good_match",
     "Full stack developer. Skills: React, Node.js, MongoDB, Express, JavaScript, Git.",
     "Full Stack Developer needed with React, Node.js, MongoDB experience."),

    ("good_match",
     "B.Com graduate. Skills: Excel, Tally, Accounting, Data Entry.",
     "Accounts Assistant role. Required: Excel, Tally, basic accounting knowledge."),

    # --- Clear poor matches (different domains entirely) ---
    ("poor_match",
     "Graphic designer. Skills: Photoshop, Illustrator, Figma, UI Design, Branding.",
     "Backend Engineer needed. Required: Python, Django, SQL, Docker, REST API."),

    ("poor_match",
     "Mechanical engineer. Skills: AutoCAD, SolidWorks, Thermodynamics, Manufacturing.",
     "Looking for a Frontend Developer with React, JavaScript, HTML, CSS skills."),

    ("poor_match",
     "HR executive. Skills: Recruitment, Onboarding, Payroll, Employee Relations.",
     "ML Engineer position requiring Python, TensorFlow, Machine Learning, NLP expertise."),

    ("poor_match",
     "Content writer. Skills: SEO, Copywriting, WordPress, Content Strategy.",
     "DevOps role: need Docker, Kubernetes, AWS, CI/CD, and Linux experience."),

    ("poor_match",
     "Sales executive. Skills: Cold Calling, CRM, Negotiation, Lead Generation.",
     "Data Analyst role requiring Python, SQL, Tableau, and strong Excel skills."),

    # --- Partial matches (some overlap, but meaningfully incomplete) ---
    ("poor_match",
     "Junior web developer. Skills: HTML, CSS only, no backend experience.",
     "Full Stack Developer needed with React, Node.js, MongoDB, SQL, Docker experience."),

    ("poor_match",
     "Excel-only data entry clerk. Skills: Excel, Data Entry.",
     "Data Scientist role requiring Python, Machine Learning, TensorFlow, Statistics, SQL."),

    ("good_match",
     "Software engineer. Skills: Java, Spring Boot, SQL, Microservices, Git, REST API.",
     "Backend Developer role: Java, Spring Boot, Microservices, SQL required."),
]

THRESHOLD = 50  # overall_score >= this => predicted "good_match"


def run_evaluation():
    results = []
    correct = 0

    for expected_label, resume_text, job_text in TEST_PAIRS:
        resume = parse_document(resume_text)
        job = parse_document(job_text)
        match = compute_match(resume, job)

        predicted_label = "good_match" if match.overall_score >= THRESHOLD else "poor_match"
        is_correct = predicted_label == expected_label
        correct += is_correct

        results.append({
            "expected": expected_label,
            "predicted": predicted_label,
            "correct": is_correct,
            "score": match.overall_score,
            "resume_snippet": resume_text[:50] + "...",
            "job_snippet": job_text[:50] + "...",
        })

    accuracy = correct / len(TEST_PAIRS) * 100

    # Precision for "good_match" predictions specifically
    predicted_good = [r for r in results if r["predicted"] == "good_match"]
    true_positives = [r for r in predicted_good if r["expected"] == "good_match"]
    precision = (len(true_positives) / len(predicted_good) * 100) if predicted_good else 0

    return results, accuracy, precision


def print_report(results, accuracy, precision):
    print("=" * 70)
    print("EVALUATION REPORT")
    print("=" * 70)
    print(f"{'#':<3} {'Expected':<12} {'Predicted':<12} {'Score':<7} {'Correct':<8}")
    print("-" * 70)
    for i, r in enumerate(results, 1):
        mark = "✓" if r["correct"] else "✗"
        print(f"{i:<3} {r['expected']:<12} {r['predicted']:<12} {r['score']:<7} {mark}")
    print("-" * 70)
    print(f"Total pairs tested: {len(results)}")
    print(f"Overall accuracy:   {accuracy:.1f}%")
    print(f"Precision (good_match predictions): {precision:.1f}%")
    print("=" * 70)

    misses = [r for r in results if not r["correct"]]
    if misses:
        print("\nMisclassified pairs (review these first):")
        for r in misses:
            print(f"  - Expected {r['expected']}, got {r['predicted']} (score={r['score']})")
            print(f"    Resume: {r['resume_snippet']}")
            print(f"    Job:    {r['job_snippet']}")


if __name__ == "__main__":
    results, accuracy, precision = run_evaluation()
    print_report(results, accuracy, precision)

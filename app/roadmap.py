"""
Roadmap Engine
---------------
Turns a list of missing skills into a concrete learning plan — what to
study, roughly how long it takes, and where to start. This is the
"come back next time ready" layer, meant to be genuinely useful advice
rather than just a list of keywords.

RESOURCE_MAP is a small curated set covering the most common skills in
SKILL_KEYWORDS (parser.py). Anything not in the map falls back to a
sensible generic suggestion so the roadmap never comes up empty.
"""

from dataclasses import dataclass
from typing import List

# skill -> (resource name, url, estimated time to a working level)
RESOURCE_MAP = {
    "python": ("Python official tutorial", "https://docs.python.org/3/tutorial/", "2-3 weeks"),
    "java": ("Java Programming (freeCodeCamp)", "https://www.freecodecamp.org/news/tag/java/", "3-4 weeks"),
    "javascript": ("The Odin Project - JavaScript", "https://www.theodinproject.com/", "3-4 weeks"),
    "sql": ("SQLBolt - interactive SQL lessons", "https://sqlbolt.com/", "1-2 weeks"),
    "react": ("React official docs", "https://react.dev/learn", "3-4 weeks"),
    "node.js": ("Node.js official guides", "https://nodejs.org/en/learn", "2-3 weeks"),
    "django": ("Django official tutorial", "https://docs.djangoproject.com/en/stable/intro/tutorial01/", "2-3 weeks"),
    "flask": ("Flask Mega-Tutorial", "https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world", "1-2 weeks"),
    "fastapi": ("FastAPI official tutorial", "https://fastapi.tiangolo.com/tutorial/", "1-2 weeks"),
    "docker": ("Docker official getting started", "https://docs.docker.com/get-started/", "1-2 weeks"),
    "kubernetes": ("Kubernetes basics tutorial", "https://kubernetes.io/docs/tutorials/kubernetes-basics/", "3-4 weeks"),
    "aws": ("AWS Cloud Practitioner Essentials (free)", "https://aws.amazon.com/training/digital/aws-cloud-practitioner-essentials/", "2-3 weeks"),
    "git": ("Git official book (Pro Git)", "https://git-scm.com/book/en/v2", "3-5 days"),
    "machine learning": ("Andrew Ng's Machine Learning Specialization", "https://www.coursera.org/specializations/machine-learning-introduction", "6-8 weeks"),
    "deep learning": ("Deep Learning Specialization (deeplearning.ai)", "https://www.coursera.org/specializations/deep-learning", "8-10 weeks"),
    "nlp": ("Hugging Face NLP Course", "https://huggingface.co/learn/nlp-course", "4-5 weeks"),
    "pandas": ("Pandas official getting started", "https://pandas.pydata.org/docs/getting_started/index.html", "1-2 weeks"),
    "numpy": ("NumPy official quickstart", "https://numpy.org/doc/stable/user/quickstart.html", "3-5 days"),
    "tensorflow": ("TensorFlow official tutorials", "https://www.tensorflow.org/tutorials", "4-5 weeks"),
    "pytorch": ("PyTorch official tutorials", "https://pytorch.org/tutorials/", "4-5 weeks"),
    "tableau": ("Tableau free training videos", "https://www.tableau.com/learn/training", "1-2 weeks"),
    "power bi": ("Power BI guided learning (Microsoft)", "https://learn.microsoft.com/en-us/power-bi/guided-learning/", "1-2 weeks"),
    "excel": ("Excel Skills for Business (Coursera, free audit)", "https://www.coursera.org/specializations/excel", "1-2 weeks"),
    "rest api": ("REST API design basics", "https://restfulapi.net/", "1 week"),
    "data structures": ("freeCodeCamp Data Structures course", "https://www.freecodecamp.org/learn/", "3-4 weeks"),
    "algorithms": ("NeetCode - structured DSA practice", "https://neetcode.io/", "4-6 weeks"),
    "system design": ("System Design Primer (GitHub)", "https://github.com/donnemartin/system-design-primer", "4-6 weeks"),
    "agile": ("Atlassian Agile Coach", "https://www.atlassian.com/agile", "3-5 days"),
    "scrum": ("Scrum.org Learning Series", "https://www.scrum.org/resources", "3-5 days"),
    "linux": ("Linux Journey (interactive)", "https://linuxjourney.com/", "2-3 weeks"),
    "ci/cd": ("CI/CD basics (GitHub Actions docs)", "https://docs.github.com/en/actions/learn-github-actions", "1-2 weeks"),
    "mongodb": ("MongoDB official basics course", "https://learn.mongodb.com/", "1-2 weeks"),
    "html": ("MDN HTML basics", "https://developer.mozilla.org/en-US/docs/Learn/HTML", "1 week"),
    "css": ("MDN CSS basics", "https://developer.mozilla.org/en-US/docs/Learn/CSS", "1-2 weeks"),
    "gst": ("GST basics (ClearTax guide)", "https://cleartax.in/s/gst-law-goods-and-services-tax", "1 week"),
    "tally": ("Tally official tutorials", "https://tallysolutions.com/tally-tutorials/", "1-2 weeks"),
    "microservices": ("Microservices.io patterns guide", "https://microservices.io/", "3-4 weeks"),
}

GENERIC_FALLBACK_TIME = "1-2 weeks"


@dataclass
class RoadmapItem:
    skill: str
    resource_name: str
    resource_url: str
    estimated_time: str


def generate_roadmap(missing_skills: List[str]) -> List[RoadmapItem]:
    """
    Turns missing skills into an ordered learning plan. Order preserves
    the order skills were listed in (typically alphabetical from the
    matcher), which is fine for a short list — for a longer list you
    might want to sort by how frequently each skill appears across job
    postings in your domain, if you have that data.
    """
    roadmap = []
    for skill in missing_skills:
        if skill in RESOURCE_MAP:
            name, url, time = RESOURCE_MAP[skill]
        else:
            name = f"Search '{skill} tutorial' on freeCodeCamp or the official docs"
            url = f"https://www.google.com/search?q={skill.replace(' ', '+')}+tutorial+official+docs"
            time = GENERIC_FALLBACK_TIME

        roadmap.append(RoadmapItem(
            skill=skill,
            resource_name=name,
            resource_url=url,
            estimated_time=time,
        ))
    return roadmap


if __name__ == "__main__":
    sample_missing = ["python", "docker", "kubernetes", "some_unlisted_skill"]
    for item in generate_roadmap(sample_missing):
        print(f"{item.skill:<20} {item.estimated_time:<12} {item.resource_name}")
        print(f"  -> {item.resource_url}")
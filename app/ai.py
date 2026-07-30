import re

from sentence_transformers import SentenceTransformer
import numpy as np

# Loaded once at import time — reused for every request.
_model = SentenceTransformer("all-MiniLM-L6-v2")


def get_similarity_score(text_a: str, text_b: str) -> float:
    """
    Embeds both texts and returns cosine similarity scaled to 0-100.
    """
    embeddings = _model.encode([text_a, text_b])
    vec_a, vec_b = embeddings[0], embeddings[1]

    cosine_sim = np.dot(vec_a, vec_b) / (np.linalg.norm(vec_a) * np.linalg.norm(vec_b))
    score = float(cosine_sim) * 100
    return round(max(0.0, min(100.0, score)), 2)


# A small curated list of common tech/soft skills.
# Extend this list freely — it directly controls what matched_skills/missing_skills can contain.
SKILL_TAXONOMY = [
    "Python", "Java", "JavaScript", "TypeScript", "C++", "Go", "Rust",
    "FastAPI", "Django", "Flask", "React", "Vue", "Angular", "Node.js",
    "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis",
    "Docker", "Kubernetes", "AWS", "GCP", "Azure",
    "Git", "CI/CD", "Linux", "REST API", "GraphQL",
    "Machine Learning", "Deep Learning", "NLP", "Pandas", "NumPy",
    "SQLAlchemy", "Pytest", "Agile", "Scrum",
    "Communication", "Leadership", "Problem Solving",
]


def extract_skills(text: str) -> list[str]:
    """
    Returns the subset of SKILL_TAXONOMY found in `text`,
    matched case-insensitively on word boundaries.
    """
    found = []
    for skill in SKILL_TAXONOMY:
        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"
        if re.search(pattern, text, flags=re.IGNORECASE):
            found.append(skill)
    return found


def compare_skills(resume_text: str, required_skills: list[str]) -> tuple[list[str], list[str]]:
    """
    Given resume text and a job's required skills list,
    returns (matched_skills, missing_skills).
    """
    resume_skills = set(extract_skills(resume_text))
    required = set(required_skills)

    matched = sorted(resume_skills & required)
    missing = sorted(required - resume_skills)
    return matched, missing
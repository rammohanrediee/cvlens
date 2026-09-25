import re

from .analysis_data import SKILL_ONTOLOGY

try:
    from pyresparser import ResumeParser
except Exception:
    ResumeParser = None


EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_PATTERN = re.compile(r"(?:(?:\+?\d{1,3}[\s-]?)?(?:\(?\d{3}\)?[\s-]?)?\d{3}[\s-]?\d{4,})")
SECTION_HEADING_PATTERN = re.compile(r"^[A-Z][A-Za-z/&,\-\s]{2,40}$")

SECTION_ALIASES = {
    "summary": ["summary", "professional summary", "profile", "objective"],
    "education": ["education", "academic background", "academics"],
    "experience": ["experience", "work experience", "employment", "professional experience"],
    "projects": ["projects", "project experience", "case studies"],
    "skills": ["skills", "technical skills", "tech stack", "core skills"],
    "certifications": ["certifications", "licenses", "certificates"],
}

DEGREE_PATTERNS = [
    r"\bB\.?\s?Tech\b",
    r"\bM\.?\s?Tech\b",
    r"\bB\.?\s?E\b",
    r"\bM\.?\s?E\b",
    r"\bBCA\b",
    r"\bMCA\b",
    r"\bBSc\b",
    r"\bMSc\b",
    r"\bBachelor(?:'s)?\b",
    r"\bMaster(?:'s)?\b",
    r"\bMBA\b",
    r"\bPh\.?\s?D\b",
]

STOP_HEADINGS = {
    "resume", "curriculum vitae", "education", "experience", "skills",
    "projects", "contact", "summary", "professional summary",
}


def normalize_space(text):
    return re.sub(r"\s+", " ", (text or "")).strip()


def normalize_token(text):
    return re.sub(r"[^a-z0-9+#]+", " ", (text or "").lower()).strip()


def build_skill_alias_map():
    alias_map = {}
    for entry in SKILL_ONTOLOGY:
        canonical = entry["name"]
        for alias in [canonical, *entry.get("aliases", [])]:
            alias_map[normalize_token(alias)] = canonical
    return alias_map


SKILL_ALIAS_MAP = build_skill_alias_map()


def canonicalize_skill(skill):
    normalized = normalize_token(skill)
    return SKILL_ALIAS_MAP.get(normalized, normalize_space(skill))


def extract_email(text):
    match = EMAIL_PATTERN.search(text or "")
    return match.group(0) if match else None


def extract_phone(text):
    for match in PHONE_PATTERN.findall(text or ""):
        digits = re.sub(r"\D", "", match)
        if 10 <= len(digits) <= 13:
            return match.strip()
    return None


def extract_name(text):
    lines = [normalize_space(line) for line in (text or "").splitlines()]
    for line in lines[:8]:
        lowered = line.lower()
        if not line or len(line) < 3 or len(line) > 60:
            continue
        if EMAIL_PATTERN.search(line) or PHONE_PATTERN.search(line):
            continue
        if any(char.isdigit() for char in line):
            continue
        if lowered in STOP_HEADINGS:
            continue
        if SECTION_HEADING_PATTERN.match(line) or line.istitle():
            parts = line.split()
            if 2 <= len(parts) <= 4:
                return line
    return None


def extract_degrees(text):
    found = []
    for pattern in DEGREE_PATTERNS:
        for match in re.finditer(pattern, text or "", flags=re.IGNORECASE):
            degree = normalize_space(match.group(0))
            if degree not in found:
                found.append(degree)
    return found


def split_sections(text):
    sections = {}
    current_key = "general"
    lines = (text or "").splitlines()

    for raw_line in lines:
        line = normalize_space(raw_line)
        if not line:
            continue

        lowered = line.lower().rstrip(":")
        matched_section = None
        for section_key, aliases in SECTION_ALIASES.items():
            if lowered in aliases:
                matched_section = section_key
                break

        if matched_section:
            current_key = matched_section
            sections.setdefault(current_key, [])
            continue

        sections.setdefault(current_key, []).append(line)

    return {key: "\n".join(values) for key, values in sections.items() if values}


def extract_skills_from_text(text):
    lowered = f" {normalize_space(text).lower()} "
    matches = []
    for entry in SKILL_ONTOLOGY:
        aliases = [entry["name"], *entry.get("aliases", [])]
        for alias in aliases:
            pattern = r"(?<![a-z0-9]){}(?![a-z0-9])".format(re.escape(alias.lower()))
            if re.search(pattern, lowered):
                canonical = entry["name"]
                if canonical not in matches:
                    matches.append(canonical)
                break
    return matches


def extract_structured_skills(text):
    sections = split_sections(text)
    scoped_text = "\n".join(
        value for key, value in sections.items()
        if key in {"skills", "projects", "experience", "summary", "general"}
    )
    return extract_skills_from_text(scoped_text or text)


def merge_resume_data(raw_text, parser_data=None):
    parser_data = parser_data or {}
    fallback_skills = extract_structured_skills(raw_text)
    merged_skills = []
    for skill in [*(parser_data.get("skills") or []), *fallback_skills]:
        canonical = canonicalize_skill(skill)
        if canonical and canonical not in merged_skills:
            merged_skills.append(canonical)

    merged = {
        "name": parser_data.get("name") or extract_name(raw_text),
        "email": parser_data.get("email") or extract_email(raw_text),
        "mobile_number": parser_data.get("mobile_number") or extract_phone(raw_text),
        "skills": merged_skills,
        "degree": parser_data.get("degree") or extract_degrees(raw_text),
        "no_of_pages": parser_data.get("no_of_pages") or max(1, (raw_text or "").count("\f") + 1),
    }
    merged["parser_source"] = "hybrid" if parser_data else "fallback"
    return merged


def parse_resume_document(file_path, raw_text):
    parser_data = None
    if ResumeParser is not None:
        try:
            parser_data = ResumeParser(file_path).get_extracted_data()
        except Exception:
            parser_data = None
    return merge_resume_data(raw_text, parser_data)

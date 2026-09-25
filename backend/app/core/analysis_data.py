import re


def normalize_catalog_token(value):
    """Normalize catalog text for stable alias comparisons."""
    return re.sub(r"[^a-z0-9+#]+", " ", (value or "").lower()).strip()


ROLE_CATALOG = [
    {
        "key": "data-analyst",
        "title": "Data Analyst",
        "field": "Data Science",
        "summary": "Analyze business data, build dashboards, write SQL, and turn metrics into operational decisions.",
        "keywords": [
            "sql", "python", "excel", "tableau", "power bi", "data analysis",
            "analytics", "dashboard", "reporting", "visualization", "statistics"
        ],
        "recommended_skills": [
            "SQL", "Power BI", "Tableau", "Data Cleaning",
            "Dashboarding", "Business Metrics", "Excel", "Storytelling"
        ],
        "courses_key": "data_science",
    },
    {
        "key": "data-scientist",
        "title": "Data Scientist",
        "field": "Data Science",
        "summary": "Build predictive models, clean data, run experiments, and communicate findings with statistics and storytelling.",
        "keywords": [
            "python", "sql", "machine learning", "tensorflow", "pytorch", "statistics",
            "data analysis", "scikit-learn", "pandas", "visualization", "experiments"
        ],
        "recommended_skills": [
            "Feature Engineering", "Model Evaluation", "A/B Testing", "Pandas",
            "Scikit-learn", "TensorFlow", "PyTorch", "SQL", "Storytelling"
        ],
        "courses_key": "data_science",
    },
    {
        "key": "machine-learning-engineer",
        "title": "Machine Learning Engineer",
        "field": "Data Science",
        "summary": "Productionize ML systems, build data pipelines, tune models, and deploy reliable data products.",
        "keywords": [
            "machine learning", "python", "mlops", "docker", "api", "deployment",
            "deep learning", "aws", "feature store", "monitoring"
        ],
        "recommended_skills": [
            "MLOps", "Model Serving", "Docker", "FastAPI", "Feature Stores",
            "Monitoring", "Deep Learning", "Cloud Deployment"
        ],
        "courses_key": "data_science",
    },
    {
        "key": "ai-engineer",
        "title": "AI Engineer",
        "field": "Data Science",
        "summary": "Build AI-powered applications, integrate LLM systems, productionize inference pipelines, and evaluate model quality.",
        "keywords": [
            "python", "llm", "rag", "vector database", "prompt engineering", "transformers",
            "api", "evaluation", "embeddings", "mlops", "deployment"
        ],
        "recommended_skills": [
            "LLM Orchestration", "RAG", "Prompt Engineering", "Embeddings",
            "Model Evaluation", "Vector Search", "Serving", "Observability"
        ],
        "courses_key": "data_science",
    },
    {
        "key": "frontend-engineer",
        "title": "Frontend Engineer",
        "field": "Web Development",
        "summary": "Build responsive interfaces, design component systems, and deliver polished user experiences on the web.",
        "keywords": [
            "javascript", "typescript", "react", "next.js", "css", "html",
            "frontend", "ui", "accessibility", "tailwind", "responsive"
        ],
        "recommended_skills": [
            "TypeScript", "Design Systems", "Accessibility", "Next.js",
            "State Management", "Performance Optimization", "Responsive Design"
        ],
        "courses_key": "web",
    },
    {
        "key": "full-stack-engineer",
        "title": "Full Stack Engineer",
        "field": "Web Development",
        "summary": "Build end-to-end products across frontend, backend, APIs, databases, and deployment workflows.",
        "keywords": [
            "javascript", "typescript", "react", "node.js", "api", "postgresql",
            "docker", "frontend", "backend", "authentication", "deployment"
        ],
        "recommended_skills": [
            "System Design", "API Design", "React", "Node.js",
            "PostgreSQL", "Docker", "Authentication", "Testing"
        ],
        "courses_key": "web",
    },
    {
        "key": "backend-engineer",
        "title": "Backend Engineer",
        "field": "Web Development",
        "summary": "Design APIs, scale services, optimize databases, and build resilient backend systems.",
        "keywords": [
            "node.js", "python", "django", "flask", "postgresql", "api",
            "backend", "redis", "docker", "microservices", "authentication"
        ],
        "recommended_skills": [
            "API Design", "Database Indexing", "Caching", "Authentication",
            "Background Jobs", "Observability", "Docker", "PostgreSQL"
        ],
        "courses_key": "web",
    },
    {
        "key": "devops-engineer",
        "title": "DevOps Engineer",
        "field": "Web Development",
        "summary": "Automate delivery pipelines, manage infrastructure, improve reliability, and scale deployment workflows.",
        "keywords": [
            "docker", "kubernetes", "aws", "azure", "gcp", "ci/cd",
            "terraform", "linux", "monitoring", "observability", "cloud"
        ],
        "recommended_skills": [
            "CI/CD", "Terraform", "Kubernetes", "Linux",
            "Cloud Architecture", "Monitoring", "Incident Response", "Automation"
        ],
        "courses_key": "web",
    },
    {
        "key": "qa-engineer",
        "title": "QA Engineer",
        "field": "Web Development",
        "summary": "Improve software quality through automated testing, regression coverage, debugging, and release confidence.",
        "keywords": [
            "testing", "qa", "automation", "selenium", "playwright", "cypress",
            "regression", "bug tracking", "quality assurance", "api testing", "debugging"
        ],
        "recommended_skills": [
            "Test Automation", "Playwright", "API Testing", "Regression Strategy",
            "Quality Metrics", "CI Testing", "Bug Triage", "Debugging"
        ],
        "courses_key": "web",
    },
    {
        "key": "android-developer",
        "title": "Android Developer",
        "field": "Android Development",
        "summary": "Ship polished Android apps, manage app architecture, and integrate mobile-first product experiences.",
        "keywords": [
            "android", "kotlin", "java", "xml", "jetpack", "compose",
            "sqlite", "firebase", "mobile", "gradle"
        ],
        "recommended_skills": [
            "Jetpack Compose", "MVVM", "Firebase", "Android Architecture",
            "Kotlin Coroutines", "Testing", "Play Store Release"
        ],
        "courses_key": "android",
    },
    {
        "key": "ios-developer",
        "title": "iOS Developer",
        "field": "IOS Development",
        "summary": "Develop iOS applications with strong native design, performance, and app store quality.",
        "keywords": [
            "ios", "swift", "swiftui", "xcode", "cocoa", "uikit",
            "mobile", "storekit", "objective-c", "apple"
        ],
        "recommended_skills": [
            "SwiftUI", "UIKit", "App Architecture", "StoreKit",
            "Unit Testing", "Performance Profiling", "App Store Release"
        ],
        "courses_key": "ios",
    },
    {
        "key": "product-designer",
        "title": "Product Designer",
        "field": "UI-UX Development",
        "summary": "Shape user journeys, prototype interfaces, and turn product ideas into intuitive experiences.",
        "keywords": [
            "figma", "ux", "ui", "wireframes", "prototype", "design systems",
            "user research", "accessibility", "visual design", "journeys"
        ],
        "recommended_skills": [
            "Interaction Design", "Design Systems", "User Research", "Accessibility",
            "Prototyping", "Usability Testing", "Visual Hierarchy"
        ],
        "courses_key": "uiux",
    },
    {
        "key": "product-manager",
        "title": "Product Manager",
        "field": "UI-UX Development",
        "summary": "Translate user and business needs into product direction, prioritize roadmaps, and align teams around measurable outcomes.",
        "keywords": [
            "product", "roadmap", "stakeholders", "analytics", "requirements", "experiments",
            "user research", "prioritization", "metrics", "strategy", "delivery"
        ],
        "recommended_skills": [
            "Roadmapping", "Requirements Writing", "Stakeholder Management", "Product Metrics",
            "Experimentation", "User Research", "Prioritization", "Communication"
        ],
        "courses_key": "uiux",
    },
]

SKILL_ONTOLOGY = [
    {"name": "Python", "aliases": ["python", "py"], "category": "Tools"},
    {"name": "SQL", "aliases": ["sql", "mysql", "postgres", "postgresql"], "category": "Tools"},
    {"name": "JavaScript", "aliases": ["javascript", "js"], "category": "Tools"},
    {"name": "TypeScript", "aliases": ["typescript", "ts"], "category": "Tools"},
    {"name": "React", "aliases": ["react", "react.js"], "category": "Tools"},
    {"name": "Next.js", "aliases": ["next.js", "nextjs"], "category": "Tools"},
    {"name": "Node.js", "aliases": ["node.js", "nodejs", "node"], "category": "Tools"},
    {"name": "FastAPI", "aliases": ["fastapi"], "category": "Tools"},
    {"name": "Flask", "aliases": ["flask"], "category": "Tools"},
    {"name": "Django", "aliases": ["django"], "category": "Tools"},
    {"name": "Docker", "aliases": ["docker", "containerization"], "category": "Tools"},
    {"name": "AWS", "aliases": ["aws", "amazon web services"], "category": "Tools"},
    {"name": "Azure", "aliases": ["azure"], "category": "Tools"},
    {"name": "GCP", "aliases": ["gcp", "google cloud"], "category": "Tools"},
    {"name": "TensorFlow", "aliases": ["tensorflow"], "category": "Tools"},
    {"name": "PyTorch", "aliases": ["pytorch"], "category": "Tools"},
    {"name": "Scikit-learn", "aliases": ["scikit-learn", "sklearn"], "category": "Tools"},
    {"name": "Pandas", "aliases": ["pandas"], "category": "Tools"},
    {"name": "Tableau", "aliases": ["tableau"], "category": "Tools"},
    {"name": "Power BI", "aliases": ["power bi", "powerbi"], "category": "Tools"},
    {"name": "Figma", "aliases": ["figma"], "category": "Tools"},
    {"name": "Git", "aliases": ["git", "github", "gitlab", "version control"], "category": "Tools"},
    {"name": "Linux", "aliases": ["linux", "unix", "bash", "shell scripting"], "category": "Tools"},
    {"name": "Redis", "aliases": ["redis"], "category": "Tools"},
    {"name": "MongoDB", "aliases": ["mongodb", "mongo db"], "category": "Tools"},
    {"name": "GraphQL", "aliases": ["graphql"], "category": "Tools"},
    {"name": "Celery", "aliases": ["celery", "background jobs", "task queue"], "category": "Tools"},
    {"name": "Pytest", "aliases": ["pytest"], "category": "Tools"},
    {"name": "GitHub Actions", "aliases": ["github actions", "github workflows"], "category": "Tools"},
    {"name": "Jira", "aliases": ["jira", "atlassian jira"], "category": "Tools"},
    {"name": "NumPy", "aliases": ["numpy"], "category": "Tools"},
    {"name": "Matplotlib", "aliases": ["matplotlib"], "category": "Tools"},
    {"name": "Kubernetes", "aliases": ["kubernetes", "k8s"], "category": "Tools"},
    {"name": "Terraform", "aliases": ["terraform"], "category": "Tools"},
    {"name": "CI/CD", "aliases": ["ci/cd", "ci cd", "continuous integration", "continuous delivery"], "category": "Tools"},
    {"name": "Selenium", "aliases": ["selenium"], "category": "Tools"},
    {"name": "Playwright", "aliases": ["playwright"], "category": "Tools"},
    {"name": "Cypress", "aliases": ["cypress"], "category": "Tools"},
    {"name": "Excel", "aliases": ["excel", "microsoft excel"], "category": "Tools"},
    {"name": "LLM", "aliases": ["llm", "large language model", "gpt"], "category": "Tools"},
    {"name": "Transformers", "aliases": ["transformers", "huggingface"], "category": "Tools"},
    {"name": "Vector Search", "aliases": ["vector search", "vector database", "vector db"], "category": "Tools"},
    {"name": "Machine Learning", "aliases": ["machine learning", "ml"], "category": "Skills"},
    {"name": "Deep Learning", "aliases": ["deep learning"], "category": "Skills"},
    {"name": "Data Analysis", "aliases": ["data analysis", "analytics"], "category": "Skills"},
    {"name": "MLOps", "aliases": ["mlops", "machine learning operations"], "category": "Skills"},
    {"name": "Model Serving", "aliases": ["model serving"], "category": "Skills"},
    {"name": "Feature Engineering", "aliases": ["feature engineering"], "category": "Skills"},
    {"name": "A/B Testing", "aliases": ["a/b testing", "ab testing"], "category": "Skills"},
    {"name": "API Design", "aliases": ["api design", "rest api", "api development"], "category": "Skills"},
    {"name": "Caching", "aliases": ["caching", "cache"], "category": "Skills"},
    {"name": "Authentication", "aliases": ["authentication", "authorization", "auth"], "category": "Skills"},
    {"name": "Observability", "aliases": ["observability", "monitoring", "logging"], "category": "Skills"},
    {"name": "Accessibility", "aliases": ["accessibility", "a11y"], "category": "Skills"},
    {"name": "Responsive Design", "aliases": ["responsive design", "responsive"], "category": "Skills"},
    {"name": "Design Systems", "aliases": ["design systems", "design system"], "category": "Skills"},
    {"name": "User Research", "aliases": ["user research"], "category": "Skills"},
    {"name": "Prototyping", "aliases": ["prototype", "prototyping"], "category": "Skills"},
    {"name": "Testing", "aliases": ["testing", "unit testing", "integration testing"], "category": "Evidence"},
    {"name": "API Testing", "aliases": ["api testing"], "category": "Evidence"},
    {"name": "Leadership", "aliases": ["leadership", "led", "mentored", "mentoring"], "category": "Evidence"},
    {"name": "Stakeholder Management", "aliases": ["stakeholder", "stakeholders"], "category": "Evidence"},
    {"name": "Performance Optimization", "aliases": ["performance", "optimization", "optimized"], "category": "Evidence"},
    {"name": "Impact Metrics", "aliases": ["improved", "reduced", "increased", "impact", "results"], "category": "Evidence"},
    {"name": "Roadmapping", "aliases": ["roadmap", "roadmapping"], "category": "Evidence"},
    {"name": "Communication", "aliases": ["communication", "communicated", "presented"], "category": "Evidence"},
    {"name": "Collaboration", "aliases": ["collaboration", "collaborated", "cross-functional"], "category": "Evidence"},
    {"name": "Documentation", "aliases": ["documentation", "documented", "technical writing"], "category": "Evidence"},
    {"name": "Problem Solving", "aliases": ["problem solving", "troubleshooting", "resolved"], "category": "Evidence"},
    {"name": "Fintech", "aliases": ["fintech", "payments", "banking"], "category": "Domain"},
    {"name": "Healthcare", "aliases": ["healthcare", "medical"], "category": "Domain"},
    {"name": "E-commerce", "aliases": ["ecommerce", "e-commerce", "retail"], "category": "Domain"},
    {"name": "SaaS", "aliases": ["saas", "b2b"], "category": "Domain"},
]

SECTION_SCORE_CONFIG = {
    "maximum_score": 100,
    "categories": ["Core Sections", "Experience", "Proof", "Personality", "Positioning"],
}


# These are intentionally data-only rules. Matching code should read ``fallback``
# instead of deciding special cases from a rule label.
SECTION_RULES = [
    {
        "key": "summary",
        "label": "Objective or Summary",
        "category": "Positioning",
        "weight": 6,
        "required": True,
        "patterns": ["objective", "career objective", "professional summary", "summary", "profile", "about me"],
        "fallback": None,
        "success": "You have added an objective or summary section.",
        "warning": "Add a sharp summary tailored to the role you want.",
    },
    {
        "key": "education",
        "label": "Education",
        "category": "Core Sections",
        "weight": 12,
        "required": True,
        "patterns": ["education", "academic background", "academic qualifications", "school", "college", "university"],
        "fallback": None,
        "success": "You have included education details.",
        "warning": "Add education details with your qualification, institution, and graduation year.",
    },
    {
        "key": "experience",
        "label": "Experience",
        "category": "Experience",
        "weight": 16,
        "required": True,
        "patterns": ["experience", "work experience", "professional experience", "work history", "employment", "career history"],
        "fallback": {"type": "bullet_count", "minimum": 2, "score": 8},
        "success": "You have included experience details.",
        "warning": "Add an experience section with ownership, outcomes, and measurable impact.",
    },
    {
        "key": "internships",
        "label": "Internships",
        "category": "Experience",
        "weight": 6,
        "required": False,
        "patterns": ["internship", "internships", "industrial training", "trainee experience"],
        "fallback": None,
        "success": "You have included internships.",
        "warning": "If relevant, add internships to show hands-on exposure.",
    },
    {
        "key": "skills",
        "label": "Skills",
        "category": "Core Sections",
        "weight": 7,
        "required": True,
        "patterns": ["skill", "skills", "technical skills", "core competencies", "technical expertise", "tech stack", "technologies"],
        "fallback": None,
        "success": "You have included a skills section.",
        "warning": "Add a focused skills section tailored to your target role.",
    },
    {
        "key": "hobbies",
        "label": "Hobbies",
        "category": "Personality",
        "weight": 4,
        "required": False,
        "patterns": ["hobbies", "hobby", "activities"],
        "fallback": None,
        "success": "You have included hobbies.",
        "warning": "Optional: include hobbies only when they add personality without taking needed space.",
    },
    {
        "key": "interests",
        "label": "Interests",
        "category": "Personality",
        "weight": 5,
        "required": False,
        "patterns": ["interests", "interest", "areas of interest"],
        "fallback": None,
        "success": "You have included interests.",
        "warning": "Optional: include interests only if they support your professional story.",
    },
    {
        "key": "achievements",
        "label": "Achievements",
        "category": "Proof",
        "weight": 13,
        "required": False,
        "patterns": ["achievements", "achievement", "awards", "honors", "accomplishments", "recognition"],
        "fallback": None,
        "success": "You have included achievements.",
        "warning": "Add awards, recognitions, or measurable achievements to strengthen credibility.",
    },
    {
        "key": "certifications",
        "label": "Certifications",
        "category": "Proof",
        "weight": 12,
        "required": False,
        "patterns": ["certifications", "certification", "licenses", "credentials", "professional development"],
        "fallback": None,
        "success": "You have included certifications.",
        "warning": "Add relevant certifications or credentials that support your target role.",
    },
    {
        "key": "projects",
        "label": "Projects",
        "category": "Experience",
        "weight": 19,
        "required": True,
        "patterns": ["projects", "project", "personal projects", "academic projects", "case study", "case studies", "portfolio projects"],
        "fallback": {"type": "bullet_count", "minimum": 2, "score": 9},
        "success": "You have included projects.",
        "warning": "Add projects with your contribution, tools used, and measurable outcomes.",
    },
]

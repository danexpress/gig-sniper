"""Profile, scoring weights, threshold, enabled sources, and env-backed settings."""
import os

from dotenv import load_dotenv

load_dotenv()

PROFILE = {
    "role": "Data Engineer",
    "years_experience": 3,
    "most_recent": "Hootsuite, large-scale ETL/ELT",
    "stack": [
        "Python", "SQL", "AWS", "dbt", "Snowflake", "Spark",
        "Databricks", "Delta Lake", "Kafka", "Flink", "Airflow", "Docker",
    ],
    "looking_for": "Remote data engineering / AI engineering contract work",
}

KEYWORD_WEIGHTS = {
    "python": 8, "sql": 6, "dbt": 10, "snowflake": 10, "airflow": 8,
    "spark": 8, "aws": 6, "databricks": 10, "kafka": 8, "flink": 6,
    "etl": 10, "elt": 10, "pipeline": 6, "data engineer": 12, "ai engineer": 10,
    "delta lake": 8, "docker": 4,
}

STAGE1_CUTOFF = 35       # minimum keyword score before spending an LLM call
SCORE_THRESHOLD = 70     # minimum final score to draft a pitch / enter the digest
BLEND_KEYWORD_WEIGHT = 0.4
BLEND_LLM_WEIGHT = 0.6
RECENCY_DAYS = 3
RECENCY_BONUS = 10
REMOTE_BONUS = 10
RATE_MENTIONED_BONUS = 10

ENABLED_SOURCES = ["remoteok", "weworkremotely", "wellfound"]

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-5")

EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "smtp")  # "smtp" or "resend"
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
DIGEST_TO = os.getenv("DIGEST_TO", SMTP_USER)
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
RESEND_FROM = os.getenv("RESEND_FROM")

SEND_EMPTY_DIGEST = os.getenv("SEND_EMPTY_DIGEST", "false").lower() == "true"

DB_PATH = os.getenv("GIG_SNIPER_DB", "gigs.db")

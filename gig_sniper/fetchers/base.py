import re
from datetime import datetime, timezone
from typing import Protocol

RATE_PATTERN = re.compile(
    r"\$\s?\d{2,4}\s?(?:/|per)\s?(?:hr|hour|day)|\$\d{2,3}[kK]\b|\$\d{1,3},\d{3}",
    re.IGNORECASE,
)


class Fetcher(Protocol):
    name: str

    def fetch(self) -> list[dict]: ...


def extract_rate(text: str) -> str | None:
    match = RATE_PATTERN.search(text or "")
    return match.group(0) if match else None


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib


def make_id(source: str, url: str) -> str:
    return hashlib.sha256(f"{source}:{url}".encode()).hexdigest()


@dataclass
class Gig:
    id: str
    source: str
    title: str
    company: str
    url: str
    description: str
    rate: str | None = None
    remote: bool = True
    posted_at: str | None = None
    fetched_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    score: int = 0
    score_reason: str = ""
    pitch: str | None = None
    notified: bool = False

    @classmethod
    def from_raw(cls, raw: dict) -> "Gig":
        source = raw["source"]
        url = raw["url"]
        return cls(
            id=make_id(source, url),
            source=source,
            title=raw.get("title", "").strip(),
            company=(raw.get("company") or "").strip(),
            url=url,
            description=(raw.get("description") or "").strip(),
            rate=raw.get("rate"),
            remote=bool(raw.get("remote", True)),
            posted_at=raw.get("posted_at"),
        )

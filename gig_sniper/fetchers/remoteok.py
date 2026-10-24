from datetime import datetime

import requests

from .base import extract_rate

NAME = "remoteok"
API_URL = "https://remoteok.com/api"
RELEVANT_TAGS = {
    "data", "data-science", "data-engineer", "etl", "sql", "python",
    "machine-learning", "ai", "analytics", "engineer", "dev", "backend",
}


class RemoteOKFetcher:
    name = NAME

    def fetch(self) -> list[dict]:
        resp = requests.get(API_URL, headers={"User-Agent": "gig-sniper/1.0"}, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        gigs = []
        for item in data:
            if not isinstance(item, dict) or "id" not in item:
                continue  # first element of the feed is a legal notice, not a job
            tags = {t.lower() for t in item.get("tags", [])}
            if not (tags & RELEVANT_TAGS):
                continue

            description = item.get("description", "") or ""
            gigs.append({
                "source": self.name,
                "title": item.get("position", ""),
                "company": item.get("company", ""),
                "url": item.get("url") or f"https://remoteok.com/remote-jobs/{item['id']}",
                "description": description,
                "rate": extract_rate(description),
                "remote": True,
                "posted_at": _parse_date(item.get("date")),
            })
        return gigs


def _parse_date(value) -> str | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).isoformat()
    except (ValueError, AttributeError):
        return None

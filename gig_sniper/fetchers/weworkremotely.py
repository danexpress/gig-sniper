from email.utils import parsedate_to_datetime

import feedparser

from .base import extract_rate

NAME = "weworkremotely"
FEED_URLS = [
    "https://weworkremotely.com/categories/remote-programming-jobs.rss",
    "https://weworkremotely.com/categories/remote-devops-sysadmin-jobs.rss",
]


class WeWorkRemotelyFetcher:
    name = NAME

    def fetch(self) -> list[dict]:
        gigs = []
        for feed_url in FEED_URLS:
            parsed = feedparser.parse(feed_url)
            for entry in parsed.entries:
                description = entry.get("summary", "") or ""
                title = entry.get("title", "")
                company = ""
                if ":" in title:
                    company, _, title = title.partition(":")
                    company, title = company.strip(), title.strip()

                gigs.append({
                    "source": self.name,
                    "title": title,
                    "company": company,
                    "url": entry.get("link", ""),
                    "description": description,
                    "rate": extract_rate(description),
                    "remote": True,
                    "posted_at": _parse_date(entry.get("published")),
                })
        return gigs


def _parse_date(value) -> str | None:
    if not value:
        return None
    try:
        return parsedate_to_datetime(value).isoformat()
    except (ValueError, TypeError):
        return None

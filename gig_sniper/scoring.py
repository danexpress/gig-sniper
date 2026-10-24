from datetime import datetime, timedelta, timezone

import config


def keyword_score(text: str, rate: str | None, remote: bool, posted_at: str | None) -> tuple[int, str]:
    text_lower = text.lower()
    points = 0
    hits = []

    for kw, weight in config.KEYWORD_WEIGHTS.items():
        if kw in text_lower:
            points += weight
            hits.append(kw)

    if rate:
        points += config.RATE_MENTIONED_BONUS
        hits.append("rate mentioned")

    if remote:
        points += config.REMOTE_BONUS
        hits.append("remote")

    if posted_at:
        try:
            posted = datetime.fromisoformat(posted_at)
            if posted.tzinfo is None:
                posted = posted.replace(tzinfo=timezone.utc)
            if datetime.now(timezone.utc) - posted <= timedelta(days=config.RECENCY_DAYS):
                points += config.RECENCY_BONUS
                hits.append("recent")
        except ValueError:
            pass

    score = max(0, min(100, points))
    reason = "Matched: " + ", ".join(hits) if hits else "No keyword matches"
    return score, reason


def blend(keyword_pts: int, llm_pts: int) -> int:
    blended = config.BLEND_KEYWORD_WEIGHT * keyword_pts + config.BLEND_LLM_WEIGHT * llm_pts
    return max(0, min(100, round(blended)))

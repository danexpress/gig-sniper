import json

import anthropic

import config

_client = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    return _client


def _profile_text() -> str:
    p = config.PROFILE
    return (
        f"{p['role']}, {p['years_experience']}+ years. Most recently: {p['most_recent']}.\n"
        f"Stack: {', '.join(p['stack'])}.\n"
        f"Looking for: {p['looking_for']}."
    )


def score_fit(title: str, description: str) -> tuple[int, str]:
    prompt = f"""You are evaluating how well a contract gig matches my profile.

My profile:
{_profile_text()}

Job posting:
Title: {title}
Description: {description[:4000]}

Respond with ONLY a JSON object, no other text: {{"score": <0-100 integer>, "reason": "<one sentence>"}}"""

    resp = _get_client().messages.create(
        model=config.CLAUDE_MODEL,
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )
    text = resp.content[0].text.strip()
    try:
        data = json.loads(text)
        return int(data["score"]), str(data["reason"])
    except (json.JSONDecodeError, KeyError, ValueError):
        return 0, "Could not parse LLM response"


def draft_pitch(title: str, company: str, description: str) -> str:
    prompt = f"""Write a tailored pitch for this contract gig, from me to the client/recruiter.

My profile:
{_profile_text()}

Job posting:
Title: {title}
Company: {company}
Description: {description[:4000]}

Write 4-5 sentences: open with specific relevance to this role, name 1-2 matching stack items, \
state availability for contract work, end with a light call to action. Professional, not salesy. \
Do not fabricate experience beyond my profile. Respond with ONLY the pitch text, no preamble."""

    resp = _get_client().messages.create(
        model=config.CLAUDE_MODEL,
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.content[0].text.strip()

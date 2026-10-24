# Gig Sniper

Finds data/AI contract gigs, scores them against my profile, drafts a pitch for the good ones,
and emails a daily digest. No UI, no auth — run it on a schedule and act on the email.

## Setup

```
pip install -r requirements.txt
cp .env.example .env
# fill in .env: ANTHROPIC_API_KEY, SMTP_USER/SMTP_PASSWORD (Gmail app password) or RESEND_API_KEY
```

Edit `config.py` to adjust the profile, keyword weights, score threshold, or enabled sources.

## Run

```
python main.py
```

First run creates `gigs.db` (SQLite) in the project directory and scores/drafts pitches for
every gig found. Later runs skip gigs already seen (deduped by source + URL) and only email
gigs that haven't been included in a digest yet.

## Schedule (cron, daily 8am)

```
0 8 * * * cd /path/to/gig_sniper && /path/to/python main.py >> run.log 2>&1
```

## Sources

- **Remote OK** — public JSON API, filtered to data/AI-relevant tags.
- **We Work Remotely** — programming + devops category RSS feeds.
- **Wellfound** — stubbed (`fetchers/wellfound.py`); no stable public API, left as a TODO.

## Notes

- Stage 1 scoring is a deterministic keyword match (no API calls). Only gigs clearing
  `STAGE1_CUTOFF` get a Claude fit-score call, to save tokens.
- Final score blends keyword and LLM scores (`BLEND_KEYWORD_WEIGHT` / `BLEND_LLM_WEIGHT`).
- Pitches are only drafted for gigs scoring >= `SCORE_THRESHOLD`.
- If `ANTHROPIC_API_KEY` is unset, the pipeline still runs end-to-end on keyword scores alone
  (no LLM scoring, no pitches) — useful for a first smoke test.

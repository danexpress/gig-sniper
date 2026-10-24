# Gig Sniper — MVP Build Spec

## Goal
A personal tool that finds data/AI contract gigs early, scores them for fit against my profile, drafts a tailored pitch for the good ones, and emails me a daily digest. No UI, no customers, no auth. It runs on a schedule and I act on the digest.

## Non-goals (do NOT build these in v1)
- No web frontend or dashboard
- No auto-sending of pitches (I review and send manually)
- No user accounts, no multi-user anything
- No LinkedIn scraping yet (hardest, add later)

## My profile (used for scoring + pitch drafting)
- Data engineer, 3+ years. Most recently Hootsuite, large-scale ETL/ELT.
- Stack: Python, SQL, AWS, dbt, Snowflake, Spark, Databricks, Delta Lake, Kafka/Flink, Airflow, Docker.
- Looking for: remote data engineering / AI engineering contract work.
- (Keep this in a config file so it's easy to edit.)

## Architecture
Simple pipeline, run end to end on a schedule:

```
fetch (per source) -> normalize -> dedupe -> score -> draft pitch (if score >= threshold) -> store -> email digest
```

- Language: Python 3.11+
- Storage: SQLite (single file, zero setup). One table `gigs`.
- Scheduler: cron for v1 (Airflow later if wanted).
- LLM: Anthropic Claude API (`claude-sonnet-5-5`), key from `ANTHROPIC_API_KEY` env var.
- Email: SMTP (Gmail app password) or Resend API. Key from env.
- Config: a `config.py` or `config.yaml` holding my profile, keyword weights, score threshold, and enabled sources.

## Sources (build each as an independent fetcher module)
Each fetcher returns a list of dicts with the same shape (see Data model). If one source errors, log it and continue — never let one break the whole run.

Start with these 3:
1. **We Work Remotely** — data jobs RSS/category page.
2. **Remote OK** — has a public API (`https://remoteok.com/api`), filter to data/AI tags.
3. **Wellfound (AngelList)** — contract/remote data roles. If scraping is hard, stub it and leave a TODO.

Design the fetcher interface so adding a 4th source later is trivial:
```python
class Fetcher(Protocol):
    name: str
    def fetch(self) -> list[dict]: ...
```

## Data model (SQLite table `gigs`)
- `id` TEXT PRIMARY KEY  (hash of source + url, for dedupe)
- `source` TEXT
- `title` TEXT
- `company` TEXT
- `url` TEXT
- `description` TEXT
- `rate` TEXT (nullable — extract if present)
- `remote` BOOLEAN
- `posted_at` TEXT (ISO, nullable)
- `fetched_at` TEXT (ISO)
- `score` INTEGER (0–100)
- `score_reason` TEXT
- `pitch` TEXT (nullable — only for scored >= threshold)
- `notified` BOOLEAN (default false — so the digest never repeats a gig)

## Scoring (two-stage, build stage 1 first)
**Stage 1 — cheap keyword score (deterministic, no LLM):**
- +points for each stack keyword present (Python, dbt, Snowflake, Airflow, Spark, AWS, Databricks, Kafka, ETL, pipeline, data engineer, AI engineer).
- +points if a rate/budget is mentioned.
- +points for recency (posted within last 3 days).
- +points if remote.
- Normalize to 0–100. Keep weights in config.

**Stage 2 — LLM fit score (only for gigs passing a low stage-1 cutoff, to save tokens):**
- Send the posting + my profile to Claude. Ask for: a fit score 0–100 and a one-sentence reason.
- Final score = blend (e.g. 0.4 * keyword + 0.6 * LLM), configurable.

## Pitch drafting
For any gig with final score >= threshold (default 70):
- Send Claude the posting + my profile.
- Ask for a tailored 4–5 sentence pitch: opens with specific relevance to the role, names 1–2 matching stack items, states availability, ends with a light call to action. Professional, not salesy. No fabricated claims beyond my profile.
- Store in `pitch`.

## Daily digest (email)
- Query gigs where `notified = false` and `score >= threshold`, ordered by score desc.
- Email a clean list: title, company, score, one-line reason, link, and the drafted pitch (so I can copy-paste).
- Mark those rows `notified = true` after a successful send.
- If zero new gigs, send nothing (or a one-line "no new gigs" — configurable).

## Project structure
```
gig_sniper/
  config.py            # profile, weights, threshold, enabled sources, env keys
  db.py                # SQLite init + upsert + queries
  models.py            # Gig dataclass / types
  llm.py               # Claude calls: score_fit(), draft_pitch()
  scoring.py           # keyword score + blend
  fetchers/
    __init__.py        # registry of enabled fetchers
    base.py            # Fetcher protocol + shared helpers
    weworkremotely.py
    remoteok.py
    wellfound.py
  digest.py            # build + send email
  main.py              # orchestrates the full pipeline
  requirements.txt
  .env.example
  README.md
```

## Requirements
```
anthropic
requests
feedparser
beautifulsoup4
python-dotenv
```
(plus `resend` if using Resend instead of SMTP)

## Run
```
python main.py            # one full pipeline run
```
Cron example (daily 8am):
```
0 8 * * * cd /path/to/gig_sniper && /path/to/python main.py >> run.log 2>&1
```

## Acceptance criteria (v1 is "done" when)
1. `python main.py` runs the full loop without crashing even if one source fails.
2. Gigs are deduped across runs (same gig never scored twice).
3. At least 2 sources return real gigs.
4. Scoring produces sensible 0–100 values with reasons.
5. Pitches are drafted only for gigs >= threshold and read as usable first drafts.
6. A digest email arrives with the gigs and their pitches.
7. A gig already sent in a prior digest is not sent again.

## Build order (do in this sequence)
1. `db.py` + `models.py` + schema.
2. One fetcher (Remote OK — it has a clean API) end to end into the DB.
3. Keyword scoring.
4. Digest email with keyword scores only. **Ship and run it here — this is already useful.**
5. Add Claude fit score.
6. Add Claude pitch drafting.
7. Add the other two fetchers.

Stop after step 4 and confirm it works before adding the LLM layers.

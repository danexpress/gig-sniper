import logging
import sys

import config
import db
from digest import send_digest
from fetchers import get_enabled_fetchers
from llm import draft_pitch, score_fit
from models import Gig
from scoring import blend, keyword_score

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("gig_sniper")


def process_fetcher(conn, fetcher) -> int:
    try:
        raw_gigs = fetcher.fetch()
    except Exception:
        log.exception("Fetcher %s failed, skipping", fetcher.name)
        return 0

    stored = 0
    for raw in raw_gigs:
        raw["source"] = fetcher.name
        if not raw.get("url") or not raw.get("title"):
            continue

        gig = Gig.from_raw(raw)
        if db.exists(conn, gig.id):
            continue

        text = f"{gig.title}\n{gig.description}"
        k_score, k_reason = keyword_score(text, gig.rate, gig.remote, gig.posted_at)

        final_score = k_score
        reason = k_reason

        if k_score >= config.STAGE1_CUTOFF and config.ANTHROPIC_API_KEY:
            try:
                llm_score, llm_reason = score_fit(gig.title, gig.description)
                final_score = blend(k_score, llm_score)
                reason = llm_reason
            except Exception:
                log.exception("LLM scoring failed for %s, falling back to keyword score", gig.url)

        gig.score = final_score
        gig.score_reason = reason

        if final_score >= config.SCORE_THRESHOLD and config.ANTHROPIC_API_KEY:
            try:
                gig.pitch = draft_pitch(gig.title, gig.company, gig.description)
            except Exception:
                log.exception("Pitch drafting failed for %s", gig.url)

        db.insert_gig(conn, gig)
        stored += 1

    log.info("%s: fetched %d, stored %d new gig(s)", fetcher.name, len(raw_gigs), stored)
    return stored


def main():
    db.init_db()
    fetchers = get_enabled_fetchers(config.ENABLED_SOURCES)
    if not fetchers:
        log.warning("No enabled fetchers configured")

    with db.connect() as conn:
        for fetcher in fetchers:
            process_fetcher(conn, fetcher)
        conn.commit()  # persist fetched/scored gigs even if the digest send below fails

        pending = db.get_pending_digest(conn, config.SCORE_THRESHOLD)
        try:
            sent = send_digest(pending)
        except Exception:
            log.exception("Digest send failed, gigs remain unnotified for next run")
            sent = False

        if sent:
            db.mark_notified(conn, [g["id"] for g in pending])
            log.info("Digest sent with %d gig(s)", len(pending))
        else:
            log.info("No digest sent (0 pending gigs)")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        log.exception("Pipeline run failed")
        sys.exit(1)

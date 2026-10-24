import smtplib
from email.mime.text import MIMEText

import config


def build_digest_html(gigs: list[dict]) -> str:
    if not gigs:
        return "<p>No new gigs today.</p>"

    rows = []
    for g in gigs:
        if g.get("pitch"):
            pitch_html = f"<pre style=\"white-space:pre-wrap;font-family:inherit;\">{g['pitch']}</pre>"
        else:
            pitch_html = "<em>(below pitch threshold)</em>"
        rate_html = f" · Rate: {g['rate']}" if g.get("rate") else ""
        rows.append(f"""
        <div style="margin-bottom:24px;padding-bottom:16px;border-bottom:1px solid #ddd;">
            <h3 style="margin:0 0 4px;"><a href="{g['url']}">{g['title']}</a> — {g['company']}</h3>
            <p style="margin:0 0 4px;"><strong>Score: {g['score']}</strong> — {g['score_reason']}</p>
            <p style="margin:0 0 8px;color:#555;">Source: {g['source']}{rate_html}</p>
            {pitch_html}
        </div>
        """)
    return f"<html><body>{''.join(rows)}</body></html>"


def send_digest(gigs: list[dict]) -> bool:
    if not gigs and not config.SEND_EMPTY_DIGEST:
        return False

    subject = f"Gig Sniper: {len(gigs)} new gig(s)" if gigs else "Gig Sniper: no new gigs today"
    html = build_digest_html(gigs)

    if config.EMAIL_BACKEND == "resend":
        _send_via_resend(subject, html)
    else:
        _send_via_smtp(subject, html)
    return True


def _send_via_smtp(subject: str, html: str):
    msg = MIMEText(html, "html")
    msg["Subject"] = subject
    msg["From"] = config.SMTP_USER
    msg["To"] = config.DIGEST_TO

    with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT) as server:
        server.starttls()
        server.login(config.SMTP_USER, config.SMTP_PASSWORD)
        server.sendmail(config.SMTP_USER, [config.DIGEST_TO], msg.as_string())


def _send_via_resend(subject: str, html: str):
    import resend

    resend.api_key = config.RESEND_API_KEY
    resend.Emails.send({
        "from": config.RESEND_FROM,
        "to": [config.DIGEST_TO],
        "subject": subject,
        "html": html,
    })

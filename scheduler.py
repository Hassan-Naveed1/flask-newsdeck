# Background scheduler that periodically updates the local cache.
import os
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from models import upsert_articles
from news import fetch_topic

log = logging.getLogger("scheduler")

def start_scheduler():
    """Starts a recurring background task to refresh topics."""
    load_dotenv(override=True)
    minutes = int(os.getenv("REFRESH_MINUTES", "15"))
    api_key = os.getenv("NEWSAPI_KEY", "")
    topics = ["tech", "business", "sports"]

    sched = BackgroundScheduler(daemon=True)

    def _job():
        if not api_key:
            log.warning("NEWSAPI_KEY missing; skipping fetch job.")
            return

        log.info("Fetch job started (topics=%s)", topics)
        total_new = 0
        for t in topics:
            try:
                items = fetch_topic(t, api_key=api_key, page=1, page_size=50)
                ins, upd = upsert_articles(items)
                total_new += ins
                log.info("Upserted topic=%s inserted=%s updated=%s", t, ins, upd)
            except Exception as e:
                log.exception("Fetch failed for topic=%s: %s", t, e)
        log.info("Fetch job finished; new rows=%s", total_new)

    # Schedule periodic execution.
    sched.add_job(_job, "interval", minutes=minutes, id="refresh_job", next_run_time=None)
    sched.start()

    # Trigger one fetch on startup so the first load has data.
    try:
        _job()
    except Exception:
        pass

    return sched

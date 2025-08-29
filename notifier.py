import logging, json
from pathlib import Path
from typing import Optional
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from .batching import batch

logger = logging.getLogger("notifier")

def _requests_session() -> requests.Session:
    s = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST", "PUT"]
    )
    s.mount("http://", HTTPAdapter(max_retries=retries))
    s.mount("https://", HTTPAdapter(max_retries=retries))
    return s

class TransientError(Exception):
    pass

@retry(
    reraise=True,
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
    retry=retry_if_exception_type(TransientError)
)
def _send_one(session: requests.Session, url: str, api_key: str, payload: dict, dry_run: bool) -> dict:
    if dry_run:
        # Simulate success without network
        return {"status": "ok", "dry_run": True, "pnr": payload.get("pnr")}
    try:
        r = session.post(url, headers={"Authorization": f"Bearer {api_key}"}, json=payload, timeout=8)
        if r.status_code >= 500:
            raise TransientError(f"Server error {r.status_code}")
        r.raise_for_status()
        return r.json() if r.headers.get("content-type","").startswith("application/json") else {"status":"ok"}
    except requests.exceptions.RequestException as e:
        # Treat timeouts/connection errors as transient
        raise TransientError(str(e))

def send_confirmations(confirmations: pd.DataFrame, out_dir: Path, cfg) -> None:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    log_path = out_dir / "notifications.log"

    if confirmations.empty:
        with open(log_path, "w") as f:
            f.write("No confirmations to send.\n")
        logger.info("No confirmations to send.")
        return

    session = _requests_session()
    url = cfg.API_URL
    key = cfg.API_KEY
    batch_size = cfg.BATCH_SIZE
    workers = cfg.WORKERS
    dry_run = cfg.DRY_RUN

    success = 0
    failed = 0

    with open(log_path, "w") as f:
        for chunk in batch(confirmations.to_dict(orient="records"), batch_size):
            # Parallelize within each batch (I/O bound)
            with ThreadPoolExecutor(max_workers=workers) as ex:
                futures = []
                for row in chunk:
                    payload = {
                        "pnr": row["PNR"],
                        "passenger": row["Passenger"],
                        "origin": row["Origin"],
                        "destination": row["Destination"],
                        "total": row["Total"],
                        "status": row["Status"]
                    }
                    futures.append(ex.submit(_send_one, session, url, key, payload, dry_run))

                for fut in as_completed(futures):
                    try:
                        res = fut.result()
                        success += 1
                        f.write(json.dumps(res) + "\n")
                    except Exception as e:
                        failed += 1
                        f.write(json.dumps({"error": str(e)}) + "\n")

    logger.info("notifications: success=%d failed=%d dry_run=%s", success, failed, dry_run)

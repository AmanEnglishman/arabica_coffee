"""
Arabica Print Client
Usage: python client.py
"""

import asyncio
import json
import logging
import os
import sqlite3
import sys
from pathlib import Path

import requests
import websockets

import sys

# When bundled by PyInstaller, use exe directory; otherwise use script directory
if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent

CONFIG_PATH = BASE_DIR / "config.json"
DB_PATH = BASE_DIR / "printed_jobs.db"
LOG_PATH = BASE_DIR / "logs" / "printer.log"

# ── Logging ────────────────────────────────────────────────────────────────────

LOG_PATH.parent.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("print_client")


# ── Config ─────────────────────────────────────────────────────────────────────

def load_config() -> dict:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


# ── Idempotency (SQLite) ───────────────────────────────────────────────────────

def _get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute(
        "CREATE TABLE IF NOT EXISTS printed_jobs (job_id INTEGER PRIMARY KEY, printed_at TEXT)"
    )
    conn.commit()
    return conn


def is_already_printed(job_id: int) -> bool:
    conn = _get_db()
    row = conn.execute("SELECT 1 FROM printed_jobs WHERE job_id=?", (job_id,)).fetchone()
    conn.close()
    return row is not None


def mark_as_printed(job_id: int) -> None:
    conn = _get_db()
    conn.execute(
        "INSERT OR IGNORE INTO printed_jobs (job_id, printed_at) VALUES (?, datetime('now'))",
        (job_id,),
    )
    conn.commit()
    conn.close()


# ── Print ──────────────────────────────────────────────────────────────────────

def do_print(cfg: dict, receipt_text: str) -> None:
    from printer import print_receipt
    print_receipt(cfg["printer_ip"], cfg["printer_port"], receipt_text)


# ── Status reporting ───────────────────────────────────────────────────────────

def report_status_http(cfg: dict, job_id: int, status: str, error: str = "") -> None:
    """Fallback HTTP status report when WebSocket is unavailable."""
    token = cfg["token"]
    server_base = cfg["server_url"].replace("wss://", "https://").replace("ws://", "http://")
    server_base = server_base.rstrip("/ws/printer/").rstrip("/")
    url = f"{server_base}/api/printer/jobs/{job_id}/status/"
    try:
        requests.post(
            url,
            json={"status": status, "error": error},
            headers={"X-Printer-Token": token},
            timeout=5,
        )
    except Exception as e:
        logger.warning(f"HTTP status report failed: {e}")


# ── Recovery: fetch pending jobs via REST ──────────────────────────────────────

def fetch_pending_jobs(cfg: dict) -> list:
    token = cfg["token"]
    server_base = cfg["server_url"].replace("wss://", "https://").replace("ws://", "http://")
    server_base = server_base.rstrip("/ws/printer/").rstrip("/")
    url = f"{server_base}/api/printer/pending/?token={token}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.ok:
            return resp.json()
    except Exception as e:
        logger.warning(f"Failed to fetch pending jobs: {e}")
    return []


# ── Job handler ────────────────────────────────────────────────────────────────

async def handle_job(ws, cfg: dict, data: dict) -> None:
    job_id = data.get("job_id")
    receipt_text = data.get("receipt_text", "")

    if not job_id:
        return

    if is_already_printed(job_id):
        logger.info(f"Job #{job_id} already printed — skipping")
        return

    logger.info(f"Print started: job #{job_id}")

    # Notify server: processing
    try:
        await ws.send(json.dumps({"type": "print_status", "job_id": job_id, "status": "processing"}))
    except Exception:
        pass

    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, do_print, cfg, receipt_text)

        mark_as_printed(job_id)
        logger.info(f"Print success: job #{job_id}")

        await ws.send(json.dumps({"type": "print_status", "job_id": job_id, "status": "printed"}))

    except Exception as e:
        logger.error(f"Print failed: job #{job_id} — {e}")
        try:
            await ws.send(json.dumps({
                "type": "print_status",
                "job_id": job_id,
                "status": "failed",
                "error": str(e),
            }))
        except Exception:
            report_status_http(cfg, job_id, "failed", str(e))


# ── WebSocket loop ─────────────────────────────────────────────────────────────

async def run(cfg: dict) -> None:
    ws_url = f"{cfg['server_url']}?token={cfg['token']}"
    reconnect = cfg.get("reconnect_interval", 5)

    while True:
        try:
            logger.info(f"Connecting to {cfg['server_url']} ...")
            async with websockets.connect(ws_url, ping_interval=30, ping_timeout=10) as ws:
                logger.info("Connected")

                # Recover pending jobs via REST on every connect
                pending = fetch_pending_jobs(cfg)
                for job_data in pending:
                    await handle_job(ws, cfg, {
                        "job_id": job_data["job_id"],
                        "receipt_text": job_data["receipt_text"],
                    })

                # Listen for new jobs
                async for message in ws:
                    try:
                        data = json.loads(message)
                    except json.JSONDecodeError:
                        continue
                    if data.get("type") == "print_job":
                        await handle_job(ws, cfg, data)

        except websockets.exceptions.ConnectionClosedError as e:
            logger.warning(f"Connection closed: {e}")
        except OSError as e:
            logger.warning(f"Connection error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")

        logger.info(f"Reconnecting in {reconnect}s ...")
        await asyncio.sleep(reconnect)


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    cfg = load_config()
    logger.info("Arabica Print Client starting")
    asyncio.run(run(cfg))

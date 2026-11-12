#!/usr/bin/env python3

import subprocess
import time
import requests
import logging
from datetime import datetime

# ==========================
# Configuration
# ==========================

HEALTHCHECK_URL = ""   # ضع رابط Healthchecks.io هنا إن وجد

CHECK_INTERVAL = 60

SERVICES = [
    "bot",
    "gost",
    "cloudflared"
]

LOG_FILE = "/opt/server/logs/bot.log"

# ==========================
# Logging
# ==========================

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

print("Watchdog Bot Started")


# ==========================
# Functions
# ==========================

def service_running(service):
    result = subprocess.run(
        ["systemctl", "is-active", service],
        capture_output=True,
        text=True
    )

    return result.stdout.strip() == "active"


def restart_service(service):
    logging.warning(f"Restarting {service}")

    subprocess.run(
        ["systemctl", "restart", service]
    )


def send_heartbeat():
    if not HEALTHCHECK_URL:
        return

    try:
        requests.get(
            HEALTHCHECK_URL,
            timeout=10
        )

        logging.info("Heartbeat sent")

    except Exception as e:
        logging.error(f"Heartbeat failed: {e}")


def write_status():
    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    with open(
        "/opt/server/logs/status.log",
        "a"
    ) as f:

        f.write(
            f"{timestamp} alive\n"
        )


# ==========================
# Main Loop
# ==========================

while True:

    try:

        for service in SERVICES:

            if not service_running(service):

                logging.error(
                    f"{service} stopped"
                )

                restart_service(service)

            else:

                logging.info(
                    f"{service} ok"
                )

        write_status()

        send_heartbeat()

        time.sleep(CHECK_INTERVAL)

    except Exception as e:

        logging.exception(
            f"Unexpected error: {e}"
        )

        time.sleep(30)

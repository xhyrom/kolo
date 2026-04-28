import asyncio
import csv
import logging
import socket

from .config import cfg
from .models import TelemetryData

logger = logging.getLogger(__name__)


class TelemetryWorker:
    def __init__(self, queue: asyncio.Queue[TelemetryData]):
        self.queue = queue

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        if not cfg.csv_file.exists():
            with cfg.csv_file.open("w", newline="") as f:
                csv.writer(f).writerow(
                    ["timestamp", "velocity", "acceleration", "distance", "revs"]
                )

    async def run(self) -> None:
        logger.info("telemetry worker started (udp + csv).")

        with cfg.csv_file.open("a", newline="") as f:
            writer = csv.writer(f)

            while True:
                try:
                    data: TelemetryData = await self.queue.get()

                    self.sock.sendto(data.to_json(), (cfg.udp_ip, cfg.udp_port))
                    writer.writerow(data.to_csv_row())

                    f.flush()

                    self.queue.task_done()

                except asyncio.CancelledError:
                    logger.info("telemetry worker shutting down...")
                    break
                except Exception as e:
                    logger.error(f"worker error: {e}", exc_info=True)

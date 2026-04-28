import asyncio
import logging

from .ble import run_ble_client
from .config import cfg
from .models import TelemetryData
from .protocol import CommandProtocol
from .session import BikeSession
from .worker import TelemetryWorker

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s[%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("main")


async def main() -> None:
    logger.info("starting application...")

    session = BikeSession()
    queue: asyncio.Queue[TelemetryData] = asyncio.Queue()

    worker = TelemetryWorker(queue)
    loop = asyncio.get_running_loop()

    transport, _ = await loop.create_datagram_endpoint(
        lambda: CommandProtocol(session), local_addr=("0.0.0.0", cfg.cmd_port)
    )

    worker_task = asyncio.create_task(worker.run())
    ble_task = asyncio.create_task(run_ble_client(session, queue))

    try:
        await asyncio.gather(ble_task)
    except asyncio.CancelledError:
        logger.info("shutting down requested...")
    finally:
        transport.close()
        worker_task.cancel()
        await asyncio.gather(worker_task, return_exceptions=True)
        logger.info("shutdown complete.")


def run() -> None:
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("script interrupted by user (ctrl+c).")


if __name__ == "__main__":
    run()

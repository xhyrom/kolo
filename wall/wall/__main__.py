import logging
from queue import Queue

from .gui import Dashboard
from .network import NetworkManager
from .storage import CsvStorage

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s[%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("main")


def run() -> None:
    logger.info("starting wall receiver application...")

    data_queue = Queue()

    storage = CsvStorage()

    network = NetworkManager(data_queue)
    network.start_listening()

    dashboard = Dashboard(data_queue, storage, network)

    try:
        dashboard.start()
    except KeyboardInterrupt:
        logger.info("interrupted by user via terminal.")
    finally:
        network.stop()
        storage.close()
        logger.info("shutdown complete.")


if __name__ == "__main__":
    run()

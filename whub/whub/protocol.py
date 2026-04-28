import asyncio
import logging

from .session import BikeSession

logger = logging.getLogger(__name__)


class CommandProtocol(asyncio.DatagramProtocol):
    def __init__(self, session: BikeSession):
        self.session = session

    def datagram_received(self, data: bytes, addr: tuple[str, int]) -> None:
        msg = data.decode("utf-8").strip().lower()

        match msg:
            case "reset":
                logger.info(f"received reset command from {addr}")
                self.session.reset()
            case "ping":
                logger.info(f"received ping from {addr}")
            case _:
                logger.warning(f"unknown command '{msg}' from {addr}")

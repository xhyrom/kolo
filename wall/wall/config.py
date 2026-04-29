import logging
import socket
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


def get_local_broadcast() -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("224.0.0.1", 1))
            my_ip = s.getsockname()[0]

        ip_parts = my_ip.split(".")
        ip_parts[3] = "255"
        broadcast_ip = ".".join(ip_parts)
        print("2aaa")
        logger.info(f"auto-detected broadcast ip: {broadcast_ip}")
        return broadcast_ip
    except Exception as e:
        logger.warning(f"failed to detect network, fallback to global: {e}")
        return "255.255.255.255"


@dataclass(frozen=True)
class Config:
    udp_port: int = 5005
    cmd_port: int = 5006
    cmd_ip: str = get_local_broadcast()
    data_dir: Path = Path("data")
    window_size: int = 150


cfg = Config()

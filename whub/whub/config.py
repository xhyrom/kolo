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
        logger.info(f"auto-detected broadcast ip: {broadcast_ip}")
        return broadcast_ip
    except Exception as e:
        logger.warning(f"failed to detect network, fallback to global: {e}")
        return "255.255.255.255"


@dataclass(frozen=True)
class Config:
    wheel_circumference_m: float = 1.52
    udp_ip: str = get_local_broadcast()
    udp_port: int = 5005
    cmd_port: int = 5006
    sensor_uuid: str = "00001816-0000-1000-8000-00805f9b34fb"
    csv_file: Path = Path("data.csv")


cfg = Config()

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    udp_port: int = 5005
    cmd_port: int = 5006
    cmd_ip: str = "255.255.255.255"
    data_dir: Path = Path("data")
    window_size: int = 150


cfg = Config()

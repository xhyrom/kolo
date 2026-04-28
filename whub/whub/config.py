from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    wheel_circumference_m: float = 1.52
    udp_ip: str = "255.255.255.255"
    udp_port: int = 5005
    cmd_port: int = 5006
    sensor_uuid: str = "00001816-0000-1000-8000-00805f9b34fb"
    csv_file: Path = Path("data.csv")


cfg = Config()

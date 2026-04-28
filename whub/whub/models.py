import json
from dataclasses import asdict, dataclass


@dataclass
class TelemetryData:
    timestamp: float
    velocity: float
    acceleration: float
    distance: float
    revs: int

    def to_json(self) -> bytes:
        return json.dumps(asdict(self)).encode("utf-8")

    def to_csv_row(self) -> list[float | int]:
        return [
            self.timestamp,
            self.velocity,
            self.acceleration,
            self.distance,
            self.revs,
        ]

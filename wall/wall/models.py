from dataclasses import dataclass


@dataclass
class TelemetryData:
    timestamp: float
    velocity: float
    acceleration: float
    distance: float
    revs: int

    @property
    def velocity_kmh(self):
        return self.velocity * 3.6

    @classmethod
    def from_json_dict(cls, data: dict) -> "TelemetryData":
        return cls(
            timestamp=data.get("timestamp", 0.0),
            velocity=data.get("velocity", 0.0),
            acceleration=data.get("acceleration", 0.0),
            distance=data.get("distance", 0.0),
            revs=data.get("revs", 0),
        )

import logging
import time
from typing import Optional

from .config import cfg
from .models import TelemetryData

logger = logging.getLogger(__name__)


class BikeSession:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.prev_revs: Optional[int] = None
        self.prev_time: Optional[int] = None
        self.prev_speed_ms: float = 0.0
        self.start_revs: Optional[int] = None
        logger.info("session reset. counters starting from 0.")

    def process_measurement(
        self, revs: Optional[int], event_time: Optional[int]
    ) -> Optional[TelemetryData]:
        if revs is None or event_time is None:
            return None

        if self.start_revs is None:
            self.start_revs = revs
            logger.info(f"initial sensor revs: {revs}. displaying 0.")

        telemetry = None

        if self.prev_revs is not None and self.prev_time is not None:
            rev_diff = (revs - self.prev_revs) % 4_294_967_296
            time_diff = (event_time - self.prev_time) % 65536

            if time_diff > 0:
                dt = time_diff / 1024.0
                speed_ms = (rev_diff * cfg.wheel_circumference_m) / dt
                accel = (speed_ms - self.prev_speed_ms) / dt

                session_revs = (revs - self.start_revs) % 4_294_967_296
                dist_m = session_revs * cfg.wheel_circumference_m

                telemetry = TelemetryData(
                    timestamp=time.time(),
                    velocity=speed_ms,
                    acceleration=accel,
                    distance=dist_m,
                    revs=session_revs,
                )
                self.prev_speed_ms = speed_ms

        self.prev_revs = revs
        self.prev_time = event_time

        return telemetry

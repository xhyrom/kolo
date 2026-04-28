import csv
import logging
from datetime import datetime

from .config import cfg
from .models import TelemetryData

logger = logging.getLogger(__name__)


class CsvStorage:
    def __init__(self) -> None:
        self.file_obj = None
        self.writer = None

        cfg.data_dir.mkdir(parents=True, exist_ok=True)
        self.start_new_session()

    def start_new_session(self) -> None:
        if self.file_obj:
            self.file_obj.close()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = cfg.data_dir / f"session_{timestamp}.csv"

        self.file_obj = filename.open("w", newline="", encoding="utf-8")
        self.writer = csv.writer(self.file_obj)
        self.writer.writerow(
            ["timestamp", "velocity", "acceleration", "distance", "revs"]
        )

        logger.info(f"started new recording: {filename}")

    def save_record(self, data: TelemetryData) -> None:
        if self.writer and self.file_obj:
            self.writer.writerow(
                [
                    data.timestamp,
                    data.velocity,
                    data.acceleration,
                    data.distance,
                    data.revs,
                ]
            )

            self.file_obj.flush()

    def close(self) -> None:
        if self.file_obj:
            self.file_obj.close()
            logger.info("closed csv file.")

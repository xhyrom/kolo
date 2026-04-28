import asyncio
import logging
from typing import Any

from bleak import BleakClient, BleakScanner
from bleak.backends.device import BLEDevice
from pycycling.cycling_speed_cadence_service import CyclingSpeedCadenceService

from .config import cfg
from .models import TelemetryData
from .session import BikeSession

logger = logging.getLogger(__name__)


async def run_ble_client(
    session: BikeSession, queue: asyncio.Queue[TelemetryData]
) -> None:
    def handle_measurement(data: Any) -> None:
        telemetry = session.process_measurement(
            revs=data.cumulative_wheel_revs, event_time=data.last_wheel_event_time
        )

        if telemetry:
            logger.info(
                f"received data -> speed: {telemetry.velocity} m/s, dist: {telemetry.distance} m"
            )

            queue.put_nowait(telemetry)

    while True:
        try:
            logger.info("scanning for garmin sensor...")
            device: BLEDevice | None = await BleakScanner.find_device_by_filter(
                lambda d, ad: cfg.sensor_uuid in ad.service_uuids, timeout=5.0
            )

            if not device:
                await asyncio.sleep(2)
                continue

            session.reset()

            async with BleakClient(device) as client:
                logger.info(f"connected to device: {device.name}")
                csc = CyclingSpeedCadenceService(client)
                csc.set_csc_measurement_handler(handle_measurement)
                await csc.enable_csc_measurement_notifications()

                while client.is_connected:
                    await asyncio.sleep(2)

        except asyncio.CancelledError:
            logger.info("ble client task cancelled.")
            raise
        except Exception as e:
            logger.error(f"connection dropped: {e}")
            await asyncio.sleep(3)

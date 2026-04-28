import json
import logging
import socket
import threading
from queue import Queue

from .config import cfg
from .models import TelemetryData

logger = logging.getLogger(__name__)


class NetworkManager:
    def __init__(self, data_queue: Queue) -> None:
        self.queue = data_queue
        self.running = True

        self.recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.recv_sock.bind(("0.0.0.0", cfg.udp_port))
        self.recv_sock.settimeout(0.5)

        self.cmd_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.cmd_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    def start_listening(self) -> None:
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start()
        logger.info("listening for udp telemetry on background thread...")

    def _listen_loop(self) -> None:
        while self.running:
            try:
                data, _ = self.recv_sock.recvfrom(1024)
                parsed = json.loads(data.decode("utf-8"))
                telemetry = TelemetryData.from_json_dict(parsed)
                self.queue.put(telemetry)
            except socket.timeout:
                continue
            except json.JSONDecodeError:
                logger.error("received malformed json.")
            except Exception as e:
                logger.error(f"udp error: {e}")

    def send_command(self, cmd: str) -> None:
        try:
            self.cmd_sock.sendto(cmd.encode("utf-8"), (cfg.cmd_ip, cfg.cmd_port))
            logger.info(f"sent command to network: {cmd.lower()}")
        except Exception as e:
            logger.error(f"failed to send command: {e}")

    def stop(self) -> None:
        logger.info("stopping network manager...")
        self.running = False
        self.thread.join(timeout=1.0)
        self.recv_sock.close()
        self.cmd_sock.close()

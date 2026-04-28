import logging
from collections import deque

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.gridspec import GridSpec
from matplotlib.ticker import MaxNLocator

from .config import cfg
from .network import NetworkManager
from .storage import CsvStorage

logger = logging.getLogger(__name__)


class Dashboard:
    def __init__(self, data_queue, storage: CsvStorage, network: NetworkManager):
        self.queue = data_queue
        self.storage = storage
        self.network = network

        self.speeds = deque(maxlen=cfg.window_size)
        self.accels = deque(maxlen=cfg.window_size)

        self.curr_dist = 0.0
        self.curr_revs = 0
        self.max_speed = 0.0

        self._setup_plot()

    def _setup_plot(self) -> None:
        # simple clean white style
        plt.style.use("default")
        self.fig = plt.figure(figsize=(12, 8))
        self.fig.canvas.manager.set_window_title("telemetry wall dashboard")

        gs = GridSpec(3, 4, height_ratios=[1, 3, 3], figure=self.fig)

        self.txt_dist = self._create_card(self.fig.add_subplot(gs[0, 0]), "DISTANCE")
        self.txt_revs = self._create_card(self.fig.add_subplot(gs[0, 1]), "REVS")
        self.txt_speed = self._create_card(
            self.fig.add_subplot(gs[0, 2]), "SPEED (km/h)"
        )
        self.txt_max = self._create_card(
            self.fig.add_subplot(gs[0, 3]), "MAX SPEED (km/h)"
        )

        self.ax_speed = self.fig.add_subplot(gs[1, :])
        (self.line_speed,) = self.ax_speed.plot(
            [], [], color="#1f77b4", lw=2, label="speed"
        )
        self.ax_speed.set_ylabel("v [km·h⁻¹]", fontsize=10, color="#333333")
        self.ax_speed.set_xlabel("t [s]", fontsize=10, loc="right", color="#333333")
        self.ax_speed.legend(loc="upper left")
        self._style_axis(self.ax_speed)

        self.ax_accel = self.fig.add_subplot(gs[2, :])
        # label="" vytvára legendu pre graf
        (self.line_accel,) = self.ax_accel.plot(
            [], [], color="#ff7f0e", lw=2, label="acceleration"
        )
        self.ax_accel.set_ylabel("a [m·s⁻²]", fontsize=10, color="#333333")
        self.ax_accel.set_xlabel("t[s]", fontsize=10, loc="right", color="#333333")
        self.ax_accel.legend(loc="upper left")
        self._style_axis(self.ax_accel)

        self.fig.canvas.mpl_connect("key_press_event", self.on_key)
        plt.tight_layout()

    def _create_card(self, ax, title: str):
        # hide standard plot lines for cards
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_edgecolor("#e0e0e0")
            spine.set_linewidth(1.5)
        ax.set_facecolor("#f9f9f9")

        # small title
        ax.text(
            0.5,
            0.75,
            title,
            ha="center",
            va="center",
            fontsize=10,
            color="#666666",
            transform=ax.transAxes,
        )
        # big bold value placeholder
        txt_obj = ax.text(
            0.5,
            0.35,
            "0.0",
            ha="center",
            va="center",
            fontsize=20,
            fontweight="bold",
            color="#111111",
            transform=ax.transAxes,
        )

        return txt_obj

    def _style_axis(self, ax) -> None:
        # HUSTEJŠIA OS X: Nastavíme maximálne 20 dielikov (aby to urobilo pekné husté štvorčeky)
        ax.xaxis.set_major_locator(MaxNLocator(nbins=20, integer=True))

        ax.grid(True, color="#eeeeee", linestyle="-")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("#cccccc")
        ax.spines["bottom"].set_color("#cccccc")

    def on_key(self, event) -> None:
        if event.key == "r":
            logger.info("triggering session reset...")
            self.network.send_command("RESET")
            self.storage.start_new_session()

            # clear local variables
            self.speeds.clear()
            self.accels.clear()
            self.curr_dist = 0.0
            self.curr_revs = 0
            self.max_speed = 0.0

            # instantly update display to zeroes
            self.txt_dist.set_text("0.0 m")
            self.txt_revs.set_text("0")
            self.txt_speed.set_text("0.0")
            self.txt_max.set_text("0.0")

    def update(self, frame):
        updated = False

        while not self.queue.empty():
            data = self.queue.get_nowait()
            self.storage.save_record(data)

            self.speeds.append(data.velocity_kmh)
            self.accels.append(data.acceleration)
            self.curr_dist = data.distance
            self.curr_revs = data.revs

            if data.velocity_kmh > self.max_speed:
                self.max_speed = data.velocity_kmh

            updated = True

        if updated and len(self.speeds) > 0:
            x_data = list(range(len(self.speeds)))

            self.line_speed.set_data(x_data, self.speeds)
            self.ax_speed.set_xlim(0, cfg.window_size)
            self.ax_speed.set_ylim(0, max(25, max(self.speeds) * 1.2))

            self.line_accel.set_data(x_data, self.accels)
            self.ax_accel.set_xlim(0, cfg.window_size)
            min_a, max_a = min(self.accels), max(self.accels)
            limit_a = max(3.0, max(abs(min_a), abs(max_a)) * 1.5)
            self.ax_accel.set_ylim(-limit_a, limit_a)

            # update cards
            dist_str = (
                f"{self.curr_dist / 1000:.3f} km"
                if self.curr_dist >= 1000
                else f"{self.curr_dist:.1f} m"
            )
            self.txt_dist.set_text(dist_str)
            self.txt_revs.set_text(str(self.curr_revs))
            self.txt_speed.set_text(f"{self.speeds[-1]:.1f}")
            self.txt_max.set_text(f"{self.max_speed:.1f}")

        return (
            self.line_speed,
            self.line_accel,
            self.txt_dist,
            self.txt_revs,
            self.txt_speed,
            self.txt_max,
        )

    def start(self) -> None:
        logger.info("starting dashboard ui...")
        self.ani = FuncAnimation(
            self.fig, self.update, interval=100, cache_frame_data=False
        )
        plt.show()

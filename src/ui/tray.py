"""System tray integration for DriverReminder."""

from __future__ import annotations

import threading
from pathlib import Path
from typing import Callable

try:
    import pystray
    from PIL import Image, ImageDraw
except ImportError:  # pragma: no cover
    pystray = None
    Image = None
    ImageDraw = None


class TrayController:
    """Encapsulates pystray icon lifecycle and menu callbacks."""

    def __init__(
        self,
        on_open: Callable[[], None],
        on_check_now: Callable[[], None],
        on_rescan: Callable[[], None],
        on_pause: Callable[[], None],
        on_resume: Callable[[], None],
        on_exit: Callable[[], None],
    ) -> None:
        self.on_open = on_open
        self.on_check_now = on_check_now
        self.on_rescan = on_rescan
        self.on_pause = on_pause
        self.on_resume = on_resume
        self.on_exit = on_exit
        self.icon = None

    def supported(self) -> bool:
        return pystray is not None and Image is not None

    def show(self) -> None:
        if not self.supported() or self.icon is not None:
            return

        image = self._load_icon()
        menu = pystray.Menu(
            pystray.MenuItem("Open Dashboard", lambda _i, _m: self.on_open()),
            pystray.MenuItem("Check Now", lambda _i, _m: self.on_check_now()),
            pystray.MenuItem("Rescan Hardware", lambda _i, _m: self.on_rescan()),
            pystray.MenuItem("Pause Reminders", lambda _i, _m: self.on_pause()),
            pystray.MenuItem("Resume Reminders", lambda _i, _m: self.on_resume()),
            pystray.MenuItem("Exit", lambda i, _m: self._exit(i)),
        )
        self.icon = pystray.Icon("driverreminder", image, "DriverReminder", menu)
        threading.Thread(target=self.icon.run, daemon=True).start()

    def hide(self) -> None:
        if self.icon:
            self.icon.stop()
            self.icon = None

    def _exit(self, icon: object) -> None:
        if icon:
            try:
                icon.stop()
            except Exception:
                pass
        self.icon = None
        self.on_exit()

    def _load_icon(self):
        icon_path = Path(__file__).resolve().parents[2] / "assets" / "icon.ico"
        if icon_path.exists():
            try:
                return Image.open(icon_path)
            except Exception:
                pass

        image = Image.new("RGB", (64, 64), color="#1f6aa5")
        if ImageDraw:
            draw = ImageDraw.Draw(image)
            draw.rectangle((8, 8, 56, 56), outline="white", width=3)
            draw.text((22, 20), "DR", fill="white")
        return image

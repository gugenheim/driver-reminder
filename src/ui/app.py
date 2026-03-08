"""CustomTkinter UI for DriverReminder."""

from __future__ import annotations

import threading
import webbrowser
from datetime import datetime
from pathlib import Path

import customtkinter as ctk

try:
    import pystray
    from PIL import Image
except ImportError:  # pragma: no cover
    pystray = None
    Image = None

from reminders.scheduler import ReminderScheduler
from scanner.hardware_scanner import HardwareScanner
from storage.config_manager import DRIVER_CATEGORIES, ConfigManager
from utils.vendor_links import get_links_for_category


class DriverReminderApp(ctk.CTk):
    """Main desktop application window."""

    def __init__(self) -> None:
        super().__init__()
        self.title("DriverReminder")
        self.geometry("1080x700")

        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        self.config_manager = ConfigManager()
        self.scanner = HardwareScanner()
        self.hardware_info = self.scanner.scan()
        self.detected_vendors = self.scanner.detect_vendors(self.hardware_info)
        self.scheduler = ReminderScheduler(lambda: self.config_manager.config)

        self._tray_icon = None
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self._build_layout()
        self.refresh_dashboard()
        self.scheduler.start()

    def _build_layout(self) -> None:
        top_frame = ctk.CTkFrame(self)
        top_frame.pack(fill="x", padx=12, pady=12)

        title = ctk.CTkLabel(top_frame, text="DriverReminder Dashboard", font=("Segoe UI", 22, "bold"))
        title.pack(side="left", padx=8, pady=8)

        warning = ctk.CTkLabel(
            self,
            text=(
                "⚠ BIOS/UEFI updates are risky. Install firmware updates only when necessary and "
                "only from official OEM pages."
            ),
            text_color="#ffb703",
            justify="left",
            wraplength=980,
        )
        warning.pack(fill="x", padx=16)

        settings_frame = ctk.CTkFrame(self)
        settings_frame.pack(fill="x", padx=12, pady=(8, 12))

        ctk.CTkLabel(settings_frame, text="Reminder Interval:").pack(side="left", padx=8, pady=8)
        self.interval_var = ctk.StringVar(value=self.config_manager.config.get("reminder_interval", "Weekly"))
        interval_menu = ctk.CTkOptionMenu(
            settings_frame,
            values=["Daily", "Weekly", "Monthly"],
            variable=self.interval_var,
            command=self._on_interval_change,
        )
        interval_menu.pack(side="left", padx=8, pady=8)

        ctk.CTkButton(settings_frame, text="Check Now (Mark All)", command=self._check_now).pack(
            side="left", padx=8, pady=8
        )
        ctk.CTkButton(settings_frame, text="Rescan Hardware", command=self._rescan_hardware).pack(
            side="left", padx=8, pady=8
        )

        self.content = ctk.CTkScrollableFrame(self)
        self.content.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    def refresh_dashboard(self) -> None:
        for widget in self.content.winfo_children():
            widget.destroy()

        for category in DRIVER_CATEGORIES:
            row = ctk.CTkFrame(self.content)
            row.pack(fill="x", pady=6, padx=6)

            last_checked = self.config_manager.config.get("last_checked", {}).get(category)
            last_checked_text = self._format_timestamp(last_checked)

            detected_for_category = self._vendors_for_category(category)
            vendors_text = ", ".join(detected_for_category) if detected_for_category else "No specific vendor detected"

            ctk.CTkLabel(row, text=category, width=230, anchor="w").pack(side="left", padx=8, pady=8)
            ctk.CTkLabel(row, text=f"Vendors: {vendors_text}", width=360, anchor="w").pack(
                side="left", padx=8, pady=8
            )
            ctk.CTkLabel(row, text=f"Last checked: {last_checked_text}", width=220, anchor="w").pack(
                side="left", padx=8, pady=8
            )

            ctk.CTkButton(
                row,
                text="Open Official Page",
                command=lambda c=category: self._open_official_link(c),
            ).pack(side="right", padx=8, pady=8)

            ctk.CTkButton(
                row,
                text="Mark Checked",
                command=lambda c=category: self._mark_category_checked(c),
            ).pack(side="right", padx=8, pady=8)

        details_frame = ctk.CTkFrame(self.content)
        details_frame.pack(fill="x", pady=8, padx=6)
        ctk.CTkLabel(details_frame, text="Detected Hardware", font=("Segoe UI", 16, "bold")).pack(
            anchor="w", padx=8, pady=8
        )

        for key, values in self.hardware_info.as_dict().items():
            ctk.CTkLabel(
                details_frame,
                text=f"{key.upper()}: {', '.join(values)}",
                anchor="w",
                justify="left",
                wraplength=980,
            ).pack(fill="x", padx=8, pady=2)

    def _vendors_for_category(self, category: str) -> list[str]:
        mapping = {
            "BIOS / UEFI firmware": ["motherboard", "cpu"],
            "Graphics drivers": ["gpu"],
            "CPU chipset drivers": ["cpu", "motherboard"],
            "WiFi drivers": ["wifi"],
            "Bluetooth drivers": ["bluetooth"],
            "Audio drivers": ["audio"],
            "Storage / NVMe drivers": ["storage"],
            "System firmware / motherboard drivers": ["motherboard"],
        }
        keys = mapping.get(category, [])
        found = []
        for key in keys:
            found.extend(self.detected_vendors.get(key, []))
        return sorted(set(found))

    def _open_official_link(self, category: str) -> None:
        vendors = self._vendors_for_category(category)
        links = get_links_for_category(category, vendors)
        if links:
            # Open first most relevant link.
            _, url = next(iter(links.items()))
            webbrowser.open(url)

    def _mark_category_checked(self, category: str) -> None:
        self.config_manager.mark_checked(category)
        self.refresh_dashboard()

    def _check_now(self) -> None:
        self.config_manager.mark_all_checked()
        self.refresh_dashboard()

    def _rescan_hardware(self) -> None:
        self.hardware_info = self.scanner.scan()
        self.detected_vendors = self.scanner.detect_vendors(self.hardware_info)
        self.refresh_dashboard()

    def _on_interval_change(self, interval: str) -> None:
        self.config_manager.set_interval(interval)

    @staticmethod
    def _format_timestamp(value: str | None) -> str:
        if not value:
            return "Never"
        try:
            parsed = datetime.fromisoformat(value)
            return parsed.strftime("%Y-%m-%d %H:%M")
        except ValueError:
            return "Never"

    def on_close(self) -> None:
        if pystray and Image:
            self.withdraw()
            self._ensure_tray_icon()
            return
        self._shutdown_and_exit()

    def _ensure_tray_icon(self) -> None:
        if self._tray_icon:
            return

        icon_path = Path(__file__).resolve().parents[2] / "assets" / "icon.ico"
        image = Image.new("RGB", (64, 64), "#1f6aa5")
        if icon_path.exists():
            try:
                image = Image.open(icon_path)
            except Exception:
                # Placeholder/non-image icon files are allowed; keep default image.
                image = Image.new("RGB", (64, 64), "#1f6aa5")

        menu = pystray.Menu(
            pystray.MenuItem("Show", self._tray_show),
            pystray.MenuItem("Quit", self._tray_quit),
        )
        self._tray_icon = pystray.Icon("driverreminder", image, "DriverReminder", menu)
        threading.Thread(target=self._tray_icon.run, daemon=True).start()

    def _tray_show(self, icon, _item) -> None:  # type: ignore[no-untyped-def]
        self.after(0, self.deiconify)
        if icon:
            icon.stop()
        self._tray_icon = None

    def _tray_quit(self, icon, _item) -> None:  # type: ignore[no-untyped-def]
        if icon:
            icon.stop()
        self._tray_icon = None
        self.after(0, self._shutdown_and_exit)

    def _shutdown_and_exit(self) -> None:
        self.scheduler.stop()
        self.destroy()

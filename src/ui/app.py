"""Main UI for DriverReminder."""

from __future__ import annotations

import webbrowser
from datetime import datetime, timedelta, timezone

import customtkinter as ctk

from reminders.scheduler import INTERVAL_DAYS, ReminderScheduler
from scanner.hardware_scanner import HardwareScanner, ScanResult
from scanner.version_detector import VersionDetector
from storage.config_manager import DRIVER_CATEGORIES, ConfigManager
from ui.tray import TrayController
from utils.startup import is_startup_enabled, set_startup_enabled
from utils.vendor_links import resolve_best_link
from utils.version_compare import compare_versions


class DriverReminderApp(ctk.CTk):
    """Desktop dashboard and tray-aware controller."""

    def __init__(self) -> None:
        super().__init__()
        self.title("DriverReminder")
        self.geometry("1240x760")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.config_manager = ConfigManager()
        startup_state = is_startup_enabled()
        if startup_state != self.config_manager.config.get("start_with_windows", False):
            self.config_manager.set_startup(startup_state)

        self.scanner = HardwareScanner()
        self.version_detector = VersionDetector()
        self.scan_result: ScanResult = self.scanner.scan()

        self.scheduler = ReminderScheduler(
            config_getter=lambda: self.config_manager.config,
            on_notified=lambda category: self.config_manager.mark_notified(category),
        )

        self.tray = TrayController(
            on_open=self._open_from_tray,
            on_check_now=lambda: self.after(0, self._check_now),
            on_rescan=lambda: self.after(0, self._rescan_hardware),
            on_pause=lambda: self.after(0, lambda: self._set_paused(True)),
            on_resume=lambda: self.after(0, lambda: self._set_paused(False)),
            on_exit=lambda: self.after(0, self._shutdown_and_exit),
        )

        self.protocol("WM_DELETE_WINDOW", self.on_window_close)
        self._build_layout()
        self._refresh_scan_cache()
        self.refresh_dashboard()
        self.scheduler.start()

    def _build_layout(self) -> None:
        top = ctk.CTkFrame(self)
        top.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(top, text="DriverReminder", font=("Segoe UI", 24, "bold")).pack(side="left", padx=8, pady=8)
        self.tray_status_label = ctk.CTkLabel(top, text="Tray: active on close" if self.tray.supported() else "Tray: unavailable")
        self.tray_status_label.pack(side="right", padx=8, pady=8)

        warning = ctk.CTkLabel(
            self,
            text="⚠ BIOS/UEFI updates are risky. Only use official OEM/motherboard sources and update only when necessary.",
            text_color="#ffb703",
            wraplength=1150,
            justify="left",
        )
        warning.pack(fill="x", padx=12)

        controls = ctk.CTkFrame(self)
        controls.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(controls, text="Reminder interval:").pack(side="left", padx=(8, 4))
        self.interval_var = ctk.StringVar(value=self.config_manager.config.get("reminder_interval", "Weekly"))
        ctk.CTkOptionMenu(controls, values=["Daily", "Weekly", "Monthly"], variable=self.interval_var, command=self._set_interval).pack(side="left", padx=4)

        self.pause_var = ctk.BooleanVar(value=self.config_manager.config.get("reminders_paused", False))
        ctk.CTkCheckBox(controls, text="Pause reminders", variable=self.pause_var, command=lambda: self._set_paused(self.pause_var.get())).pack(side="left", padx=10)

        self.startup_var = ctk.BooleanVar(value=self.config_manager.config.get("start_with_windows", False))
        ctk.CTkCheckBox(controls, text="Start DriverReminder when Windows starts", variable=self.startup_var, command=self._toggle_startup).pack(side="left", padx=10)

        self.minimize_var = ctk.BooleanVar(value=self.config_manager.config.get("minimize_to_tray", True))
        ctk.CTkCheckBox(controls, text="Minimize to tray on close", variable=self.minimize_var, command=self._toggle_minimize_to_tray).pack(side="left", padx=10)

        ctk.CTkButton(controls, text="Check All Now", command=self._check_now).pack(side="right", padx=8)
        ctk.CTkButton(controls, text="Rescan Hardware", command=self._rescan_hardware).pack(side="right", padx=8)

        self.scroll = ctk.CTkScrollableFrame(self)
        self.scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def refresh_dashboard(self) -> None:
        for w in self.scroll.winfo_children():
            w.destroy()

        for category in DRIVER_CATEGORIES:
            card = ctk.CTkFrame(self.scroll)
            card.pack(fill="x", padx=6, pady=6)

            scan = self.scan_result.by_category.get(category)
            hw_text = ", ".join(scan.hardware) if scan else "Not detected"
            vendors = scan.vendors if scan else []
            vendor_text = ", ".join(vendors) if vendors else "Unknown"
            installed = scan.installed_version if scan else "Installed version unavailable"
            latest = self.version_detector.lookup_latest(category, vendors)
            compare = compare_versions(installed, latest)
            last_checked_raw = self.config_manager.config["last_checked"].get(category)
            last_checked = self._fmt_dt(last_checked_raw)
            overdue = "Overdue" if self._is_overdue(last_checked_raw) else "On schedule"

            title = ctk.CTkLabel(card, text=category, font=("Segoe UI", 16, "bold"))
            title.pack(anchor="w", padx=10, pady=(8, 4))

            ctk.CTkLabel(card, text=f"Hardware: {hw_text}", wraplength=1120, justify="left").pack(anchor="w", padx=10)
            ctk.CTkLabel(card, text=f"Vendors: {vendor_text}").pack(anchor="w", padx=10)
            ctk.CTkLabel(card, text=f"Installed version: {installed}").pack(anchor="w", padx=10)
            ctk.CTkLabel(card, text=f"Latest version: {latest}").pack(anchor="w", padx=10)
            ctk.CTkLabel(card, text=f"Latest comparison: {compare}").pack(anchor="w", padx=10)
            ctk.CTkLabel(card, text=f"Last checked: {last_checked} | Reminder status: {overdue}").pack(anchor="w", padx=10, pady=(0, 8))

            btn_row = ctk.CTkFrame(card, fg_color="transparent")
            btn_row.pack(fill="x", padx=10, pady=(0, 10))
            ctk.CTkButton(btn_row, text="Open Official Page", command=lambda c=category: self._open_link(c)).pack(side="right", padx=6)
            ctk.CTkButton(btn_row, text="Mark Checked", command=lambda c=category: self._mark_checked(c)).pack(side="right", padx=6)

    def _open_link(self, category: str) -> None:
        scan = self.scan_result.by_category.get(category)
        vendors = scan.vendors if scan else []
        _, url = resolve_best_link(category, vendors, self.scan_result.oem_vendor)
        webbrowser.open(url)

    def _mark_checked(self, category: str) -> None:
        self.config_manager.mark_checked(category)
        self.refresh_dashboard()

    def _check_now(self) -> None:
        self.config_manager.mark_all_checked()
        self.refresh_dashboard()

    def _rescan_hardware(self) -> None:
        self.scan_result = self.scanner.scan()
        self._refresh_scan_cache()
        self.refresh_dashboard()

    def _refresh_scan_cache(self) -> None:
        cache = {
            "oem_vendor": self.scan_result.oem_vendor,
            "categories": {
                cat: {
                    "hardware": scan.hardware,
                    "vendors": scan.vendors,
                    "installed_version": scan.installed_version,
                }
                for cat, scan in self.scan_result.by_category.items()
            },
        }
        self.config_manager.set_scan_cache(cache)

    def _set_interval(self, interval: str) -> None:
        self.config_manager.set_interval(interval)
        self.refresh_dashboard()

    def _set_paused(self, paused: bool) -> None:
        self.pause_var.set(paused)
        self.config_manager.set_paused(paused)

    def _toggle_startup(self) -> None:
        desired = self.startup_var.get()
        success = set_startup_enabled(desired)
        if not success:
            self.startup_var.set(self.config_manager.config.get("start_with_windows", False))
            return
        self.config_manager.set_startup(desired)

    def _toggle_minimize_to_tray(self) -> None:
        self.config_manager.set_minimize_to_tray(self.minimize_var.get())

    def on_window_close(self) -> None:
        if self.config_manager.config.get("minimize_to_tray", True) and self.tray.supported():
            self.withdraw()
            self.tray.show()
            return
        self._shutdown_and_exit()

    def _open_from_tray(self) -> None:
        self.after(0, self.deiconify)
        self.after(0, self.lift)
        self.after(0, self.focus_force)
        self.tray.hide()

    def _shutdown_and_exit(self) -> None:
        self.tray.hide()
        self.scheduler.stop()
        self.destroy()

    def _is_overdue(self, last_checked: str | None) -> bool:
        if self.config_manager.config.get("reminders_paused", False):
            return False
        if not last_checked:
            return True
        try:
            checked_dt = datetime.fromisoformat(last_checked)
        except ValueError:
            return True
        days = INTERVAL_DAYS.get(self.config_manager.config.get("reminder_interval", "Weekly"), 7)
        return datetime.now(timezone.utc) - checked_dt >= timedelta(days=days)

    @staticmethod
    def _fmt_dt(value: str | None) -> str:
        if not value:
            return "Never"
        try:
            return datetime.fromisoformat(value).strftime("%Y-%m-%d %H:%M")
        except ValueError:
            return "Never"

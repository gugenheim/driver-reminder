"""Windows hardware and installed driver version detection."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import psutil

try:
    import wmi
except ImportError:  # pragma: no cover
    wmi = None


@dataclass
class CategoryScan:
    hardware: list[str]
    vendors: list[str]
    installed_version: str


@dataclass
class ScanResult:
    by_category: dict[str, CategoryScan]
    oem_vendor: str


class HardwareScanner:
    """Collects hardware information and safe installed-version data using WMI."""

    VENDOR_PATTERNS = {
        "NVIDIA": ["nvidia"],
        "AMD": ["amd", "radeon", "advanced micro devices"],
        "Intel": ["intel"],
        "Realtek": ["realtek"],
        "Qualcomm": ["qualcomm", "atheros"],
        "Broadcom": ["broadcom"],
        "Dell": ["dell"],
        "HP": ["hp", "hewlett"],
        "Lenovo": ["lenovo"],
        "ASUS": ["asus"],
        "Acer": ["acer"],
        "MSI": ["micro-star", "msi"],
    }

    def __init__(self) -> None:
        self.connection = wmi.WMI() if wmi else None

    def scan(self) -> ScanResult:
        if not self.connection:
            return self._fallback_scan()

        try:
            video = list(self.connection.Win32_VideoController())
            cpus = list(self.connection.Win32_Processor())
            boards = list(self.connection.Win32_BaseBoard())
            bios = list(self.connection.Win32_BIOS())
            pnp = list(self.connection.Win32_PnPSignedDriver())
            scsi = list(self.connection.Win32_SCSIController())
            systems = list(self.connection.Win32_ComputerSystem())

            oem_vendor = self._detect_oem([getattr(s, "Manufacturer", "") for s in systems])

            gpu_hw = self._unique([getattr(v, "Name", "") for v in video])
            gpu_ver = self._first_non_empty([getattr(v, "DriverVersion", "") for v in video])

            cpu_hw = self._unique([getattr(c, "Name", "") for c in cpus])
            board_hw = self._unique(
                [f"{getattr(b, 'Manufacturer', '')} {getattr(b, 'Product', '')}".strip() for b in boards]
            )
            bios_ver = self._first_non_empty(
                [f"{getattr(b, 'SMBIOSBIOSVersion', '')}".strip() for b in bios if getattr(b, "SMBIOSBIOSVersion", None)]
            )

            wifi = self._driver_rows(pnp, ["wi-fi", "wireless", "802.11"])
            bt = self._driver_rows(pnp, ["bluetooth"])
            audio = self._driver_rows(pnp, ["audio", "sound"])
            storage = self._unique([getattr(s, "Name", "") for s in scsi])
            storage_ver = self._first_non_empty([getattr(s, "DriverVersion", "") for s in scsi])

            by_category = {
                "BIOS / UEFI firmware": self._entry(board_hw or ["Motherboard not detected"], bios_ver),
                "Graphics drivers": self._entry(gpu_hw, gpu_ver),
                "CPU chipset drivers": self._entry(cpu_hw + board_hw, "Installed version unavailable"),
                "WiFi drivers": self._entry(wifi[0], wifi[1]),
                "Bluetooth drivers": self._entry(bt[0], bt[1]),
                "Audio drivers": self._entry(audio[0], audio[1]),
                "Storage / NVMe drivers": self._entry(storage, storage_ver),
                "System firmware / motherboard drivers": self._entry(board_hw, "Installed version unavailable"),
            }
            return ScanResult(by_category=by_category, oem_vendor=oem_vendor)
        except Exception:
            return self._fallback_scan()

    def _entry(self, hardware: list[str], version: str) -> CategoryScan:
        hw = self._unique(hardware) or ["Not detected"]
        vendors = self._detect_vendors(hw)
        return CategoryScan(
            hardware=hw,
            vendors=vendors,
            installed_version=version or "Installed version unavailable",
        )

    def _fallback_scan(self) -> ScanResult:
        cpu_text = f"CPU cores: {psutil.cpu_count(logical=True)}" if hasattr(psutil, "cpu_count") else "Unknown CPU"
        by_category = {
            "BIOS / UEFI firmware": CategoryScan(["Unknown motherboard"], [], "Installed version unavailable"),
            "Graphics drivers": CategoryScan(["Unknown GPU"], [], "Installed version unavailable"),
            "CPU chipset drivers": CategoryScan([cpu_text], [], "Installed version unavailable"),
            "WiFi drivers": CategoryScan(["Not detected"], [], "Installed version unavailable"),
            "Bluetooth drivers": CategoryScan(["Not detected"], [], "Installed version unavailable"),
            "Audio drivers": CategoryScan(["Not detected"], [], "Installed version unavailable"),
            "Storage / NVMe drivers": CategoryScan(["Not detected"], [], "Installed version unavailable"),
            "System firmware / motherboard drivers": CategoryScan(["Unknown motherboard"], [], "Installed version unavailable"),
        }
        return ScanResult(by_category=by_category, oem_vendor="Unknown")

    def _driver_rows(self, rows: Iterable[object], keywords: list[str]) -> tuple[list[str], str]:
        matched = [r for r in rows if any(k in str(getattr(r, "DeviceName", "")).lower() for k in keywords)]
        hardware = self._unique([getattr(r, "DeviceName", "") for r in matched]) or ["Not detected"]
        version = self._first_non_empty([getattr(r, "DriverVersion", "") for r in matched])
        return hardware, version

    def _detect_vendors(self, hardware: list[str]) -> list[str]:
        text = " ".join(hardware).lower()
        out = [vendor for vendor, pats in self.VENDOR_PATTERNS.items() if any(p in text for p in pats)]
        return sorted(set(out))

    def _detect_oem(self, manufacturers: list[str]) -> str:
        for maker in manufacturers:
            low = maker.lower()
            for vendor, pats in self.VENDOR_PATTERNS.items():
                if vendor in {"NVIDIA", "AMD", "Intel", "Realtek", "Qualcomm", "Broadcom"}:
                    continue
                if any(p in low for p in pats):
                    return vendor
        return "Unknown"

    @staticmethod
    def _unique(items: Iterable[str]) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        for raw in items:
            item = (raw or "").strip()
            if item and item not in seen:
                seen.add(item)
                out.append(item)
        return out

    @staticmethod
    def _first_non_empty(values: Iterable[str]) -> str:
        for value in values:
            txt = (value or "").strip()
            if txt:
                return txt
        return "Installed version unavailable"

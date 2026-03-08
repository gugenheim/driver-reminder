"""Hardware discovery helpers using WMI and psutil."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import psutil

try:
    import wmi
except ImportError:  # pragma: no cover
    wmi = None


@dataclass
class HardwareInfo:
    gpu: list[str]
    cpu: list[str]
    motherboard: list[str]
    wifi: list[str]
    bluetooth: list[str]
    audio: list[str]
    storage: list[str]

    def as_dict(self) -> dict[str, list[str]]:
        return {
            "gpu": self.gpu,
            "cpu": self.cpu,
            "motherboard": self.motherboard,
            "wifi": self.wifi,
            "bluetooth": self.bluetooth,
            "audio": self.audio,
            "storage": self.storage,
        }


class HardwareScanner:
    """Collect hardware information and infer likely vendors."""

    VENDORS = {
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

    def scan(self) -> HardwareInfo:
        if not self.connection:
            return self._fallback_scan()

        try:
            gpus = [gpu.Name for gpu in self.connection.Win32_VideoController() if gpu.Name]
            cpus = [cpu.Name for cpu in self.connection.Win32_Processor() if cpu.Name]
            baseboards = [
                f"{board.Manufacturer} {board.Product}".strip()
                for board in self.connection.Win32_BaseBoard()
                if board.Manufacturer or board.Product
            ]
            pnp_entities = [item.Name for item in self.connection.Win32_PnPEntity() if item.Name]
            disk_controllers = [
                ctrl.Name for ctrl in self.connection.Win32_SCSIController() if ctrl.Name
            ]

            return HardwareInfo(
                gpu=self._unique(gpus),
                cpu=self._unique(cpus),
                motherboard=self._unique(baseboards),
                wifi=self._filter_devices(pnp_entities, ["wi-fi", "wireless", "802.11"]),
                bluetooth=self._filter_devices(pnp_entities, ["bluetooth"]),
                audio=self._filter_devices(pnp_entities, ["audio", "sound"]),
                storage=self._unique(disk_controllers),
            )
        except Exception:
            return self._fallback_scan()

    def detect_vendors(self, hardware_info: HardwareInfo) -> dict[str, list[str]]:
        detected: dict[str, list[str]] = {}

        for category, items in hardware_info.as_dict().items():
            vendors = []
            lower_items = " ".join(items).lower()
            for vendor, patterns in self.VENDORS.items():
                if any(pattern in lower_items for pattern in patterns):
                    vendors.append(vendor)
            detected[category] = vendors

        return detected

    def _fallback_scan(self) -> HardwareInfo:
        cpu_name = ["Unknown CPU"]
        if hasattr(psutil, "cpu_count"):
            cpu_name = [f"CPU cores: {psutil.cpu_count(logical=True)}"]
        return HardwareInfo(
            gpu=["Unknown GPU"],
            cpu=cpu_name,
            motherboard=["Unknown motherboard"],
            wifi=["Unknown WiFi adapter"],
            bluetooth=["Unknown Bluetooth adapter"],
            audio=["Unknown audio device"],
            storage=["Unknown storage controller"],
        )

    @staticmethod
    def _filter_devices(items: Iterable[str], keywords: list[str]) -> list[str]:
        filtered = [item for item in items if any(key in item.lower() for key in keywords)]
        return HardwareScanner._unique(filtered or ["Not detected"])

    @staticmethod
    def _unique(items: Iterable[str]) -> list[str]:
        seen = set()
        ordered = []
        for item in items:
            if item and item not in seen:
                seen.add(item)
                ordered.append(item)
        return ordered or ["Not detected"]

"""Official vendor support link mapping."""

from __future__ import annotations

VENDOR_LINKS: dict[str, str] = {
    "NVIDIA": "https://www.nvidia.com/Download/index.aspx",
    "AMD": "https://www.amd.com/en/support",
    "Intel": "https://www.intel.com/content/www/us/en/download-center/home.html",
    "Realtek": "https://www.realtek.com/Download/List?cate_id=593",
    "Qualcomm": "https://www.qualcomm.com/support/software",
    "Broadcom": "https://www.broadcom.com/support/download-search",
    "Dell": "https://www.dell.com/support/home/drivers",
    "HP": "https://support.hp.com/drivers",
    "Lenovo": "https://support.lenovo.com/us/en/downloads",
    "ASUS": "https://www.asus.com/support/download-center/",
    "Acer": "https://www.acer.com/us-en/support/drivers-and-manuals",
    "MSI": "https://www.msi.com/support/download",
}

CATEGORY_VENDOR_PRIORITY: dict[str, list[str]] = {
    "BIOS / UEFI firmware": ["Dell", "HP", "Lenovo", "ASUS", "Acer", "MSI"],
    "Graphics drivers": ["NVIDIA", "AMD", "Intel"],
    "CPU chipset drivers": ["AMD", "Intel", "Dell", "HP", "Lenovo", "ASUS", "Acer", "MSI"],
    "WiFi drivers": ["Intel", "Qualcomm", "Broadcom", "Realtek", "Dell", "HP", "Lenovo", "ASUS", "Acer", "MSI"],
    "Bluetooth drivers": ["Intel", "Qualcomm", "Broadcom", "Realtek", "Dell", "HP", "Lenovo", "ASUS", "Acer", "MSI"],
    "Audio drivers": ["Realtek", "Dell", "HP", "Lenovo", "ASUS", "Acer", "MSI"],
    "Storage / NVMe drivers": ["Intel", "AMD", "Dell", "HP", "Lenovo", "ASUS", "Acer", "MSI"],
    "System firmware / motherboard drivers": ["Dell", "HP", "Lenovo", "ASUS", "Acer", "MSI"],
}


def resolve_best_link(category: str, detected_vendors: list[str], oem_vendor: str) -> tuple[str, str]:
    """Return the best (vendor, url) based on category and detected vendors."""
    priority = CATEGORY_VENDOR_PRIORITY.get(category, [])
    candidates = list(dict.fromkeys(detected_vendors + ([oem_vendor] if oem_vendor else [])))

    for preferred in priority:
        if preferred in candidates and preferred in VENDOR_LINKS:
            return preferred, VENDOR_LINKS[preferred]

    for vendor in candidates:
        if vendor in VENDOR_LINKS:
            return vendor, VENDOR_LINKS[vendor]

    # Ultimate fallback to Intel download center as generic safe source.
    return "Intel", VENDOR_LINKS["Intel"]

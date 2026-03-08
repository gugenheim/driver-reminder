"""Official support links for vendors and update categories."""

from __future__ import annotations

CATEGORY_LINKS: dict[str, dict[str, str]] = {
    "BIOS / UEFI firmware": {
        "Dell": "https://www.dell.com/support/home/drivers",
        "HP": "https://support.hp.com/drivers",
        "Lenovo": "https://support.lenovo.com/us/en/downloads",
        "ASUS": "https://www.asus.com/support/download-center/",
        "Acer": "https://www.acer.com/us-en/support/drivers-and-manuals",
        "MSI": "https://www.msi.com/support/download",
    },
    "Graphics drivers": {
        "NVIDIA": "https://www.nvidia.com/Download/index.aspx",
        "AMD": "https://www.amd.com/en/support/download/drivers.html",
        "Intel": "https://www.intel.com/content/www/us/en/download-center/home.html",
    },
    "CPU chipset drivers": {
        "AMD": "https://www.amd.com/en/support/download/drivers.html",
        "Intel": "https://www.intel.com/content/www/us/en/download-center/home.html",
    },
    "WiFi drivers": {
        "Intel": "https://www.intel.com/content/www/us/en/download-center/home.html",
        "Qualcomm": "https://www.qualcomm.com/support/software",
        "Broadcom": "https://www.broadcom.com/support/download-search",
        "Realtek": "https://www.realtek.com/Download/List?cate_id=584",
    },
    "Bluetooth drivers": {
        "Intel": "https://www.intel.com/content/www/us/en/download-center/home.html",
        "Qualcomm": "https://www.qualcomm.com/support/software",
        "Broadcom": "https://www.broadcom.com/support/download-search",
        "Realtek": "https://www.realtek.com/Download/List?cate_id=584",
    },
    "Audio drivers": {
        "Realtek": "https://www.realtek.com/Download/List?cate_id=593",
    },
    "Storage / NVMe drivers": {
        "Intel": "https://www.intel.com/content/www/us/en/download-center/home.html",
        "AMD": "https://www.amd.com/en/support/download/drivers.html",
    },
    "System firmware / motherboard drivers": {
        "Dell": "https://www.dell.com/support/home/drivers",
        "HP": "https://support.hp.com/drivers",
        "Lenovo": "https://support.lenovo.com/us/en/downloads",
        "ASUS": "https://www.asus.com/support/download-center/",
        "Acer": "https://www.acer.com/us-en/support/drivers-and-manuals",
        "MSI": "https://www.msi.com/support/download",
    },
}

GENERAL_VENDOR_LINKS = {
    "NVIDIA": "https://www.nvidia.com/Download/index.aspx",
    "AMD": "https://www.amd.com/en/support/download/drivers.html",
    "Intel": "https://www.intel.com/content/www/us/en/download-center/home.html",
    "Realtek": "https://www.realtek.com/Downloads/",
    "Qualcomm": "https://www.qualcomm.com/support/software",
    "Broadcom": "https://www.broadcom.com/support/download-search",
    "Dell": "https://www.dell.com/support/home/drivers",
    "HP": "https://support.hp.com/drivers",
    "Lenovo": "https://support.lenovo.com/us/en/downloads",
    "ASUS": "https://www.asus.com/support/download-center/",
    "Acer": "https://www.acer.com/us-en/support/drivers-and-manuals",
    "MSI": "https://www.msi.com/support/download",
}


def get_links_for_category(category: str, vendors: list[str]) -> dict[str, str]:
    """Return official URLs for the given category and detected vendors."""
    category_map = CATEGORY_LINKS.get(category, {})
    resolved: dict[str, str] = {}

    for vendor in vendors:
        if vendor in category_map:
            resolved[vendor] = category_map[vendor]
        elif vendor in GENERAL_VENDOR_LINKS:
            resolved[vendor] = GENERAL_VENDOR_LINKS[vendor]

    if not resolved:
        for vendor, url in category_map.items():
            resolved[vendor] = url

    return resolved

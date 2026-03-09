from src.utils.vendor_links import resolve_best_link


def test_prefers_gpu_vendor_for_graphics() -> None:
    vendor, link = resolve_best_link("Graphics drivers", ["NVIDIA", "Intel"], "Dell")
    assert vendor == "NVIDIA"
    assert "nvidia.com" in link


def test_uses_oem_for_bios_when_component_vendor_present() -> None:
    vendor, link = resolve_best_link("BIOS / UEFI firmware", ["Intel"], "Lenovo")
    assert vendor == "Lenovo"
    assert "lenovo" in link.lower()


def test_fallback_link_always_available() -> None:
    vendor, link = resolve_best_link("Audio drivers", [], "Unknown")
    assert vendor
    assert link.startswith("https://")

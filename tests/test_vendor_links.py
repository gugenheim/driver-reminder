from src.utils.vendor_links import get_links_for_category


def test_vendor_link_resolution_prefers_category_link() -> None:
    links = get_links_for_category("Graphics drivers", ["NVIDIA"])
    assert "NVIDIA" in links
    assert "nvidia.com" in links["NVIDIA"]


def test_vendor_link_resolution_fallbacks_to_category_defaults() -> None:
    links = get_links_for_category("Audio drivers", ["UnknownVendor"])
    assert "Realtek" in links

import pytest
from pathlib import Path
from PIL import Image


def test_asset_paths_exist():
    """Verify all required assets exist"""
    assets_dir = Path(__file__).parent.parent.parent / "assets"

    required_assets = [
        "logo/primary/edgetaxai-horizontal-color.svg",
        "logo/primary/edgetaxai-vertical-color.svg",
        "logo/icon/edgetaxai-icon-color.svg",
        "logo/favicon/favicon.ico",
        "logo/app-icon/app-icon-android.png",
        "logo/app-icon/app-icon-ios.png",
    ]

    for asset in required_assets:
        assert (assets_dir / asset).exists(), f"Missing required asset: {asset}"


def test_image_formats():
    """Verify image formats are correct"""
    assets_dir = Path(__file__).parent.parent.parent / "assets"

    svg_files = list(assets_dir.rglob("*.svg"))
    png_files = list(assets_dir.rglob("*.png"))
    ico_files = list(assets_dir.rglob("*.ico"))

    for svg in svg_files:
        with open(svg, "r") as f:
            content = f.read()
            assert content.startswith("<?xml") or content.startswith(
                "<svg"
            ), f"Invalid SVG format: {svg}"

    # Verify PNG format
    for png in png_files:
        img = Image.open(png)
        assert img.format == "PNG", f"Invalid PNG format: {png}"


def test_favicon_sizes():
    """Verify favicon includes all required sizes"""
    favicon_dir = Path(__file__).parent.parent.parent / "assets" / "logo" / "favicon"
    required_sizes = ["16x16", "32x32", "96x96"]

    for size in required_sizes:
        assert (
            favicon_dir / f"favicon-{size}.png"
        ).exists(), f"Missing favicon size: {size}"


def test_app_icon_dimensions():
    """Verify app icon dimensions meet platform requirements"""
    assets_dir = Path(__file__).parent.parent.parent / "assets"

    # Test Android icon
    android_icon = Image.open(assets_dir / "logo" / "app-icon" / "app-icon-android.png")
    assert android_icon.size == (192, 192), "Android icon must be 192x192"

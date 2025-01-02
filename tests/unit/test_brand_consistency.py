import pytest
from pathlib import Path
import json
import re
import cssutils


def test_color_consistency():
    """Verify color usage matches design tokens"""
    with open("src/styles/tokens.js", "r") as file:
        content = file.read()
        # Extract color definitions
        primary_color = re.search(r'main: [\'"]#([0-9A-Fa-f]{6})[\'"]', content).group(
            1
        )

        # Check color usage in components
        components_directory = Path("src/components")
        for javascript_file in components_directory.rglob("*.js"):
            with open(javascript_file, "r") as component_file:
                component_content = component_file.read()
                assert (
                    primary_color.lower() in component_content.lower()
                ), f"Inconsistent color usage in {javascript_file}"


def test_typography_consistency():
    """Verify typography matches design system"""
    with open("src/styles/tokens.js", "r") as file:
        content = file.read()
        font_family = re.search(r'primary: [\'"]([^\'"]+)[\'"]', content).group(1)

        # Check font usage in components
        components_directory = Path("src/components")
        for javascript_file in components_directory.rglob("*.js"):
            with open(javascript_file, "r") as component_file:
                component_content = component_file.read()
                assert (
                    font_family in component_content
                ), f"Inconsistent font usage in {javascript_file}"


def test_spacing_consistency():
    """Verify spacing matches design tokens"""
    with open("src/styles/tokens.js", "r") as file:
        content = file.read()
        spacing_values = re.findall(r"spacing: {([^}]+)}", content)[0]

        # Check spacing usage in components
        components_directory = Path("src/components")
        for javascript_file in components_directory.rglob("*.js"):
            with open(javascript_file, "r") as component_file:
                component_content = component_file.read()
                for spacing_value in re.findall(r"\d+", spacing_values):
                    assert (
                        spacing_value in component_content
                    ), f"Inconsistent spacing in {javascript_file}"


def test_dark_mode_colors():
    """Verify dark mode color implementation"""
    with open("src/styles/tokens.js", "r") as f:
        content = f.read()
        dark_mode_colors = re.findall(r"darkMode:\s*{([^}]+)}", content)[0]

        components_dir = Path("src/components")
        for js_file in components_dir.rglob("*.js"):
            with open(js_file, "r") as component_file:
                component_content = component_file.read()
                assert (
                    "darkMode" in component_content
                ), f"Missing dark mode support in {js_file}"

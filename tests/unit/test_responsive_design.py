import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ExpectedConditions
import time

@pytest.mark.parametrize("viewport", [
    (375, 667),  # iPhone SE
    (390, 844),  # iPhone 12
    (768, 1024), # iPad
    (1280, 800), # Laptop
    (1920, 1080) # Desktop
])
def test_responsive_layout(driver, viewport):
    """Test responsive layout at different viewport sizes"""
    width, height = viewport
    driver.set_window_size(width, height)
    
    # Test critical components
    driver.get("/dashboard")
    
    # Check if navigation is properly displayed
    navigation = WebDriverWait(driver, 10).until(
        ExpectedConditions.presence_of_element_located((By.CLASS_NAME, "navigation"))
    )
    
    # Verify logo visibility
    logo = driver.find_element(By.CLASS_NAME, "logo")
    assert logo.is_displayed(), f"Logo not visible at {width}x{height}"
    
    # Check responsive menu
    if width < 768:
        menu_button = driver.find_element(By.CLASS_NAME, "menu-button")
        assert menu_button.is_displayed(), f"Menu button not visible on mobile"
    else:
        navigation_items = driver.find_elements(By.CLASS_NAME, "nav-item")
        assert all(item.is_displayed() for item in navigation_items), f"Nav items not visible on desktop"

def test_image_scaling():
    """Test that images scale properly across different viewport sizes"""
    viewports = [(375, 667), (1920, 1080)]
    for width, height in viewports:
        driver.set_window_size(width, height)
        images = driver.find_elements(By.TAG_NAME, "img")
        for img in images:
            assert img.is_displayed(), f"Image not visible at {width}x{height}"
            
def test_font_scaling():
    """Test that fonts scale appropriately"""
    viewports = [(375, 667), (1920, 1080)]
    for width, height in viewports:
        driver.set_window_size(width, height)
        headings = driver.find_elements(By.TAG_NAME, "h1")
        for heading in headings:
            font_size = heading.value_of_css_property("font-size")
            assert int(font_size.replace('px', '')) > 0

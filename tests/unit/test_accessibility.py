import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from axe_selenium_python import Axe
from selenium.webdriver.common.keys import Keys

def test_color_contrast():
    """Test color contrast meets WCAG guidelines"""
    driver.get("/dashboard")
    axe = Axe(driver)
    results = axe.run()
    violations = results["violations"]
    
    for violation in violations:
        if violation["id"] == "color-contrast":
            pytest.fail(f"Color contrast issue: {violation['description']}")

def test_aria_labels():
    """Test proper ARIA labels are present"""
    driver.get("/dashboard")
    interactive_elements = driver.find_elements(By.CSS_SELECTOR, "button, input, select")
    
    for element in interactive_elements:
        assert element.get_attribute("aria-label") or element.get_attribute("aria-labelledby"), \
            f"Missing ARIA label on element: {element.tag_name}"

def test_keyboard_navigation():
    """Test keyboard navigation functionality"""
    driver.get("/dashboard")
    focusable_elements = driver.find_elements(
        By.CSS_SELECTOR, 
        "a[href], button, input, select, textarea, [tabindex]:not([tabindex='-1'])"
    )
    
    for element in focusable_elements:
        element.send_keys(Keys.TAB)
        assert driver.switch_to.active_element == element, \
            f"Element not focusable: {element.tag_name}"

def test_image_alt_text():
    """Test all images have alt text"""
    driver.get("/dashboard")
    images = driver.find_elements(By.TAG_NAME, "img")
    
    for image in images:
        assert image.get_attribute("alt"), \
            f"Missing alt text on image: {image.get_attribute('src')}"

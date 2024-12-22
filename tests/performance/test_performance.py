import pytest
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_page_load_time():
    """Test page load performance"""
    start_time = time.time()
    driver.get("/dashboard")
    load_time = time.time() - start_time
    assert load_time < 3.0, f"Page load took {load_time} seconds"

def test_api_response_time():
    """Test API endpoint response times"""
    endpoints = [
        "/api/expenses",
        "/api/reports",
        "/api/tax-optimization",
        "/api/mileage"
    ]
    
    for endpoint in endpoints:
        start_time = time.time()
        response = requests.get(f"http://localhost:5000{endpoint}")
        response_time = time.time() - start_time
        assert response_time < 1.0, f"API endpoint {endpoint} took {response_time} seconds"

def test_memory_usage():
    """Test memory usage during operations"""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # Convert to MB
    
    # Perform memory-intensive operation
    driver.get("/dashboard")
    driver.find_element(By.ID, "load-data").click()
    
    final_memory = process.memory_info().rss / 1024 / 1024
    memory_increase = final_memory - initial_memory
    
    assert memory_increase < 100, f"Memory usage increased by {memory_increase}MB"

def test_animation_smoothness():
    """Test animation frame rate"""
    from selenium.webdriver.common.action_chains import ActionChains
    
    driver.get("/dashboard")
    menu_button = driver.find_element(By.ID, "menu-toggle")
    
    # Measure frame timing
    start_time = time.time()
    ActionChains(driver).move_to_element(menu_button).click().perform()
    end_time = time.time()
    
    animation_duration = end_time - start_time
    assert animation_duration < 0.3, f"Animation took {animation_duration} seconds"

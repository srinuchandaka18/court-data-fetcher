from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def test_selenium():
    try:
        print("Testing Selenium setup...")
        
        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in background
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Setup WebDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Test navigation
        driver.get("https://www.google.com")
        print(f"✓ Successfully navigated to: {driver.title}")
        
        driver.quit()
        print("✓ Selenium setup working correctly!")
        
    except Exception as e:
        print(f"✗ Selenium test failed: {e}")
        print("Make sure Chrome browser is installed on your system")

if __name__ == "__main__":
    test_selenium()

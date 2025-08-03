from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

def inspect_delhi_high_court():
    """Inspect the actual Delhi High Court website structure"""
    
    # Setup Chrome (non-headless to see what's happening)
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        print("🔍 Inspecting Delhi High Court website...")
        
        # Navigate to the main site
        driver.get("https://delhihighcourt.nic.in/")
        time.sleep(3)
        
        print(f"📄 Page Title: {driver.title}")
        print(f"🔗 Current URL: {driver.current_url}")
        
        # Look for case status/search links
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Find all links that might lead to case search
        case_links = []
        for link in soup.find_all('a', href=True):
            href = link.get('href', '').lower()
            text = link.get_text().strip().lower()
            
            if any(keyword in href or keyword in text for keyword in 
                   ['case', 'status', 'search', 'enquiry', 'cause list']):
                case_links.append({
                    'text': link.get_text().strip(),
                    'href': link.get('href')
                })
        
        print("\n📋 Found potential case search links:")
        for i, link in enumerate(case_links[:10], 1):  # Show first 10
            print(f"{i}. {link['text']} -> {link['href']}")
        
        # Try to find the most likely case search page
        likely_urls = [
            "/case_status",
            "/casestatus", 
            "/case-search",
            "/search",
            "/cause-list",
            "/daily-order"
        ]
        
        print("\n🎯 Testing likely case search URLs:")
        for url in likely_urls:
            try:
                test_url = f"https://delhihighcourt.nic.in{url}"
                driver.get(test_url)
                time.sleep(2)
                
                if "404" not in driver.title and "error" not in driver.title.lower():
                    print(f"✅ Found working URL: {test_url}")
                    print(f"   Page title: {driver.title}")
                    
                    # Inspect forms on this page
                    inspect_forms_on_page(driver)
                    break
                else:
                    print(f"❌ {test_url} - Not found")
            except:
                print(f"❌ {test_url} - Error accessing")
        
        print("\n⏳ Browser will stay open for 30 seconds for manual inspection...")
        print("Feel free to manually navigate to the case search page to see the form structure.")
        time.sleep(30)
        
    except Exception as e:
        print(f"❌ Error during inspection: {e}")
    finally:
        driver.quit()

def inspect_forms_on_page(driver):
    """Inspect all forms on the current page"""
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    forms = soup.find_all('form')
    
    print(f"\n📝 Found {len(forms)} form(s) on this page:")
    
    for i, form in enumerate(forms, 1):
        print(f"\n--- Form {i} ---")
        print(f"Action: {form.get('action', 'Not specified')}")
        print(f"Method: {form.get('method', 'GET')}")
        
        # Find all input fields
        inputs = form.find_all(['input', 'select', 'textarea'])
        print(f"Form fields ({len(inputs)}):")
        
        for input_field in inputs:
            field_type = input_field.get('type', input_field.name)
            field_name = input_field.get('name', 'unnamed')
            field_id = input_field.get('id', 'no-id')
            
            if input_field.name == 'select':
                options = [opt.get_text().strip() for opt in input_field.find_all('option')][:5]
                print(f"  - {field_type}: name='{field_name}', id='{field_id}' (options: {options}...)")
            else:
                placeholder = input_field.get('placeholder', '')
                print(f"  - {field_type}: name='{field_name}', id='{field_id}', placeholder='{placeholder}'")

if __name__ == "__main__":
    inspect_delhi_high_court()

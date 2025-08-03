from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

def inspect_specific_case_pages():
    """Inspect the specific case search pages we found"""
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # URLs we discovered
    case_urls = [
        "https://delhihighcourt.nic.in/app/get-case-type-status",
        "https://delhihighcourt.nic.in/app/case-number",
        "https://delhihighcourt.nic.in/web/case-history-0"
    ]
    
    try:
        for url in case_urls:
            print(f"\n{'='*60}")
            print(f"🔍 Inspecting: {url}")
            print('='*60)
            
            try:
                driver.get(url)
                time.sleep(3)
                
                print(f"📄 Page Title: {driver.title}")
                print(f"✅ Status: Page loaded successfully")
                
                # Parse and inspect forms
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                inspect_forms_detailed(soup, url)
                
            except Exception as e:
                print(f"❌ Error loading {url}: {e}")
        
        print(f"\n{'='*60}")
        print("⏳ Browser staying open for manual inspection...")
        print("Navigate to the working case search page and examine the form structure.")
        print("Look for: dropdown options, input field names, submit button.")
        print('='*60)
        time.sleep(45)  # Extended time for manual inspection
        
    finally:
        driver.quit()

def inspect_forms_detailed(soup, url):
    """Detailed form inspection"""
    forms = soup.find_all('form')
    
    if not forms:
        print("❌ No forms found on this page")
        return
    
    print(f"📝 Found {len(forms)} form(s):")
    
    for i, form in enumerate(forms, 1):
        print(f"\n--- Form {i} ---")
        print(f"Action: {form.get('action', 'Not specified')}")
        print(f"Method: {form.get('method', 'GET').upper()}")
        print(f"Class: {form.get('class', 'No class')}")
        print(f"ID: {form.get('id', 'No ID')}")
        
        # Find all form inputs
        form_elements = form.find_all(['input', 'select', 'textarea', 'button'])
        
        if form_elements:
            print(f"\nForm Elements ({len(form_elements)}):")
            
            for element in form_elements:
                element_info = []
                element_info.append(f"Type: {element.name}")
                
                if element.get('type'):
                    element_info.append(f"input-type: {element.get('type')}")
                
                if element.get('name'):
                    element_info.append(f"name: '{element.get('name')}'")
                
                if element.get('id'):
                    element_info.append(f"id: '{element.get('id')}'")
                
                if element.get('class'):
                    element_info.append(f"class: '{' '.join(element.get('class'))}'")
                
                if element.get('placeholder'):
                    element_info.append(f"placeholder: '{element.get('placeholder')}'")
                
                # For select elements, show options
                if element.name == 'select':
                    options = [opt.get_text().strip() for opt in element.find_all('option') if opt.get_text().strip()]
                    if options:
                        element_info.append(f"options: {options[:5]}{'...' if len(options) > 5 else ''}")
                
                print(f"  • {' | '.join(element_info)}")
        else:
            print("❌ No form elements found")

if __name__ == "__main__":
    inspect_specific_case_pages()

import requests
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import logging
from urllib.parse import urljoin, urlparse
import json
import pytesseract
import os
from PIL import Image, ImageEnhance, ImageFilter

# Configure Tesseract path for Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Test configuration
try:
    print(f"✓ Tesseract version: {pytesseract.get_tesseract_version()}")
except Exception as e:
    print(f"❌ Tesseract configuration error: {e}")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CourtScraper:
    def __init__(self, target_court="delhi_high_court", demo_mode=False):
        self.demo_mode = demo_mode
        
        if self.demo_mode:
            from demo_scraper import DemoCourtScraper
            self.demo_scraper = DemoCourtScraper()
            logger.info("🎭 Running in DEMO MODE - using simulated data")
            return
        
        self.target_court = target_court
        self.setup_court_config()
        self.setup_selenium()
        self.session = requests.Session()
        
    def setup_court_config(self):
        """Configure court-specific settings with EXACT discovered structure"""
        if self.target_court == "delhi_high_court":
            self.base_url = "https://delhihighcourt.nic.in"
            # Use the EXACT working URL we discovered
            self.case_search_url = "https://delhihighcourt.nic.in/app/case-number"
            
            # Use the EXACT form selectors from inspection
            self.form_selectors = {
                'form_id': 'search1',
                'case_type': 'select[name="case_type"]',
                'case_number': 'input[name="case_number"]',
                'year': 'select[name="year"]',
                'captcha_input': 'input[name="captchaInput"]',
                'captcha_image': 'img[src*="captcha"]',
                'submit': 'button[id="search"]',
                '_token': 'input[name="_token"]',
                'randomid': 'input[name="randomid"]'
            }
        else:
            raise ValueError(f"Unsupported court: {self.target_court}")
    
    def setup_selenium(self):
        """Setup Selenium WebDriver with optimal configurations"""
        chrome_options = Options()
        
        # Essential options for stability
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        # Optional: Run in headless mode (comment out for debugging)
        # chrome_options.add_argument("--headless")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 15)
        logger.info("✓ Chrome WebDriver initialized successfully")
    
    def search_case(self, case_type, case_number, filing_year):
        """Main method to search for case details"""
        
        if self.demo_mode:
            return self.demo_scraper.search_case(case_type, case_number, filing_year)
        
        start_time = time.time()
        
        try:
            logger.info(f"Searching case: {case_type} {case_number}/{filing_year}")
            
            # Navigate to the EXACT working URL
            self.driver.get(self.case_search_url)
            time.sleep(3)
            
            # Wait for form to load
            form = self.wait.until(
                EC.presence_of_element_located((By.ID, self.form_selectors['form_id']))
            )
            logger.info("✓ Form loaded successfully")
            
            # Fill form fields using EXACT selectors
            success = self.fill_search_form_exact(case_type, case_number, filing_year)
            if not success:
                return {"error": "Failed to fill search form"}
            
            # Handle CAPTCHA
            captcha_solved = self.handle_captcha_exact()
            if not captcha_solved:
                return {"error": "CAPTCHA solving failed or required manual intervention"}
            
            # Submit form and wait for results
            submit_success = self.submit_form_and_wait_exact()
            if not submit_success:
                return {"error": "Form submission failed or results not loaded"}
            
            # Parse results
            result = self.parse_case_details()
            result['search_duration'] = time.time() - start_time
            
            return result
            
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return {"error": f"Search failed: {str(e)}"}
    
    def fill_search_form_exact(self, case_type, case_number, filing_year):
        """Fill form using exact discovered selectors"""
        try:
            # Select case type using exact selector
            case_type_select = Select(self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.form_selectors['case_type']))
            ))
            
            # Get available options for case type
            options = [option.text for option in case_type_select.options if option.text != 'Select']
            logger.info(f"Available case types: {options[:5]}...")
            
            # Try to match the case type
            matched = False
            for option in case_type_select.options:
                if option.text != 'Select' and case_type.lower() in option.text.lower():
                    case_type_select.select_by_visible_text(option.text)
                    logger.info(f"✓ Selected case type: {option.text}")
                    matched = True
                    break
            
            if not matched:
                # Default to first available option
                case_type_select.select_by_index(1)
                logger.warning(f"Case type '{case_type}' not found, using default")
            
            # Enter case number using exact selector
            case_number_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.form_selectors['case_number']))
            )
            case_number_input.clear()
            case_number_input.send_keys(case_number)
            logger.info(f"✓ Entered case number: {case_number}")
            
            # Select year using exact selector
            year_select = Select(self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.form_selectors['year']))
            ))
            
            year_options = [option.text for option in year_select.options if option.text != 'Select']
            logger.info(f"Available years: {year_options}")
            
            if str(filing_year) in year_options:
                year_select.select_by_visible_text(str(filing_year))
                logger.info(f"✓ Selected year: {filing_year}")
            else:
                logger.warning(f"Year {filing_year} not available, using 2024")
                year_select.select_by_visible_text('2024')
            
            return True
            
        except Exception as e:
            logger.error(f"Form filling failed: {str(e)}")
            return False
        
    def handle_captcha_exact(self):
        """Handle CAPTCHA with automatic numeric solving"""
        try:
            captcha_input = self.driver.find_elements(By.CSS_SELECTOR, self.form_selectors.get('captcha_input', 'input[name="captchaInput"]'))
            
            if not captcha_input:
                logger.info("No CAPTCHA input field found")
                return True
            
            logger.info("CAPTCHA field detected")
            
            # Check if CAPTCHA image exists
            captcha_images = self.driver.find_elements(By.CSS_SELECTOR, 'img[src*="captcha"]')
            
            if captcha_images:
                logger.info("CAPTCHA image found - attempting automatic numeric solving")
                
                # Try automatic solving first
                if self.solve_numeric_captcha(captcha_images[0], captcha_input[0]):
                    logger.info("✓ CAPTCHA solved automatically!")
                    time.sleep(1)  # Wait for solution to register
                    return True
                else:
                    # Fall back to manual if automatic fails
                    logger.warning("⚠ Automatic solving failed, requiring manual intervention")
                    return self.manual_captcha_solving()
            else:
                logger.info("CAPTCHA input found but no image - may not be required")
                return True
                
        except Exception as e:
            logger.error(f"CAPTCHA handling failed: {str(e)}")
            return False

    def solve_numeric_captcha(self, captcha_image, captcha_input):
        """Automatically solve numeric CAPTCHA using enhanced OCR"""
        try:
            logger.info("Starting automatic CAPTCHA solving...")
            
            # Take screenshot of CAPTCHA
            captcha_image.screenshot("captcha_temp.png")
            
            # Open and preprocess the image for better OCR
            image = Image.open("captcha_temp.png")
            
            # Convert to grayscale for better OCR
            image = image.convert('L')
            
            # Enhance image for better number recognition
            # Increase contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.5)
            
            # Increase sharpness
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(2.0)
            
            # Apply slight blur to smooth noise
            image = image.filter(ImageFilter.MedianFilter(size=1))
            
            # Save processed image for debugging
            image.save("captcha_processed.png")
            logger.info("✓ Image preprocessing completed")
            
            # Configure Tesseract specifically for numbers only
            # This configuration is optimized for numeric CAPTCHAs
            custom_config = r'--oem 3 --psm 8 -c tessedit_char_whitelist=0123456789'
            
            # Extract text using OCR
            captcha_text = pytesseract.image_to_string(image, config=custom_config).strip()
            
            # Clean the result - keep only numbers
            import re
            captcha_numbers = re.sub(r'[^0-9]', '', captcha_text)
            
            logger.info(f"OCR extracted: '{captcha_text}' -> cleaned: '{captcha_numbers}'")
            
            # Validate that we got reasonable numbers (adjust length as needed)
            if captcha_numbers and len(captcha_numbers) >= 3 and len(captcha_numbers) <= 8:
                # Enter the solution
                captcha_input.clear()
                time.sleep(0.3)
                captcha_input.send_keys(captcha_numbers)
                time.sleep(0.5)
                
                logger.info(f"✓ Entered CAPTCHA solution: {captcha_numbers}")
                return True
            else:
                logger.warning(f"❌ Invalid CAPTCHA result: '{captcha_numbers}' (length: {len(captcha_numbers) if captcha_numbers else 0})")
                return False
                
        except ImportError as e:
            logger.error(f"❌ Missing dependencies: {e}")
            logger.error("Install with: pip install pytesseract pillow")
            return False
        except Exception as e:
            logger.error(f"❌ Numeric CAPTCHA solving failed: {str(e)}")
            return False
        finally:
            # Clean up temporary files
            try:
                if os.path.exists("captcha_temp.png"):
                    os.remove("captcha_temp.png")
                if os.path.exists("captcha_processed.png"):
                    os.remove("captcha_processed.png")
            except:
                pass

    def manual_captcha_solving(self):
        """Fallback to manual CAPTCHA solving"""
        try:
            # Make browser window prominent
            self.driver.set_window_position(0, 0)
            self.driver.maximize_window()
            
            print("\n" + "="*60)
            print("🔒 AUTOMATIC CAPTCHA SOLVING FAILED!")
            print("Please solve the CAPTCHA manually:")
            print("1. Look at the browser window")
            print("2. Read the numbers in the CAPTCHA image")
            print("3. Type them in the CAPTCHA field")
            print("4. Press Enter here to continue")
            print("="*60)
            
            input("Press Enter after solving CAPTCHA manually: ")
            return True
            
        except Exception as e:
            logger.error(f"Manual CAPTCHA fallback failed: {str(e)}")
            return False

    
    def submit_form_and_wait_exact(self):
        """Submit form using exact selector"""
        try:
            # Find submit button using exact selector
            submit_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, self.form_selectors['submit']))
            )
            
            logger.info("✓ Submit button found, clicking...")
            submit_button.click()
            
            # Wait for page to change or results to load
            self.wait.until(
                EC.any_of(
                    EC.presence_of_element_located((By.TAG_NAME, "table")),
                    EC.presence_of_element_located((By.CLASS_NAME, "result")),
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'result')]")),
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'No record')]"))
                )
            )
            
            time.sleep(3)  # Additional wait for content to load
            logger.info("✓ Results page loaded")
            return True
            
        except Exception as e:
            logger.error(f"Form submission failed: {str(e)}")
            return False
    
    def parse_case_details(self):
        """Enhanced parsing for Delhi High Court structure"""
        try:
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Save HTML for analysis
            with open('delhi_court_response.html', 'w', encoding='utf-8') as f:
                f.write(page_source)
            
            # Check for SweetAlert popup (common in court websites)
            sweetalert = soup.find('div', class_='swal2-popup')
            if sweetalert:
                alert_text = sweetalert.get_text(strip=True)
                if 'no record' in alert_text.lower() or 'not found' in alert_text.lower():
                    return {"error": "No records found for the given case details"}
            
            # Enhanced extraction strategies...
            case_details = {
                "parties_names": self.extract_parties_names(soup),
                "filing_date": self.extract_filing_date(soup),
                "next_hearing_date": self.extract_next_hearing_date(soup),
                "case_status": self.extract_case_status(soup),
                "pdf_links": self.extract_pdf_links(soup),
                "additional_info": self.extract_additional_info(soup)
            }

    

            return case_details
            
        except Exception as e:
            logger.error(f"Enhanced parsing failed: {str(e)}")
            return {"error": f"Parsing failed: {str(e)}"}

    
    def check_no_results(self, soup):
        """Check if no results were found"""
        no_result_indicators = [
            "no record found", "no records found", "no data found",
            "record not found", "case not found", "not available",
            "no results", "invalid case"
        ]
        
        page_text = soup.get_text().lower()
        return any(indicator in page_text for indicator in no_result_indicators)
    
    def extract_parties_names(self, soup):
        """Extract parties' names"""
        strategies = [
            lambda: self.extract_by_label(soup, ["parties", "petitioner", "appellant", "vs", "respondent"]),
            lambda: self.extract_from_table_header(soup, "parties"),
            lambda: self.extract_by_pattern(soup, r"([A-Z][a-zA-Z\s]+)\s+(?:vs?\.?|v\.?)\s+([A-Z][a-zA-Z\s]+)")
        ]
        
        for strategy in strategies:
            try:
                result = strategy()
                if result and result != "Not found" and len(result) > 5:
                    return result
            except:
                continue
        
        return "Not found"
    
    def extract_filing_date(self, soup):
        """Extract filing date"""
        return self.extract_by_label(soup, ["filing date", "date of filing", "registered on", "filed on"])
    
    def extract_next_hearing_date(self, soup):
        """Extract next hearing date"""
        return self.extract_by_label(soup, ["next hearing", "next date", "hearing date", "next listing"])
    
    def extract_case_status(self, soup):
        """Extract case status"""
        return self.extract_by_label(soup, ["status", "case status", "stage", "current status"])
    
    def extract_by_label(self, soup, labels):
        """Generic extraction by label text"""
        for label in labels:
            # Try table-based extraction
            label_cell = soup.find("td", string=re.compile(label, re.I))
            if label_cell:
                next_cell = label_cell.find_next_sibling("td")
                if next_cell:
                    text = next_cell.get_text(strip=True)
                    if text and len(text) > 1:
                        return text
            
            # Try other HTML structures
            for tag in ["span", "div", "p", "strong"]:
                element = soup.find(tag, string=re.compile(label, re.I))
                if element:
                    next_element = element.find_next_sibling()
                    if next_element:
                        text = next_element.get_text(strip=True)
                        if text and len(text) > 1:
                            return text
        
        return "Not found"
    
    def extract_from_table_header(self, soup, header_text):
        """Extract data from table with specific header"""
        try:
            header = soup.find("th", string=re.compile(header_text, re.I))
            if header:
                headers = header.parent.find_all("th")
                col_index = headers.index(header)
                
                table = header.find_parent("table")
                data_rows = table.find_all("tr")[1:]
                if data_rows:
                    data_cells = data_rows[0].find_all("td")
                    if len(data_cells) > col_index:
                        return data_cells[col_index].get_text(strip=True)
        except:
            pass
        
        return "Not found"
    
    def extract_by_pattern(self, soup, pattern):
        """Extract using regex pattern"""
        try:
            text = soup.get_text()
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        except:
            pass
        
        return "Not found"
    
    def extract_pdf_links(self, soup):
        """Extract PDF download links"""
        pdf_links = []
        try:
            # Find all PDF links
            pdf_anchors = soup.find_all("a", href=re.compile(r"\.pdf", re.I))
            
            for anchor in pdf_anchors:
                pdf_url = anchor.get("href")
                if pdf_url:
                    if not pdf_url.startswith("http"):
                        pdf_url = urljoin(self.base_url, pdf_url)
                    
                    pdf_links.append({
                        "title": anchor.get_text(strip=True) or "Court Document",
                        "url": pdf_url
                    })
            
        except Exception as e:
            logger.error(f"PDF extraction failed: {str(e)}")
        
        return pdf_links
    
    def extract_additional_info(self, soup):
        """Extract additional case information"""
        additional_info = {}
        try:
            tables = soup.find_all("table")
            for table in tables:
                rows = table.find_all("tr")
                for row in rows:
                    cells = row.find_all(["td", "th"])
                    if len(cells) >= 2:
                        key = cells[0].get_text(strip=True)
                        value = cells[1].get_text(strip=True)
                        if key and value and len(key) < 50 and len(value) > 1:
                            additional_info[key.lower().replace(" ", "_")] = value
        except:
            pass
        
        return additional_info
    
    def __del__(self):
        """Cleanup WebDriver"""
        try:
            if hasattr(self, 'driver'):
                self.driver.quit()
                logger.info("✓ WebDriver cleaned up")
        except:
            pass

# Test the updated scraper
if __name__ == "__main__":
    print("Testing Updated Court Scraper...")
    
    # Test in demo mode first
    print("\n1. Testing DEMO MODE:")
    demo_scraper = CourtScraper(demo_mode=True)
    result = demo_scraper.search_case("Civil Appeal", "123", 2024)
    print(f"Demo result: {result}")
    
    # Test real scraper
    print("\n2. Testing REAL SCRAPER:")
    real_scraper = CourtScraper(demo_mode=False)
    result = real_scraper.search_case("ARB.A.", "123", 2024)
    print(f"Real result: {result}")


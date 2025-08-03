import time
import json
import random
from datetime import datetime, timedelta

class DemoCourtScraper:
    """Demo scraper that simulates court data fetching for testing"""
    
    def __init__(self):
        self.demo_cases = {
            ("Civil Appeal", "123", 2024): {
                "parties_names": "John Doe vs State of Delhi",
                "filing_date": "15/01/2024",
                "next_hearing_date": "25/08/2024",
                "case_status": "Pending Arguments",
                "pdf_links": [
                    {"title": "Petition", "url": "https://example.com/petition.pdf"},
                    {"title": "Previous Order", "url": "https://example.com/order.pdf"}
                ],
                "additional_info": {
                    "court_number": "Court No. 5",
                    "judge": "Hon'ble Justice XYZ",
                    "case_type_full": "Civil Appeal"
                }
            },
            ("ARB.A.", "123", 2024): {
                "parties_names": "XYZ Corporation vs ABC Limited",
                "filing_date": "10/02/2024",
                "next_hearing_date": "20/08/2024",
                "case_status": "Under Arguments",
                "pdf_links": [
                    {"title": "Arbitration Petition", "url": "https://example.com/arb.pdf"}
                ],
                "additional_info": {
                    "court_number": "Court No. 3",
                    "judge": "Hon'ble Justice ABC",
                    "case_type_full": "Arbitration Appeal"
                }
            }
        }
    
    def search_case(self, case_type, case_number, filing_year):
        """Simulate case search with realistic delays"""
        
        print(f"🔍 [DEMO] Searching for: {case_type} {case_number}/{filing_year}")
        
        # Simulate network delay
        time.sleep(random.uniform(1, 3))
        
        case_key = (case_type, case_number, int(filing_year))
        
        if case_key in self.demo_cases:
            result = self.demo_cases[case_key].copy()
            result['search_duration'] = random.uniform(2, 5)
            result['raw_html'] = f"<html><body>Demo data for {case_type} {case_number}/{filing_year}</body></html>"
            
            print("✅ [DEMO] Case found in demo database")
            return result
        else:
            print("❌ [DEMO] Case not found in demo database")
            return {"error": "No records found for the given case details"}

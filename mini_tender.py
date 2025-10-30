import json
import os
import csv
from datetime import datetime
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Architecture and consultancy related keywords
KEYWORDS = [
    'architect', 'architecture', 'architectural', 'design',
    'consultancy', 'consultant', 'consulting', 'supervision',
    'engineering design', 'structural', 'building design',
    'master plan', 'feasibility study', 'detailed design',
    'construction supervision', 'project management consultant',
    'dpr', 'survey', 'estimate', 'drawing', 'technical', 'planning'
]

class BolpatraScraper:
    def __init__(self, headless=True):
        self.headless = headless
        self.driver = None
    
    def init_driver(self):
        """Initialize Chrome WebDriver with options."""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless')
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--ignore-ssl-errors')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_page_load_timeout(30)
            print("✓ WebDriver initialized successfully")
            return True
        except Exception as e:
            print(f"✗ Failed to initialize WebDriver: {e}")
            print("Make sure ChromeDriver is installed: pip install webdriver-manager")
            return False
    
    def close(self):
        """Close the browser."""
        if self.driver:
            self.driver.quit()
            print("✓ Browser closed")
    
    def scrape_tenders(self, scrape_all_pages=True):
        """
        Scrape tenders from bolpatra.gov.np
        Returns list of tender dictionaries
        scrape_all_pages: If True, scrapes until no more pages available
        """
        if not self.driver:
            if not self.init_driver():
                return []
        
        tenders = []
        base_url = "https://bolpatra.gov.np/egp"
        
        try:
            print("\n📡 Connecting to Bolpatra...")
            
            # Navigate to public tenders page
            self.driver.get(f"{base_url}/public")
            time.sleep(3)  # Wait for page load
            
            print("✓ Page loaded successfully")
            
            # Try to find and click on "Published Bids" or similar
            try:
                # Look for the bid opportunities link
                opportunities_link = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.LINK_TEXT, "Bid Opportunities"))
                )
                opportunities_link.click()
                time.sleep(2)
            except:
                # Alternative: direct navigation
                self.driver.get(f"{base_url}/searchOpportunity")
                time.sleep(3)
            
            print("✓ Navigated to tender listings")
            
            # Scrape all pages
            page = 1
            while True:
                print(f"\n📄 Scraping page {page}...")
                
                page_tenders = self.scrape_current_page()
                tenders.extend(page_tenders)
                
                print(f"   Found {len(page_tenders)} tenders on this page")
                
                # Try to go to next page
                if scrape_all_pages:
                    if not self.go_to_next_page():
                        print("   ✓ Reached last page")
                        break
                    page += 1
                else:
                    break
                
                time.sleep(2)  # Be polite to the server
            
            print(f"\n✓ Total tenders scraped: {len(tenders)}")
            return tenders
            
        except Exception as e:
            print(f"✗ Error during scraping: {e}")
            return tenders
    
    def scrape_current_page(self):
        """Scrape all tenders from the current page."""
        tenders = []
        
        try:
            # Wait for tender table/list to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
            
            # Find all tender rows (adjust selectors based on actual HTML)
            # Common patterns in Nepali government sites:
            tender_rows = self.driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
            
            if not tender_rows:
                # Try alternative selectors
                tender_rows = self.driver.find_elements(By.CSS_SELECTOR, ".tender-row")
            
            if not tender_rows:
                tender_rows = self.driver.find_elements(By.CSS_SELECTOR, "tr.data-row")
            
            for row in tender_rows:
                try:
                    tender_data = self.parse_tender_row(row)
                    if tender_data:
                        tenders.append(tender_data)
                except Exception as e:
                    continue
            
        except TimeoutException:
            print("   Timeout waiting for tender table")
        except Exception as e:
            print(f"   Error scraping page: {e}")
        
        return tenders
    
    def parse_tender_row(self, row):
        """Parse individual tender row."""
        try:
            # Get all cells in the row
            cells = row.find_elements(By.TAG_NAME, "td")
            
            if len(cells) < 4:
                return None
            
            # Common structure (adjust based on actual site):
            # [#, Tender No, Title, Organization, Type, Amount, Deadline, Status]
            
            # Extract title (usually in 2nd or 3rd column)
            title = ""
            for i in [1, 2, 3]:
                if i < len(cells):
                    text = cells[i].text.strip()
                    if len(text) > 20:  # Likely the title
                        title = text
                        break
            
            if not title:
                return None
            
            # Extract organization
            organization = ""
            for cell in cells:
                text = cell.text.strip()
                if any(org_word in text.lower() for org_word in ['office', 'department', 'ministry', 'division']):
                    organization = text
                    break
            
            # Extract amount
            amount = 0
            for cell in cells:
                text = cell.text.strip()
                # Look for numbers with Rs or NPR
                amount_match = re.search(r'(?:Rs\.?|NPR)?\s*([\d,]+(?:\.\d+)?)', text)
                if amount_match:
                    amount_str = amount_match.group(1).replace(',', '')
                    try:
                        amount = float(amount_str)
                        break
                    except:
                        pass
            
            # Extract deadline
            deadline = ""
            for cell in cells:
                text = cell.text.strip()
                # Look for date patterns (YYYY-MM-DD or DD/MM/YYYY or DD-MM-YYYY)
                date_match = re.search(r'(\d{4}[-/]\d{2}[-/]\d{2}|\d{2}[-/]\d{2}[-/]\d{4})', text)
                if date_match:
                    date_str = date_match.group(1)
                    deadline = self.normalize_date(date_str)
                    break
            
            # Extract category/type
            category = "Not specified"
            for cell in cells:
                text = cell.text.strip().lower()
                if 'consult' in text:
                    category = "Consultancy"
                    break
                elif 'goods' in text:
                    category = "Goods"
                    break
                elif 'works' in text or 'construction' in text:
                    category = "Works"
                    break
            
            # Try to click and get more details
            try:
                # Look for view/detail link
                detail_link = row.find_element(By.CSS_SELECTOR, "a.btn, a.view-btn, a[href*='detail']")
                detail_url = detail_link.get_attribute('href')
            except:
                detail_url = None
            
            return {
                'title': title,
                'organization': organization or "Not specified",
                'amount': amount,
                'deadline': deadline or "Not specified",
                'category': category,
                'province': "Not specified",
                'description': "",
                'source': 'Bolpatra',
                'scraped_date': datetime.now().strftime("%Y-%m-%d"),
                'url': detail_url
            }
            
        except Exception as e:
            return None
    
    def normalize_date(self, date_str):
        """Convert various date formats to YYYY-MM-DD."""
        try:
            # Try different formats
            for fmt in ["%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d"]:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.strftime("%Y-%m-%d")
                except:
                    continue
            return date_str
        except:
            return date_str
    
    def go_to_next_page(self):
        """Navigate to next page of results."""
        try:
            # Look for next button
            next_button = self.driver.find_element(By.CSS_SELECTOR, 
                "a.next, button.next, a[aria-label='Next'], li.next a")
            
            if 'disabled' in next_button.get_attribute('class'):
                return False
            
            next_button.click()
            time.sleep(2)
            return True
            
        except NoSuchElementException:
            return False
    
    def get_tender_details(self, tender_url):
        """Get detailed information about a specific tender."""
        try:
            self.driver.get(tender_url)
            time.sleep(2)
            
            # Scrape additional details from detail page
            # This would include full description, documents, etc.
            description_elem = self.driver.find_element(By.CSS_SELECTOR, ".description, .detail")
            description = description_elem.text.strip()
            
            return {'description': description}
            
        except Exception as e:
            return {}


class TenderManager:
    def __init__(self):
        self.json_filename = "tenders.json"
        self.csv_filename = "tenders.csv"
        self.tenders = []
        self.scraper = None
        self.load_data()
    
    def load_data(self):
        """Load tenders from JSON or CSV, prioritizing JSON."""
        # Try loading from JSON first
        if os.path.exists(self.json_filename):
            print(f"📂 Loading data from {self.json_filename}...")
            self.tenders = self.load_from_json()
        # If no JSON, try CSV
        elif os.path.exists(self.csv_filename):
            print(f"📂 Loading data from {self.csv_filename}...")
            self.tenders = self.load_from_csv()
        # If neither exists, use defaults
        else:
            print("📂 No existing data found, starting with defaults...")
            self.tenders = self.get_default_tenders()
        
        print(f"✓ Loaded {len(self.tenders)} tender(s)")
    
    def load_from_json(self):
        """Load tenders from JSON file."""
        try:
            with open(self.json_filename, "r", encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠ Error loading JSON: {e}")
            return self.get_default_tenders()
    
    def load_from_csv(self):
        """Load tenders from CSV file."""
        try:
            tenders = []
            with open(self.csv_filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Convert amount to float
                    if 'amount' in row:
                        try:
                            row['amount'] = float(row['amount'])
                        except:
                            row['amount'] = 0
                    tenders.append(row)
            return tenders
        except Exception as e:
            print(f"⚠ Error loading CSV: {e}")
            return self.get_default_tenders()
    
    def save_to_json(self):
        """Save tenders to JSON file."""
        try:
            with open(self.json_filename, "w", encoding='utf-8') as f:
                json.dump(self.tenders, f, indent=2, ensure_ascii=False)
            print(f"✓ Saved to {self.json_filename}")
        except Exception as e:
            print(f"✗ Error saving JSON: {e}")
    
    def save_to_csv(self):
        """Save tenders to CSV file."""
        try:
            if not self.tenders:
                print("⚠ No tenders to save")
                return
            
            # Get all possible fields
            fieldnames = set()
            for tender in self.tenders:
                fieldnames.update(tender.keys())
            fieldnames = sorted(fieldnames)
            
            with open(self.csv_filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.tenders)
            print(f"✓ Saved to {self.csv_filename}")
        except Exception as e:
            print(f"✗ Error saving CSV: {e}")
    
    def save_data(self, format='both'):
        """Save tenders to file(s).
        
        Args:
            format: 'json', 'csv', or 'both' (default)
        """
        if format in ['json', 'both']:
            self.save_to_json()
        if format in ['csv', 'both']:
            self.save_to_csv()
    
    def get_default_tenders(self):
        """Return default sample tenders."""
        return [
            {
                "title": "Architectural Design for Community Building",
                "province": "Bagmati",
                "organization": "Urban Dev Office",
                "amount": 500000,
                "deadline": "2025-02-15",
                "category": "Consultancy",
                "description": "Design services for community center",
                "source": "Manual",
                "scraped_date": datetime.now().strftime("%Y-%m-%d")
            }
        ]
    
    def is_relevant_tender(self, title, description=""):
        """Check if tender is related to architecture or consultancy."""
        text = (title + " " + description).lower()
        return any(keyword in text for keyword in KEYWORDS)
    
    def scrape_bolpatra(self, headless=True):
        """Scrape ALL available tenders from Bolpatra using Selenium."""
        print("\n" + "="*60)
        print(" BOLPATRA WEB SCRAPER ".center(60))
        print("="*60)
        print("\n🔍 Scraping ALL available pages...")
        
        try:
            self.scraper = BolpatraScraper(headless=headless)
            
            if not self.scraper.init_driver():
                print("\n✗ Failed to initialize browser")
                print("Install ChromeDriver: pip install webdriver-manager")
                print("Then add to your code:")
                print("  from webdriver_manager.chrome import ChromeDriverManager")
                print("  webdriver.Chrome(ChromeDriverManager().install())")
                return 0
            
            # Scrape all pages (scrape_all_pages=True)
            scraped_tenders = self.scraper.scrape_tenders(scrape_all_pages=True)
            
            # Filter for relevant tenders
            relevant_tenders = [
                t for t in scraped_tenders 
                if self.is_relevant_tender(t['title'], t.get('description', ''))
            ]
            
            # Add new tenders (avoid duplicates)
            added = 0
            duplicates = 0
            for tender in relevant_tenders:
                # Check for duplicates by title and organization
                is_duplicate = any(
                    t['title'] == tender['title'] and 
                    t['organization'] == tender['organization'] 
                    for t in self.tenders
                )
                
                if not is_duplicate:
                    self.tenders.append(tender)
                    added += 1
                else:
                    duplicates += 1
            
            # Save to both JSON and CSV
            if added > 0:
                self.save_data(format='both')
            
            print(f"\n{'='*60}")
            print(f"📊 SCRAPING RESULTS:")
            print(f"{'='*60}")
            print(f"   Total entries scraped: {len(scraped_tenders)}")
            print(f"   Relevant (arch/consultancy): {len(relevant_tenders)}")
            print(f"   New tenders added: {added}")
            print(f"   Duplicates skipped: {duplicates}")
            print(f"   Total tenders in database: {len(self.tenders)}")
            print(f"{'='*60}")
            
            return added
            
        except Exception as e:
            print(f"\n✗ Scraping error: {e}")
            import traceback
            traceback.print_exc()
            return 0
        finally:
            if self.scraper:
                self.scraper.close()
    
    def view_all_tenders(self, filter_relevant=True):
        """Display all tenders."""
        display_tenders = self.tenders
        
        if filter_relevant:
            display_tenders = [
                t for t in self.tenders 
                if self.is_relevant_tender(t['title'], t.get('description', ''))
            ]
        
        if not display_tenders:
            print("\nNo tenders found matching criteria.")
            return
        
        print(f"\n{'='*80}")
        print(f"{'TENDER LISTINGS':^80}")
        print(f"{'='*80}\n")
        
        for i, tender in enumerate(display_tenders, 1):
            print(f"[{i}] {tender['title']}")
            print(f"    Organization: {tender['organization']}")
            print(f"    Province: {tender.get('province', 'N/A')}")
            print(f"    Amount: NPR {tender['amount']:,.2f}")
            print(f"    Deadline: {tender['deadline']}")
            print(f"    Category: {tender.get('category', 'N/A')}")
            print(f"    Source: {tender.get('source', 'Unknown')}")
            if tender.get('scraped_date'):
                print(f"    Scraped: {tender['scraped_date']}")
            if tender.get('description'):
                print(f"    Description: {tender['description'][:100]}...")
            if tender.get('url'):
                print(f"    URL: {tender['url']}")
            print()
    
    def search_tenders(self):
        """Search tenders with multiple criteria."""
        print("\n--- Search Tenders ---")
        print("1. By Province")
        print("2. By Title/Keyword")
        print("3. By Organization")
        print("4. By Amount Range")
        print("5. By Deadline (after date)")
        print("6. By Category")
        
        choice = input("Choose search type: ").strip()
        
        results = []
        
        if choice == "1":
            term = input("Enter province: ").strip().lower()
            results = [t for t in self.tenders if term in t.get('province', '').lower()]
        
        elif choice == "2":
            term = input("Enter keyword: ").strip().lower()
            results = [t for t in self.tenders if term in t['title'].lower() or 
                      term in t.get('description', '').lower()]
        
        elif choice == "3":
            term = input("Enter organization: ").strip().lower()
            results = [t for t in self.tenders if term in t['organization'].lower()]
        
        elif choice == "4":
            try:
                min_amt = float(input("Enter minimum amount: "))
                max_amt = float(input("Enter maximum amount: "))
                results = [t for t in self.tenders if min_amt <= t['amount'] <= max_amt]
            except ValueError:
                print("Invalid amount entered.")
                return
        
        elif choice == "5":
            date_str = input("Enter deadline (YYYY-MM-DD): ").strip()
            try:
                search_date = datetime.strptime(date_str, "%Y-%m-%d")
                results = [
                    t for t in self.tenders 
                    if t['deadline'] != 'Not specified' and
                    datetime.strptime(t['deadline'], "%Y-%m-%d") >= search_date
                ]
            except ValueError:
                print("Invalid date format.")
                return
        
        elif choice == "6":
            category = input("Enter category (Consultancy/Goods/Works): ").strip()
            results = [t for t in self.tenders if category.lower() in t.get('category', '').lower()]
        
        # Filter for relevant tenders
        results = [t for t in results if self.is_relevant_tender(
            t['title'], 
            t.get('description', '')
        )]
        
        if results:
            print(f"\n✓ Found {len(results)} matching tender(s):\n")
            for i, tender in enumerate(results, 1):
                print(f"[{i}] {tender['title']}")
                print(f"    Organization: {tender['organization']}")
                print(f"    Amount: NPR {tender['amount']:,.2f}")
                print(f"    Deadline: {tender['deadline']}")
                print()
        else:
            print("\n✗ No matching architecture/consultancy tenders found.")
    
    def add_tender(self):
        """Add a new tender manually."""
        print("\n--- Add New Tender ---")
        
        title = input("Enter title: ").strip()
        
        if not self.is_relevant_tender(title):
            confirm = input(
                "This doesn't appear to be an architecture/consultancy tender. "
                "Add anyway? (y/n): "
            ).lower()
            if confirm != 'y':
                print("Tender not added.")
                return
        
        province = input("Enter province: ").strip()
        organization = input("Enter organization: ").strip()
        
        try:
            amount = float(input("Enter amount: "))
        except ValueError:
            print("Invalid amount. Tender not added.")
            return
        
        deadline = input("Enter deadline (YYYY-MM-DD): ").strip()
        
        try:
            datetime.strptime(deadline, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format. Use YYYY-MM-DD.")
            return
        
        category = input("Enter category (Consultancy/Goods/Works): ").strip()
        description = input("Enter description (optional): ").strip()
        
        new_tender = {
            "title": title,
            "province": province,
            "organization": organization,
            "amount": amount,
            "deadline": deadline,
            "category": category,
            "description": description,
            "source": "Manual",
            "scraped_date": datetime.now().strftime("%Y-%m-%d")
        }
        
        self.tenders.append(new_tender)
        self.save_data(format='both')
        print("\n✓ Tender added and saved to both JSON and CSV!")
    
    def export_to_csv(self):
        """Export relevant tenders to a timestamped CSV file."""
        filename = f"tenders_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        relevant_tenders = [
            t for t in self.tenders 
            if self.is_relevant_tender(t['title'], t.get('description', ''))
        ]
        
        if not relevant_tenders:
            print("\n⚠ No relevant tenders to export")
            return
        
        try:
            # Get all possible fields
            fieldnames = set()
            for tender in relevant_tenders:
                fieldnames.update(tender.keys())
            fieldnames = sorted(fieldnames)
            
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(relevant_tenders)
            
            print(f"\n✓ Exported {len(relevant_tenders)} tenders to {filename}")
        except Exception as e:
            print(f"\n✗ Error exporting: {e}")
    
    def choose_save_format(self):
        """Let user choose save format."""
        print("\n--- Save Data ---")
        print("1. Save to JSON only")
        print("2. Save to CSV only")
        print("3. Save to both JSON and CSV")
        
        choice = input("Choose format: ").strip()
        
        if choice == "1":
            self.save_data(format='json')
        elif choice == "2":
            self.save_data(format='csv')
        elif choice == "3":
            self.save_data(format='both')
        else:
            print("Invalid choice.")


def main():
    """Main program loop."""
    tm = TenderManager()
    
    print("\n" + "="*70)
    print(" TENDER MANAGEMENT SYSTEM ".center(70, "="))
    print(" (Architecture & Consultancy Focus) ".center(70))
    print(" [Powered by Selenium Web Scraper] ".center(70))
    print("="*70)
    
    while True:
        print("\n--- Main Menu ---")
        print("1. View all relevant tenders")
        print("2. Search tenders")
        print("3. Add tender manually")
        print("4. 🌐 Scrape tenders from Bolpatra (Auto - All Pages)")
        print("5. Export to CSV (timestamped)")
        print("6. View all tenders (including non-relevant)")
        print("7. Save current data")
        print("8. Statistics")
        print("9. Exit")
        
        choice = input("\nEnter your choice: ").strip()
        
        if choice == "1":
            tm.view_all_tenders(filter_relevant=True)
        
        elif choice == "2":
            tm.search_tenders()
        
        elif choice == "3":
            tm.add_tender()
        
        elif choice == "4":
            print("\n🌐 Starting automatic web scraper...")
            print("⏳ This will scrape ALL available pages automatically...")
            headless = input("Run browser in headless mode? (y/n, default=y): ").lower() != 'n'
            
            count = tm.scrape_bolpatra(headless=headless)
            
            if count > 0:
                print(f"\n✓ Successfully added {count} new relevant tender(s)!")
                print(f"✓ Data saved to both {tm.json_filename} and {tm.csv_filename}")
            else:
                print("\n⚠ No new relevant tenders found or scraping failed.")
        
        elif choice == "5":
            tm.export_to_csv()
        
        elif choice == "6":
            tm.view_all_tenders(filter_relevant=False)
        
        elif choice == "7":
            tm.choose_save_format()
        
        elif choice == "8":
            total = len(tm.tenders)
            relevant = len([t for t in tm.tenders if tm.is_relevant_tender(t['title'])])
            
            # Calculate by source
            sources = {}
            for t in tm.tenders:
                source = t.get('source', 'Unknown')
                sources[source] = sources.get(source, 0) + 1
            
            print(f"\n📊 Statistics:")
            print(f"{'='*50}")
            print(f"   Total tenders: {total}")
            print(f"   Relevant (arch/consultancy): {relevant}")
            print(f"   Non-relevant: {total - relevant}")
            print(f"\n   By Source:")
            for source, count in sources.items():
                print(f"      {source}: {count}")
            print(f"{'='*50}")
        
        elif choice == "9":
            print("\n💾 Saving data before exit...")
            tm.save_data(format='both')
            print("\n👋 Thank you for using the Tender Management System!")
            break
        
        else:
            print("\n⚠ Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
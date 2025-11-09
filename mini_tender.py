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
        self.checkpoint_file = "scraper_checkpoint.json"
        
    def save_checkpoint(self, page_number):
        """Save the current page number to resume later."""
        try:
            checkpoint_data = {
                'last_page': page_number,
                'timestamp': datetime.now().isoformat(),
                'url': self.driver.current_url if self.driver else None
            }
            with open(self.checkpoint_file, 'w') as f:
                json.dump(checkpoint_data, f)
            print(f"   ✓ Checkpoint saved: page {page_number}")
        except Exception as e:
            print(f"   ⚠ Could not save checkpoint: {e}")
    
    def load_checkpoint(self):
        """Load the last saved checkpoint if it exists."""
        try:
            if os.path.exists(self.checkpoint_file):
                with open(self.checkpoint_file, 'r') as f:
                    data = json.load(f)
                    last_page = data.get('last_page', 1)
                    last_url = data.get('url')
                    timestamp = data.get('timestamp')
                    print(f"\n📋 Found checkpoint from {timestamp}")
                    print(f"   Last scraped page: {last_page}")
                    return last_page, last_url
        except Exception as e:
            print(f"   ⚠ Could not load checkpoint: {e}")
        return 1, None
    
    def clear_checkpoint(self):
        """Clear the checkpoint after successful completion."""
        if os.path.exists(self.checkpoint_file):
            try:
                os.remove(self.checkpoint_file)
                print("   ✓ Checkpoint cleared")
            except:
                pass
    
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
    
    def scrape_tenders(self, scrape_all_pages=True, resume=True):
        """
        Scrape tenders from bolpatra.gov.np
        Yields tender dictionaries one at a time
        scrape_all_pages: If True, scrapes until no more pages available
        resume: If True, attempts to resume from last checkpoint
        """
        if not self.driver:
            if not self.init_driver():
                return
        
        base_url = "https://bolpatra.gov.np/egp"
        
        try:
            print("\n📡 Connecting to Bolpatra...")
            
            # Load checkpoint if resuming
            start_page = 1
            if resume:
                start_page, last_url = self.load_checkpoint()
                if last_url:
                    print(f"   Resuming from page {start_page}")
                    self.driver.get(last_url)
                    time.sleep(3)
                else:
                    start_page = 1
            
            # If not resuming or no valid checkpoint, start from beginning
            if start_page == 1:
                self.driver.get(f"{base_url}/searchOpportunity")
                time.sleep(3)  # Wait for page load
                print("✓ Page loaded successfully")
                
                # Try to find and click on "Published Bids" or similar
                try:
                    # Look for the bid opportunities link
                    opportunities_link = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.LINK_TEXT, "Published bids"))
                    )
                    opportunities_link.click()
                    time.sleep(2)
                except:
                    # Alternative: direct navigation
                    self.driver.get(f"{base_url}/searchOpportunity")
                    time.sleep(3)
            
            print("✓ Navigated to tender listings")
            
            # Scrape all pages
            page = start_page
            tenders_on_page = 0
            total_tenders = 0
            
            while True:
                print(f"\n📄 Scraping page {page}...")
                tenders_on_page = 0
                
                # Get tenders one at a time
                for tender in self.scrape_current_page():
                    tenders_on_page += 1
                    total_tenders += 1
                    yield tender
                
                print(f"   Found {tenders_on_page} tenders on this page")
                print(f"   Total tenders so far: {total_tenders}")
                
                # Save checkpoint after successful page processing
                self.save_checkpoint(page)
                
                # Try to go to next page
                if scrape_all_pages:
                    if not self.go_to_next_page():
                        print("   ✓ Reached last page")
                        self.clear_checkpoint()  # Clear checkpoint on successful completion
                        break
                    page += 1
                else:
                    self.clear_checkpoint()  # Clear checkpoint on successful completion
                    break
                
                time.sleep(2)  # Be polite to the server
            
            print(f"\n✓ Total tenders scraped: {total_tenders}")
            
        except Exception as e:
            print(f"✗ Error during scraping: {e}")
            print(f"   💡 Tip: Run again with resume=True to continue from page {page}")
            import traceback
            traceback.print_exc()
            
    def scrape_current_page(self):
        """Scrape tenders from the current page, yielding them one at a time."""
        try:
            # Wait for the main tender table
            tender_table = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table#dashBoardBidResult"))
            )
            
            # First get the header row to identify columns
            headers = tender_table.find_elements(By.CSS_SELECTOR, "thead tr th")
            
            
            # Find all tender rows
            tender_rows = tender_table.find_elements(By.CSS_SELECTOR, "table#dashBoardBidResult tbody tr")
            print(f"   Found {len(tender_rows)} tender rows")
            
            for row in tender_rows:
                try:
                    tender_data = self.parse_tender_row(row)
                    if tender_data:
                        yield tender_data  # Yield each tender as it's parsed
                except Exception as e:
                    print(f"   ⚠ Error parsing row: {str(e)}")
                    continue
            
        except TimeoutException:
            print("   Timeout waiting for tender table")
        except Exception as e:
            print(f"   Error scraping page: {e}")
            
        return  # Generator function ends here
    
    def parse_tender_row(self, row):
        """Parse individual tender row."""
        try:
            # Get all cells in the row
            cells = row.find_elements(By.TAG_NAME, "td")
            
            # Known column indices (0-based)
            SI_NO = 0
            IFB_NO = 1
            TITLE = 2
            PUBLIC_ENTITY = 3
            PROCUREMENT_TYPE = 4
            STATUS = 5
            NOTICE_DATE = 6
            SUBMISSION_DATE = 7
            DAYS_LEFT = 8

            if len(cells) < 9:  # Ensure we have all expected columns
                return None
                
            # Extract data using known positions
            ifb = cells[IFB_NO].text.strip()
            if not ifb:
                return None
            
            # Extract data using known positions
            title = cells[TITLE].text.strip()
            if not title:
                return None
                
            # Get organization directly from its known column
            public_entity_name = cells[PUBLIC_ENTITY].text.strip()

            # Get notice date directly from its known column
            notice_date = cells[NOTICE_DATE].text.strip()

            # Get submission deadline directly from its column
            deadline = cells[SUBMISSION_DATE].text.strip()
            if deadline:
                deadline = self.normalize_date(deadline)
            
            # Extract category/type from procurement type column
            procurement_type = cells[PROCUREMENT_TYPE].text.strip().lower()

            return {
                'ifb_no': ifb,
                'title': title,
                'organization': public_entity_name or "Not specified",
                'deadline': deadline or "Not specified",
                'Procurement Type': procurement_type or "Not specified",
                'notice date': notice_date,
                'province': "Not specified",
                'source': 'Bolpatra',
                'scraped_date': datetime.now().strftime("%Y-%m-%d"),
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
        """Navigate to next page if valid tenders exist."""
        try:
            # Wait for rows to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table#dashBoardBidResult tbody tr"))
            )
            tender_rows = self.driver.find_elements(By.CSS_SELECTOR, "table#dashBoardBidResult tbody tr")

            has_valid_tenders = False
            for row in tender_rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) < 5:
                    continue
                print("Columns found:", len(cells), [c.text for c in cells])  # debug
                days_left_text = cells[-1].text.strip()  # safer to take last column
                try:
                    days_left = int(re.search(r'\d+', days_left_text).group())
                    if days_left > 28:
                        has_valid_tenders = True
                        break
                except ValueError:
                    continue

            if not has_valid_tenders:
                print("   No tenders with >28 days left found on this page")
                return False

            # Find next page button (multiple fallbacks)
            try:
                next_button = self.driver.find_element(By.CSS_SELECTOR, "a#next, button#next, img.next")
            except NoSuchElementException:
                print("   ⚠ No next button found.")
                return False

            # Check if disabled
            if not next_button.is_enabled() or "disabled" in next_button.get_attribute("outerHTML").lower():
                print("   🚫 Next button disabled or hidden.")
                return False

            # Click next and wait for reload
            next_button.click()
            WebDriverWait(self.driver, 10).until(EC.staleness_of(tender_rows[0]))
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table#dashBoardBidResult tbody tr"))
            )
            time.sleep(1)
            print("➡️  Moved to next page successfully.")
            return True

        except NoSuchElementException:
            print("   ⚠ Table not found.")
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
    
    def scrape_bolpatra(self, headless=True, resume=True):
        """
        Scrape ALL available tenders from Bolpatra using Selenium.
        
        Args:
            headless: Run browser in headless mode (default: True)
            resume: Try to resume from last checkpoint (default: True)
        """
        print("\n" + "="*60)
        print(" BOLPATRA WEB SCRAPER ".center(60))
        print("="*60)
        print("\n🔍 Scraping ALL available pages...")
        if resume:
            print("   📋 Will attempt to resume from last checkpoint")
        
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
            
            # Process each tender as we get it
            added = 0
            duplicates = 0
            
            for tender in scraped_tenders:
                if not self.is_relevant_tender(tender['title'], tender.get('description', '')):
                    continue
                    
                # Check for duplicates by title and organization
                is_duplicate = any(
                    t['title'] == tender['title'] and 
                    t['organization'] == tender['organization'] 
                    for t in self.tenders
                )
                
                if not is_duplicate:
                    self.tenders.append(tender)
                    print(f"\n✓ New tender found: {tender['title'][:60]}...")
                    # Save immediately after each new tender
                    self.save_data(format='both')
                    added += 1
                else:
                    print(f"\n↺ Duplicate tender: {tender['title'][:60]}...")
                    duplicates += 1
            
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
            print(f"    Public entity name: {tender['organization']}")
            print(f"    Province: {tender.get('province', 'N/A')}")
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
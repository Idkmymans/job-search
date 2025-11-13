
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
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Improved include/exclude lists for a hybrid filter
INCLUDE_KEYWORDS = [
    "architect", "architecture", "architectural", "design", "consultancy",
    "consultant", "supervision", "engineering design", "structural", 
    "building", "hospital", "school", "campus", "office", "housing",
    "infrastructure", "layout", "survey", "mapping", "master plan",
    "feasibility", "dpr", "detailed project report", "urban", 
    "complex", "terminal", "hall", "park", "stadium", "facility", "center"
]

EXCLUDE_KEYWORDS = [
    "supply", "delivery", "purchase", "repair", "maintenance",
    "vehicle", "road", "bridge", "culvert", "pipeline", "water supply",
    "drainage", "medicine", "drug", "equipment", "machinery", "printing",
    "it support", "software", "hardware", "stationery",
    "agriculture", "fertilizer", "river", "sand", "gravel",
    "cement", "pavement", "asphalt"
]

class BolpatraScraper:
    def __init__(self, headless=True):
        self.headless = headless
        self.driver = None
        
    # Checkpoint system removed: persistent de-duplication is handled via
    # TenderManager.seen_keys (seen_keys.json). The checkpoint functions were
    # intentionally removed to keep scraping stateless between runs because
    # seen-keys prevent re-saving duplicates.
    
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
            
            # Always start from the main search page
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
            except Exception:
                # Alternative: direct navigation
                self.driver.get(f"{base_url}/searchOpportunity")
                time.sleep(3)
            
            print("✓ Navigated to tender listings")
            
            # Scrape all pages
            page = 1
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
                
                # Handle pagination: try to go to the next page; stop when navigation fails
                next_page = page + 1
                if scrape_all_pages:
                    if not self.go_to_next_page(next_page):
                        print("   ✓ Reached last page or navigation failed")
                        break
                    page = next_page  # Update page number only after successful navigation
                else:
                    break
                
                time.sleep(2)  # Be polite to the server
            
            print(f"\n✓ Total tenders scraped: {total_tenders}")
            
        except Exception as e:
            print(f"✗ Error during scraping: {e}")
            print("   💡 Tip: Run again to retry; persistent seen-keys will avoid duplicate saves.")
            import traceback
            traceback.print_exc()
            
    def scrape_current_page(self):
        """Scrape tenders from the current page, yielding them one at a time."""
        try:
            # Wait for the main tender table
            tender_table = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table#dashBoardBidResult"))
            )
            
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

            # Get notice/publication date and normalize it
            notice_date_raw = cells[NOTICE_DATE].text.strip()
            notice_date = self.normalize_date(notice_date_raw) if notice_date_raw else ""

            # Get submission deadline directly from its column (may not be used)
            deadline = cells[SUBMISSION_DATE].text.strip()
            if deadline:
                deadline = self.normalize_date(deadline)

            # Prefer the 'Days left' column value if present. It's a table column
            # that may contain 'Expired' or a number like '27 days'. Fall back to
            # computing from deadline if Days-left column is empty/unparseable.
            days_left = None
            days_left_text = ""
            try:
                days_left_text = cells[DAYS_LEFT].text.strip()
            except Exception:
                days_left_text = ""

            if days_left_text:
                days_left = self.parse_days_left_text(days_left_text)

            # Fallback: compute days left from deadline if parse failed
            if days_left is None and deadline:
                try:
                    dt = datetime.strptime(deadline, "%Y-%m-%d")
                    days_left = (dt - datetime.now()).days
                except Exception:
                    days_left = None
            
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
                'days_left': days_left,
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

    @staticmethod
    def parse_days_left_text(days_text: str):
        """Parse the 'Days left' text from the table and return integer days.

        Examples handled:
          '27', '27 days', '27 day(s)', 'Expired', 'Expired - 0', '-' -> returns -1
        Returns an int or None if parsing fails.
        """
        if not days_text:
            return None
        t = days_text.strip().lower()
        if 'expir' in t or 'expired' in t:
            return -1
        # Try to extract an integer
        m = re.search(r"(\d+)", t)
        if m:
            try:
                return int(m.group(1))
            except:
                return None
        return None
    
    def go_to_next_page(self, next_page):
        """Navigate to next page of tender listings."""
        try:
            
            # Find and clear the page input
            goto_input = self.driver.find_element(By.CSS_SELECTOR, "table#pager tbody tr input.gotoPage")
            goto_input.clear()
            goto_input.send_keys(str(next_page))
            time.sleep(1)  # Brief pause after typing
            
            # Click the go button
            gobutton = self.driver.find_element(By.CSS_SELECTOR, "table#pager tbody tr img.goto")

            # Wait for any global overlay (modal/spinner) to disappear which can
            # block clicks. Some pages show an overlay with id 'overlay' or class
            # 'overlayCss'. Wait for invisibility if present.
            try:
                WebDriverWait(self.driver, 8).until(
                    EC.invisibility_of_element_located((By.ID, "overlay"))
                )
            except Exception:
                # ignore - overlay might not exist
                pass

            try:
                WebDriverWait(self.driver, 8).until(
                    EC.invisibility_of_element_located((By.CSS_SELECTOR, ".overlayCss"))
                )
            except Exception:
                pass

            # Scroll the button into view and use JS click to avoid interception
            try:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", gobutton)
            except Exception:
                pass

            try:
                # JS click is more resilient to overlapping elements
                self.driver.execute_script("arguments[0].click();", gobutton)
            except Exception:
                # Fall back to normal click
                gobutton.click()
            
            # Wait for the page to load and verify we're on the right page
            try:
                # Wait for table to load
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "table#dashBoardBidResult tbody tr"))
                )
                
                
                print(f"✅ Successfully navigated to page {next_page}")
                return True
                
            except TimeoutException:
                print(f"⚠ Page {next_page} appears to be empty or failed to load")
                return False
                
        except Exception as e:
            print(f"⚠ Failed to navigate to page {next_page}: {str(e)}")
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
        self.seen_keys_file = "seen_keys.json"
        self.non_relevant_seen_file = "non_relevant_seen_keys.json"
        self.seen_keys = set()
        self.non_relevant_seen_keys = set()
        self.tenders = []
        self.scraper = None
        self.load_data()
        # load or build persisted seen-keys to avoid duplicates across runs
        self.load_seen_keys()
    
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

    def _make_key(self, title, organization, pub_date=None):
        """Create a stable key for a tender based on title and organization.

        Keys are lower-cased and stripped to reduce false negatives due to
        capitalization/whitespace differences.
        """
        # New key shape: title ||| organization ||| pub_date
        t = (title or "").strip().lower()
        o = (organization or "").strip().lower()
        p = (pub_date or "").strip().lower()
        return f"{t}|||{o}|||{p}"

    def load_seen_keys(self):
        """Load persisted seen-keys from disk or build from loaded tenders."""
        try:
            if os.path.exists(self.seen_keys_file):
                with open(self.seen_keys_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # stored as list of strings
                    self.seen_keys = set(data)
                    print(f"✓ Loaded {len(self.seen_keys)} seen keys from {self.seen_keys_file}")
                    # continue to also try loading non-relevant keys
            if os.path.exists(self.non_relevant_seen_file):
                with open(self.non_relevant_seen_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.non_relevant_seen_keys = set(data)
                    print(f"✓ Loaded {len(self.non_relevant_seen_keys)} non-relevant seen keys from {self.non_relevant_seen_file}")
                    return
        except Exception as e:
            print(f"⚠ Error loading seen keys: {e}")

        # If file not present or failed to load, build from currently loaded tenders
        self.seen_keys = set()
        self.non_relevant_seen_keys = set()
        for t in self.tenders:
            key = self._make_key(t.get('title'), t.get('organization'), t.get('notice date') or t.get('scraped_date'))
            # decide where to put the key based on relevancy
            try:
                if self.is_relevant_tender(t.get('title'), t.get('description', '')):
                    self.seen_keys.add(key)
                else:
                    self.non_relevant_seen_keys.add(key)
            except Exception:
                # if any error, put into seen_keys to avoid reprocessing
                self.seen_keys.add(key)
        # persist the rebuilt keys
        self.save_seen_keys()
        self.save_non_relevant_seen_keys()

    def save_seen_keys(self):
        """Persist the seen-keys set to disk."""
        try:
            with open(self.seen_keys_file, 'w', encoding='utf-8') as f:
                json.dump(list(self.seen_keys), f, indent=2, ensure_ascii=False)
            # small confirmation
            # print(f"✓ Saved {len(self.seen_keys)} seen keys to {self.seen_keys_file}")
        except Exception as e:
            print(f"⚠ Error saving seen keys: {e}")

    def save_non_relevant_seen_keys(self):
        """Persist the non-relevant seen-keys set to disk."""
        try:
            with open(self.non_relevant_seen_file, 'w', encoding='utf-8') as f:
                json.dump(list(self.non_relevant_seen_keys), f, indent=2, ensure_ascii=False)
            # print(f"✓ Saved {len(self.non_relevant_seen_keys)} non-relevant seen keys to {self.non_relevant_seen_file}")
        except Exception as e:
            print(f"⚠ Error saving non-relevant seen keys: {e}")
    
    def save_to_json(self):
        """Save tenders to JSON file."""
        try:
            print(f"\n💾 Saving {len(self.tenders)} tenders to {self.json_filename}")
            
            # DEBUG: Print the first tender as a sample
            if self.tenders:
                print(f"   Sample tender being saved: {self.tenders[0]['title']}")
            
            with open(self.json_filename, "w", encoding='utf-8') as f:
                json.dump(self.tenders, f, indent=2, ensure_ascii=False)
            
            # Verify the save by checking file size
            file_size = os.path.getsize(self.json_filename)
            print(f"✓ Saved to {self.json_filename} (Size: {file_size} bytes)")
            
        except Exception as e:
            print(f"✗ Error saving JSON: {e}")
            import traceback
            traceback.print_exc()
    
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
    

    @staticmethod
    def is_architecture_related(title: str) -> bool:
        """Improved architecture-related tender filter (title-only)."""
        if not title:
            return False
        text = title.lower()

        # 1️⃣ Quick pre-filter
        if not any(k in text for k in INCLUDE_KEYWORDS):
            return False
        if any(k in text for k in EXCLUDE_KEYWORDS):
            return False

        # 2️⃣ Context reinforcement
        strong_contexts = ["building", "hospital", "school", "campus", "office", "complex", "hall", "housing", "facility", "center"]
        if any(ctx in text for ctx in strong_contexts):
            return True

        # 3️⃣ Catch high-confidence consultancy/design indicators
        if any(k in text for k in ["dpr", "feasibility", "master plan", "architect", "consult", "supervision", "design"]):
            return True

        # 4️⃣ Hybrid heuristic: at least two positives, zero negatives
        matches = [k for k in INCLUDE_KEYWORDS if k in text]
        return len(matches) >= 2


    @staticmethod
    def is_relevant_tender(title: str, context: str = "") -> bool:
        """Hybrid relevancy check combining title + optional context."""
        title_text = (title or "").strip().lower()
        context_text = (context or "").strip().lower()

        if TenderManager.is_architecture_related(title_text):
            return True

        combined = f"{title_text} {context_text}".strip()
        if not combined:
            return False
        if any(ex in combined for ex in EXCLUDE_KEYWORDS):
            return False
        return any(inc in combined for inc in INCLUDE_KEYWORDS)
    
    def scrape_bolpatra(self, headless=True):
        """
        Scrape ALL available tenders from Bolpatra using Selenium.

        Args:
            headless: Run browser in headless mode (default: True)

        Note:
            Checkpoint/resume behavior was removed in favor of a persistent
            `seen_keys.json` file which prevents duplicate saves across runs.
        """
        print("\n" + "="*60)
        print(" BOLPATRA WEB SCRAPER ".center(60))
        print("="*60)
        print("\n🔍 Scraping ALL available pages...")
        # Note: checkpoint system removed; persistent seen-keys avoid duplicates across runs
        
        try:
            self.scraper = BolpatraScraper(headless=headless)
            
            if not self.scraper.init_driver():
                print("\n✗ Failed to initialize browser")
                print("Install ChromeDriver: pip install webdriver-manager")
                print("Then add to your code:")
                print("  from webdriver_manager.chrome import ChromeDriverManager")
                print("  webdriver.Chrome(ChromeDriverManager().install())")
                return 0
            
            # Stream scraped tenders from the scraper generator. We iterate
            # directly so that each tender can be processed and saved to disk
            # immediately (no in-memory list of all scraped results).
            added = 0
            duplicates = 0
            total_scraped = 0
            relevant_count = 0

            stopped_early = False
            for tender in self.scraper.scrape_tenders(scrape_all_pages=True):
                total_scraped += 1

                # Create a persistent key for the tender (title|org|notice_date)
                key = self._make_key(
                    tender.get('title'),
                    tender.get('organization'),
                    tender.get('notice date') or tender.get('scraped_date')
                )

                # If the key exists in either seen set, skip
                if key in self.seen_keys or key in self.non_relevant_seen_keys:
                    print(f"\n↺ Duplicate tender (seen before): {tender.get('title','')[:60]}...")
                    duplicates += 1
                    continue

                # Build context for relevancy checking
                context_text = (
                    str(tender.get('description', '')) + " " + str(tender.get('organization', ''))
                ).strip()

                # Check relevancy
                is_relevant = self.is_relevant_tender(tender.get('title', ''), context_text)

                # DAYS LEFT FILTER: decide behavior based on days_left
                days_left_val = tender.get('days_left')

                if not is_relevant:
                    # Non-relevant: persist to non-relevant seen keys for audit
                    print(f"   Non-relevant tender (marked seen): {tender.get('title','')[:60]}...")
                    self.non_relevant_seen_keys.add(key)
                    self.save_non_relevant_seen_keys()
                    continue

                # At this point the tender is relevant
                relevant_count += 1

                # If days_left is unknown or <=7, mark as seen (do not save).
                if days_left_val is None:
                    print(f"   Relevant but unknown deadline, marking as seen (not saved): {tender.get('title','')[:60]}...")
                    self.seen_keys.add(key)
                    self.save_seen_keys()
                    continue

                if days_left_val <= 7:
                    print(f"   Found relevant tender with days_left={days_left_val} <= 7; marking as seen and ending scrape: {tender.get('title','')[:60]}...")
                    self.seen_keys.add(key)
                    self.save_seen_keys()
                    stopped_early = True
                    break

                # Save the tender (days_left > 7)
                self.tenders.append(tender)
                print(f"\n✓ New relevant tender found: {tender.get('title','')[:60]}...")
                print(f"   Current tenders in memory: {len(self.tenders)}")
                self.save_to_json()
                # Persist seen key for this relevant tender
                self.seen_keys.add(key)
                self.save_seen_keys()
                added += 1
            
            if stopped_early:
                print("\n⚠ Stopped early due to encountering a tender with days_left <= 7")

            print(f"\n{'='*60}")
            print(f"📊 SCRAPING RESULTS:")
            print(f"{'='*60}")
            print(f"   Total entries scraped: {total_scraped}")
            print(f"   Relevant (arch/consultancy): {relevant_count}")
            print(f"   New tenders added: {added}")
            print(f"   Duplicates skipped: {duplicates}")
            print(f"   Total tenders in database: {len(self.tenders)}")
            print(f"{'='*60}")
            
            return added
            
        except Exception as e:
            print(f"\n✗ this is a  Scraping error: {e}")
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
            
            "organization": organization,

            "amount": amount,
            "deadline": deadline,
            "category": category,
            "description": description,
            "source": "Manual",
            "scraped_date": datetime.now().strftime("%Y-%m-%d")
        }
        
        # Prevent duplicates across runs by checking persisted seen-keys
        # Use scraped_date as publication date for manual entries
        key = self._make_key(
            new_tender.get('title'),
            new_tender.get('organization'),
            new_tender.get('scraped_date')
        )
        if key in self.seen_keys:
            print("\n↺ This tender appears to be a duplicate and was not added.")
            return

        self.tenders.append(new_tender)
        # Persist only to JSON for now (CSV can be enabled if desired)
        self.save_to_json()
        # update seen keys and persist
        self.seen_keys.add(key)
        self.save_seen_keys()
        print("\n✓ Tender added and saved to JSON!")
    
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
        print("7. clear tenders")
        print("8. Save current data")
        print("9. Statistics")
        print("10. Exit")
        
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
            confirm = input(
                "Are you sure you want to clear ALL tenders from memory? (y/n): "
            ).lower()
            if confirm == 'y':
                tm.tenders = []
                tm.save_data(format='both')
                print("\n✓ All tenders cleared from memory and saved.")
            else:
                print("Operation cancelled.")

        elif choice == "8":
            tm.choose_save_format()
        
        elif choice == "9":
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
        
        elif choice == "10":
            print("\n💾 Saving data before exit...")
            tm.save_data(format='both')
            print("\n👋 Thank you for using the Tender Management System!")
            break
        
        else:
            print("\n⚠ Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
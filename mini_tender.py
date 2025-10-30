import json
import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import re

# Architecture and consultancy related keywords
KEYWORDS = [
    'architect', 'architecture', 'architectural', 'design',
    'consultancy', 'consultant', 'consulting', 'supervision',
    'engineering design', 'structural', 'building design',
    'master plan', 'feasibility study', 'detailed design',
    'construction supervision', 'project management consultant'
]

class TenderManager:
    def __init__(self):
        self.filename = "tenders.json"
        self.tenders = self.load_tenders()
    
    def load_tenders(self):
        """Load tenders from file if exists, else start with defaults."""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r", encoding='utf-8') as f:
                    return json.load(f)
            except:
                return self.get_default_tenders()
        return self.get_default_tenders()
    
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
                "description": "Design services for community center"
            },
            {
                "title": "Construction Supervision Consultant",
                "province": "Karnali",
                "organization": "DoR",
                "amount": 1200000,
                "deadline": "2025-03-20",
                "category": "Consultancy",
                "description": "Road construction supervision services"
            },
            {
                "title": "Architectural Services for School Building",
                "province": "Bagmati",
                "organization": "MoEST",
                "amount": 800000,
                "deadline": "2025-02-28",
                "category": "Consultancy",
                "description": "Complete architectural design and supervision"
            }
        ]
    
    def save_tenders(self):
        """Save tenders to file."""
        with open(self.filename, "w", encoding='utf-8') as f:
            json.dump(self.tenders, f, indent=2, ensure_ascii=False)
    
    def is_relevant_tender(self, title, description=""):
        """Check if tender is related to architecture or consultancy."""
        text = (title + " " + description).lower()
        return any(keyword in text for keyword in KEYWORDS)
    
    def scrape_bolpatra(self):
        """
        Scrape tenders from bolpatra.gov.np
        Note: This is a template. Actual implementation requires:
        - Handling authentication/session
        - Dealing with CAPTCHA
        - Proper SSL certificate handling
        - Rate limiting
        """
        try:
            # URL for published bids
            url = "https://bolpatra.gov.np/egp/searchOpportunity"
            
            # Session with SSL verification disabled (use cautiously)
            session = requests.Session()
            session.verify = False
            
            # You would need to handle login and session here
            # For now, this is a placeholder structure
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            # Consultancy category filter
            params = {
                'procurementCategory': 'CONSULTANCY',
                'status': 'ACTIVE'
            }
            
            response = session.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Parse tender listings (structure depends on actual website)
                tender_rows = soup.find_all('tr', class_='tender-row')  # Adjust selector
                
                scraped_count = 0
                for row in tender_rows:
                    try:
                        tender_data = self.parse_tender_row(row)
                        if tender_data and self.is_relevant_tender(
                            tender_data['title'], 
                            tender_data.get('description', '')
                        ):
                            # Check if tender already exists
                            if not any(t['title'] == tender_data['title'] for t in self.tenders):
                                self.tenders.append(tender_data)
                                scraped_count += 1
                    except Exception as e:
                        print(f"Error parsing tender row: {e}")
                        continue
                
                self.save_tenders()
                return scraped_count
            else:
                print(f"Failed to fetch data: Status {response.status_code}")
                return 0
                
        except requests.exceptions.SSLError:
            print("SSL Certificate error. Consider using alternative data sources.")
            return 0
        except Exception as e:
            print(f"Error scraping data: {e}")
            print("Using local data instead.")
            return 0
    
    def parse_tender_row(self, row):
        """Parse a tender row from the website."""
        # This is a template - adjust based on actual HTML structure
        try:
            title = row.find('td', class_='title').text.strip()
            organization = row.find('td', class_='organization').text.strip()
            amount_text = row.find('td', class_='amount').text.strip()
            deadline = row.find('td', class_='deadline').text.strip()
            
            # Extract amount (remove NPR, commas, etc.)
            amount = float(re.sub(r'[^\d.]', '', amount_text))
            
            return {
                'title': title,
                'organization': organization,
                'amount': amount,
                'deadline': deadline,
                'category': 'Consultancy',
                'province': 'Not specified',
                'description': ''
            }
        except Exception as e:
            return None
    
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
            if tender.get('description'):
                print(f"    Description: {tender['description']}")
            print()
    
    def search_tenders(self):
        """Search tenders with multiple criteria."""
        print("\n--- Search Tenders ---")
        print("1. By Province")
        print("2. By Title")
        print("3. By Organization")
        print("4. By Amount Range")
        print("5. By Deadline")
        
        choice = input("Choose search type: ").strip()
        
        results = []
        
        if choice == "1":
            term = input("Enter province: ").strip().lower()
            results = [t for t in self.tenders if term in t.get('province', '').lower()]
        
        elif choice == "2":
            term = input("Enter title keyword: ").strip().lower()
            results = [t for t in self.tenders if term in t['title'].lower()]
        
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
                    if datetime.strptime(t['deadline'], "%Y-%m-%d") >= search_date
                ]
            except ValueError:
                print("Invalid date format.")
                return
        
        # Filter for relevant tenders
        results = [t for t in results if self.is_relevant_tender(
            t['title'], 
            t.get('description', '')
        )]
        
        if results:
            print(f"\nFound {len(results)} matching tender(s):\n")
            for tender in results:
                print(json.dumps(tender, indent=2, ensure_ascii=False))
                print()
        else:
            print("\nNo matching architecture/consultancy tenders found.")
    
    def add_tender(self):
        """Add a new tender manually."""
        print("\n--- Add New Tender ---")
        
        title = input("Enter title: ").strip()
        
        # Check if relevant
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
        
        # Validate deadline format
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
            "description": description
        }
        
        self.tenders.append(new_tender)
        self.save_tenders()
        print("\n✓ Tender added successfully!")
    
    def filter_settings(self):
        """Configure filter settings."""
        print("\n--- Filter Settings ---")
        print("Current keywords:", ", ".join(KEYWORDS[:5]), "...")
        print("\n1. View all keywords")
        print("2. Add custom keyword")
        print("3. Back")
        
        choice = input("Choose: ").strip()
        
        if choice == "1":
            print("\nCurrent keywords:")
            for kw in KEYWORDS:
                print(f"  - {kw}")
        elif choice == "2":
            new_kw = input("Enter new keyword: ").strip().lower()
            if new_kw and new_kw not in KEYWORDS:
                KEYWORDS.append(new_kw)
                print(f"✓ Added '{new_kw}' to keywords.")

def main():
    """Main program loop."""
    tm = TenderManager()
    
    print("\n" + "="*60)
    print(" TENDER MANAGEMENT SYSTEM ".center(60, "="))
    print(" (Architecture & Consultancy Focus) ".center(60))
    print("="*60)
    
    while True:
        print("\n--- Main Menu ---")
        print("1. View all relevant tenders")
        print("2. Search tenders")
        print("3. Add tender manually")
        print("4. Scrape new tenders from Bolpatra")
        print("5. Filter settings")
        print("6. View all tenders (including non-relevant)")
        print("7. Exit")
        
        choice = input("\nEnter your choice: ").strip()
        
        if choice == "1":
            tm.view_all_tenders(filter_relevant=True)
        
        elif choice == "2":
            tm.search_tenders()
        
        elif choice == "3":
            tm.add_tender()
        
        elif choice == "4":
            print("\nAttempting to scrape tenders...")
            print("Note: Bolpatra.gov.np requires authentication and has SSL issues.")
            print("This feature is currently limited. Consider using their API if available.\n")
            
            count = tm.scrape_bolpatra()
            if count > 0:
                print(f"✓ Successfully scraped {count} new relevant tender(s)!")
            else:
                print("No new tenders scraped. Using local data.")
        
        elif choice == "5":
            tm.filter_settings()
        
        elif choice == "6":
            tm.view_all_tenders(filter_relevant=False)
        
        elif choice == "7":
            print("\nThank you for using the Tender Management System!")
            break
        
        else:
            print("\n⚠ Invalid choice. Please try again.")

if __name__ == "__main__":
    # Suppress SSL warnings for development
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    main()
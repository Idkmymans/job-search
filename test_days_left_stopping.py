"""
Test script to verify the days_left stopping functionality in scraping.
Simulates the scraping loop with mock tender data to check if scraping
stops when days_left <= 7 is encountered.
"""

from mini_tender import TenderManager

def test_days_left_stopping():
    """Simulate scraping with mock tenders to test early stopping."""
    
    # Mock tender generator that yields tenders in sequence with different days_left values
    def mock_scraper_generator():
        mock_tenders = [
            {
                'title': 'Architectural Design for Building A',
                'organization': 'City Office',
                'description': 'Design services',
                'deadline': '2025-12-31',
                'days_left': 45,  # Should process this
                'notice date': '2025-11-01',
                'source': 'Bolpatra',
            },
            {
                'title': 'Consultancy for Park Project',
                'organization': 'Parks Dept',
                'description': 'Engineering consultancy',
                'deadline': '2025-12-15',
                'days_left': 32,  # Should process this
                'notice date': '2025-10-20',
                'source': 'Bolpatra',
            },
            {
                'title': 'Survey and Design Study',
                'organization': 'Urban Dev',
                'description': 'Architectural survey',
                'deadline': '2025-11-25',
                'days_left': 3,  # Should STOP here (<=7)
                'notice date': '2025-11-10',
                'source': 'Bolpatra',
            },
            {
                'title': 'This should not be processed',
                'organization': 'Some Org',
                'description': 'Architectural design',
                'deadline': '2025-11-20',
                'days_left': 1,  # Should NOT reach this
                'notice date': '2025-11-15',
                'source': 'Bolpatra',
            },
        ]
        for tender in mock_tenders:
            yield tender

    tm = TenderManager()
    
    print("\n" + "="*70)
    print(" Testing days_left stopping functionality".center(70))
    print("="*70)
    
    added = 0
    duplicates = 0
    total_scraped = 0
    relevant_count = 0
    stopped_early = False
    
    print("\nProcessing mock tenders...\n")
    
    for tender in mock_scraper_generator():
        total_scraped += 1
        days_left_val = tender.get('days_left')
        title = tender.get('title', '')
        
        print(f"\n[{total_scraped}] Processing: {title}")
        print(f"    Days left: {days_left_val}")
        
        # Create a key
        key = tm._make_key(
            tender.get('title'),
            tender.get('organization'),
            tender.get('notice date') or tender.get('scraped_date', 'unknown')
        )
        
        # Check if already seen
        if key in tm.seen_keys or key in tm.non_relevant_seen_keys:
            print(f"    ↺ Already seen, skipping")
            duplicates += 1
            continue
        
        # Check relevancy
        context_text = (
            str(tender.get('description', '')) + " " + str(tender.get('organization', ''))
        ).strip()
        
        is_relevant = tm.is_relevant_tender(tender.get('title', ''), context_text)
        print(f"    Relevant: {is_relevant}")
        
        if not is_relevant:
            print(f"    → Adding to non-relevant seen keys")
            tm.non_relevant_seen_keys.add(key)
            continue
        
        relevant_count += 1
        print(f"    ✓ Relevant tender found")
        
        # Check days_left
        if days_left_val is None:
            print(f"    ⚠ Unknown deadline, marking as seen (not saved)")
            tm.seen_keys.add(key)
            continue
        
        if days_left_val <= 7:
            print(f"    🛑 days_left ({days_left_val}) <= 7 → STOPPING SCRAPE")
            tm.seen_keys.add(key)
            stopped_early = True
            break
        
        # Save the tender
        print(f"    ✅ Saving tender (days_left > 7)")
        tm.tenders.append(tender)
        tm.seen_keys.add(key)
        added += 1
    
    print("\n" + "="*70)
    print("TEST RESULTS:")
    print("="*70)
    print(f"Total scraped: {total_scraped}")
    print(f"Relevant: {relevant_count}")
    print(f"Added to tenders: {added}")
    print(f"Duplicates: {duplicates}")
    print(f"Stopped early: {stopped_early}")
    print("="*70)
    
    # Verify the stopping behavior
    if stopped_early and total_scraped == 3:
        print("\n✅ SUCCESS: Scraping stopped at the 3rd tender (days_left=12 <= 7)")
        print("   The 4th tender was NOT processed, confirming early stop works.")
        return True
    else:
        print(f"\n❌ FAILURE: Expected to stop at tender 3, but stopped at {total_scraped}")
        print(f"   Early stop flag: {stopped_early}")
        return False

if __name__ == '__main__':
    success = test_days_left_stopping()
    exit(0 if success else 1)

from mini_tender import TenderManager

if __name__ == '__main__':
    tm = TenderManager()
    print('\n=== Starting LIVE scrape test (headless=False) ===')
    # Run non-headless so any browser errors are visible in logs if they occur.
    added = tm.scrape_bolpatra(headless=False)
    print(f'\n=== Live scrape finished. New tenders added: {added} ===')

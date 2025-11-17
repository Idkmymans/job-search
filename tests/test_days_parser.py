from mini_tender import BolpatraScraper

cases = ['27', '27 days', '27 day(s)', 'Expired', '0', '-','Expired - 0']
for c in cases:
    print(f"input: {c!r} -> {BolpatraScraper.parse_days_left_text(c)!r}")

from mini_tender import TenderManager
from datetime import datetime

print('Starting simulated tender processing test...')

tm = TenderManager()

samples = [
    {
        'title': 'Architectural Design for Park',
        'organization': 'City Office A',
        'deadline': '2025-12-31',
        'days_left': 45,
        'notice date': '2025-10-01',
        'description': 'Architectural design and planning of a new park',
    },
    {
        'title': 'Consultancy for Survey',
        'organization': 'Rural Dev B',
        'deadline': '2025-11-20',
        'days_left': 10,
        'notice date': '2025-11-01',
        'description': 'Survey and feasibility study',
    },
    {
        'title': 'Structural assessment',
        'organization': 'Org C',
        'deadline': '2025-10-01',
        'days_left': -1,
        'notice date': '2025-09-01',
        'description': 'Structural assessment for school building',
    },
]

added = 0
marked_seen = 0

for t in samples:
    ctx = (t.get('description','') + ' ' + t.get('organization','')).strip()
    print('\nProcessing sample:', t['title'])
    if not tm.is_relevant_tender(t['title'], ctx):
        print('  Not relevant, skipping')
        continue
    days = t.get('days_left')
    key = tm._make_key(t.get('title'), t.get('organization'), t.get('notice date'))
    if key in tm.seen_keys:
        print('  Already seen (from file), skipping')
        continue
    if days is None or days <= 21:
        print(f"  days_left={days} -> marking as seen but not saving")
        tm.seen_keys.add(key)
        tm.save_seen_keys()
        marked_seen += 1
        continue
    # save
    tm.tenders.append(t)
    tm.save_to_json()
    tm.seen_keys.add(key)
    tm.save_seen_keys()
    added += 1

print('\nTest summary:')
print('  added:', added)
print('  marked_seen:', marked_seen)
print('  total tenders in tm.tenders:', len(tm.tenders))
print('  total seen keys:', len(tm.seen_keys))
print('Test complete.')

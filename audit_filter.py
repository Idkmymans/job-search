import json
from mini_tender import TenderManager

"""
Simple audit harness: runs the hybrid filter over tenders.json and prints a
summary of which entries are accepted (relevant) or rejected (non-relevant).
Also writes `audit_results.json` with details for later tuning.
"""

def run_audit():
    tm = TenderManager()
    try:
        with open(tm.json_filename, 'r', encoding='utf-8') as f:
            tenders = json.load(f)
    except Exception as e:
        print(f"Failed to load {tm.json_filename}: {e}")
        return

    results = []
    accepted = 0
    rejected = 0

    for i, t in enumerate(tenders, 1):
        title = t.get('title', '')
        context = t.get('description', '') + ' ' + t.get('organization', '')
        is_rel = tm.is_relevant_tender(title, context)
        results.append({
            'index': i,
            'title': title,
            'organization': t.get('organization', ''),
            'relevant': bool(is_rel),
            'days_left': t.get('days_left'),
        })
        if is_rel:
            accepted += 1
        else:
            rejected += 1

    print(f"Total tenders checked: {len(tenders)}")
    print(f"Accepted (relevant): {accepted}")
    print(f"Rejected (non-relevant): {rejected}")

    out_file = 'audit_results.json'
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"Wrote detailed results to {out_file}")


if __name__ == '__main__':
    run_audit()

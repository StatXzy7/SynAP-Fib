"""Verify every cited DOI resolves to the stated title via the Crossref API."""
import json
import re
import time
import urllib.request
import pathlib

bib = pathlib.Path('references.bib').read_text(encoding='utf-8')
entries = {}
for m in re.finditer(r'^@\w+\{([^,\s]+),(.*?)^\}', bib, re.M | re.S):
    key = m.group(1)
    body = m.group(2)
    title = re.search(r'title\s*=\s*\{(.+?)\}', body, re.S)
    doi = re.search(r'doi\s*=\s*\{([^}]+)\}', body)
    year = re.search(r'year\s*=\s*\{(\d{4})\}', body)
    entries[key] = {
        'title': re.sub(r'\s+', ' ', title.group(1)) if title else None,
        'doi': doi.group(1) if doi else None,
        'year': year.group(1) if year else None,
    }

for key, e in entries.items():
    if not e['doi']:
        print(f'{key}: NO DOI in bib')
        continue
    url = 'https://api.crossref.org/works/' + e['doi']
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'cite-audit/1.0 (mailto:audit@example.org)'})
        with urllib.request.urlopen(req, timeout=30) as r:
            d = json.load(r)['message']
        cr_title = re.sub(r'\s+', ' ', d.get('title', [''])[0]) if d.get('title') else ''
        cr_year = str(d.get('issued', {}).get('date-parts', [[None]])[0][0])
        t_ok = e['title'].lower().rstrip('.') in cr_title.lower() or cr_title.lower().rstrip('.') in e['title'].lower()
        y_ok = (e['year'] == cr_year) or (e['year'] is None)
        status = 'OK' if (t_ok and y_ok) else 'MISMATCH'
        print(f'{key}: {status} | bib-year={e["year"]} crossref-year={cr_year}')
        if status == 'MISMATCH':
            print(f'    bib:    {e["title"][:100]}')
            print(f'    crossref: {cr_title[:100]}')
    except Exception as ex:
        print(f'{key}: FETCH-FAIL {type(ex).__name__}: {ex}')
    time.sleep(0.4)

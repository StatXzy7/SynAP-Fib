"""Gate 2 axis-1/2 audit: every DOI entry in references.bib vs Crossref.

Checks existence (DOI resolves), title match, year, volume, issue, pages/article-number.
Prints one line per entry: OK or the mismatching fields.
"""
import json
import re
import time
import urllib.request
import pathlib

BIB = pathlib.Path('references.bib').read_text(encoding='utf-8')

entries = {}
for m in re.finditer(r'^@(\w+)\{([^,\s]+),(.*?)^\}', BIB, re.M | re.S):
    kind, key, body = m.group(1), m.group(2), m.group(3)

    def field(name):
        fm = re.search(rf'{name}\s*=\s*\{{(.*?)\}}\s*,?\s*$', body, re.M | re.S)
        return re.sub(r'\s+', ' ', fm.group(1)).strip() if fm else None

    entries[key] = {
        'kind': kind,
        'title': field('title'),
        'doi': field('doi'),
        'year': field('year'),
        'volume': field('volume'),
        'number': field('number'),
        'pages': field('pages'),
    }


def norm(s):
    return re.sub(r'[^a-z0-9]', '', (s or '').lower())


def pages_match(bib_pages, crossref):
    cr_pages = crossref.get('page') or ''
    cr_artnum = crossref.get('article-number') or ''
    if not bib_pages:
        return True if (cr_pages or cr_artnum) else True
    b = norm(bib_pages)
    if b and (b in norm(cr_pages) or b in norm(cr_artnum) or norm(cr_artnum) in b):
        return True
    # booktitle (inproceedings) pages may legitimately differ from Crossref; flag for manual check
    return False


print(f'{len(entries)} entries')
for key, e in sorted(entries.items()):
    if not e['doi']:
        print(f'{key}: NO-DOI ({e["kind"]}) — manual existence check required')
        continue
    try:
        req = urllib.request.Request(
            'https://api.crossref.org/works/' + e['doi'],
            headers={'User-Agent': 'gate2-audit/1.0 (mailto:audit@example.org)'})
        with urllib.request.urlopen(req, timeout=30) as r:
            d = json.load(r)['message']
    except Exception as ex:
        print(f'{key}: FETCH-FAIL {type(ex).__name__}: {ex}')
        time.sleep(0.4)
        continue

    problems = []
    cr_title = (d.get('title') or [''])[0]
    if e['title'] and norm(e['title']) not in norm(cr_title) and norm(cr_title) not in norm(e['title']):
        problems.append(f'title: bib={e["title"][:60]!r} crossref={cr_title[:60]!r}')
    cr_year = str((d.get('issued') or {}).get('date-parts', [[None]])[0][0])
    if e['year'] and e['year'] != cr_year:
        problems.append(f'year: bib={e["year"]} crossref={cr_year}')
    cr_vol = str(d.get('volume') or '')
    if e['volume'] and e['volume'] != cr_vol:
        problems.append(f'volume: bib={e["volume"]} crossref={cr_vol!r}')
    cr_issue = str(d.get('issue') or '')
    if e['number'] and e['number'] != cr_issue:
        problems.append(f'issue: bib={e["number"]} crossref={cr_issue!r}')
    if not pages_match(e['pages'], d):
        problems.append(f'pages: bib={e["pages"]!r} crossref pages={d.get("page")!r} artnum={d.get("article-number")!r}')

    status = 'OK' if not problems else 'MISMATCH'
    print(f'{key}: {status} [year={cr_year} vol={cr_vol!r} issue={cr_issue!r} '
          f'pages={d.get("page")!r} artnum={d.get("article-number")!r}]')
    for p in problems:
        print(f'    {p}')
    time.sleep(0.4)

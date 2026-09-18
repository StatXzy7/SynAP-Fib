"""Fetch abstracts for all cited works with DOIs, curl-based with backoff.

Some hosts intermittently drop TLS handshakes from urllib; curl with retry
handles them. Writes tables/cited_abstracts.json.
"""
import json
import re
import pathlib
import subprocess
import time

bib = pathlib.Path('references.bib').read_text(encoding='utf-8')
entries = []
for m in re.finditer(r'^@\w+\{([^,\s]+),(.*?)^\}', bib, re.M | re.S):
    key, body = m.group(1), m.group(2)
    doi = re.search(r'doi\s*=\s*\{([^}]+)\}', body)
    if doi:
        entries.append((key, doi.group(1)))

out = {}
for key, doi in entries:
    url = 'https://api.openalex.org/works/https://doi.org/' + doi
    raw = None
    for attempt in range(5):
        proc = subprocess.run(
            ['curl', '-sS', '--max-time', '60', url],
            capture_output=True, text=True, encoding='utf-8')
        if proc.returncode == 0 and proc.stdout.strip().startswith('{'):
            try:
                raw = json.loads(proc.stdout)
                break
            except json.JSONDecodeError:
                pass
        time.sleep(8 + attempt * 8)
    if raw is None:
        print(f'FAIL {key}')
        out[key] = {'doi': doi, 'title': '', 'abstract': ''}
        continue

    abstract = raw.get('abstract_inverted_index')
    if abstract:
        pos = {}
        for word, idxs in abstract.items():
            for i in idxs:
                pos[i] = word
        text = ' '.join(pos[i] for i in sorted(pos))
    else:
        text = ''
    out[key] = {'doi': doi, 'title': raw.get('title', ''), 'abstract': text}
    print(f'ok {key} ({len(text)} chars abstract)')
    time.sleep(1)

pathlib.Path('tables/cited_abstracts.json').write_text(
    json.dumps(out, indent=1, ensure_ascii=False), encoding='utf-8')
print(f'\nwrote tables/cited_abstracts.json ({len(out)} entries)')

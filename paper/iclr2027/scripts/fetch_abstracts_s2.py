"""Fetch abstracts from Semantic Scholar for entries OpenAlex lacks."""
import json
import pathlib
import subprocess
import time

want = {
    'zhou2020mtlabus': '10.1016/j.media.2020.101918',
    'shamtl2021': '10.1007/s11548-021-02445-7',
    'opticdisc2020': '10.1016/j.cmpb.2020.105717',
    'usfibrosisgan2022': '10.1016/j.crad.2022.06.003',
    'microflow2023': '10.1007/s00330-023-09436-z',
    'liverspleen2025': '10.1007/s00535-025-02331-y',
    'corn2023': '10.1007/s10044-023-01181-9',
}

out = {}
for key, doi in want.items():
    url = f'https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}?fields=title,abstract'
    raw = None
    for attempt in range(4):
        proc = subprocess.run(
            ['curl', '-sS', '--max-time', '60', url],
            capture_output=True, text=True, encoding='utf-8')
        if proc.returncode == 0 and proc.stdout.strip().startswith('{'):
            try:
                raw = json.loads(proc.stdout)
                break
            except json.JSONDecodeError:
                pass
        time.sleep(10)
    if raw is None or 'abstract' not in raw:
        print(f'FAIL {key}')
        out[key] = ''
        continue
    out[key] = raw.get('abstract') or ''
    print(f'ok {key} ({len(out[key])} chars)')
    time.sleep(2)

existing = json.loads(pathlib.Path('tables/cited_abstracts.json').read_text(encoding='utf-8'))
for k, a in out.items():
    if a and k in existing:
        existing[k]['abstract'] = a
pathlib.Path('tables/cited_abstracts.json').write_text(
    json.dumps(existing, indent=1, ensure_ascii=False), encoding='utf-8')
print('\nmerged into tables/cited_abstracts.json')

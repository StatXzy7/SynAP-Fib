"""Cross-check cite keys vs bib entries for the SynAP-Fib manuscript."""
import re
import pathlib

cited = {}
for f in ['sections/01_introduction.tex', 'sections/02_related_work.tex',
          'sections/03_methods.tex', 'sections/04_results.tex',
          'sections/05_discussion.tex', 'main.tex', 'supplementary.tex']:
    p = pathlib.Path(f)
    if not p.exists():
        continue
    t = p.read_text(encoding='utf-8')
    pat = re.compile(r'\\cite\{([^}]*)\}')
    for m in pat.finditer(t):
        for k in m.group(1).split(','):
            k = k.strip()
            cited.setdefault(k, set()).add(f)

bib = set()
for m in re.finditer(r'^@\w+\{([^,\s]+),',
                     pathlib.Path('references.bib').read_text(encoding='utf-8'), re.M):
    bib.add(m.group(1))

print('cited keys:', len(cited), '| bib entries:', len(bib))
print()
print('CITED BUT MISSING IN BIB:')
for k in sorted(cited.keys() - bib):
    print(' ', k, '->', sorted(cited[k]))
print()
print('IN BIB BUT UNCITED:')
for k in sorted(bib - cited.keys()):
    print(' ', k)

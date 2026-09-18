"""Print each citation with its surrounding context for the P2 support audit."""
import re
import pathlib

files = ['sections/01_introduction.tex', 'sections/02_related_work.tex',
         'sections/03_methods.tex', 'main.tex']
for f in files:
    t = pathlib.Path(f).read_text(encoding='utf-8')
    pat = re.compile(r'\\cite\{([^}]*)\}')
    for m in pat.finditer(t):
        start = max(0, m.start() - 300)
        end = min(len(t), m.end() + 140)
        ctx = t[start:end].replace('\n', ' ')
        ctx = re.sub(r'\s+', ' ', ctx)
        print(f'--- {f} [{m.group(1)}]')
        print(f'    ...{ctx}...')
        print()

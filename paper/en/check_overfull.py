import re

with open('main_final.log', 'r') as f:
    log = f.read()

overfull = re.findall(r'Overfull \hbox \(([0-9.]+)pt too wide\).*? at lines? ([0-9]+(?:--[0-9]+)?)', log)

print(f"Found {len(overfull)} overfull hbox warnings:")
for width, lines in overfull[:10]:
    if float(width) > 5:  # Only report significant overflows
        print(f"  {width}pt too wide at lines {lines}")

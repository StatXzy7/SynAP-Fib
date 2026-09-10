"""Offline checks for the combined paper/code repository; never runs experiments."""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def check() -> None:
    errors = []
    frozen = ROOT / 'reproducibility/ae_cor_v2_seed2026'
    manifest = json.loads((frozen / 'snapshot_manifest.json').read_text(encoding='utf-8'))
    for item in manifest['files']:
        path = frozen / item['path']
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:
            errors.append(f'Frozen snapshot mismatch: {item["path"]}')
    imported = json.loads((ROOT / 'docs/IMPORT_MANIFEST.json').read_text(encoding='utf-8'))
    snapshot_entry = next(r for r in imported['files'] if r['destination'] == 'reproducibility/ae_cor_v2_seed2026/snapshot_manifest.json')
    if hashlib.sha256((frozen / 'snapshot_manifest.json').read_bytes()).hexdigest() != snapshot_entry['source_sha256']:
        errors.append('Frozen snapshot manifest differs from imported original')

    files = subprocess.check_output(['git', '-C', str(ROOT), 'ls-files', '-z']).decode('utf-8').split('\0')
    texts = {'.py', '.md', '.tex', '.bib', '.json', '.yaml', '.yml', '.toml', '.ps1', '.csv', '.drawio', '.txt'}
    forbidden_suffixes = {'.pt', '.pth', '.ckpt', '.safetensors', '.npz', '.npy', '.parquet', '.pem', '.key'}
    forbidden_dirs = {'data', 'research-private', 'checkpoints', 'artifacts', '__pycache__', '.pytest_cache'}
    secret_patterns = [r'gh[pousr]_[A-Za-z0-9]{30,}', r'github_pat_[A-Za-z0-9_]{40,}', r'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----']
    for rel in filter(None, files):
        path = ROOT / rel
        if path.suffix in forbidden_suffixes or forbidden_dirs.intersection(path.parts) or path.name == '.env':
            errors.append(f'Unexpected tracked artifact: {rel}')
        if path.suffix in texts or path.name in {'.gitignore', '.gitattributes'}:
            try:
                text = path.read_text(encoding='utf-8-sig')
                if '\ufffd' in text:
                    errors.append(f'Unicode replacement character: {rel}')
                if any(re.search(pattern, text) for pattern in secret_patterns):
                    errors.append(f'Possible credential in: {rel}')
                if path.suffix == '.py':
                    ast.parse(text, filename=rel)
            except (UnicodeError, SyntaxError) as exc:
                errors.append(f'Text/syntax error: {rel}: {exc}')

    for language in ('en', 'zh'):
        base = ROOT / 'paper' / language
        shared = ROOT / 'paper/en'
        for path in base.rglob('*.tex'):
            text = path.read_text(encoding='utf-8')
            text = re.sub(r'(?<!\\)%[^\n]*', '', text)
            for command, raw in re.findall(r'\\(input|include|includegraphics|bibliography)(?:\[[^\]]*\])?\{([^}]+)\}', text):
                for ref in raw.split(','):
                    if command in ('input', 'include'):
                        relative = ref if ref.endswith('.tex') else ref + '.tex'
                        candidates = [base / relative]
                    elif command == 'bibliography':
                        candidates = [base / (ref if ref.endswith('.bib') else ref + '.bib')]
                    else:
                        candidates = [base / ref, shared / ref]
                    if not any(p.is_file() and p.resolve().is_relative_to(ROOT) for p in candidates):
                        errors.append(f'Missing/outside paper dependency: {path.relative_to(ROOT)} -> {raw}')
    if errors:
        raise SystemExit('\n'.join(errors))
    print(f'PASS: {len(list(filter(None, files)))} tracked files; UTF-8/Python syntax; paper dependencies; {len(manifest["files"])} frozen file hashes and original manifest; artifact/credential patterns.')


if __name__ == '__main__':
    check()

import json
import os

BASE = 'handpickedfonts'
CATEGORIES = [
    ('sans-serif', 'Handpicked — Sans-Serif', 'sans-serif'),
    ('serif', 'Handpicked — Serif', 'serif'),
    ('script', 'Handpicked — Script', 'cursive'),
]
EXT_MAP = {
    '.ttf': 'truetype',
    '.otf': 'opentype',
    '.woff2': 'woff2',
    '.woff': 'woff',
}

css_rules = []
groups = []

for folder, label, fallback in CATEGORIES:
    cat_path = os.path.join(BASE, folder)
    os.makedirs(cat_path, exist_ok=True)
    items = []

    for root, dirs, files in sorted(os.walk(cat_path)):
        dirs[:] = [d for d in sorted(dirs) if d != '__MACOSX']
        for fname in sorted(files):
            if fname.startswith('._'):
                continue
            ext = os.path.splitext(fname)[1].lower()
            if ext not in EXT_MAP:
                continue

            rel_path = os.path.relpath(os.path.join(root, fname), BASE).replace('\\', '/')
            # Clean display name from filename
            raw_name = os.path.splitext(fname)[0]
            clean_name = raw_name.replace('_', ' ').replace('-', ' ').strip()
            # Avoid duplicate names if multiple formats exist
            if any(i['name'] == clean_name for i in items):
                continue

            fmt = EXT_MAP[ext]
            css_rules.append(
                f"@font-face {{\n"
                f"  font-family: '{clean_name}';\n"
                f"  src: url('./{rel_path}') format('{fmt}');\n"
                f"  font-weight: normal;\n"
                f"  font-style: normal;\n"
                f"}}"
            )
            items.append({
                'name': clean_name,
                'css': f"'{clean_name}', {fallback}",
            })

    if items:
        groups.append({'label': label, 'items': items})

with open(os.path.join(BASE, 'fonts.css'), 'w', encoding='utf-8') as f:
    f.write('\n\n'.join(css_rules) + '\n')

with open(os.path.join(BASE, 'handpicked.js'), 'w', encoding='utf-8') as f:
    f.write('window.HANDPICKED_GROUPS = ' + json.dumps(groups, ensure_ascii=False, indent=2) + ';\n')

print(f"Generated {len(css_rules)} @font-face rules across {len(groups)} categories.")

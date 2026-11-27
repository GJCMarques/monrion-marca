import json
import os
import re

BASE = 'handpickedfonts'
CATEGORIES = [
    ('sans-serif', 'Handpicked — Sans-Serif', 'sans-serif'),
    ('serif', 'Handpicked — Serif', 'serif'),
    ('script', 'Handpicked — Script', 'cursive'),
]
EXT_PRIORITY = {'.woff2': 4, '.otf': 3, '.ttf': 2, '.woff': 1}
EXT_FORMAT = {'.ttf': 'truetype', '.otf': 'opentype', '.woff2': 'woff2', '.woff': 'woff'}

FAMILY_NAMES = {
    'coconat-main': 'Coconat',
    'dof': 'DOF',
    'existence-light': 'Existence',
    'godber': 'Godber',
    'intro-black': 'Intro',
    'jost': 'Jost',
    'lemonmilk': 'Lemon Milk',
    'sifonn': 'Sifonn Pro',
    'antro-vectra': 'Antro Vectra',
    'biloxi-script': 'Biloxi Script',
    'zapfino': 'Zapfino',
    'isenheim-main': 'Isenheim',
    'ltsoul-v2': 'LT Soul',
    'tenderness_0601': 'Tenderness',
    'écrou_regular': 'Écrou',
}

def detect_weight(fname_lower):
    m = re.search(r'(?<!\d)([1-9]00)(?!\d)', fname_lower)
    if m:
        return int(m.group(1))
    if 'hairline' in fname_lower:
        return 100
    if 'thin' in fname_lower:
        return 200
    if 'light' in fname_lower or 'fin' in fname_lower:
        return 300
    if 'medium' in fname_lower:
        return 500
    if 'semibold' in fname_lower or 'demi' in fname_lower or 'semi' in fname_lower:
        return 600
    if 'bolder' in fname_lower or 'bold' in fname_lower:
        return 700
    if 'heavy' in fname_lower or 'hevy' in fname_lower:
        return 800
    if 'black' in fname_lower:
        return 900
    return 400

def detect_style(fname_lower):
    if 'italic' in fname_lower or re.search(r'[-_]it(?:\.|$)', fname_lower):
        return 'italic'
    return 'normal'

css_rules = []
groups = []

for folder, label, fallback in CATEGORIES:
    cat_path = os.path.join(BASE, folder)
    os.makedirs(cat_path, exist_ok=True)
    items = []

    for fam_dir in sorted(os.listdir(cat_path)):
        fam_path = os.path.join(cat_path, fam_dir)
        if not os.path.isdir(fam_path):
            continue

        fam_name = FAMILY_NAMES.get(fam_dir.lower(), fam_dir.replace('-', ' ').replace('_', ' ').title())
        variants = {}  # (weight, style) -> (priority, rel_path, ext)

        for root, dirs, files in sorted(os.walk(fam_path)):
            dirs[:] = [d for d in sorted(dirs) if d != '__MACOSX']
            for fname in sorted(files):
                if fname.startswith('._'):
                    continue
                ext = os.path.splitext(fname)[1].lower()
                if ext not in EXT_PRIORITY:
                    continue

                low = fname.lower()
                # Skip special decorative sub-variants if standard exists for same weight/style
                w = detect_weight(low)
                st = detect_style(low)
                prio = EXT_PRIORITY[ext]
                if 'inline' in low or 'stencil' in low or 'unicase' in low or 'ext' in low:
                    prio -= 10

                rel_path = os.path.relpath(os.path.join(root, fname), BASE).replace('\\', '/')
                key = (w, st)
                if key not in variants or prio > variants[key][0]:
                    variants[key] = (prio, rel_path, ext)

        if not variants:
            continue

        for (w, st), (_, rel_path, ext) in sorted(variants.items()):
            fmt = EXT_FORMAT[ext]
            css_rules.append(
                f"@font-face {{\n"
                f"  font-family: '{fam_name}';\n"
                f"  src: url('./{rel_path}') format('{fmt}');\n"
                f"  font-weight: {w};\n"
                f"  font-style: {st};\n"
                f"}}"
            )

        items.append({
            'name': fam_name,
            'css': f"'{fam_name}', {fallback}",
        })

    if items:
        groups.append({'label': label, 'items': items})

with open(os.path.join(BASE, 'fonts.css'), 'w', encoding='utf-8') as f:
    f.write('\n\n'.join(css_rules) + '\n')

with open(os.path.join(BASE, 'handpicked.js'), 'w', encoding='utf-8') as f:
    f.write('window.HANDPICKED_GROUPS = ' + json.dumps(groups, ensure_ascii=False, indent=2) + ';\n')

print(f"Generated {len(css_rules)} @font-face rules for {sum(len(g['items']) for g in groups)} families.")

from pathlib import Path

root = Path('extracted')
out = Path('out/selection_sync_diag.txt')
out.parent.mkdir(parents=True, exist_ok=True)

needles = [
    'CentralMindPtState', 'selected', 'selectedProgram', 'selected_pt',
    'current PT', 'CURRENT_PT', 'mascotLine', 'widgetLine',
    'MindTrainingStore', 'setSelected', 'selectedMuscle', 'selectedTitle',
    '오늘의 마음 PT', 'crown', '대표', 'MascotWidgetPrefs', 'youngify'
]

chunks = []
for p in root.rglob('*'):
    if not p.is_file() or p.suffix.lower() not in {'.java', '.kt'}:
        continue
    try:
        t = p.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        continue
    low = t.lower()
    hits = []
    for n in needles:
        start = 0
        while True:
            idx = low.find(n.lower(), start)
            if idx < 0:
                break
            hits.append(idx)
            start = idx + max(1, len(n))
    if hits:
        chunks.append(f'\n\n================ FILE: {p} ================\n')
        # Merge nearby contexts so methods/listeners stay readable.
        ranges = []
        for i in sorted(set(hits)):
            a, b = max(0, i - 2600), min(len(t), i + 5200)
            if ranges and a <= ranges[-1][1] + 300:
                ranges[-1] = (ranges[-1][0], max(ranges[-1][1], b))
            else:
                ranges.append((a, b))
        for n, (a, b) in enumerate(ranges[:20], 1):
            chunks.append(f'\n--- CONTEXT {n} chars {a}:{b} ---\n{t[a:b]}\n')

# Also dump key files whole when present; these are small enough and eliminate guessing.
for name in ['MascotWidgetPrefs.java', 'CentralMindPtState.java', 'MindTrainingStore.java']:
    for p in root.rglob(name):
        try:
            t = p.read_text(encoding='utf-8', errors='ignore')
            chunks.append(f'\n\n================ FULL FILE: {p} ================\n{t}\n')
        except Exception:
            pass

text = ''.join(chunks) + '\nSELECTION_SYNC_DIAG_DONE\n'
out.write_text(text, encoding='utf-8')
print(text)
print(f'WROTE_DIAG={out}')

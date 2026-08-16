from pathlib import Path
import shutil

root = Path('extracted')
out = Path('out/selection_sync_diag.txt')
out.parent.mkdir(parents=True, exist_ok=True)
full_dir = Path('out/v101824_sources')
full_dir.mkdir(parents=True, exist_ok=True)

needles = [
    'CentralMindPtState', 'selected', 'selectedProgram', 'selected_pt',
    'current PT', 'CURRENT_PT', 'mascotLine', 'widgetLine',
    'MindTrainingStore', 'setSelected', 'selectedMuscle', 'selectedTitle',
    '오늘의 마음 PT', 'crown', '대표', 'MascotWidgetPrefs', 'youngify',
    'LauncherSurfaceAccessibilityService'
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
        ranges = []
        for i in sorted(set(hits)):
            a, b = max(0, i - 2600), min(len(t), i + 5200)
            if ranges and a <= ranges[-1][1] + 300:
                ranges[-1] = (ranges[-1][0], max(ranges[-1][1], b))
            else:
                ranges.append((a, b))
        for n, (a, b) in enumerate(ranges[:20], 1):
            chunks.append(f'\n--- CONTEXT {n} chars {a}:{b} ---\n{t[a:b]}\n')

names = [
    'MascotWidgetPrefs.java', 'CentralMindPtState.java', 'MindTrainingStore.java',
    'OverlayService.java', 'LauncherSurfaceAccessibilityService.java',
    'MaeumMonClockWidget.java', 'CounselingProgramAnalyzer.java',
    'TherapySurfaceContext.java', 'TherapySurfacePolicyV501.java',
    'widget_maeummon_clock.xml', 'widget_maeummon_large.xml',
    'widget_maeummon_medium.xml', 'widget_maeummon_small.xml',
    'widget_maeummon_narrow.xml', 'maeummon_clock_widget_info.xml'
]
for name in names:
    for p in root.rglob(name):
        try:
            t = p.read_text(encoding='utf-8', errors='ignore')
            chunks.append(f'\n\n================ FULL FILE: {p} ================\n{t}\n')
            shutil.copy2(p, full_dir / name)
        except Exception:
            pass

text = ''.join(chunks) + '\nSELECTION_SYNC_DIAG_DONE\n'
out.write_text(text, encoding='utf-8')
print(text)
print(f'WROTE_DIAG={out}')
print(f'WROTE_FULL_SOURCES={full_dir}')

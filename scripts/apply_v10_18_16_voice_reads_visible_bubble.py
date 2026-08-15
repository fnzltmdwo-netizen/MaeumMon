from pathlib import Path
import re

root = Path('extracted')
app = root / 'app/src/main/java/com/maeummon/app'
overlay = app / 'OverlayService.java'
text = overlay.read_text(encoding='utf-8')

print('=== TextView declarations in OverlayService ===')
for m in re.finditer(r'(?:android\.widget\.)?TextView\s+(\w+)\s*=\s*new\s+(?:android\.widget\.)?TextView\([^;]+;', text, re.S):
    var = m.group(1)
    start = max(0, m.start()-180)
    end = min(len(text), m.end()+700)
    print(f'--- VAR {var} ---')
    print(text[start:end])

print('=== TTS calls in OverlayService ===')
for m in re.finditer(r'TtsManager\.speak\([^;]+;', text):
    start = max(0, m.start()-600)
    end = min(len(text), m.end()+500)
    print('--- TTS ---')
    print(text[start:end])

raise SystemExit('v10.18.16 diagnostic complete')

from pathlib import Path
import re

root = Path('extracted')
app = root / 'app/src/main/java/com/maeummon/app'
overlay = app / 'OverlayService.java'
gradle = root / 'app/build.gradle'

text = overlay.read_text(encoding='utf-8')

anchor = '                final String result = filtered;\n'
if anchor not in text:
    raise SystemExit('v10.18.16: tap result anchor missing')

insert = '''                final String result = filtered;\n                String currentPtTapLine = CentralMindPtState.mascotLine(OverlayService.this);\n                final String tapLine = (currentPtTapLine != null && !currentPtTapLine.trim().isEmpty())\n                        ? currentPtTapLine.trim() : result;\n'''
text = text.replace(anchor, insert, 1)

repls = {
    '                        lastComfortLine = result;': '                        lastComfortLine = tapLine;',
    '                        rememberComfortLine(result);': '                        rememberComfortLine(tapLine);',
    '                        updateSpeech(result);': '                        updateSpeech(tapLine);',
    '                            TtsManager.speak(OverlayService.this, result);': '                            TtsManager.speak(OverlayService.this, tapLine);',
    '                        final long holdMs = comfortHoldMs(result);': '                        final long holdMs = comfortHoldMs(tapLine);',
}
for old, new in repls.items():
    if old not in text:
        raise SystemExit('v10.18.16: expected tap block line missing: ' + old.strip())
    text = text.replace(old, new, 1)

overlay.write_text(text, encoding='utf-8')

g = gradle.read_text(encoding='utf-8')
g, n1 = re.subn(r'versionCode\s+\d+', 'versionCode 101816', g, count=1)
g, n2 = re.subn(r'versionName\s+"[^"]+"', 'versionName "10.18.16"', g, count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit('v10.18.16: gradle version anchor missing')
gradle.write_text(g, encoding='utf-8')

print('Applied v10.18.16: mascot tap bubble + TTS now use current PT mascot line')

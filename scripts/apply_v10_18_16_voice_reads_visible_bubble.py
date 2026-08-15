from pathlib import Path
import re

root = Path('extracted')
app = root / 'app/src/main/java/com/maeummon/app'
overlay = app / 'OverlayService.java'
gradle = root / 'app/build.gradle'

text = overlay.read_text(encoding='utf-8')

# Keep a reference to the actual visible speech TextView so tap-TTS reads exactly what is on screen.
if 'private android.widget.TextView currentSpeechView;' not in text:
    class_match = re.search(r'public class OverlayService[^\{]*\{', text)
    if not class_match:
        raise SystemExit('v10.18.16: OverlayService class anchor missing')
    insert_pos = class_match.end()
    text = text[:insert_pos] + '\n    private android.widget.TextView currentSpeechView;\n' + text[insert_pos:]

# Capture the visible TextView. Prefer the known local variable name `speech` used by the overlay builder.
assign_pat = re.compile(r'(TextView\s+speech\s*=\s*new\s+TextView\([^;]+;)', re.S)
m = assign_pat.search(text)
if not m:
    # Some versions may use android.widget.TextView explicitly.
    assign_pat = re.compile(r'(android\.widget\.TextView\s+speech\s*=\s*new\s+android\.widget\.TextView\([^;]+;)', re.S)
    m = assign_pat.search(text)
if not m:
    raise SystemExit('v10.18.16: visible speech TextView creation anchor missing')
if 'currentSpeechView = speech;' not in text[m.end():m.end()+120]:
    text = text[:m.end()] + '\n        currentSpeechView = speech;' + text[m.end():]

# Replace ONLY TTS calls inside OverlayService so they speak the currently displayed bubble text.
# Preserve the old expression strictly as a fallback if the view is not ready.
call_pat = re.compile(r'TtsManager\.speak\(([^,]+),\s*([^;\n]+)\);')
replacements = 0

def repl(match):
    global replacements
    ctx = match.group(1).strip()
    old_expr = match.group(2).strip()
    # Avoid double-patching if workflow is re-run unexpectedly.
    if 'currentSpeechView' in old_expr:
        return match.group(0)
    replacements += 1
    visible_expr = '(currentSpeechView != null && currentSpeechView.getText() != null && currentSpeechView.getText().length() > 0 ? currentSpeechView.getText().toString() : ' + old_expr + ')'
    return f'TtsManager.speak({ctx}, {visible_expr});'

text = call_pat.sub(repl, text)
if replacements < 1:
    raise SystemExit('v10.18.16: no TtsManager.speak call found in OverlayService')

overlay.write_text(text, encoding='utf-8')

# Version bump only.
g = gradle.read_text(encoding='utf-8')
g, n1 = re.subn(r'versionCode\s+\d+', 'versionCode 101816', g, count=1)
g, n2 = re.subn(r'versionName\s+"[^"]+"', 'versionName "10.18.16"', g, count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit('v10.18.16: gradle version anchor missing')
gradle.write_text(g, encoding='utf-8')

print(f'Applied v10.18.16: mascot tap voice reads visible bubble text ({replacements} TTS call(s) patched)')

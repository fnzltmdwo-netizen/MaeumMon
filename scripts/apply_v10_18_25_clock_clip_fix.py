from pathlib import Path
import re

root = Path('extracted')
widget = root / 'app/src/main/java/com/maeummon/app/MaeumMonClockWidget.java'
gradle = root / 'app/build.gradle'

text = widget.read_text(encoding='utf-8')

# Replace the full TextSpec selector with wider time canvases and slightly smaller time glyphs.
pattern = re.compile(r'    private static TextSpec specForLayout\(int layout\) \{.*?\n    \}', re.S)
replacement = '''    private static TextSpec specForLayout(int layout) {
        // v10.18.25: clock bitmaps need generous horizontal headroom.
        // Samsung launcher may clip the rightmost glyph when the source bitmap is too tight,
        // especially for 5-char times such as 12:10 / 23:59. Keep the ImageView size unchanged
        // and render onto a wider bitmap; centerInside will scale the whole clock safely.
        if (layout == R.layout.widget_maeummon_small)  return new TextSpec(66f, 34f, 480, 108, 330, 64);
        if (layout == R.layout.widget_maeummon_narrow) return new TextSpec(70f, 38f, 540, 118, 370, 70);
        if (layout == R.layout.widget_maeummon_medium) return new TextSpec(112f, 58f, 760, 174, 540, 94);
        if (layout == R.layout.widget_maeummon_large)  return new TextSpec(114f, 62f, 860, 196, 660, 108);
        return new TextSpec(108f, 56f, 820, 184, 600, 102);
    }'''

new_text, count = pattern.subn(replacement, text, count=1)
if count != 1:
    raise SystemExit(f'v10.18.25: specForLayout replacement failed count={count}')

# Force a fixed two-digit hour format so clock length is deterministic (always HH:mm = 5 chars).
new_text = new_text.replace(
    'new SimpleDateFormat(DateFormat.is24HourFormat(context) ? "H:mm" : "h:mm", Locale.KOREA)',
    'new SimpleDateFormat(DateFormat.is24HourFormat(context) ? "HH:mm" : "hh:mm", Locale.KOREA)'
)

widget.write_text(new_text, encoding='utf-8')

g = gradle.read_text(encoding='utf-8')
g = re.sub(r'versionCode\s+\d+', 'versionCode 101825', g)
g = re.sub(r'versionName\s+"[^"]+"', 'versionName "10.18.25"', g)
gradle.write_text(g, encoding='utf-8')

print('Applied v10.18.25 widget clock clipping fix')

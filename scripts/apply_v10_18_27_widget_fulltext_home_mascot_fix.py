from pathlib import Path
import re

root = Path('extracted')
app = root / 'app/src/main/java/com/maeummon/app'
res = root / 'app/src/main/res/layout'
gradle = root / 'app/build.gradle'

# -----------------------------------------------------------------------------
# 1) CLOCK: do not force a leading zero on single-digit hours.
#    On Samsung One UI the widget's physical ImageView width is launcher-controlled;
#    01:00 is wider than 1:00 and can lose the last glyph even with a wide source bitmap.
#    Return to the user's device-native compact format while preserving v10.18.25 bitmap headroom.
# -----------------------------------------------------------------------------
widget = app / 'MaeumMonClockWidget.java'
w = widget.read_text(encoding='utf-8')
w = w.replace(
    'new SimpleDateFormat(DateFormat.is24HourFormat(context) ? "HH:mm" : "hh:mm", Locale.KOREA)',
    'new SimpleDateFormat(DateFormat.is24HourFormat(context) ? "H:mm" : "h:mm", Locale.KOREA)'
)

# Give PT text substantially more source characters. The previous 54/68/84 caps could
# produce a literal ellipsis before Android layout even got a chance to wrap the text.
pat = re.compile(r'''        int widgetMaxChars = \(layout == R\.layout\.widget_maeummon_medium\) \? \d+
                : \(layout == R\.layout\.widget_maeummon_clock\) \? \d+
                : \(layout == R\.layout\.widget_maeummon_large\) \? \d+
                : \(layout == R\.layout\.widget_maeummon_narrow\) \? \d+
                : \d+;''')
replacement = '''        int widgetMaxChars = (layout == R.layout.widget_maeummon_medium) ? 100
                : (layout == R.layout.widget_maeummon_clock) ? 120
                : (layout == R.layout.widget_maeummon_large) ? 140
                : (layout == R.layout.widget_maeummon_narrow) ? 100
                : 72;'''
w, n = pat.subn(replacement, w, count=1)
if n != 1:
    raise SystemExit('v10.18.27: widgetMaxChars anchor missing')

# The shared policy call was also capped at 68 chars.
w = w.replace('TherapySurfacePolicyV501.compactWidgetText(line, 68)',
              'TherapySurfacePolicyV501.compactWidgetText(line, 120)')
widget.write_text(w, encoding='utf-8')

# Central PT source: v10.18.24 intentionally raised 31 -> 68, but 68 is still visibly
# truncated in the user's screenshot. Preserve the full short exercise instead.
central = app / 'CentralMindPtState.java'
c = central.read_text(encoding='utf-8')
c = re.sub(r'(compact\([^\n]+?),\s*68\)', r'\1, 120)', c)
central.write_text(c, encoding='utf-8')

# -----------------------------------------------------------------------------
# 2) PT LAYOUT: remove Android ellipsizing and allow more wrapped lines.
#    We target only the PT/message TextView (the one carrying maxLines=4 after v10.18.24).
# -----------------------------------------------------------------------------
height_map = {
    'widget_maeummon_clock.xml':  [('104dp', '128dp')],
    'widget_maeummon_large.xml':  [('124dp', '148dp')],
    'widget_maeummon_medium.xml': [('86dp', '110dp')],
    'widget_maeummon_narrow.xml': [('98dp', '122dp')],
}

for name, height_reps in height_map.items():
    path = res / name
    text = path.read_text(encoding='utf-8')
    for old, new in height_reps:
        if old in text:
            text = text.replace(old, new, 1)

    tag_pattern = re.compile(r'<TextView\b(?:(?!</?TextView\b).)*?android:maxLines="4"(?:(?!</?TextView\b).)*?/?>', re.S)
    m = tag_pattern.search(text)
    if not m:
        raise SystemExit(f'v10.18.27: PT TextView maxLines=4 missing in {name}')
    tag = m.group(0)
    tag = tag.replace('android:maxLines="4"', 'android:maxLines="6"', 1)
    # Remove any XML-level forced truncation from the PT text only.
    tag = re.sub(r'\s+android:ellipsize="[^"]+"', '', tag)
    # Keep descenders safe and give the last line extra baseline room.
    tag = re.sub(r'android:paddingBottom="[^"]+"', 'android:paddingBottom="10dp"', tag, count=1)
    if 'android:paddingBottom=' not in tag:
        tag = tag.replace('android:maxLines="6"', 'android:maxLines="6"\n            android:paddingBottom="10dp"', 1)
    if 'android:includeFontPadding=' not in tag:
        tag = tag.replace('android:maxLines="6"', 'android:maxLines="6"\n            android:includeFontPadding="true"', 1)
    text = text[:m.start()] + tag + text[m.end():]
    path.write_text(text, encoding='utf-8')

# -----------------------------------------------------------------------------
# 3) MASCOT: restore a safe fallback for Samsung One UI Home.
#    v10.18.24 made fallback home=false unconditionally, which means after reinstall
#    (or whenever accessibility classification is unavailable) the mascot can never appear.
#    Use launcher package equality as fallback, while still rejecting known non-home classes.
# -----------------------------------------------------------------------------
overlay = app / 'OverlayService.java'
o = overlay.read_text(encoding='utf-8')
strict = '''            } else {
                // v10.18.24 strict HOME-only rule.
                // UsageStats cannot reliably distinguish Samsung Home from All Apps/Finder because
                // they can share the same launcher package/class. Ambiguous means HIDE, never SHOW.
                updateForegroundPackage();
                home = false;
            }'''
safe = '''            } else {
                // v10.18.27 Samsung One UI fallback.
                // After reinstall/accessibility restart there may be no classifier state yet.
                // In that case, allow the actual launcher package as HOME, but continue to block
                // recognizable Recents / Apps / Finder / folder surfaces.
                updateForegroundPackage();
                home = launcherPackage != null
                        && !launcherPackage.isEmpty()
                        && launcherPackage.equals(lastForegroundPackage);

                String cls = lastForegroundClass == null ? "" : lastForegroundClass.toLowerCase();
                if (cls.contains("recents") || cls.contains("overview") || cls.contains("allapps")
                        || cls.contains("drawer") || cls.contains("appslist") || cls.contains("finder")
                        || cls.contains("folder") || cls.contains("folderview") || cls.contains("openfolder")) {
                    home = false;
                }
            }'''
if strict not in o:
    raise SystemExit('v10.18.27: strict overlay fallback anchor missing')
o = o.replace(strict, safe, 1)
overlay.write_text(o, encoding='utf-8')

# Version bump.
g = gradle.read_text(encoding='utf-8')
g = re.sub(r'versionCode\s+\d+', 'versionCode 101827', g)
g = re.sub(r'versionName\s+"[^"]+"', 'versionName "10.18.27"', g)
gradle.write_text(g, encoding='utf-8')

print('Applied v10.18.27: compact clock + full PT text + One UI home mascot fallback')

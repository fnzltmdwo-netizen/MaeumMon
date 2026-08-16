from pathlib import Path
import re

root = Path('extracted')
app = root / 'app/src/main/java/com/maeummon/app'
layout_dir = root / 'app/src/main/res/layout'
gradle = root / 'app/build.gradle'

# v10.18.28b: robust structural fix applied after v10.18.27.

# 1) Clock rows: make time bitmap fluid in clock/large layouts.
for name in ['widget_maeummon_clock.xml', 'widget_maeummon_large.xml']:
    path = layout_dir / name
    t = path.read_text(encoding='utf-8')
    t = t.replace('<LinearLayout android:id="@+id/timeWrap" android:layout_width="wrap_content"',
                  '<LinearLayout android:id="@+id/timeWrap" android:layout_width="match_parent"', 1)
    t = t.replace('<LinearLayout android:layout_width="wrap_content" android:layout_height="wrap_content" android:gravity="center_vertical" android:orientation="horizontal">',
                  '<LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content" android:gravity="center_vertical" android:orientation="horizontal">', 1)
    # Replace whatever fixed dp width v10.18.27 currently has.
    t, n = re.subn(r'(<ImageView android:id="@\+id/widgetTimeBitmap" android:layout_width=")\d+dp(" )',
                   r'\g<1>0dp\2android:layout_weight="1" ', t, count=1)
    if n != 1 and 'android:id="@+id/widgetTimeBitmap" android:layout_width="0dp"' not in t:
        raise SystemExit(f'v10.18.28b: time bitmap width anchor missing in {name}')
    if name == 'widget_maeummon_clock.xml':
        t = t.replace('android:paddingLeft="22dp"', 'android:paddingLeft="12dp"', 1)
        t = t.replace('android:paddingRight="22dp"', 'android:paddingRight="12dp"', 1)
    else:
        t = t.replace('android:paddingLeft="30dp"', 'android:paddingLeft="16dp"', 1)
        t = t.replace('android:paddingRight="30dp"', 'android:paddingRight="16dp"', 1)
    path.write_text(t, encoding='utf-8')

# 2) PT text: replace only the cap block, then fit the already-generated line.
widget = app / 'MaeumMonClockWidget.java'
w = widget.read_text(encoding='utf-8')
cap_pat = re.compile(r'''        int widgetMaxChars = \(layout == R\.layout\.widget_maeummon_medium\) \? \d+\n                : \(layout == R\.layout\.widget_maeummon_clock\) \? \d+\n                : \(layout == R\.layout\.widget_maeummon_large\) \? \d+\n                : \(layout == R\.layout\.widget_maeummon_narrow\) \? \d+\n                : \d+;''')
cap_repl = '''        int widgetMaxChars = (layout == R.layout.widget_maeummon_medium) ? 52
                : (layout == R.layout.widget_maeummon_clock) ? 58
                : (layout == R.layout.widget_maeummon_large) ? 66
                : (layout == R.layout.widget_maeummon_narrow) ? 50
                : 42;
        line = fitWidgetMessage(line, widgetMaxChars);'''
w, n = cap_pat.subn(cap_repl, w, count=1)
if n != 1:
    raise SystemExit('v10.18.28b: widgetMaxChars anchor missing')

anchor = '    private static void scheduleNextUpdate(Context context) {'
if 'private static String fitWidgetMessage(String raw, int maxChars)' not in w:
    if anchor not in w:
        raise SystemExit('v10.18.28b: scheduleNextUpdate anchor missing')
    helper = r'''    private static String fitWidgetMessage(String raw, int maxChars) {
        if (raw == null) return "";
        String s = raw.replace('\n', ' ').replace('\r', ' ').replaceAll("\\s+", " ").trim();
        if (s.length() <= maxChars) return s;
        int hard = Math.min(maxChars, s.length());
        int bestSentence = -1;
        int bestClause = -1;
        for (int i = 12; i < hard; i++) {
            char ch = s.charAt(i);
            if (ch == '.' || ch == '!' || ch == '?' || ch == '。' || ch == '！' || ch == '？') bestSentence = i + 1;
            else if (ch == ',' || ch == '·' || ch == ';' || ch == '，') bestClause = i;
        }
        if (bestSentence >= Math.min(24, hard)) return s.substring(0, bestSentence).trim();
        int cut = bestClause >= Math.min(22, hard) ? bestClause : s.lastIndexOf(' ', hard);
        if (cut < Math.min(22, hard)) cut = hard;
        String out = s.substring(0, cut).trim();
        while (out.endsWith(",") || out.endsWith("·") || out.endsWith(";") || out.endsWith("，")) out = out.substring(0, out.length() - 1).trim();
        if (!(out.endsWith(".") || out.endsWith("!") || out.endsWith("?") || out.endsWith("다") || out.endsWith("요") || out.endsWith("해") || out.endsWith("자"))) out += ".";
        return out;
    }

'''
    w = w.replace(anchor, helper + anchor, 1)
widget.write_text(w, encoding='utf-8')

# PT bubble geometry: safer line count and slightly wider text area.
layout_specs = {
    'widget_maeummon_clock.xml': ('96dp', '76dp', '12sp', '11sp'),
    'widget_maeummon_large.xml': ('126dp', '100dp', '16sp', '14sp'),
    'widget_maeummon_medium.xml': ('66dp', '60dp', '10sp', '9sp'),
    'widget_maeummon_narrow.xml': ('66dp', '58dp', '10sp', '9sp'),
}
for name, (m_old, m_new, s_old, s_new) in layout_specs.items():
    path = layout_dir / name
    t = path.read_text(encoding='utf-8')
    t = t.replace(f'android:layout_marginStart="{m_old}"', f'android:layout_marginStart="{m_new}"', 1)
    t = t.replace(f'android:textSize="{s_old}"', f'android:textSize="{s_new}"', 1)
    t = t.replace('android:maxLines="6"', 'android:maxLines="5"', 1)
    t = re.sub(r'\s+android:ellipsize="[^"]+"', '', t)
    path.write_text(t, encoding='utf-8')

# 3) Mascot classifier: ordinary SystemUI events must not destroy HOME state.
access = app / 'LauncherSurfaceAccessibilityService.java'
a = access.read_text(encoding='utf-8')
systemui_pat = re.compile(r'''        if \(lowerPkg\.contains\("systemui"\)\) \{.*?            return;\n        \}''', re.S)
systemui_repl = '''        if (lowerPkg.contains("systemui")) {
            if (cls.contains("recents") || cls.contains("overview") || info.hasRecentKeyword) {
                saveMode(MODE_BLOCKED);
            }
            return;
        }'''
a, n = systemui_pat.subn(systemui_repl, a, count=1)
if n != 1:
    raise SystemExit('v10.18.28b: SystemUI classifier block missing')
access.write_text(a, encoding='utf-8')

# Enabled accessibility can be UNKNOWN after reinstall/restart; fall back to launcher package.
overlay = app / 'OverlayService.java'
o = overlay.read_text(encoding='utf-8')
enabled_pat = re.compile(r'''            if \(LauncherSurfaceAccessibilityService\.isEnabled\(OverlayService\.this\)\) \{.*?            \} else \{''', re.S)
enabled_repl = '''            if (LauncherSurfaceAccessibilityService.isEnabled(OverlayService.this)) {
                String surfaceMode = getSharedPreferences(AppPrefs.PREFS, MODE_PRIVATE)
                        .getString(LauncherSurfaceAccessibilityService.PREF_MODE,
                                LauncherSurfaceAccessibilityService.MODE_UNKNOWN);
                if (LauncherSurfaceAccessibilityService.MODE_HOME.equals(surfaceMode)) {
                    home = true;
                } else if (LauncherSurfaceAccessibilityService.MODE_BLOCKED.equals(surfaceMode)) {
                    home = false;
                } else {
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
                }
            } else {'''
o, n = enabled_pat.subn(enabled_repl, o, count=1)
if n != 1:
    raise SystemExit('v10.18.28b: enabled accessibility branch missing')
overlay.write_text(o, encoding='utf-8')

# Version bump stays 10.18.28.
g = gradle.read_text(encoding='utf-8')
g = re.sub(r'versionCode\s+\d+', 'versionCode 101828', g)
g = re.sub(r'versionName\s+"[^"]+"', 'versionName "10.18.28"', g)
gradle.write_text(g, encoding='utf-8')

print('Applied v10.18.28b structural clock/PT/OneUI mascot fix')

from pathlib import Path
import re

root = Path('extracted')
app = root / 'app/src/main/java/com/maeummon/app'
layout_dir = root / 'app/src/main/res/layout'
gradle = root / 'app/build.gradle'

# -----------------------------------------------------------------------------
# v10.18.28 - structural fix based on the final rendered One UI screenshots.
# 1) Clock: fixed-width time rows overflow narrow launcher cells. Make the row fluid.
# 2) PT: never let a long exercise be physically clipped mid-thought. Use a layout-safe
#    complete-clause fitter and give the bubble more horizontal room.
# 3) Mascot: SystemUI noise must not permanently mark HOME as blocked; when the
#    accessibility classifier is UNKNOWN, fall back to launcher package detection.
# -----------------------------------------------------------------------------

# 1) CLOCK LAYOUT ---------------------------------------------------------------
# The classic clock/large layouts used fixed 250dp/230dp time bitmaps inside a
# wrap_content row. Together with moon + sparkle this can exceed the actual Samsung
# launcher cell width, clipping the final minute digit. Convert those rows to fluid width.
for name, old_width in [('widget_maeummon_clock.xml', '250dp'), ('widget_maeummon_large.xml', '230dp')]:
    path = layout_dir / name
    t = path.read_text(encoding='utf-8')

    # timeWrap must consume the available widget width instead of requesting its own width.
    marker = '<LinearLayout android:id="@+id/timeWrap" android:layout_width="wrap_content"'
    if marker in t:
        t = t.replace(marker, '<LinearLayout android:id="@+id/timeWrap" android:layout_width="match_parent"', 1)

    # The horizontal child row should also be fluid.
    child = '<LinearLayout android:layout_width="wrap_content" android:layout_height="wrap_content" android:gravity="center_vertical" android:orientation="horizontal">'
    if child in t:
        t = t.replace(child, '<LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content" android:gravity="center_vertical" android:orientation="horizontal">', 1)

    # Time image takes whatever space remains between moon and sparkle.
    old = f'<ImageView android:id="@+id/widgetTimeBitmap" android:layout_width="{old_width}"'
    new = '<ImageView android:id="@+id/widgetTimeBitmap" android:layout_width="0dp" android:layout_weight="1"'
    if old not in t:
        raise SystemExit(f'v10.18.28: fixed time bitmap anchor missing in {name}')
    t = t.replace(old, new, 1)

    # Slightly reduce horizontal padding so small launcher resizes still have safe headroom.
    if name == 'widget_maeummon_clock.xml':
        t = t.replace('android:paddingLeft="22dp"', 'android:paddingLeft="12dp"', 1)
        t = t.replace('android:paddingRight="22dp"', 'android:paddingRight="12dp"', 1)
    else:
        t = t.replace('android:paddingLeft="30dp"', 'android:paddingLeft="16dp"', 1)
        t = t.replace('android:paddingRight="30dp"', 'android:paddingRight="16dp"', 1)

    path.write_text(t, encoding='utf-8')

# 2) PT MESSAGE -----------------------------------------------------------------
widget = app / 'MaeumMonClockWidget.java'
w = widget.read_text(encoding='utf-8')

# Replace the current 100/120/140 caps + shared compact call with a complete-clause
# fitter sized to what each physical layout can actually show.
pat = re.compile(r'''        int widgetMaxChars = \(layout == R\.layout\.widget_maeummon_medium\) \? \d+
                : \(layout == R\.layout\.widget_maeummon_clock\) \? \d+
                : \(layout == R\.layout\.widget_maeummon_large\) \? \d+
                : \(layout == R\.layout\.widget_maeummon_narrow\) \? \d+
                : \d+;
        line = TherapySurfacePolicyV501\.compactWidgetText\(line, \d+\);''')
replacement = '''        // v10.18.28: fit to the *physical* bubble, not an arbitrary large source cap.
        // A shorter complete thought is better than showing a longer sentence cut at the bottom.
        int widgetMaxChars = (layout == R.layout.widget_maeummon_medium) ? 52
                : (layout == R.layout.widget_maeummon_clock) ? 58
                : (layout == R.layout.widget_maeummon_large) ? 66
                : (layout == R.layout.widget_maeummon_narrow) ? 50
                : 42;
        line = fitWidgetMessage(line, widgetMaxChars);'''
w, n = pat.subn(replacement, w, count=1)
if n != 1:
    raise SystemExit('v10.18.28: widget message cap block missing')

# Add a local fitter before scheduleNextUpdate. It never emits an ellipsis and never
# ends on a dangling comma/connector. Prefer a full sentence, then a complete clause.
anchor = '    private static void scheduleNextUpdate(Context context) {'
if anchor not in w:
    raise SystemExit('v10.18.28: scheduleNextUpdate anchor missing')
helper = r'''    private static String fitWidgetMessage(String raw, int maxChars) {
        if (raw == null) return "";
        String s = raw.replace('\n', ' ').replace('\r', ' ').replaceAll("\\s+", " ").trim();
        if (s.length() <= maxChars) return s;

        int hard = Math.min(maxChars, s.length());
        int bestSentence = -1;
        int bestClause = -1;
        for (int i = 12; i < hard; i++) {
            char ch = s.charAt(i);
            if (ch == '.' || ch == '!' || ch == '?' || ch == '。' || ch == '！' || ch == '？') {
                bestSentence = i + 1;
            } else if (ch == ',' || ch == '·' || ch == ';' || ch == '，') {
                bestClause = i;
            }
        }
        if (bestSentence >= Math.min(24, hard)) return s.substring(0, bestSentence).trim();

        int cut = bestClause >= Math.min(22, hard) ? bestClause : s.lastIndexOf(' ', hard);
        if (cut < Math.min(22, hard)) cut = hard;
        String out = s.substring(0, cut).trim();
        while (out.endsWith(",") || out.endsWith("·") || out.endsWith(";") || out.endsWith("，")) {
            out = out.substring(0, out.length() - 1).trim();
        }
        if (!(out.endsWith(".") || out.endsWith("!") || out.endsWith("?") || out.endsWith("다") || out.endsWith("요") || out.endsWith("해") || out.endsWith("자"))) {
            out += ".";
        }
        return out;
    }

'''
w = w.replace(anchor, helper + anchor, 1)
widget.write_text(w, encoding='utf-8')

# Bubble geometry: widen content area, use a slightly smaller readable font, and cap
# lines below the physical height so Samsung RemoteViews never crops the final baseline.
layout_specs = {
    'widget_maeummon_clock.xml': {'start_old': 'android:layout_marginStart="96dp"', 'start_new': 'android:layout_marginStart="76dp"', 'size_old': 'android:textSize="12sp"', 'size_new': 'android:textSize="11sp"'},
    'widget_maeummon_large.xml': {'start_old': 'android:layout_marginStart="126dp"', 'start_new': 'android:layout_marginStart="100dp"', 'size_old': 'android:textSize="16sp"', 'size_new': 'android:textSize="14sp"'},
    'widget_maeummon_medium.xml': {'start_old': 'android:layout_marginStart="66dp"', 'start_new': 'android:layout_marginStart="60dp"', 'size_old': 'android:textSize="10sp"', 'size_new': 'android:textSize="9sp"'},
    'widget_maeummon_narrow.xml': {'start_old': 'android:layout_marginStart="66dp"', 'start_new': 'android:layout_marginStart="58dp"', 'size_old': 'android:textSize="10sp"', 'size_new': 'android:textSize="9sp"'},
}
for name, spec in layout_specs.items():
    path = layout_dir / name
    t = path.read_text(encoding='utf-8')
    if spec['start_old'] in t:
        t = t.replace(spec['start_old'], spec['start_new'], 1)
    if spec['size_old'] in t:
        t = t.replace(spec['size_old'], spec['size_new'], 1)
    # v10.18.27 used maxLines=6. Five safe lines + complete-thought fitting avoids crop.
    t = t.replace('android:maxLines="6"', 'android:maxLines="5"', 1)
    # Keep Android from inventing an ellipsis.
    t = re.sub(r'\s+android:ellipsize="[^"]+"', '', t)
    path.write_text(t, encoding='utf-8')

# 3) MASCOT / HOME CLASSIFICATION ----------------------------------------------
access = app / 'LauncherSurfaceAccessibilityService.java'
a = access.read_text(encoding='utf-8')
blocked_systemui = '''        if (lowerPkg.contains("systemui")) {
            // Notification shade / quick settings / recents are not the launcher home surface.
            // If SystemUI owns the active root, hide immediately instead of preserving stale HOME.
            saveMode(MODE_BLOCKED);
            return;
        }'''
safe_systemui = '''        if (lowerPkg.contains("systemui")) {
            // v10.18.28: ordinary One UI status/navigation events must not erase a valid HOME.
            // Only explicit Recents/Overview evidence blocks the mascot.
            if (cls.contains("recents") || cls.contains("overview") || info.hasRecentKeyword) {
                saveMode(MODE_BLOCKED);
            }
            return;
        }'''
if blocked_systemui not in a:
    raise SystemExit('v10.18.28: SystemUI classifier block missing')
a = a.replace(blocked_systemui, safe_systemui, 1)
access.write_text(a, encoding='utf-8')

overlay = app / 'OverlayService.java'
o = overlay.read_text(encoding='utf-8')
old_enabled = '''            if (LauncherSurfaceAccessibilityService.isEnabled(OverlayService.this)) {
                // 접근성 서비스가 켜져 있으면 active-window 판정을 단일 source로 사용한다.
                // UsageStats와 섞으면 홈/최근앱 전환 순간 서로 다른 값을 내서 깜빡일 수 있다.
                String surfaceMode = getSharedPreferences(AppPrefs.PREFS, MODE_PRIVATE)
                        .getString(LauncherSurfaceAccessibilityService.PREF_MODE,
                                LauncherSurfaceAccessibilityService.MODE_UNKNOWN);
                home = LauncherSurfaceAccessibilityService.MODE_HOME.equals(surfaceMode);
            } else {'''
new_enabled = '''            if (LauncherSurfaceAccessibilityService.isEnabled(OverlayService.this)) {
                String surfaceMode = getSharedPreferences(AppPrefs.PREFS, MODE_PRIVATE)
                        .getString(LauncherSurfaceAccessibilityService.PREF_MODE,
                                LauncherSurfaceAccessibilityService.MODE_UNKNOWN);
                if (LauncherSurfaceAccessibilityService.MODE_HOME.equals(surfaceMode)) {
                    home = true;
                } else if (LauncherSurfaceAccessibilityService.MODE_BLOCKED.equals(surfaceMode)) {
                    home = false;
                } else {
                    // v10.18.28: an enabled accessibility service can still be UNKNOWN after
                    // reinstall/restart. Fall back instead of making the mascot disappear forever.
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
if old_enabled not in o:
    raise SystemExit('v10.18.28: enabled accessibility branch missing')
o = o.replace(old_enabled, new_enabled, 1)
overlay.write_text(o, encoding='utf-8')

# Version bump.
g = gradle.read_text(encoding='utf-8')
g = re.sub(r'versionCode\s+\d+', 'versionCode 101828', g)
g = re.sub(r'versionName\s+"[^"]+"', 'versionName "10.18.28"', g)
gradle.write_text(g, encoding='utf-8')

print('Applied v10.18.28 structural clock/PT/OneUI mascot fix')

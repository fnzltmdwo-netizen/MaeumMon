from pathlib import Path
import re

root = Path('extracted')
app = root / 'app/src/main/java/com/maeummon/app'
live = app / 'LiveMindManager.java'
profile = app / 'UnifiedTherapyProfile.java'
pt = app / 'MindPtActivity.java'
shared = app / 'SharedCounselingLinkActivity.java'
central = app / 'CentralMindPtState.java'
overlay = app / 'OverlayService.java'
gradle = root / 'app/build.gradle'

# 1) Make the currently selected PT part of LiveMindManager's canonical context/hash.
text = live.read_text(encoding='utf-8')
anchor = '        StringBuilder sb = new StringBuilder();\n'
if anchor not in text:
    raise SystemExit('v10.18.12: LiveMindManager recentContext anchor missing')
insert = '''        StringBuilder sb = new StringBuilder();\n        CentralMindPtState.Snapshot activePt = CentralMindPtState.current(c);\n        if (activePt.active) {\n            sb.append("[현재 선택된 마음 PT / 앱 전체 공통]\\n");\n            sb.append("모드: ").append(CentralMindPtState.modeLabel(activePt.mode)).append("\\n");\n            sb.append("힘: ").append(activePt.muscle).append("\\n");\n            if (!activePt.exercise.isEmpty()) sb.append("오늘 연습: ").append(activePt.exercise).append("\\n");\n            if (!activePt.criterion.isEmpty()) sb.append("성공 기준: ").append(activePt.criterion).append("\\n");\n            sb.append("이 PT가 하루 편지·해주고 싶은 말·다마고치·위젯·내 방에서 공통으로 우선된다.\\n\\n");\n        }\n'''
text = text.replace(anchor, insert, 1)
# local fallback words should also follow active PT before legacy formulation practice.
old = '        String shared = UnifiedTherapyProfile.mascotLine(c);'
new = '        String shared = CentralMindPtState.mascotLine(c);\n        if (shared.isEmpty()) shared = UnifiedTherapyProfile.mascotLine(c);'
if old not in text:
    raise SystemExit('v10.18.12: localWords shared anchor missing')
text = text.replace(old, new, 1)
live.write_text(text, encoding='utf-8')

# 2) Unified profile helper should prefer current PT, so local daily-letter fallback and other surfaces sync too.
text = profile.read_text(encoding='utf-8')
pat = re.compile(r'    public static String currentPractice\(Context c\) \{\n        JSONObject p = TherapyMemoryManager\.getProfile\(c\);\n        return first\(p, "experiment", "effective_intervention", "reframe"\);\n    \}')
rep = '''    public static String currentPractice(Context c) {\n        CentralMindPtState.Snapshot s = CentralMindPtState.current(c);\n        if (s.active) {\n            if (!s.exercise.isEmpty()) return s.exercise;\n            if (!s.muscle.isEmpty()) return s.muscle;\n        }\n        JSONObject p = TherapyMemoryManager.getProfile(c);\n        return first(p, "experiment", "effective_intervention", "reframe");\n    }'''
text, n = pat.subn(rep, text, count=1)
if n != 1:
    raise SystemExit('v10.18.12: UnifiedTherapyProfile currentPractice anchor missing')
profile.write_text(text, encoding='utf-8')

# 3) Any PT selection / new one-off PT / outcome advance invalidates letter+words cache immediately.
text = pt.read_text(encoding='utf-8')
count = text.count('        MaeumMonClockWidget.refreshAll(this);')
if count < 3:
    raise SystemExit(f'v10.18.12: expected >=3 MindPt widget refresh anchors, got {count}')
text = text.replace('        MaeumMonClockWidget.refreshAll(this);',
                    '        LiveMindManager.onMindChanged(this);\n        MaeumMonClockWidget.refreshAll(this);')
pt.write_text(text, encoding='utf-8')

# Counseling import/reanalysis can also change active PT/programs: invalidate all downstream live surfaces.
text = shared.read_text(encoding='utf-8')
text = text.replace('MaeumMonClockWidget.refreshAll(this);',
                    'LiveMindManager.onMindChanged(this); MaeumMonClockWidget.refreshAll(this);')
shared.write_text(text, encoding='utf-8')

# 4) Mascot: never cut a Korean sentence in the middle with an ellipsis.
text = central.read_text(encoding='utf-8')
start = text.find('    public static String mascotLine(Context context) {')
end = text.find('    public static String roomSummary(Context context) {', start)
if start < 0 or end < 0:
    raise SystemExit('v10.18.12: CentralMindPtState mascotLine anchors missing')
new_method = '''    public static String mascotLine(Context context) {\n        Snapshot s = current(context);\n        if (!s.active) return "";\n        String action = s.exercise.isEmpty() ? s.rationale : s.exercise;\n        String one = firstCompleteThought(action, 118);\n        if ("RECOVERY".equals(s.mode)) return "승재야, 오늘은 더 버티기보다 회복을 고르는 날이야. " + one;\n        if ("STABILIZE".equals(s.mode)) return "지금은 서두르지 말고 오늘 정한 연습 하나만 해보자. " + one;\n        if ("REVIEW".equals(s.mode)) return "오늘은 잘잘못보다 다음에 알아차릴 신호 하나만 찾으면 돼. " + one;\n        if ("MAINTENANCE".equals(s.mode)) return "이미 조금씩 네 힘이 된 부분이야. 오늘도 가볍게 한 번 써보자. " + one;\n        if (!one.isEmpty()) return "오늘 PT는 ‘" + compact(s.muscle, 26) + "’. " + one;\n        return "오늘 PT는 ‘" + compact(s.muscle, 30) + "’. 이 힘을 한 번 써보자.";\n    }\n\n    private static String firstCompleteThought(String s, int max) {\n        if (s == null) return "";\n        String clean = s.replace('\\n', ' ').replace('\\r', ' ').replaceAll("\\\\s+", " ").trim();\n        if (clean.isEmpty()) return "";\n        int hard = Math.min(clean.length(), max);\n        int best = -1;\n        for (int i = 0; i < hard; i++) {\n            char ch = clean.charAt(i);\n            if ((ch == '.' || ch == '!' || ch == '?' || ch == '。' || ch == '！' || ch == '？') && i >= 18) {\n                best = i + 1;\n                break;\n            }\n        }\n        if (best > 0) return clean.substring(0, best).trim();\n        if (clean.length() <= max) return clean;\n        int cut = clean.lastIndexOf(' ', hard);\n        if (cut < 24) cut = hard;\n        String out = clean.substring(0, cut).trim();\n        if (!(out.endsWith(".") || out.endsWith("!") || out.endsWith("?") || out.endsWith("다") || out.endsWith("요"))) out += ".";\n        return out;\n    }\n\n'''
text = text[:start] + new_method + text[end:]
central.write_text(text, encoding='utf-8')

# 5) Give mascot bubble more width; height remains wrap_content so complete thought can show naturally.
text = overlay.read_text(encoding='utf-8')
text, n1 = re.subn(r'root\.addView\(speech, new LinearLayout\.LayoutParams\(dp\(196\), LinearLayout\.LayoutParams\.WRAP_CONTENT\)\);',
                   'root.addView(speech, new LinearLayout.LayoutParams(dp(232), LinearLayout.LayoutParams.WRAP_CONTENT));', text, count=1)
text, n2 = re.subn(r'params = new WindowManager\.LayoutParams\(\n\s*dp\(212\),',
                   'params = new WindowManager.LayoutParams(\n                dp(248),', text, count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit(f'v10.18.12: overlay size anchors missing {n1}/{n2}')
overlay.write_text(text, encoding='utf-8')

# Version bump.
g = gradle.read_text(encoding='utf-8')
g, n1 = re.subn(r'versionCode\s+\d+', 'versionCode 101812', g, count=1)
g, n2 = re.subn(r'versionName\s+"[^"]+"', 'versionName "10.18.12"', g, count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit('v10.18.12: gradle version anchor missing')
gradle.write_text(g, encoding='utf-8')

print('Applied v10.18.12 unified PT sync + natural mascot bubble')

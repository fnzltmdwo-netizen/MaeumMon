from pathlib import Path
import re

root = Path('extracted')
app = root / 'app/src/main/java/com/maeummon/app'
gradle = root / 'app/build.gradle'

# -----------------------------------------------------------------------------
# v10.18.29 - corpus-distilled warm/clear PT surface
# Keep internal PT mechanics, but make the visible experience feel like a counselor
# guiding one small practice at a time. The rules below are distilled from the RC7
# counseling corpus/operating policy already used by MaeumMon: understand first,
# compress to one core sentence, link to the maintenance mechanism, then give the
# smallest observable intervention and review the outcome.
# -----------------------------------------------------------------------------

presenter = app / 'OhStylePtDisplay.java'
presenter.write_text(r'''package com.maeummon.app;

/**
 * User-facing PT language adapter.
 * Internal DB axes stay intact; only the surface is translated into short everyday Korean.
 */
public final class OhStylePtDisplay {
    private OhStylePtDisplay() {}

    public static String title(String muscle, String exercise) {
        String m = clean(muscle);
        String e = clean(exercise);
        String all = (m + " " + e).toLowerCase(java.util.Locale.KOREA);
        if (has(all, "관계 신호", "판단 유예", "사실과 해석", "사실/해석", "거절 신호"))
            return "답이 없다고 바로 나쁜 뜻으로 정하지 않는 연습";
        if (has(all, "확인행동", "재확인", "확인 행동", "계속 확인"))
            return "불안하다고 계속 확인하지 않는 연습";
        if (has(all, "대인관계 에너지", "접촉량", "사회적 접촉", "에너지 조절"))
            return "사람에게 맞추느라 내가 다 닳지 않는 연습";
        if (has(all, "경계", "거절", "싫다고", "부탁을 거절"))
            return "싫은 건 작게 말하고도 관계를 지켜보는 연습";
        if (has(all, "불확실", "애매함", "모르는 상태"))
            return "모르는 걸 바로 결론내리지 않고 두는 연습";
        if (has(all, "트라우마", "과거 기억", "과거 사건", "재경험"))
            return "예전 일에 다시 휩쓸릴 때 지금의 나를 지키는 연습";
        if (has(all, "충동", "결정 보류", "24시간", "차단", "손절"))
            return "불안할 때 큰 결정을 바로 하지 않는 연습";
        if (has(all, "자기 가치", "내 가치", "비교", "소속"))
            return "상대 반응 때문에 내 가치까지 흔들지 않는 연습";
        if (has(all, "감정 표현", "상태 전달", "욕구", "요청"))
            return "내 상태와 필요한 걸 짧게 말해보는 연습";

        String base = m;
        base = base.replace("을 다루는 힘", "").replace("를 다루는 힘", "")
                .replace("하는 힘", "").replace("힘", "").trim();
        base = base.replace("조절력", "").replace("회복력", "").replace("유예력", "")
                .replace("내성", "").replace("강화", "").trim();
        if (base.isEmpty()) base = firstClause(e, 30);
        if (base.isEmpty()) return "오늘 마음을 조금 다르게 다뤄보는 연습";
        if (base.endsWith("연습")) return base;
        return base + " 연습";
    }

    public static String why(String raw) {
        String s = clean(raw);
        if (s.isEmpty()) return "이 반응이 자꾸 반복돼서, 오늘은 한 군데만 작게 바꿔보는 거야.";
        s = easyWords(s);
        String out = firstSentence(s, 92);
        if (out.isEmpty()) out = firstClause(s, 82);
        return out;
    }

    public static String action(String raw) {
        String s = clean(raw);
        if (s.isEmpty()) return "오늘 비슷한 장면 하나에서 평소와 다른 행동을 한 번만 해보자.";
        s = easyWords(s);
        String out = firstSentence(s, 92);
        if (out.isEmpty()) out = firstClause(s, 84);
        return out;
    }

    public static String success(String raw) {
        String s = clean(raw);
        if (s.isEmpty()) return "한 번이라도 평소와 다르게 해봤으면 성공이야.";
        s = easyWords(s)
                .replace("성공 기준은", "")
                .replace("성공 기준:", "")
                .trim();
        String out = firstSentence(s, 84);
        if (out.isEmpty()) out = firstClause(s, 76);
        if (!out.endsWith(".") && !out.endsWith("!") && !out.endsWith("?") && !out.endsWith("야") && !out.endsWith("해")) out += ".";
        return out;
    }

    public static String mascot(String muscle, String exercise) {
        String a = action(exercise);
        if (a.length() > 70) a = firstClause(a, 66);
        return "우리 오늘은 이것만 해보자. " + a;
    }

    private static String easyWords(String s) {
        return s
                .replace("유지기제", "반복되는 흐름")
                .replace("가치판단", "내가 붙인 판단")
                .replace("자동적 관계 위험 판단", "관계가 나빠졌다는 빠른 결론")
                .replace("인지 왜곡", "생각이 한쪽으로 쏠리는 것")
                .replace("판단 유예", "결론을 잠깐 미루기")
                .replace("불확실성", "모르는 상태")
                .replace("재확인", "다시 확인")
                .replace("일반화", "다른 비슷한 상황에서도 써보기")
                .replace("자기 가치", "내 가치")
                .replace("대인관계", "사람 관계")
                .replace("사회적 접촉", "사람 만나기")
                .replace("완화", "조금 낮추기")
                .replace("조절", "다루기");
    }

    private static boolean has(String s, String... keys) {
        for (String k : keys) if (s.contains(k.toLowerCase(java.util.Locale.KOREA))) return true;
        return false;
    }

    private static String clean(String s) {
        if (s == null) return "";
        return s.replace('\n', ' ').replace('\r', ' ').replaceAll("\\s+", " ").trim();
    }

    private static String firstSentence(String s, int max) {
        if (s.isEmpty()) return "";
        int hard = Math.min(max, s.length());
        int best = -1;
        for (int i = 0; i < hard; i++) {
            char ch = s.charAt(i);
            if (ch == '.' || ch == '!' || ch == '?' || ch == '。' || ch == '！' || ch == '？') { best = i + 1; break; }
        }
        if (best > 0) return s.substring(0, best).trim();
        return "";
    }

    private static String firstClause(String s, int max) {
        if (s.isEmpty()) return "";
        if (s.length() <= max) return s;
        int hard = Math.min(max, s.length());
        int cut = -1;
        char[] stops = new char[]{',', '·', ';', '，'};
        for (int i = 18; i < hard; i++) {
            char ch = s.charAt(i);
            for (char stop : stops) if (ch == stop) cut = i;
        }
        if (cut < 18) cut = s.lastIndexOf(' ', hard);
        if (cut < 18) cut = hard;
        return s.substring(0, cut).trim();
    }
}
''', encoding='utf-8')

# -----------------------------------------------------------------------------
# 1) PT GENERATION: inject corpus-distilled style policy into model-facing analyzers.
# -----------------------------------------------------------------------------
analyzer = app / 'CounselingProgramAnalyzer.java'
a = analyzer.read_text(encoding='utf-8')

if 'private static String ohStylePtRules()' not in a:
    anchor = '    private static void normalizeDisplayMuscleNames(Analysis analysis) {'
    if anchor not in a:
        raise SystemExit('v10.18.29: analyzer normalization anchor missing')
    rules = r'''    private static String ohStylePtRules() {
        return " [RC7 상담사례에서 압축한 마음 PT 운영규칙] " +
                "훈련을 만들기 전에 먼저 사용자가 왜 그렇게 반응했는지 한 문장으로 이해 가능하게 재정의한다. " +
                "전문가가 사례기록을 쓰듯 설명하지 말고, 사용자가 읽고 '아 그래서 내가 그랬구나'가 먼저 와야 한다. " +
                "한 PT의 사용자 표면은 왜 내가 이러는지 1~2문장, 오늘 바꿀 것 딱 하나, 바로 해볼 행동 하나, 최소 성공기준 하나로 만든다. " +
                "첫 단계는 오늘 한 장면에서 한 번 해보면 판정 가능한 최소유효강도여야 한다. 불안 0, 완벽한 감정조절, 장기간 반복을 성공기준으로 쓰지 않는다. " +
                "exercise_text는 언제 어떤 신호가 왔을 때 무엇을 할지를 생활말 1~2문장으로 쓴다. 한 단계에 행동을 여러 개 몰아넣지 않는다. " +
                "success_criterion은 '불안해도 이 행동을 한 번 했다'처럼 관찰 가능한 최소 성공으로 쓴다. " +
                "rationale은 유지기제를 설명하되 유지기제, 인지왜곡, 불확실성 내성, 가치판단 분리 같은 전문표현을 사용자에게 그대로 던지지 말고 일상어로 번역한다. " +
                "muscle_name은 내부 축을 구분할 수 있게 유지하되 사용자에게 보였을 때 검사명·치료계획서처럼 들리는 '조절력/회복력/유예력/내성/강화/전문' 표현을 피한다. " +
                "가능하면 '답이 없다고 바로 나쁜 뜻으로 정하지 않는 연습', '불안하다고 계속 확인하지 않는 연습', '싫은 건 작게 말해보는 연습'처럼 실제 변화가 보이는 이름을 쓴다. " +
                "여러 단계가 필요해도 모델은 내부적으로만 단계의 길을 설계하고, 각 단계 자체는 한 번에 하나의 핵심 행동만 갖게 한다. " +
                "사용자가 이전 해석을 정정했다면 현재 설명을 우선하고 과거 가설을 되살리지 않는다. " +
                "개입은 현재 formulation의 유지기제와 연결하고 가장 작은 유효 강도부터 시작한다. HELPED/PARTIAL/NO_CHANGE/WORSE 결과에 따라 같은 숙제를 기계적으로 반복하지 않는다. ";
    }

'''
    a = a.replace(anchor, rules + anchor, 1)

# Main synthesis.
a = a.replace('callResponses(apiKey, chosenModel, synthesisSystem, synthesisUser, 3000)',
              'callResponses(apiKey, chosenModel, synthesisSystem + ohStylePtRules(), synthesisUser, 3000)')
# Incremental analyzer.
a = a.replace('callResponses(apiKey, chosenModel, system, user, 2600)',
              'callResponses(apiKey, chosenModel, system + ohStylePtRules(), user, 2600)')
# Coverage-gap structured output.
a = a.replace('callResponsesJson(apiKey, chosenModel, system +\n                " programs는 최대 2개, 각 steps는 최대 3개로 제한하고 JSON을 반드시 끝까지 완결한다.",',
              'callResponsesJson(apiKey, chosenModel, system + ohStylePtRules() +\n                " programs는 최대 2개, 각 steps는 최대 3개로 제한하고 JSON을 반드시 끝까지 완결한다.",')
# Step refinement structured output.
a = a.replace('callResponsesJson(apiKey, chosenModel, system +\n                " programs는 현재 PT 개수를 넘지 말고 각 steps는 최대 3개로 제한하며, 긴 설명도 반드시 완결된 문자열로 끝낸다.",',
              'callResponsesJson(apiKey, chosenModel, system + ohStylePtRules() +\n                " programs는 현재 PT 개수를 넘지 말고 각 steps는 최대 3개로 제한하며, 긴 설명도 반드시 완결된 문자열로 끝낸다.",')
# Secondary editors.
a = a.replace('callResponses(apiKey, model, system, user, 3400)',
              'callResponses(apiKey, model, system + ohStylePtRules(), user, 3400)')
a = a.replace('callResponses(apiKey, model, system, user, 3600)',
              'callResponses(apiKey, model, system + ohStylePtRules(), user, 3600)')
# Any remaining final-program style calls using chosenModel/system are also translated.
a = a.replace('callResponses(apiKey, chosenModel, system, user, 3400)',
              'callResponses(apiKey, chosenModel, system + ohStylePtRules(), user, 3400)')

analyzer.write_text(a, encoding='utf-8')

# -----------------------------------------------------------------------------
# 2) MIND PT SCREEN: concise surface for both old and newly generated PTs.
# -----------------------------------------------------------------------------
activity = app / 'MindPtActivity.java'
m = activity.read_text(encoding='utf-8')

m = m.replace('text.append(p.muscleName).append("\\n\\n");',
              'text.append(OhStylePtDisplay.title(p.muscleName, "")).append("\\n\\n");')
m = m.replace('String reason = friendlyReason(p.reason);',
              'String reason = OhStylePtDisplay.why(p.reason);')
m = m.replace('text.append("\\n\\n🧩 왜 이 PT가 생겼어?\\n").append(reason);',
              'text.append("\\n\\n💛 왜 이 연습이 필요해?\\n").append(reason);')

m = m.replace('muscleText.setText(s.muscle);',
              'muscleText.setText(OhStylePtDisplay.title(s.muscle, s.exercise));')
m = m.replace('exerciseText.setText(s.exercise);',
              'exerciseText.setText(OhStylePtDisplay.action(s.exercise));')
m = m.replace('criterionText.setText(s.criterion);',
              'criterionText.setText(OhStylePtDisplay.success(s.criterion));')
m = m.replace('rationaleText.setText(friendlyRationale(s.rationale));',
              'rationaleText.setText(OhStylePtDisplay.why(s.rationale));')

m = m.replace('muscleText.setText(r.muscleName);',
              'muscleText.setText(OhStylePtDisplay.title(r.muscleName, r.exerciseText));')
m = m.replace('exerciseText.setText(r.exerciseText);',
              'exerciseText.setText(OhStylePtDisplay.action(r.exerciseText));')
m = m.replace('criterionText.setText(r.successCriterion);',
              'criterionText.setText(OhStylePtDisplay.success(r.successCriterion));')
m = m.replace('rationaleText.setText(friendlyRationale(r.rationale));',
              'rationaleText.setText(OhStylePtDisplay.why(r.rationale));')

# Long roadmap made the page read like a workbook. Keep it internally but hide it on the default surface.
old_bind = '''        roadmapLabel.setVisibility(View.VISIBLE);\n        roadmapText.setVisibility(View.VISIBLE);\n        roadmapText.setText(roadmap);'''
new_bind = '''        // v10.18.29: the full curriculum remains in DB but the default PT surface shows only today's step.\n        roadmapLabel.setVisibility(View.GONE);\n        roadmapText.setVisibility(View.GONE);'''
if old_bind in m:
    m = m.replace(old_bind, new_bind, 1)

# Friendly reason/rationale methods are now short adapters rather than full stored prose.
m = re.sub(r'''    private String friendlyReason\(String reason\) \{.*?\n    \}''',
           '''    private String friendlyReason(String reason) {\n        return OhStylePtDisplay.why(reason);\n    }''', m, count=1, flags=re.S)
m = re.sub(r'''    private String friendlyRationale\(String rationale\) \{.*?\n    \}''',
           '''    private String friendlyRationale(String rationale) {\n        return OhStylePtDisplay.why(rationale);\n    }''', m, count=1, flags=re.S)

activity.write_text(m, encoding='utf-8')

# -----------------------------------------------------------------------------
# 3) CENTRAL PT: widget / mascot / room use the same translated language.
# -----------------------------------------------------------------------------
central = app / 'CentralMindPtState.java'
c = central.read_text(encoding='utf-8')

start = c.find('    public static String compactWidgetLine(Context context) {')
end = c.find('    public static String mascotLine(Context context) {', start)
if start >= 0 and end > start:
    c = c[:start] + r'''    public static String compactWidgetLine(Context context) {
        Snapshot s = current(context);
        if (!s.active) return "";
        String title = OhStylePtDisplay.title(s.muscle, s.exercise);
        String action = OhStylePtDisplay.action(s.exercise.isEmpty() ? s.rationale : s.exercise);
        if ("RECOVERY".equals(s.mode)) return "오늘은 쉬어가는 연습 · " + action;
        if ("STABILIZE".equals(s.mode)) return "지금은 이것만 · " + action;
        return title + " · " + action;
    }

''' + c[end:]

start = c.find('    public static String mascotLine(Context context) {')
end = c.find('    private static String completeThoughts(', start)
if start >= 0 and end > start:
    c = c[:start] + r'''    public static String mascotLine(Context context) {
        Snapshot s = current(context);
        if (!s.active) return "";
        String action = s.exercise.isEmpty() ? s.rationale : s.exercise;
        if ("RECOVERY".equals(s.mode)) return "우리 오늘은 더 버티지 말고 쉬어가자.";
        if ("STABILIZE".equals(s.mode)) return "우리 서두르지 말고 이것부터 해보자. " + OhStylePtDisplay.action(action);
        if ("REVIEW".equals(s.mode)) return "우리 잘잘못 말고, 다음에 알아차릴 것 하나만 보자.";
        return OhStylePtDisplay.mascot(s.muscle, action);
    }

''' + c[end:]

c = c.replace('return modeLabel(s.mode) + "\\n🌱 " + s.muscle + "\\n🏋️ " + s.exercise;',
              'return modeLabel(s.mode) + "\\n🌱 " + OhStylePtDisplay.title(s.muscle, s.exercise) + "\\n🏋️ " + OhStylePtDisplay.action(s.exercise);')
central.write_text(c, encoding='utf-8')

# MascotWidgetPrefs can be a direct widget source on some layouts/settings.
prefs = app / 'MascotWidgetPrefs.java'
if prefs.exists():
    p = prefs.read_text(encoding='utf-8')
    p = p.replace('return "오늘의 PT · " + s.muscle;',
                  'return OhStylePtDisplay.title(s.muscle, s.exercise);')
    p = p.replace('return "오늘의 PT · " + s.muscle + "\\n" + ex;',
                  'return OhStylePtDisplay.title(s.muscle, s.exercise) + "\\n" + OhStylePtDisplay.action(ex);')
    prefs.write_text(p, encoding='utf-8')

# Version bump.
g = gradle.read_text(encoding='utf-8')
g = re.sub(r'versionCode\s+\d+', 'versionCode 101829', g)
g = re.sub(r'versionName\s+"[^"]+"', 'versionName "10.18.29"', g)
gradle.write_text(g, encoding='utf-8')

print('Applied v10.18.29 corpus-distilled warm/clear Mind PT')

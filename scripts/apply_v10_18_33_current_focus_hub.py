from pathlib import Path
import re

root = Path('extracted')
app = root / 'app/src/main/java/com/maeummon/app'
gradle = root / 'app/build.gradle'

# v10.18.33
# One shared CURRENT_FOCUS for the whole app:
# heart = current core meaning, brain = repeated flow, sprout = today's one action.
# PT, widget, mascot and room should never invent separate priorities.

focus = app / 'CurrentCounselingFocus.java'
focus.write_text(r'''package com.maeummon.app;

import android.content.Context;
import android.content.SharedPreferences;

/**
 * Single user-facing counseling focus shared by every surface.
 * This is intentionally tiny: one core understanding, one repeated flow, one next action.
 */
public final class CurrentCounselingFocus {
    private CurrentCounselingFocus() {}
    private static final String PREF = "maeummon_current_focus_v1";
    private static final String K_CORE = "core";
    private static final String K_FLOW = "flow";
    private static final String K_ACTION = "action";
    private static final String K_SOURCE = "source";
    private static final String K_UPDATED = "updated";

    public static final class Snapshot {
        public final String core, flow, action, source;
        public final long updatedAt;
        Snapshot(String core, String flow, String action, String source, long updatedAt) {
            this.core = clean(core); this.flow = clean(flow); this.action = clean(action);
            this.source = clean(source); this.updatedAt = updatedAt;
        }
        public boolean isEmpty() { return core.isEmpty() && flow.isEmpty() && action.isEmpty(); }
    }

    public static Snapshot read(Context c) {
        SharedPreferences p = c.getSharedPreferences(PREF, Context.MODE_PRIVATE);
        return new Snapshot(p.getString(K_CORE, ""), p.getString(K_FLOW, ""),
                p.getString(K_ACTION, ""), p.getString(K_SOURCE, ""), p.getLong(K_UPDATED, 0L));
    }

    public static void save(Context c, String core, String flow, String action, String source) {
        String cc = clean(core), ff = clean(flow), aa = clean(action);
        if (cc.isEmpty() && ff.isEmpty() && aa.isEmpty()) return;
        c.getSharedPreferences(PREF, Context.MODE_PRIVATE).edit()
                .putString(K_CORE, cc).putString(K_FLOW, ff).putString(K_ACTION, aa)
                .putString(K_SOURCE, clean(source)).putLong(K_UPDATED, System.currentTimeMillis()).apply();
    }

    /** Refresh the shared focus from the currently selected PT after counseling has chosen it. */
    public static void updateFromPt(Context c, String muscle, String rationale, String exercise) {
        String title = OhStylePtDisplay.title(muscle, exercise);
        String why = OhStylePtDisplay.why(rationale);
        String action = OhStylePtDisplay.action(exercise);
        String flow;
        String all = (clean(muscle) + " " + clean(rationale) + " " + clean(exercise));
        if (contains(all, "답", "무반응", "관계 신호", "거절"))
            flow = "애매한 신호 → 나쁜 뜻으로 빠르게 결론 → 불안이 커짐 → 확인하고 싶어짐";
        else if (contains(all, "확인", "재확인"))
            flow = "불안 → 바로 확인함 → 잠깐 안심 → 다음 애매함을 더 견디기 어려워짐";
        else if (contains(all, "경계", "거절", "싫"))
            flow = "상대가 불편해할까 걱정 → 내 욕구를 접음 → 지침/서운함이 쌓임";
        else if (contains(all, "충동", "손절", "차단", "결정"))
            flow = "마음이 급해짐 → 큰 결정을 빨리 함 → 나중에 다시 흔들림";
        else if (contains(all, "과부하", "번아웃", "압도", "회복"))
            flow = "참고 버팀 → 부담이 쌓임 → 한꺼번에 압도됨 → 모든 걸 피하고 싶어짐";
        else
            flow = title;
        save(c, why, flow, action, "MIND_PT");
    }

    public static String widgetLine(Context c) {
        Snapshot s = read(c);
        if (s.action.isEmpty()) return "";
        return "오늘은 이것만 · " + shortText(s.action, 150);
    }

    public static String mascotLine(Context c) {
        Snapshot s = read(c);
        if (s.action.isEmpty()) return "";
        return "우리 오늘은 이것만 해보자. " + shortText(s.action, 120);
    }

    public static String roomSummary(Context c) {
        Snapshot s = read(c);
        if (s.isEmpty()) return "";
        StringBuilder b = new StringBuilder();
        if (!s.core.isEmpty()) b.append("❤️ 요즘 가장 중요한 마음\n").append(shortText(s.core, 180));
        if (!s.flow.isEmpty()) {
            if (b.length() > 0) b.append("\n\n");
            b.append("🧠 반복되는 흐름\n").append(shortText(s.flow, 180));
        }
        if (!s.action.isEmpty()) {
            if (b.length() > 0) b.append("\n\n");
            b.append("🌱 오늘은 이것만\n").append(shortText(s.action, 160));
        }
        return b.toString();
    }

    private static boolean contains(String s, String... keys) {
        for (String k : keys) if (s.contains(k)) return true;
        return false;
    }
    private static String clean(String s) {
        if (s == null) return "";
        return s.replace('\n',' ').replace('\r',' ').replaceAll("\\s+", " ").trim();
    }
    private static String shortText(String s, int n) {
        String x = clean(s);
        if (x.length() <= n) return x;
        int cut = x.lastIndexOf(' ', n);
        if (cut < n / 2) cut = n;
        return x.substring(0, cut).trim() + "…";
    }
}
''', encoding='utf-8')

# Seed CURRENT_FOCUS whenever Mind PT restores the selected/current step.
activity = app / 'MindPtActivity.java'
m = activity.read_text(encoding='utf-8')
seed = 'CurrentCounselingFocus.updateFromPt(this, s.muscle, s.rationale, s.exercise);'
if seed not in m:
    anchor = 'muscleText.setText(OhStylePtDisplay.title(s.muscle, s.exercise));'
    if anchor not in m:
        anchor = 'muscleText.setText(s.muscle);'
    if anchor in m:
        m = m.replace(anchor, seed + '\n        ' + anchor, 1)
    else:
        raise SystemExit('v10.18.33: MindPt restore anchor missing')
activity.write_text(m, encoding='utf-8')

# Every everyday surface first consults CURRENT_FOCUS; legacy PT text remains fallback.
central = app / 'CentralMindPtState.java'
c = central.read_text(encoding='utf-8')

def inject_first_return(text, signature, code):
    pos = text.find(signature)
    if pos < 0: return text, False
    brace = text.find('{', pos)
    if brace < 0: return text, False
    if code.strip() in text[brace:brace+500]: return text, True
    return text[:brace+1] + '\n' + code + text[brace+1:], True

c, ok1 = inject_first_return(c, 'public static String compactWidgetLine(Context context)',
'''        String shared = CurrentCounselingFocus.widgetLine(context);
        if (shared != null && !shared.trim().isEmpty()) return shared;
''')
c, ok2 = inject_first_return(c, 'public static String mascotLine(Context context)',
'''        String shared = CurrentCounselingFocus.mascotLine(context);
        if (shared != null && !shared.trim().isEmpty()) return shared;
''')
c, ok3 = inject_first_return(c, 'public static String roomSummary(Context context)',
'''        String shared = CurrentCounselingFocus.roomSummary(context);
        if (shared != null && !shared.trim().isEmpty()) return shared;
''')
if not (ok1 and ok2 and ok3):
    raise SystemExit('v10.18.33: CentralMindPtState focus surface anchors missing')
central.write_text(c, encoding='utf-8')

# Model-facing rule: every successful counseling/PT synthesis must end in the same three-item hierarchy.
analyzer = app / 'CounselingProgramAnalyzer.java'
a = analyzer.read_text(encoding='utf-8')
needle = '상담, GPT 링크, 마음 PT, 위젯, 다마고치, 리포트는 서로 다른 조언을 만들지 말고 같은 최우선 formulation과 다음 개입을 공유해야 한다.'
extra = (' 상담이 충분히 정리됐을 때 내부적으로 항상 CURRENT_FOCUS 3요소를 일치시킨다: '
         'HEART=지금 반응을 가장 잘 설명하는 핵심 마음/두려움 한 문장, '
         'FLOW=그 마음이 반복 문제를 유지하는 실제 흐름 한 문장, '
         'SPROUT=오늘 생활에서 해볼 관찰 가능한 행동 딱 하나. '
         '새 직접근거나 사용자 정정이 생기면 이 세 요소도 즉시 다시 계산하고 오래된 PT 설명을 우선하지 않는다.')
if 'CURRENT_FOCUS 3요소' not in a and needle in a:
    # Director class owns the policy string in v32, so also strengthen PT-specific rule here.
    marker = '개입은 현재 formulation의 유지기제와 연결하고 가장 작은 유효 강도부터 시작한다.'
    if marker in a:
        a = a.replace(marker, marker + extra, 1)
analyzer.write_text(a, encoding='utf-8')

# Shared link re-audit marker.
shared = app / 'SharedCounselingLinkActivity.java'
s = shared.read_text(encoding='utf-8')
s = re.sub(r'private static final String COLLECTOR_VERSION = "v\d+";', 'private static final String COLLECTOR_VERSION = "v7";', s, count=1)
s = re.sub(r'private static final int CROWN_POLICY_VERSION = \d+;', 'private static final int CROWN_POLICY_VERSION = 33;', s, count=1)
shared.write_text(s, encoding='utf-8')

# Version bump.
g = gradle.read_text(encoding='utf-8')
g = re.sub(r'versionCode\s+\d+', 'versionCode 101833', g)
g = re.sub(r'versionName\s+"[^"]+"', 'versionName "10.18.33"', g)
gradle.write_text(g, encoding='utf-8')

print('Applied v10.18.33: shared CURRENT_FOCUS heart/flow/action hub across PT, widget, mascot and room')

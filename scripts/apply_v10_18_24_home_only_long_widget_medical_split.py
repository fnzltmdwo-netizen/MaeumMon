from pathlib import Path
import re

root = Path('extracted')
app = root / 'app/src/main/java/com/maeummon/app'
res = root / 'app/src/main/res/layout'
gradle = root / 'app/build.gradle'

# -----------------------------------------------------------------------------
# 1) Hard separation: medical-management content stays in raw counseling/safety
#    context, never in the visible Mind PT / widget / mascot training surface.
# -----------------------------------------------------------------------------
medical_policy = app / 'MedicalPtPolicy.java'
medical_policy.write_text(r'''package com.maeummon.app;

import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import java.util.Locale;

/**
 * Mind PT is a psychological practice surface, not a medication/medical-management surface.
 * Medical facts remain in counseling/safety records, but are excluded from PT display/activation surfaces.
 */
public final class MedicalPtPolicy {
    private MedicalPtPolicy() {}

    private static final String[] MEDICAL_TERMS = new String[]{
            "의료진", "담당 의료", "의사에게", "의사와", "의사 상담", "병원", "진료", "처방",
            "복약", "복용량", "복용 시간", "복용시간", "약물", "약 복용", "약을 복용", "약을 먹",
            "부작용", "용량", "투약", "증량", "감량", "약 중단", "복용 중단", "약효", "의료적",
            "medication", "doctor", "hospital", "prescription", "dosage", "side effect"
    };

    public static boolean containsMedicalTerms(String raw) {
        if (raw == null || raw.trim().isEmpty()) return false;
        String s = raw.toLowerCase(Locale.KOREA);
        for (String k : MEDICAL_TERMS) if (s.contains(k.toLowerCase(Locale.KOREA))) return true;
        // Numeric medication-dose notation is also a medical-management signal.
        if (s.matches(".*\\b\\d+(?:\\.\\d+)?\\s*mg\\b.*")) return true;
        return false;
    }

    public static boolean isMedicalCore(String muscle, String exercise, String criterion) {
        return containsMedicalTerms(muscle) || containsMedicalTerms(exercise) || containsMedicalTerms(criterion);
    }

    public static boolean isProgramMedical(SQLiteDatabase db, long programId) {
        if (db == null || programId <= 0) return false;
        Cursor c = db.rawQuery(
                "SELECT p.name,p.muscle_name,s.exercise_text,s.success_criterion " +
                        "FROM counseling_programs p LEFT JOIN counseling_program_steps s ON s.program_id=p.id " +
                        "WHERE p.id=? ORDER BY s.step_order ASC",
                new String[]{String.valueOf(programId)});
        try {
            while (c.moveToNext()) {
                if (isMedicalCore(c.getString(1), c.getString(2), c.getString(3))
                        || containsMedicalTerms(c.getString(0))) return true;
            }
        } finally { c.close(); }
        return false;
    }

    /** Background medical context is not allowed to leak into a visible PT reason. */
    public static String cleanVisibleReason(String reason) {
        if (reason == null) return "";
        if (!containsMedicalTerms(reason)) return reason;
        return "상담 원문에서 확인된 반복 패턴을 바탕으로 만든 마음 연습이야.";
    }
}
''', encoding='utf-8')

# Future/generated PTs: visible PT JSON itself must be medical-language free.
analyzer = app / 'CounselingProgramAnalyzer.java'
a = analyzer.read_text(encoding='utf-8')
rule = (
    '의료문구 완전 분리 규칙: 상담 원문과 안전 맥락에는 의료 정보를 보존하되 마음 PT JSON의 name, muscleName, mechanism, reason, steps의 exerciseText, successCriterion, rationale에는 '
    '의료진·의사·병원·진료·처방·복약·복용량·약물·부작용·용량·증량·감량·약 중단 같은 의료관리 문구를 쓰지 않는다. '
    '이런 의료관리 행동은 PT로 변환하지 말고, 독립적으로 연습 가능한 비의료 심리 능력만 PT로 만든다. '
    '의료 내용이 단지 상담 배경이라면 PT reason에도 그 의료 문구를 재노출하지 말고 심리 패턴의 근거만 생활말로 설명한다. '
)
marker = '반드시 JSON 하나만 출력한다.'
if rule not in a and marker in a:
    a = a.replace(marker, rule + marker)
a = re.sub(r'CROWN_POLICY_VERSION\s*=\s*\d+', 'CROWN_POLICY_VERSION = 20', a)
analyzer.write_text(a, encoding='utf-8')

# Existing saved PTs: hide truly medical-management programs, but preserve normal psychological PTs.
store = app / 'MindTrainingStore.java'
s = store.read_text(encoding='utf-8')
old = 'x.status = safe(c.getString(6)); x.stepCount = c.getInt(7); x.doneSteps = c.isNull(8) ? 0 : c.getInt(8); out.add(x);'
new = ('x.status = safe(c.getString(6)); x.stepCount = c.getInt(7); x.doneSteps = c.isNull(8) ? 0 : c.getInt(8); '
       'if (MedicalPtPolicy.isProgramMedical(helper.getReadableDatabase(), x.id)) continue; '
       'x.reason = MedicalPtPolicy.cleanVisibleReason(x.reason); out.add(x);')
if old not in s:
    raise SystemExit('v10.18.24: programsForCounseling anchor missing')
s = s.replace(old, new, 1)
store.write_text(s, encoding='utf-8')

# The central active PT source skips old active medical-management sessions entirely.
central = app / 'CentralMindPtState.java'
c = central.read_text(encoding='utf-8')
start = c.find('    public static Snapshot current(Context context) {')
end = c.find('    public static String compactWidgetLine(Context context) {', start)
if start < 0 or end < 0:
    raise SystemExit('v10.18.24: CentralMindPtState current anchors missing')
current_method = r'''    public static Snapshot current(Context context) {
        MindTrainingDbHelper helper = new MindTrainingDbHelper(context.getApplicationContext());
        Cursor c = helper.getReadableDatabase().rawQuery(
                "SELECT t.id,t.mode,m.name,t.exercise_text,t.success_criterion,t.rationale,t.created_at " +
                        "FROM training_sessions t JOIN mind_muscles m ON m.id=t.muscle_id " +
                        "WHERE t.completed_at IS NULL AND t.superseded_at IS NULL ORDER BY t.created_at DESC LIMIT 12", null);
        try {
            while (c.moveToNext()) {
                String muscle = safe(c.getString(2));
                String exercise = safe(c.getString(3));
                String criterion = safe(c.getString(4));
                if (MedicalPtPolicy.isMedicalCore(muscle, exercise, criterion)) continue;

                Snapshot out = new Snapshot();
                out.trainingId = c.getLong(0);
                out.mode = safe(c.getString(1));
                out.muscle = muscle;
                out.exercise = exercise;
                out.criterion = criterion;
                out.rationale = MedicalPtPolicy.cleanVisibleReason(safe(c.getString(5)));
                out.createdAt = c.getLong(6);
                out.active = true;
                return out;
            }
            return new Snapshot();
        } finally {
            c.close();
            helper.close();
        }
    }

'''
c = c[:start] + current_method + c[end:]
# Active PT was previously hard-truncated to 31 chars before the widget even laid it out.
c = c.replace('compact("오늘은 회복이 훈련이야 · " + s.exercise, 31)', 'compact("오늘은 회복이 훈련이야 · " + s.exercise, 68)')
c = c.replace('compact("지금은 속도를 늦추는 연습 · " + s.exercise, 31)', 'compact("지금은 속도를 늦추는 연습 · " + s.exercise, 68)')
c = c.replace('compact("오늘은 복기하는 날 · " + s.exercise, 31)', 'compact("오늘은 복기하는 날 · " + s.exercise, 68)')
c = c.replace('compact("이미 키운 힘을 가볍게 써보자 · " + s.exercise, 31)', 'compact("이미 키운 힘을 가볍게 써보자 · " + s.exercise, 68)')
c = c.replace('compact("오늘의 PT · " + s.muscle + " · " + action, 31)', 'compact("오늘의 PT · " + s.muscle + " · " + action, 68)')
central.write_text(c, encoding='utf-8')

# -----------------------------------------------------------------------------
# 2) Widget: longer PT text and clock text that dynamically fits its bitmap.
# -----------------------------------------------------------------------------
widget = app / 'MaeumMonClockWidget.java'
w = widget.read_text(encoding='utf-8')
old_caps = '''        int widgetMaxChars = (layout == R.layout.widget_maeummon_medium) ? 28
                : (layout == R.layout.widget_maeummon_clock) ? 32
                : (layout == R.layout.widget_maeummon_large) ? 42
                : 30;'''
new_caps = '''        int widgetMaxChars = (layout == R.layout.widget_maeummon_medium) ? 54
                : (layout == R.layout.widget_maeummon_clock) ? 68
                : (layout == R.layout.widget_maeummon_large) ? 84
                : (layout == R.layout.widget_maeummon_narrow) ? 50
                : 32;'''
if old_caps not in w:
    raise SystemExit('v10.18.24: widget cap anchor missing')
w = w.replace(old_caps, new_caps, 1)
w = w.replace('return TherapySurfacePolicyV501.compactWidgetText(line, 30);',
              'return TherapySurfacePolicyV501.compactWidgetText(line, 68);', 1)

# Prevent 11:18 -> 11:1 clipping: fit the glossy font to the actual bitmap width.
old_render = '''        Typeface typeface = getWidgetTypeface(context);

        Paint glow = basePaint(typeface, textPx);'''
new_render = '''        Typeface typeface = getWidgetTypeface(context);

        float fittedTextPx = textPx;
        Paint measurePaint = basePaint(typeface, fittedTextPx);
        float safeWidth = Math.max(1f, widthPx - (strongGlow ? 34f : 24f));
        float measuredWidth = measurePaint.measureText(text == null ? "" : text);
        if (measuredWidth > safeWidth && measuredWidth > 0f) {
            fittedTextPx = Math.max(18f, fittedTextPx * (safeWidth / measuredWidth));
        }

        Paint glow = basePaint(typeface, fittedTextPx);'''
if old_render not in w:
    raise SystemExit('v10.18.24: clock render anchor missing')
w = w.replace(old_render, new_render, 1)
w = w.replace('Paint darkOutline = basePaint(typeface, textPx);', 'Paint darkOutline = basePaint(typeface, fittedTextPx);', 1)
w = w.replace('Paint lightOutline = basePaint(typeface, textPx);', 'Paint lightOutline = basePaint(typeface, fittedTextPx);', 1)
w = w.replace('Paint fill = basePaint(typeface, textPx);', 'Paint fill = basePaint(typeface, fittedTextPx);', 1)
widget.write_text(w, encoding='utf-8')

policy = app / 'TherapySurfacePolicyV501.java'
p = policy.read_text(encoding='utf-8')
p = p.replace('위젯은 18~30자 안팎의 한 문장만 쓴다. 핵심 재정의 전체를 설명하지 말고 오늘의 CHANGE_TARGET 또는 PRACTICE 하나만 생활말로 압축한다. 말줄임표로 잘린 문장을 만들지 않는다.',
              '위젯은 약 45~70자 안팎까지 사용할 수 있다. 오늘의 CHANGE_TARGET 또는 PRACTICE를 생활말로 충분히 이해되게 쓰고, 화면에서는 2~4줄로 자연스럽게 줄바꿈되게 한다. 문장 중간을 말줄임표로 잘라 의미가 끊기게 만들지 않는다.')
policy.write_text(p, encoding='utf-8')

# Give the longer PT enough physical lines on every visible message layout.
layout_changes = {
    'widget_maeummon_clock.xml': [('android:maxLines="3"', 'android:maxLines="4"'), ('android:minHeight="72dp"', 'android:minHeight="92dp"'), ('android:textSize="13sp"', 'android:textSize="12sp"')],
    'widget_maeummon_large.xml': [('android:maxLines="3"', 'android:maxLines="4"'), ('android:minHeight="96dp"', 'android:minHeight="112dp"'), ('android:textSize="18sp"', 'android:textSize="16sp"')],
    'widget_maeummon_medium.xml': [('android:layout_height="62dp"', 'android:layout_height="74dp"'), ('android:maxLines="3"', 'android:maxLines="4"')],
    'widget_maeummon_narrow.xml': [('android:maxLines="3"', 'android:maxLines="4"'), ('android:minHeight="70dp"', 'android:minHeight="86dp"')],
}
for name, reps in layout_changes.items():
    path = res / name
    t = path.read_text(encoding='utf-8')
    for oldv, newv in reps:
        if oldv in t:
            t = t.replace(oldv, newv, 1)
    path.write_text(t, encoding='utf-8')

# -----------------------------------------------------------------------------
# 3) Mascot overlay: only show when HOME is positively confirmed.
# -----------------------------------------------------------------------------
overlay = app / 'OverlayService.java'
o = overlay.read_text(encoding='utf-8')
old_fallback = '''            } else {
                // 접근성 서비스가 꺼져 있을 때만 기존 UsageStats fallback.
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
new_fallback = '''            } else {
                // v10.18.24 strict HOME-only rule.
                // UsageStats cannot reliably distinguish Samsung Home from All Apps/Finder because
                // they can share the same launcher package/class. Ambiguous means HIDE, never SHOW.
                updateForegroundPackage();
                home = false;
            }'''
if old_fallback not in o:
    raise SystemExit('v10.18.24: overlay fallback anchor missing')
o = o.replace(old_fallback, new_fallback, 1)
overlay.write_text(o, encoding='utf-8')

access = app / 'LauncherSurfaceAccessibilityService.java'
l = access.read_text(encoding='utf-8')
old_sysui = '''        if (lowerPkg.contains("systemui")) {
            if (cls.contains("recents") || cls.contains("overview") || info.hasRecentKeyword) {
                saveMode(MODE_BLOCKED);
            }
            // 단순 상태바/알림 아이콘 이벤트는 이전 판정을 유지한다.
            return;
        }'''
new_sysui = '''        if (lowerPkg.contains("systemui")) {
            // Notification shade / quick settings / recents are not the launcher home surface.
            // If SystemUI owns the active root, hide immediately instead of preserving stale HOME.
            saveMode(MODE_BLOCKED);
            return;
        }'''
if old_sysui not in l:
    raise SystemExit('v10.18.24: systemui classifier anchor missing')
l = l.replace(old_sysui, new_sysui, 1)
access.write_text(l, encoding='utf-8')

# Version bump.
g = gradle.read_text(encoding='utf-8')
g = re.sub(r'versionCode\s+\d+', 'versionCode 101824', g)
g = re.sub(r'versionName\s+"[^"]+"', 'versionName "10.18.24"', g)
gradle.write_text(g, encoding='utf-8')

print('Applied v10.18.24: strict home-only mascot + longer widget + clock fit + medical PT split')

from pathlib import Path
import re

root = Path('extracted')
app = root / 'app/src/main/java/com/maeummon/app'
res = root / 'app/src/main/res'
layout = res / 'layout/activity_mind_pt.xml'
manifest = root / 'app/src/main/AndroidManifest.xml'
central = app / 'CentralMindPtState.java'
pt = app / 'MindPtActivity.java'
gradle = root / 'app/build.gradle'

# 1) Shared preferences helper: preserve PT content, only soften the language.
prefs_java = r'''package com.maeummon.app;

import android.content.Context;
import android.content.SharedPreferences;

public final class MascotWidgetPrefs {
    private static final String PREF = "mascot_widget_settings";
    private static final String KEY_YOUNG = "young_seungjae_tone";
    private static final String KEY_BUBBLE = "bubble_length";
    private static final String KEY_WIDGET = "widget_detail";

    private MascotWidgetPrefs() {}

    public static boolean youngTone(Context c) {
        return c.getSharedPreferences(PREF, Context.MODE_PRIVATE).getBoolean(KEY_YOUNG, true);
    }

    public static int bubbleLength(Context c) {
        return c.getSharedPreferences(PREF, Context.MODE_PRIVATE).getInt(KEY_BUBBLE, 1); // 0 short, 1 normal, 2 long
    }

    public static int widgetDetail(Context c) {
        return c.getSharedPreferences(PREF, Context.MODE_PRIVATE).getInt(KEY_WIDGET, 1); // 0 title, 1 title+exercise
    }

    public static void save(Context c, boolean young, int bubble, int widget) {
        c.getSharedPreferences(PREF, Context.MODE_PRIVATE).edit()
                .putBoolean(KEY_YOUNG, young)
                .putInt(KEY_BUBBLE, bubble)
                .putInt(KEY_WIDGET, widget)
                .apply();
    }

    public static int bubbleMax(Context c) {
        int v = bubbleLength(c);
        return v == 0 ? 92 : (v == 2 ? 300 : 175);
    }

    // Preserve the original training content/details; only change formal/clinical phrasing into
    // a simple "young Seungjae" voice. Numbers, choices and conditions are intentionally untouched.
    public static String youngify(String raw) {
        if (raw == null) return "";
        String s = raw.trim();
        if (s.isEmpty()) return s;
        s = s.replace("선택하거나 제안합니다.", "하나 골라보거나 말해보자.")
             .replace("선택합니다.", "골라보자.")
             .replace("제안합니다.", "말해보자.")
             .replace("기록합니다.", "적어보자.")
             .replace("전달합니다.", "말해보자.")
             .replace("확인합니다.", "살펴보자.")
             .replace("시도합니다.", "해보자.")
             .replace("적용합니다.", "써보자.")
             .replace("유지합니다.", "그대로 해보자.")
             .replace("필요합니다.", "필요해.")
             .replace("가능합니다.", "할 수 있어.")
             .replace("수 있습니다.", "수 있어.")
             .replace("입니다.", "이야.")
             .replace("됩니다.", "돼.")
             .replace("결정하지 말고", "바로 정하지 말고")
             .replace("부담을 낮추는 조건", "덜 힘들게 만드는 방법")
             .replace("대인 약속", "사람 만나는 약속")
             .replace("판단 유보", "바로 결론내리지 않기");
        // Generic formal ending conversion, after specific replacements above.
        s = s.replace("합니다.", "해보자.")
             .replace("하세요.", "해보자.");
        return s;
    }

    public static String widgetLine(Context c) {
        CentralMindPtState.Snapshot s = CentralMindPtState.current(c);
        if (!s.active) return "";
        if (widgetDetail(c) == 0 || s.exercise == null || s.exercise.trim().isEmpty()) {
            return "오늘의 PT · " + s.muscle;
        }
        String ex = s.exercise.replace('\n', ' ').replace('\r', ' ').replaceAll("\\s+", " ").trim();
        if (ex.length() > 72) {
            int cut = ex.lastIndexOf(' ', 72);
            if (cut < 28) cut = 72;
            ex = ex.substring(0, cut).trim();
        }
        if (youngTone(c)) ex = youngify(ex);
        return "오늘의 PT · " + s.muscle + "\n" + ex;
    }
}
'''
(app / 'MascotWidgetPrefs.java').write_text(prefs_java, encoding='utf-8')

# 2) Settings screen. Plain Activity keeps dependencies minimal.
settings_java = r'''package com.maeummon.app;

import android.app.Activity;
import android.os.Bundle;
import android.graphics.Color;
import android.graphics.drawable.GradientDrawable;
import android.view.View;
import android.widget.*;

public class MascotWidgetSettingsActivity extends Activity {
    private int mint = Color.parseColor("#9BE2CB");
    private int text = Color.parseColor("#55546B");

    @Override protected void onCreate(Bundle b) {
        super.onCreate(b);
        ScrollView scroll = new ScrollView(this);
        scroll.setFillViewport(true);
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(22), dp(26), dp(22), dp(30));
        root.setBackgroundColor(Color.parseColor("#FBFAFF"));
        scroll.addView(root, new ScrollView.LayoutParams(-1, -2));

        TextView title = t("🐣 다마고치 · 위젯 설정", 26, true); root.addView(title);
        TextView sub = t("마음 PT의 내용은 그대로 두고, 보여주는 말투와 길이만 바꿔.", 14, false);
        sub.setTextColor(Color.parseColor("#85839A")); add(root, sub, 0, 4, 0, 22);

        final Switch young = new Switch(this);
        young.setText("어린 승재 말투"); young.setTextSize(17); young.setTextColor(text);
        young.setChecked(MascotWidgetPrefs.youngTone(this));
        addCard(root, young);
        TextView youngHelp = t("PT의 숫자·조건·행동은 그대로 유지하고, 딱딱한 표현만 어린 승재처럼 쉽게 바꿔.", 13, false);
        youngHelp.setTextColor(Color.parseColor("#85839A")); add(root, youngHelp, 10, 6, 6, 20);

        root.addView(t("💬 다마고치 말풍선 길이", 17, true));
        final RadioGroup bubble = new RadioGroup(this); bubble.setOrientation(RadioGroup.HORIZONTAL);
        String[] bl = {"짧게", "보통", "길게"};
        for (int i=0;i<3;i++) { RadioButton r = new RadioButton(this); r.setText(bl[i]); r.setId(100+i); bubble.addView(r, new RadioGroup.LayoutParams(0,-2,1f)); }
        bubble.check(100 + MascotWidgetPrefs.bubbleLength(this)); addCard(root, bubble);

        root.addView(t("🕰️ 위젯 문구", 17, true));
        final RadioGroup widget = new RadioGroup(this); widget.setOrientation(RadioGroup.VERTICAL);
        RadioButton w0 = new RadioButton(this); w0.setId(200); w0.setText("PT 이름만 깔끔하게"); widget.addView(w0);
        RadioButton w1 = new RadioButton(this); w1.setId(201); w1.setText("PT 이름 + 오늘 연습"); widget.addView(w1);
        widget.check(200 + MascotWidgetPrefs.widgetDetail(this)); addCard(root, widget);

        Button save = new Button(this); save.setText("💚 저장하고 바로 적용"); save.setTextSize(16); save.setTextColor(Color.WHITE);
        save.setAllCaps(false); save.setBackground(round(mint, 26, Color.parseColor("#7DCBB0")));
        LinearLayout.LayoutParams sp = new LinearLayout.LayoutParams(-1, dp(58)); sp.setMargins(0, dp(22), 0, dp(10)); root.addView(save, sp);
        save.setOnClickListener(v -> {
            int bval = Math.max(0, bubble.getCheckedRadioButtonId() - 100);
            int wval = Math.max(0, widget.getCheckedRadioButtonId() - 200);
            MascotWidgetPrefs.save(this, young.isChecked(), bval, wval);
            try { LiveMindManager.onMindChanged(this); } catch (Throwable ignored) {}
            try { MaeumMonClockWidget.refreshAll(this); } catch (Throwable ignored) {}
            Toast.makeText(this, "다마고치와 위젯에 바로 적용했어 🐣", Toast.LENGTH_SHORT).show();
        });

        Button back = new Button(this); back.setText("← 돌아가기"); back.setAllCaps(false); back.setTextColor(text);
        back.setBackground(round(Color.WHITE, 24, Color.parseColor("#E5E2EE")));
        LinearLayout.LayoutParams bp = new LinearLayout.LayoutParams(-1, dp(52)); root.addView(back, bp); back.setOnClickListener(v -> finish());
        setContentView(scroll);
    }

    private TextView t(String s, int sp, boolean bold) { TextView v=new TextView(this); v.setText(s); v.setTextSize(sp); v.setTextColor(text); if (bold) v.setTypeface(null, android.graphics.Typeface.BOLD); return v; }
    private void add(LinearLayout r, View v, int l,int t,int rr,int b){ LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,-2); p.setMargins(dp(l),dp(t),dp(rr),dp(b)); r.addView(v,p); }
    private void addCard(LinearLayout r, View v){ LinearLayout box=new LinearLayout(this); box.setPadding(dp(15),dp(13),dp(15),dp(13)); box.setBackground(round(Color.WHITE,24,Color.parseColor("#E7E3EF"))); box.addView(v,new LinearLayout.LayoutParams(-1,-2)); add(r,box,0,8,0,18); }
    private GradientDrawable round(int c,int rad,int stroke){ GradientDrawable g=new GradientDrawable(); g.setColor(c); g.setCornerRadius(dp(rad)); g.setStroke(dp(1),stroke); return g; }
    private int dp(int v){ return Math.round(v*getResources().getDisplayMetrics().density); }
}
'''
(app / 'MascotWidgetSettingsActivity.java').write_text(settings_java, encoding='utf-8')

# 3) Rewrite mascotLine: same PT details, only tone changes. Bubble length is user-controlled.
text = central.read_text(encoding='utf-8')
start = text.find('    public static String mascotLine(Context context) {')
end = text.find('    public static String roomSummary(Context context) {', start)
if start < 0 or end < 0:
    raise SystemExit('v10.18.13: mascotLine anchors missing')
new_method = r'''    public static String mascotLine(Context context) {
        Snapshot s = current(context);
        if (!s.active) return "";
        String action = s.exercise.isEmpty() ? s.rationale : s.exercise;
        String core = completeThoughts(action, MascotWidgetPrefs.bubbleMax(context));
        if (MascotWidgetPrefs.youngTone(context)) {
            core = MascotWidgetPrefs.youngify(core);
            if ("RECOVERY".equals(s.mode)) return "우리 오늘은 더 버티지 말고 쉬어가자. " + core;
            if ("STABILIZE".equals(s.mode)) return "우리 서두르지 말고 이것부터 해보자. " + core;
            if ("REVIEW".equals(s.mode)) return "우리 잘잘못 말고 다음에 알아차릴 것만 하나 보자. " + core;
            if ("MAINTENANCE".equals(s.mode)) return "이건 이제 조금씩 우리 힘이 되고 있어. 오늘도 한 번 써보자. " + core;
            return "우리 오늘은 이걸 해보자. " + core;
        }
        if ("RECOVERY".equals(s.mode)) return "오늘은 더 버티기보다 회복을 고르는 날이야. " + core;
        if ("STABILIZE".equals(s.mode)) return "지금은 서두르지 말고 오늘 정한 연습 하나만 해보자. " + core;
        if (!core.isEmpty()) return "오늘 PT는 ‘" + compact(s.muscle, 26) + "’. " + core;
        return "오늘 PT는 ‘" + compact(s.muscle, 30) + "’. 이 힘을 한 번 써보자.";
    }

    private static String completeThoughts(String s, int max) {
        if (s == null) return "";
        String clean = s.replace('\n', ' ').replace('\r', ' ').replaceAll("\\s+", " ").trim();
        if (clean.isEmpty() || clean.length() <= max) return clean;
        int hard = Math.min(clean.length(), max);
        int best = -1;
        for (int i = 18; i < hard; i++) {
            char ch = clean.charAt(i);
            if (ch == '.' || ch == '!' || ch == '?' || ch == '。' || ch == '！' || ch == '？') best = i + 1;
        }
        if (best > 0) return clean.substring(0, best).trim();
        int cut = clean.lastIndexOf(' ', hard);
        if (cut < 30) cut = hard;
        String out = clean.substring(0, cut).trim();
        if (!(out.endsWith(".") || out.endsWith("!") || out.endsWith("?") || out.endsWith("다") || out.endsWith("요"))) out += ".";
        return out;
    }

'''
text = text[:start] + new_method + text[end:]
central.write_text(text, encoding='utf-8')

# 4) Bottom settings button in Mind PT screen.
x = layout.read_text(encoding='utf-8')
if '@+id/openMascotWidgetSettingsButton' not in x:
    idx = x.rfind('</LinearLayout>')
    if idx < 0: raise SystemExit('v10.18.13: root LinearLayout closing tag missing')
    button = '''\n        <Button\n            android:id="@+id/openMascotWidgetSettingsButton"\n            android:layout_width="match_parent"\n            android:layout_height="56dp"\n            android:layout_marginTop="16dp"\n            android:layout_marginBottom="8dp"\n            android:text="🐣 다마고치 · 위젯 설정"\n            android:textSize="15sp"\n            android:textStyle="bold"\n            android:textColor="@color/brown"\n            android:background="@drawable/bg_nav_growth"\n            android:stateListAnimator="@null"\n            android:onClick="openMascotWidgetSettings" />\n'''
    x = x[:idx] + button + x[idx:]
layout.write_text(x, encoding='utf-8')

# Handler method avoids touching onCreate/findViewById wiring.
text = pt.read_text(encoding='utf-8')
if 'openMascotWidgetSettings(android.view.View view)' not in text:
    pos = text.rfind('\n}')
    if pos < 0: raise SystemExit('v10.18.13: MindPtActivity closing brace missing')
    meth = '''\n    public void openMascotWidgetSettings(android.view.View view) {\n        startActivity(new android.content.Intent(this, MascotWidgetSettingsActivity.class));\n    }\n'''
    text = text[:pos] + meth + text[pos:]
pt.write_text(text, encoding='utf-8')

# 5) Register settings Activity.
m = manifest.read_text(encoding='utf-8')
if 'MascotWidgetSettingsActivity' not in m:
    m = m.replace('</application>', '        <activity android:name=".MascotWidgetSettingsActivity" android:exported="false" />\n    </application>', 1)
manifest.write_text(m, encoding='utf-8')

# 6) Best-effort widget sync: if widget already uses central room/mascot text, route it through settings helper.
widget = app / 'MaeumMonClockWidget.java'
if widget.exists():
    w = widget.read_text(encoding='utf-8')
    w = w.replace('CentralMindPtState.mascotLine(context)', 'MascotWidgetPrefs.widgetLine(context)')
    w = w.replace('CentralMindPtState.roomSummary(context)', 'MascotWidgetPrefs.widgetLine(context)')
    w = w.replace('CentralMindPtState.mascotLine(c)', 'MascotWidgetPrefs.widgetLine(c)')
    w = w.replace('CentralMindPtState.roomSummary(c)', 'MascotWidgetPrefs.widgetLine(c)')
    widget.write_text(w, encoding='utf-8')

# Version bump.
g = gradle.read_text(encoding='utf-8')
g, n1 = re.subn(r'versionCode\s+\d+', 'versionCode 101813', g, count=1)
g, n2 = re.subn(r'versionName\s+"[^"]+"', 'versionName "10.18.13"', g, count=1)
if n1 != 1 or n2 != 1: raise SystemExit('v10.18.13: version anchor missing')
gradle.write_text(g, encoding='utf-8')

print('Applied v10.18.13 young-Seungjae tone + mascot/widget settings screen')

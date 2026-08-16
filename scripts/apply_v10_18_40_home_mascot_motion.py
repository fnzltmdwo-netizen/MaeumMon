from pathlib import Path
import re

root = Path('extracted')
app = root / 'app/src/main/java/com/maeummon/app'
res = root / 'app/src/main/res'
layout_dir = res / 'layout'
drawable = res / 'drawable'
gradle = root / 'app/build.gradle'

# v10.18.40
# First screen only: keep ONE approved second-sister mascot image and animate the View.
# No new reinterpretation of the character. Counseling/PT logic is untouched.

# 1) Motion controller: same drawable, five gentle states.
controller = app / 'SecondSisterMascotMotion.java'
controller.write_text(r'''package com.maeummon.app;

import android.animation.Animator;
import android.animation.AnimatorListenerAdapter;
import android.animation.AnimatorSet;
import android.animation.ObjectAnimator;
import android.animation.ValueAnimator;
import android.view.View;
import android.view.animation.AccelerateDecelerateInterpolator;

/**
 * Keeps the approved second-sister artwork fixed and animates only the ImageView.
 * This avoids redrawing/reinterpreting the mascot on every screen.
 */
public final class SecondSisterMascotMotion {
    public enum State { IDLE, TALK, HAPPY, WORRY, SLEEP }

    private SecondSisterMascotMotion() {}

    public static void apply(View v, State state) {
        if (v == null) return;
        v.animate().cancel();
        v.clearAnimation();
        v.setRotation(0f);
        v.setScaleX(1f);
        v.setScaleY(1f);
        v.setAlpha(1f);
        v.setTranslationY(0f);

        switch (state) {
            case TALK: talk(v); break;
            case HAPPY: happy(v); break;
            case WORRY: worry(v); break;
            case SLEEP: sleep(v); break;
            case IDLE:
            default: idle(v); break;
        }
    }

    public static void idle(View v) {
        ObjectAnimator floatY = ObjectAnimator.ofFloat(v, View.TRANSLATION_Y, 0f, -12f, 0f);
        floatY.setDuration(2800L);
        floatY.setRepeatCount(ValueAnimator.INFINITE);
        floatY.setInterpolator(new AccelerateDecelerateInterpolator());
        floatY.start();
    }

    public static void talk(View v) {
        ObjectAnimator sy = ObjectAnimator.ofFloat(v, View.SCALE_Y, 1f, 1.025f, 1f);
        ObjectAnimator sx = ObjectAnimator.ofFloat(v, View.SCALE_X, 1f, 1.015f, 1f);
        sy.setRepeatCount(ValueAnimator.INFINITE);
        sx.setRepeatCount(ValueAnimator.INFINITE);
        sy.setDuration(520L); sx.setDuration(520L);
        AnimatorSet set = new AnimatorSet();
        set.playTogether(sx, sy); set.start();
    }

    public static void happy(View v) {
        ObjectAnimator up = ObjectAnimator.ofFloat(v, View.TRANSLATION_Y, 0f, -18f, 0f);
        ObjectAnimator scaleX = ObjectAnimator.ofFloat(v, View.SCALE_X, 1f, 1.06f, 1f);
        ObjectAnimator scaleY = ObjectAnimator.ofFloat(v, View.SCALE_Y, 1f, 1.06f, 1f);
        AnimatorSet set = new AnimatorSet();
        set.playTogether(up, scaleX, scaleY);
        set.setDuration(700L);
        set.addListener(new AnimatorListenerAdapter() {
            @Override public void onAnimationEnd(Animator animation) { idle(v); }
        });
        set.start();
    }

    public static void worry(View v) {
        ObjectAnimator sway = ObjectAnimator.ofFloat(v, View.ROTATION, 0f, -1.8f, 1.8f, 0f);
        sway.setDuration(1500L);
        sway.setRepeatCount(ValueAnimator.INFINITE);
        sway.start();
    }

    public static void sleep(View v) {
        ObjectAnimator floatY = ObjectAnimator.ofFloat(v, View.TRANSLATION_Y, 0f, 5f, 0f);
        ObjectAnimator alpha = ObjectAnimator.ofFloat(v, View.ALPHA, 1f, .86f, 1f);
        floatY.setDuration(3400L); alpha.setDuration(3400L);
        floatY.setRepeatCount(ValueAnimator.INFINITE); alpha.setRepeatCount(ValueAnimator.INFINITE);
        AnimatorSet set = new AnimatorSet();
        set.playTogether(floatY, alpha); set.start();
    }
}
''', encoding='utf-8')

# 2) First-screen hero card: one canonical character only.
layout = layout_dir / 'activity_mind_pt.xml'
if layout.exists():
    x = layout.read_text(encoding='utf-8')

    # Remove the old v38/v39 injected hero if present so there is only one mascot hero.
    x = re.sub(
        r'\s*<FrameLayout[^>]*android:layout_height="178dp"[^>]*>\s*<ImageView[^>]*(?:secondSisterHero|strawberryBunnyHero)[^>]*/>\s*</FrameLayout>\s*',
        '\n', x, count=1, flags=re.S)

    # Find the root vertical LinearLayout and insert a real home-style hero.
    if '@+id/secondSisterHomeHero' not in x:
        m = re.search(r'(<LinearLayout\b[^>]*android:orientation="vertical"[^>]*>)', x, re.S)
        if not m:
            raise SystemExit('v10.18.40: root vertical layout not found')
        hero = '''
        <FrameLayout
            android:id="@+id/secondSisterHeroCard"
            android:layout_width="match_parent"
            android:layout_height="300dp"
            android:layout_marginBottom="18dp"
            android:background="@drawable/bg_strawberry_glass">

            <TextView
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:layout_gravity="top|start"
                android:layout_marginStart="18dp"
                android:layout_marginTop="16dp"
                android:text="🌙 오늘도 네 옆에 있을게"
                android:textColor="@color/moon_light"
                android:textSize="15sp"
                android:textStyle="bold" />

            <ImageView
                android:id="@+id/secondSisterHomeHero"
                android:layout_width="210dp"
                android:layout_height="250dp"
                android:layout_gravity="center_horizontal|bottom"
                android:src="@drawable/second_sister_moon_mage"
                android:scaleType="fitCenter"
                android:contentDescription="둘째동생 메인 캐릭터" />

            <TextView
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:layout_gravity="bottom|end"
                android:layout_marginEnd="18dp"
                android:layout_marginBottom="15dp"
                android:text="✨"
                android:textSize="22sp" />
        </FrameLayout>
'''
        x = x[:m.end()] + hero + x[m.end():]

    # Remove visible legacy child/young mascot ImageViews when their resource names are obvious.
    x = re.sub(r'\s*<ImageView\b(?=[^>]*(?:young|child|little|seungjae|mascot_boy))[^>]*/>\s*', '\n', x, flags=re.I|re.S)
    layout.write_text(x, encoding='utf-8')

# 3) Wire the hero animation into MindPtActivity without changing PT logic.
activity = app / 'MindPtActivity.java'
if activity.exists():
    t = activity.read_text(encoding='utf-8')

    # Insert after setContentView if possible, once only.
    marker = 'SecondSisterMascotMotion.apply(secondSisterHomeHero, SecondSisterMascotMotion.State.IDLE);'
    if marker not in t:
        pat = re.compile(r'(setContentView\([^;]+;)', re.S)
        mm = pat.search(t)
        if not mm:
            raise SystemExit('v10.18.40: setContentView anchor missing')
        init = '''\n        final android.widget.ImageView secondSisterHomeHero = findViewById(R.id.secondSisterHomeHero);\n        if (secondSisterHomeHero != null) {\n            SecondSisterMascotMotion.apply(secondSisterHomeHero, SecondSisterMascotMotion.State.IDLE);\n            secondSisterHomeHero.setOnClickListener(v -> SecondSisterMascotMotion.apply(secondSisterHomeHero, SecondSisterMascotMotion.State.HAPPY));\n            secondSisterHomeHero.setOnLongClickListener(v -> {\n                SecondSisterMascotMotion.apply(secondSisterHomeHero, SecondSisterMascotMotion.State.TALK);\n                v.postDelayed(() -> SecondSisterMascotMotion.apply(secondSisterHomeHero, SecondSisterMascotMotion.State.IDLE), 2200L);\n                return true;\n            });\n        }\n'''
        t = t[:mm.end()] + init + t[mm.end():]
    activity.write_text(t, encoding='utf-8')

# 4) Clean identity wording on settings: no rabbit / young-Seungjae mascot labels.
settings = app / 'MascotWidgetSettingsActivity.java'
if settings.exists():
    s = settings.read_text(encoding='utf-8')
    replacements = {
        '어린 승재': '둘째동생',
        '토끼 친구': '둘째동생',
        '스트로베리문 토끼': '둘째동생',
        '🐣': '🌙',
        '🐰': '🌙'
    }
    for a, b in replacements.items():
        s = s.replace(a, b)
    settings.write_text(s, encoding='utf-8')

# 5) Version bump.
g = gradle.read_text(encoding='utf-8')
g = re.sub(r'versionCode\s+\d+', 'versionCode 101840', g)
g = re.sub(r'versionName\s+"[^"]+"', 'versionName "10.18.40"', g)
gradle.write_text(g, encoding='utf-8')

print('Applied v10.18.40: first-screen fixed second-sister mascot + real View motion states')

package com.seungjae.dangifreepass;

import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.ComponentName;
import android.content.Intent;
import android.content.res.ColorStateList;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.net.Uri;
import android.os.Bundle;
import android.provider.Settings;
import android.text.TextUtils;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.Space;
import android.widget.TextView;
import android.widget.Toast;

public final class MainActivity extends Activity {
    private static final String TARGET_PACKAGE = "com.stn.mobile_player";
    private static final String TARGET_ACTIVITY = "com.stn.mobile_player.ui.MainActivity";
    private static final int BLUE = Color.rgb(37, 88, 209);
    private static final int TEXT = Color.rgb(30, 35, 48);
    private static final int MUTED = Color.rgb(99, 108, 128);

    private TextView statusView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(createContentView());
    }

    @Override
    protected void onResume() {
        super.onResume();
        refreshStatus();
    }

    private View createContentView() {
        ScrollView scroll = new ScrollView(this);
        scroll.setFillViewport(true);
        scroll.setBackgroundColor(Color.rgb(246, 248, 253));

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setGravity(Gravity.CENTER_HORIZONTAL);
        root.setPadding(dp(24), dp(42), dp(24), dp(32));
        scroll.addView(root, new ScrollView.LayoutParams(
                ScrollView.LayoutParams.MATCH_PARENT,
                ScrollView.LayoutParams.WRAP_CONTENT));

        TextView logo = text("D", 38, Color.WHITE, Typeface.BOLD);
        logo.setGravity(Gravity.CENTER);
        logo.setBackground(roundRect(BLUE, 24));
        root.addView(logo, params(dp(84), dp(84), 0, 0, 0, 24));

        TextView title = text("공단기 프리패스\n바로가기", 27, TEXT, Typeface.BOLD);
        title.setGravity(Gravity.CENTER);
        title.setLineSpacing(0f, 1.08f);
        root.addView(title, params(-1, -2, 0, 0, 0, 12));

        TextView subtitle = text(
                "정식 단기PLAYER를 열고\n‘내 강의실 → 프리패스’까지 자동으로 이동해요.",
                16, MUTED, Typeface.NORMAL);
        subtitle.setGravity(Gravity.CENTER);
        subtitle.setLineSpacing(0f, 1.25f);
        root.addView(subtitle, params(-1, -2, 0, 0, 0, 24));

        statusView = text("권한 상태 확인 중…", 15, MUTED, Typeface.BOLD);
        statusView.setGravity(Gravity.CENTER);
        statusView.setPadding(dp(14), dp(12), dp(14), dp(12));
        root.addView(statusView, params(-1, -2, 0, 0, 0, 18));

        Button openButton = button("프리패스 열기", true);
        openButton.setOnClickListener(v -> openFreePass());
        root.addView(openButton, params(-1, dp(56), 0, 0, 0, 12));

        Button permissionButton = button("자동 이동 권한 설정", false);
        permissionButton.setOnClickListener(v -> openAccessibilitySettings());
        root.addView(permissionButton, params(-1, dp(54), 0, 0, 0, 22));

        TextView guide = text(
                "처음 한 번만\n설정 화면에서 ‘공단기 프리패스 자동 이동’을 켜주세요.\n\n"
                        + "이 앱은 로그인·결제·이용권·영상 데이터에 접근하지 않고, "
                        + "버튼을 누른 뒤 45초 동안 정식 단기PLAYER 화면의 "
                        + "‘내 강의실’과 ‘프리패스’ 글자만 찾아 눌러요.",
                14, MUTED, Typeface.NORMAL);
        guide.setLineSpacing(0f, 1.25f);
        guide.setPadding(dp(18), dp(18), dp(18), dp(18));
        guide.setBackground(roundRect(Color.WHITE, 18));
        root.addView(guide, params(-1, -2, 0, 0, 0, 0));

        Space bottomSpace = new Space(this);
        root.addView(bottomSpace, params(1, dp(16), 0, 0, 0, 0));
        return scroll;
    }

    private void openFreePass() {
        if (!isAccessibilityServiceEnabled()) {
            Toast.makeText(this, "먼저 자동 이동 권한을 켜주세요.", Toast.LENGTH_LONG).show();
            openAccessibilitySettings();
            return;
        }

        FreePassAccessibilityService.arm(this);

        Intent playerIntent = new Intent();
        playerIntent.setClassName(TARGET_PACKAGE, TARGET_ACTIVITY);
        playerIntent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP);
        try {
            startActivity(playerIntent);
            finish();
        } catch (ActivityNotFoundException error) {
            FreePassAccessibilityService.disarm(this);
            Toast.makeText(this, "Google Play 정식 단기PLAYER를 먼저 설치해주세요.", Toast.LENGTH_LONG).show();
            openPlayStore();
        }
    }

    private void openAccessibilitySettings() {
        try {
            startActivity(new Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS));
        } catch (ActivityNotFoundException error) {
            Toast.makeText(this, "설정 → 접근성 → 설치된 앱에서 권한을 켜주세요.", Toast.LENGTH_LONG).show();
        }
    }

    private void openPlayStore() {
        try {
            startActivity(new Intent(Intent.ACTION_VIEW,
                    Uri.parse("market://details?id=" + TARGET_PACKAGE)));
        } catch (ActivityNotFoundException error) {
            startActivity(new Intent(Intent.ACTION_VIEW,
                    Uri.parse("https://play.google.com/store/apps/details?id=" + TARGET_PACKAGE)));
        }
    }

    private boolean isAccessibilityServiceEnabled() {
        String enabled = Settings.Secure.getString(
                getContentResolver(), Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES);
        if (enabled == null) {
            return false;
        }

        TextUtils.SimpleStringSplitter splitter = new TextUtils.SimpleStringSplitter(':');
        splitter.setString(enabled);
        while (splitter.hasNext()) {
            ComponentName component = ComponentName.unflattenFromString(splitter.next());
            if (component != null
                    && getPackageName().equals(component.getPackageName())
                    && FreePassAccessibilityService.class.getName().equals(component.getClassName())) {
                return true;
            }
        }
        return false;
    }

    private void refreshStatus() {
        if (statusView == null) {
            return;
        }
        boolean enabled = isAccessibilityServiceEnabled();
        statusView.setText(enabled ? "● 자동 이동 준비 완료" : "○ 자동 이동 권한이 꺼져 있어요");
        statusView.setTextColor(enabled ? Color.rgb(23, 125, 76) : Color.rgb(184, 79, 52));
        statusView.setBackground(roundRect(
                enabled ? Color.rgb(226, 246, 234) : Color.rgb(255, 238, 232), 16));
    }

    private Button button(String label, boolean primary) {
        Button result = new Button(this);
        result.setText(label);
        result.setTextSize(16);
        result.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        result.setAllCaps(false);
        result.setTextColor(primary ? Color.WHITE : BLUE);
        result.setBackgroundTintList(ColorStateList.valueOf(
                primary ? BLUE : Color.rgb(230, 236, 252)));
        result.setGravity(Gravity.CENTER);
        return result;
    }

    private TextView text(String value, int sizeSp, int color, int style) {
        TextView result = new TextView(this);
        result.setText(value);
        result.setTextSize(sizeSp);
        result.setTextColor(color);
        result.setTypeface(Typeface.DEFAULT, style);
        return result;
    }

    private GradientDrawable roundRect(int color, int radiusDp) {
        GradientDrawable drawable = new GradientDrawable();
        drawable.setColor(color);
        drawable.setCornerRadius(dp(radiusDp));
        return drawable;
    }

    private LinearLayout.LayoutParams params(
            int width, int height, int left, int top, int right, int bottom) {
        LinearLayout.LayoutParams result = new LinearLayout.LayoutParams(width, height);
        result.setMargins(dp(left), dp(top), dp(right), dp(bottom));
        return result;
    }

    private int dp(int value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }
}

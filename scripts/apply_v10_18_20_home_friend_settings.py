from pathlib import Path
import re

root = Path('extracted')
app = root / 'app/src/main/java/com/maeummon/app'
settings = app / 'MascotWidgetSettingsActivity.java'
gradle = root / 'app/build.gradle'

text = settings.read_text(encoding='utf-8')
anchor = '        // OpenAI API key accordion. Uses the exact same preference key as the rest of MaeumMon.\n'
if anchor not in text:
    raise SystemExit('v10.18.20: settings anchor missing')

section = r'''        // Home friend controls gathered here too. Existing overlay service / Android permissions are reused.
        final LinearLayout homeBox = new LinearLayout(this);
        homeBox.setOrientation(LinearLayout.VERTICAL);
        homeBox.setBackground(round(Color.parseColor("#FFFDF8"), 24, Color.parseColor("#ECE4D4")));
        homeBox.setPadding(dp(15), dp(12), dp(15), dp(12));

        final TextView homeHeader = t("🌤️ 바탕화면 친구   ▸", 17, true);
        homeHeader.setPadding(0, dp(4), 0, dp(4));
        homeBox.addView(homeHeader, new LinearLayout.LayoutParams(-1, -2));

        final LinearLayout homeContent = new LinearLayout(this);
        homeContent.setOrientation(LinearLayout.VERTICAL);
        homeContent.setPadding(0, dp(12), 0, 0);
        homeContent.setVisibility(View.GONE);

        final android.content.SharedPreferences homePrefs = getSharedPreferences("home_friend_settings", MODE_PRIVATE);

        final Switch overlay = new Switch(this);
        overlay.setText("어린 승재를 홈화면 위에 띄우기");
        overlay.setTextSize(15); overlay.setTextColor(text);
        boolean overlayRunning = homePrefs.getBoolean("overlay_enabled", false);
        overlay.setChecked(overlayRunning);
        homeContent.addView(overlay, new LinearLayout.LayoutParams(-1, -2));

        final Switch boot = new Switch(this);
        boot.setText("휴대폰을 켜면 자동으로 나오기");
        boot.setTextSize(15); boot.setTextColor(text);
        boot.setChecked(homePrefs.getBoolean("boot_enabled", false));
        LinearLayout.LayoutParams btp = new LinearLayout.LayoutParams(-1, -2); btp.setMargins(0, dp(5), 0, 0);
        homeContent.addView(boot, btp);

        TextView homeHint = t("짧게 누르면 상담창이 열리고, 드래그하면 위치를 바꿀 수 있어. 다른 앱에서는 숨고 홈에서만 나타나게 권한을 켜줘.", 12, false);
        homeHint.setTextColor(Color.parseColor("#85839A"));
        LinearLayout.LayoutParams hhp = new LinearLayout.LayoutParams(-1, -2); hhp.setMargins(dp(3), dp(8), dp(3), dp(8));
        homeContent.addView(homeHint, hhp);

        Button usage = new Button(this);
        usage.setText("홈화면 감지 권한 열기"); usage.setAllCaps(false); usage.setTextColor(text);
        usage.setBackground(round(Color.parseColor("#F9FFFC"), 20, Color.parseColor("#D5EDE4")));
        LinearLayout.LayoutParams hup = new LinearLayout.LayoutParams(-1, dp(50)); hup.setMargins(0, dp(4), 0, 0);
        homeContent.addView(usage, hup);

        Button accessibility = new Button(this);
        accessibility.setText("최근 앱·앱 목록 숨김 감지 켜기"); accessibility.setAllCaps(false); accessibility.setTextColor(text);
        accessibility.setBackground(round(Color.parseColor("#F9FFFC"), 20, Color.parseColor("#D5EDE4")));
        LinearLayout.LayoutParams hap = new LinearLayout.LayoutParams(-1, dp(50)); hap.setMargins(0, dp(8), 0, 0);
        homeContent.addView(accessibility, hap);

        final TextView homeStatus = t("", 12, false);
        homeStatus.setTextColor(Color.parseColor("#6A9588"));
        LinearLayout.LayoutParams hsp = new LinearLayout.LayoutParams(-1, -2); hsp.setMargins(dp(3), dp(8), dp(3), 0);
        homeContent.addView(homeStatus, hsp);

        homeBox.addView(homeContent, new LinearLayout.LayoutParams(-1, -2));
        add(root, homeBox, 0, 8, 0, 10);

        homeHeader.setOnClickListener(v -> {
            boolean show = homeContent.getVisibility() != View.VISIBLE;
            homeContent.setVisibility(show ? View.VISIBLE : View.GONE);
            homeHeader.setText(show ? "🌤️ 바탕화면 친구   ▾" : "🌤️ 바탕화면 친구   ▸");
        });

        overlay.setOnCheckedChangeListener((button, checked) -> {
            homePrefs.edit().putBoolean("overlay_enabled", checked).apply();
            if (checked) {
                if (android.os.Build.VERSION.SDK_INT >= 23 && !android.provider.Settings.canDrawOverlays(this)) {
                    overlay.setChecked(false);
                    try {
                        android.content.Intent pi = new android.content.Intent(android.provider.Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                                android.net.Uri.parse("package:" + getPackageName()));
                        startActivity(pi);
                    } catch (Throwable ignored) {}
                    homeStatus.setText("먼저 ‘다른 앱 위에 표시’ 권한을 허용해줘.");
                    return;
                }
                try {
                    android.content.Intent i = new android.content.Intent(this, OverlayService.class);
                    if (android.os.Build.VERSION.SDK_INT >= 26) startForegroundService(i); else startService(i);
                    homeStatus.setText("어린 승재를 바탕화면에 띄웠어 🐣");
                } catch (Throwable e) { homeStatus.setText("바탕화면 친구를 켜지 못했어: " + e.getMessage()); }
            } else {
                try { stopService(new android.content.Intent(this, OverlayService.class)); } catch (Throwable ignored) {}
                homeStatus.setText("바탕화면 친구를 숨겼어.");
            }
        });

        boot.setOnCheckedChangeListener((button, checked) -> {
            homePrefs.edit().putBoolean("boot_enabled", checked).apply();
            // Also mirror common historical keys so the existing boot receiver keeps working across old builds.
            getSharedPreferences(AppPrefs.PREFS, MODE_PRIVATE).edit()
                    .putBoolean("overlay_boot", checked)
                    .putBoolean("overlay_boot_enabled", checked)
                    .putBoolean("start_overlay_on_boot", checked)
                    .apply();
            homeStatus.setText(checked ? "휴대폰을 켠 뒤 바탕화면 친구가 다시 나오게 저장했어." : "자동 시작을 껐어.");
        });

        usage.setOnClickListener(v -> {
            try { startActivity(new android.content.Intent(android.provider.Settings.ACTION_USAGE_ACCESS_SETTINGS)); }
            catch (Throwable e) { homeStatus.setText("사용정보 접근 설정을 열지 못했어."); }
        });

        accessibility.setOnClickListener(v -> {
            try { startActivity(new android.content.Intent(android.provider.Settings.ACTION_ACCESSIBILITY_SETTINGS)); }
            catch (Throwable e) { homeStatus.setText("접근성 설정을 열지 못했어."); }
        });

'''
text = text.replace(anchor, section + anchor, 1)
settings.write_text(text, encoding='utf-8')

# Version only. PT generation / structure is intentionally untouched.
g = gradle.read_text(encoding='utf-8')
g = re.sub(r'versionCode\s+\d+', 'versionCode 101820', g)
g = re.sub(r'versionName\s+"[^"]+"', 'versionName "10.18.20"', g)
gradle.write_text(g, encoding='utf-8')

print('Applied v10.18.20 home friend settings integration; PT structure untouched')

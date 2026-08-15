from pathlib import Path
import re

root=Path('extracted')
app=root/'app/src/main/java/com/maeummon/app'
settings=app/'MascotWidgetSettingsActivity.java'
backup=app/'BackupRestoreManager.java'
gradle=root/'app/build.gradle'

# Add newly introduced UI prefs to portable backup.
bt=backup.read_text(encoding='utf-8')
old='''            "maeummon_widget_prefs",\n            "maeummon_therapy_memory",'''
new='''            "maeummon_widget_prefs",\n            "mascot_widget_settings",\n            "home_friend_settings",\n            "maeummon_therapy_memory",'''
if old in bt:
    bt=bt.replace(old,new,1)
elif '"mascot_widget_settings"' not in bt:
    raise SystemExit('v10.18.21: backup pref anchor missing')
backup.write_text(bt,encoding='utf-8')

st=settings.read_text(encoding='utf-8')

# request codes
class_anchor='''public class MascotWidgetSettingsActivity extends Activity {\n    private int mint = Color.parseColor("#9BE2CB");'''
class_repl='''public class MascotWidgetSettingsActivity extends Activity {\n    private static final int REQ_BACKUP_SAVE = 6211;\n    private static final int REQ_BACKUP_RESTORE = 6212;\n    private int mint = Color.parseColor("#9BE2CB");'''
if class_anchor in st:
    st=st.replace(class_anchor,class_repl,1)
elif 'REQ_BACKUP_SAVE = 6211' not in st:
    raise SystemExit('v10.18.21: class anchor missing')

# Insert accordion immediately above the global save/apply button so it is at the bottom of settings.
anchor='''        Button save = new Button(this); save.setText("💚 저장하고 바로 적용"); save.setTextSize(16); save.setTextColor(Color.WHITE);'''
section=r'''        // Portable full backup / restore. Reuses the original BackupRestoreManager format.
        final LinearLayout backupBox = new LinearLayout(this);
        backupBox.setOrientation(LinearLayout.VERTICAL);
        backupBox.setBackground(round(Color.parseColor("#F8FBFF"), 24, Color.parseColor("#DCE8F2")));
        backupBox.setPadding(dp(15), dp(12), dp(15), dp(12));

        final TextView backupHeader = t("💾 백업 · 복원   ▸", 17, true);
        backupHeader.setPadding(0, dp(4), 0, dp(4));
        backupBox.addView(backupHeader, new LinearLayout.LayoutParams(-1, -2));

        final LinearLayout backupContent = new LinearLayout(this);
        backupContent.setOrientation(LinearLayout.VERTICAL);
        backupContent.setPadding(0, dp(11), 0, 0);
        backupContent.setVisibility(View.GONE);

        TextView backupHelp = t("상담 원문·마음 PT·왕관·훈련 진행도·결과·다마고치/위젯 설정을 JSON 하나로 저장하고 다시 불러와. OpenAI/Typecast API Key와 일기 PIN은 보안을 위해 백업하지 않아.", 12, false);
        backupHelp.setTextColor(Color.parseColor("#777C8E"));
        backupContent.addView(backupHelp, new LinearLayout.LayoutParams(-1, -2));

        LinearLayout backupButtons = new LinearLayout(this);
        backupButtons.setOrientation(LinearLayout.HORIZONTAL);
        Button backupSave = new Button(this);
        backupSave.setText("☁️ 전체 백업 저장"); backupSave.setAllCaps(false); backupSave.setTextColor(text);
        backupSave.setBackground(round(Color.WHITE, 20, Color.parseColor("#D5E3ED")));
        Button backupRestore = new Button(this);
        backupRestore.setText("🌙 백업 파일 복원"); backupRestore.setAllCaps(false); backupRestore.setTextColor(Color.WHITE);
        backupRestore.setBackground(round(mint, 20, Color.parseColor("#7DCBB0")));
        LinearLayout.LayoutParams bb1 = new LinearLayout.LayoutParams(0, dp(52), 1f); bb1.setMargins(0, dp(10), dp(5), 0);
        LinearLayout.LayoutParams bb2 = new LinearLayout.LayoutParams(0, dp(52), 1f); bb2.setMargins(dp(5), dp(10), 0, 0);
        backupButtons.addView(backupSave, bb1); backupButtons.addView(backupRestore, bb2);
        backupContent.addView(backupButtons, new LinearLayout.LayoutParams(-1, -2));

        TextView backupHint = t("앱을 바꾸거나 다시 설치하기 전에는 한 번 저장해두면 제일 안전해 💚", 12, false);
        backupHint.setTextColor(Color.parseColor("#8D91A0"));
        LinearLayout.LayoutParams bhp = new LinearLayout.LayoutParams(-1, -2); bhp.setMargins(dp(3), dp(8), dp(3), 0);
        backupContent.addView(backupHint, bhp);

        backupBox.addView(backupContent, new LinearLayout.LayoutParams(-1, -2));
        add(root, backupBox, 0, 10, 0, 8);

        backupHeader.setOnClickListener(v -> {
            boolean show = backupContent.getVisibility() != View.VISIBLE;
            backupContent.setVisibility(show ? View.VISIBLE : View.GONE);
            backupHeader.setText(show ? "💾 백업 · 복원   ▾" : "💾 백업 · 복원   ▸");
        });
        backupSave.setOnClickListener(v -> openBackupCreateDocument());
        backupRestore.setOnClickListener(v -> new android.app.AlertDialog.Builder(this)
                .setTitle("백업을 복원할까?")
                .setMessage("현재 상담/PT 데이터가 백업 파일 내용으로 교체돼. 필요한 현재 데이터가 있다면 먼저 백업 저장을 해줘.")
                .setPositiveButton("복원 파일 선택", (d,w) -> openBackupRestoreDocument())
                .setNegativeButton("취소", null).show());

'''
if anchor not in st:
    raise SystemExit('v10.18.21: global save anchor missing')
st=st.replace(anchor,section+anchor,1)

# Add helper/activity result methods before typecast helper if available.
method_anchor='''    private String typecastSummary() {'''
methods=r'''    private void openBackupCreateDocument() {
        android.content.Intent intent = new android.content.Intent(android.content.Intent.ACTION_CREATE_DOCUMENT);
        intent.addCategory(android.content.Intent.CATEGORY_OPENABLE);
        intent.setType("application/json");
        String name = "MaeumMon_backup_" + new java.text.SimpleDateFormat("yyyyMMdd_HHmm", java.util.Locale.KOREA).format(new java.util.Date()) + ".json";
        intent.putExtra(android.content.Intent.EXTRA_TITLE, name);
        startActivityForResult(intent, REQ_BACKUP_SAVE);
    }

    private void openBackupRestoreDocument() {
        android.content.Intent intent = new android.content.Intent(android.content.Intent.ACTION_OPEN_DOCUMENT);
        intent.addCategory(android.content.Intent.CATEGORY_OPENABLE);
        intent.setType("application/json");
        startActivityForResult(intent, REQ_BACKUP_RESTORE);
    }

    @Override protected void onActivityResult(int requestCode, int resultCode, android.content.Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (resultCode != RESULT_OK || data == null || data.getData() == null) return;
        android.net.Uri uri = data.getData();
        try {
            if (requestCode == REQ_BACKUP_SAVE) {
                BackupRestoreManager.exportToUri(this, uri);
                Toast.makeText(this, "마음몬 전체 백업 저장 완료 ☁️", Toast.LENGTH_LONG).show();
            } else if (requestCode == REQ_BACKUP_RESTORE) {
                BackupRestoreManager.restoreFromUri(this, uri);
                try { LiveMindManager.onMindChanged(this); } catch (Throwable ignored) {}
                try { MaeumMonClockWidget.refreshAll(this); } catch (Throwable ignored) {}
                try {
                    android.content.SharedPreferences hp = getSharedPreferences("home_friend_settings", MODE_PRIVATE);
                    if (hp.getBoolean("overlay_enabled", false) && android.provider.Settings.canDrawOverlays(this)) {
                        stopService(new android.content.Intent(this, OverlayService.class));
                        android.content.Intent svc = new android.content.Intent(this, OverlayService.class);
                        if (android.os.Build.VERSION.SDK_INT >= 26) startForegroundService(svc); else startService(svc);
                    }
                } catch (Throwable ignored) {}
                Toast.makeText(this, "백업 복원 완료 🌙 설정과 마음 PT를 다시 불러왔어.", Toast.LENGTH_LONG).show();
                recreate();
            }
        } catch (Exception e) {
            Toast.makeText(this, "백업 처리 실패: " + e.getMessage(), Toast.LENGTH_LONG).show();
        }
    }

'''
if method_anchor not in st:
    raise SystemExit('v10.18.21: method anchor missing')
st=st.replace(method_anchor,methods+method_anchor,1)
settings.write_text(st,encoding='utf-8')

# Version bump only; no PT-generation policy change.
gt=gradle.read_text(encoding='utf-8')
gt=re.sub(r'versionCode\s+\d+', 'versionCode 101821', gt, count=1)
gt=re.sub(r'versionName\s+"[^"]+"', 'versionName "10.18.21"', gt, count=1)
gradle.write_text(gt,encoding='utf-8')
print('Applied v10.18.21 backup restore settings tab')

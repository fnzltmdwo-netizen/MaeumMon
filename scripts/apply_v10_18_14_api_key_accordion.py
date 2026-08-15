from pathlib import Path
import re

root = Path('extracted')
app = root / 'app/src/main/java/com/maeummon/app'
settings = app / 'MascotWidgetSettingsActivity.java'
gradle = root / 'app/build.gradle'

text = settings.read_text(encoding='utf-8')

# Add the collapsible OpenAI API Key section just before the main Save button.
anchor = '        Button save = new Button(this); save.setText("💚 저장하고 바로 적용");'
if anchor not in text:
    raise SystemExit('v10.18.14: settings save anchor missing')

section = r'''        // OpenAI API key accordion. Uses the exact same preference key as the rest of MaeumMon.
        final android.content.SharedPreferences appPrefs = getSharedPreferences(AppPrefs.PREFS, MODE_PRIVATE);
        final LinearLayout apiBox = new LinearLayout(this);
        apiBox.setOrientation(LinearLayout.VERTICAL);
        apiBox.setBackground(round(Color.WHITE, 24, Color.parseColor("#E7E3EF")));
        apiBox.setPadding(dp(15), dp(12), dp(15), dp(12));

        final TextView apiHeader = t("🔑 OpenAI API Key 설정   ▸", 17, true);
        apiHeader.setPadding(0, dp(4), 0, dp(4));
        apiBox.addView(apiHeader, new LinearLayout.LayoutParams(-1, -2));

        final LinearLayout apiContent = new LinearLayout(this);
        apiContent.setOrientation(LinearLayout.VERTICAL);
        apiContent.setPadding(0, dp(12), 0, 0);
        apiContent.setVisibility(View.GONE);

        final TextView apiStatus = t("", 13, false);
        apiStatus.setTextColor(Color.parseColor("#85839A"));
        apiContent.addView(apiStatus, new LinearLayout.LayoutParams(-1, -2));

        final EditText apiInput = new EditText(this);
        apiInput.setSingleLine(true);
        apiInput.setTextSize(14);
        apiInput.setTextColor(text);
        apiInput.setHint("새 OpenAI API Key를 입력해줘");
        apiInput.setHintTextColor(Color.parseColor("#AAA8B8"));
        apiInput.setInputType(android.text.InputType.TYPE_CLASS_TEXT | android.text.InputType.TYPE_TEXT_VARIATION_PASSWORD);
        apiInput.setPadding(dp(14), dp(10), dp(14), dp(10));
        apiInput.setBackground(round(Color.parseColor("#FAF8FF"), 18, Color.parseColor("#E4DFF2")));
        LinearLayout.LayoutParams aip = new LinearLayout.LayoutParams(-1, dp(50));
        aip.setMargins(0, dp(10), 0, dp(8));
        apiContent.addView(apiInput, aip);

        TextView apiHint = t("저장된 키 원문은 화면에 다시 표시하지 않아. 새 키를 넣고 저장하면 기존 키를 교체해.", 12, false);
        apiHint.setTextColor(Color.parseColor("#9693A5"));
        apiContent.addView(apiHint, new LinearLayout.LayoutParams(-1, -2));

        LinearLayout apiButtons = new LinearLayout(this);
        apiButtons.setOrientation(LinearLayout.HORIZONTAL);
        Button apiSave = new Button(this);
        apiSave.setText("🔐 키 저장");
        apiSave.setAllCaps(false);
        apiSave.setTextColor(Color.WHITE);
        apiSave.setBackground(round(mint, 20, Color.parseColor("#7DCBB0")));
        Button apiClear = new Button(this);
        apiClear.setText("키 지우기");
        apiClear.setAllCaps(false);
        apiClear.setTextColor(text);
        apiClear.setBackground(round(Color.parseColor("#FFF0F2"), 20, Color.parseColor("#F2D4D9")));
        LinearLayout.LayoutParams ab1 = new LinearLayout.LayoutParams(0, dp(48), 1f);
        ab1.setMargins(0, dp(10), dp(5), 0);
        LinearLayout.LayoutParams ab2 = new LinearLayout.LayoutParams(0, dp(48), 1f);
        ab2.setMargins(dp(5), dp(10), 0, 0);
        apiButtons.addView(apiSave, ab1);
        apiButtons.addView(apiClear, ab2);
        apiContent.addView(apiButtons, new LinearLayout.LayoutParams(-1, -2));
        apiBox.addView(apiContent, new LinearLayout.LayoutParams(-1, -2));
        add(root, apiBox, 0, 8, 0, 6);

        final Runnable refreshApiStatus = () -> {
            String key = appPrefs.getString(AppPrefs.KEY_API_KEY, "");
            if (key == null || key.trim().isEmpty()) {
                apiStatus.setText("현재 상태 · API Key 없음");
            } else {
                String k = key.trim();
                String tail = k.length() > 4 ? k.substring(k.length() - 4) : "••••";
                apiStatus.setText("현재 상태 · 등록됨  ·  ••••••••" + tail);
            }
        };
        refreshApiStatus.run();

        apiHeader.setOnClickListener(v -> {
            boolean show = apiContent.getVisibility() != View.VISIBLE;
            apiContent.setVisibility(show ? View.VISIBLE : View.GONE);
            apiHeader.setText(show ? "🔑 OpenAI API Key 설정   ▾" : "🔑 OpenAI API Key 설정   ▸");
        });

        apiSave.setOnClickListener(v -> {
            String key = apiInput.getText().toString().trim();
            if (key.isEmpty()) {
                Toast.makeText(this, "새 API Key를 입력해줘.", Toast.LENGTH_SHORT).show();
                return;
            }
            appPrefs.edit().putString(AppPrefs.KEY_API_KEY, key).apply();
            apiInput.setText("");
            refreshApiStatus.run();
            try { LiveMindManager.onMindChanged(this); } catch (Throwable ignored) {}
            Toast.makeText(this, "OpenAI API Key 저장 완료 🔐", Toast.LENGTH_SHORT).show();
        });

        apiClear.setOnClickListener(v -> {
            appPrefs.edit().remove(AppPrefs.KEY_API_KEY).apply();
            apiInput.setText("");
            refreshApiStatus.run();
            try { LiveMindManager.onMindChanged(this); } catch (Throwable ignored) {}
            Toast.makeText(this, "저장된 API Key를 지웠어.", Toast.LENGTH_SHORT).show();
        });

'''
text = text.replace(anchor, section + anchor, 1)
settings.write_text(text, encoding='utf-8')

# Version bump.
g = gradle.read_text(encoding='utf-8')
g, n1 = re.subn(r'versionCode\s+\d+', 'versionCode 101814', g, count=1)
g, n2 = re.subn(r'versionName\s+"[^"]+"', 'versionName "10.18.14"', g, count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit('v10.18.14: gradle version anchor missing')
gradle.write_text(g, encoding='utf-8')

print('Applied v10.18.14 collapsible OpenAI API Key settings')

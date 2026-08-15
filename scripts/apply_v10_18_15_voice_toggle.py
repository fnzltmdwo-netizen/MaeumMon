from pathlib import Path
import re

root = Path('extracted')
app = root / 'app/src/main/java/com/maeummon/app'
settings = app / 'MascotWidgetSettingsActivity.java'
gradle = root / 'app/build.gradle'

text = settings.read_text(encoding='utf-8')

# Add a voice toggle backed by the EXISTING overlay voice preference.
# OverlayService already reads AppPrefs.KEY_OVERLAY_VOICE and calls TtsManager.speak(...),
# so we deliberately do not replace the existing tap/TTS path.
anchor = '        root.addView(t("💬 다마고치 말풍선 길이", 17, true));\n'
if anchor not in text:
    raise SystemExit('v10.18.15: bubble section anchor missing')

voice_ui = '''        final android.content.SharedPreferences voicePrefs = getSharedPreferences(AppPrefs.PREFS, MODE_PRIVATE);\n        final Switch touchVoice = new Switch(this);\n        touchVoice.setText("🔊 다마고치 터치 음성");\n        touchVoice.setTextSize(17);\n        touchVoice.setTextColor(text);\n        touchVoice.setChecked(voicePrefs.getBoolean(AppPrefs.KEY_OVERLAY_VOICE, false));\n        addCard(root, touchVoice);\n        TextView voiceHelp = t("켜두면 다마고치를 눌렀을 때 지금 말풍선에 나온 말을 기존 음성 엔진으로 읽어줘. 기존 Typecast/TTS 설정은 그대로 사용해.", 13, false);\n        voiceHelp.setTextColor(Color.parseColor("#85839A"));\n        add(root, voiceHelp, 10, 6, 6, 20);\n\n'''
text = text.replace(anchor, voice_ui + anchor, 1)

# Persist the voice toggle together with the existing mascot/widget settings.
save_anchor = '            MascotWidgetPrefs.save(this, young.isChecked(), bval, wval);\n'
if save_anchor not in text:
    raise SystemExit('v10.18.15: save listener anchor missing')
text = text.replace(
    save_anchor,
    save_anchor + '            voicePrefs.edit().putBoolean(AppPrefs.KEY_OVERLAY_VOICE, touchVoice.isChecked()).apply();\n',
    1,
)

# Helpful confirmation should mention voice too.
text = text.replace(
    'Toast.makeText(this, "다마고치와 위젯에 바로 적용했어 🐣", Toast.LENGTH_SHORT).show();',
    'Toast.makeText(this, "다마고치·위젯·터치 음성에 바로 적용했어 🐣🔊", Toast.LENGTH_SHORT).show();',
    1,
)

settings.write_text(text, encoding='utf-8')

# Version bump only. Existing OverlayService click/TtsManager behavior remains untouched.
g = gradle.read_text(encoding='utf-8')
g, n1 = re.subn(r'versionCode\s+\d+', 'versionCode 101815', g, count=1)
g, n2 = re.subn(r'versionName\s+"[^"]+"', 'versionName "10.18.15"', g, count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit('v10.18.15: gradle version anchor missing')
gradle.write_text(g, encoding='utf-8')

print('Applied v10.18.15 voice toggle while preserving existing mascot tap/TTS path')

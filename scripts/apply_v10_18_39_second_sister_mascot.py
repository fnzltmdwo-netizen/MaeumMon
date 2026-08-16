from pathlib import Path
import re

root = Path('extracted')
app = root / 'app/src/main/java/com/maeummon/app'
res = root / 'app/src/main/res'
drawable = res / 'drawable'
layout_dir = res / 'layout'
gradle = root / 'app/build.gradle'

# v10.18.39
# Replace the Strawberry Moon rabbit with the approved second-sister-inspired
# silver-haired moon mage mascot. Counseling / PT logic is untouched.

# -----------------------------------------------------------------------------
# 1) Main mascot vector: silver twin tails, green eyes, pointed ears,
#    white/gold cape, red jewel accents and a crescent staff.
# -----------------------------------------------------------------------------
(drawable / 'second_sister_moon_mage.xml').write_text('''<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="190dp" android:height="230dp"
    android:viewportWidth="190" android:viewportHeight="230">

    <!-- soft moon aura -->
    <path android:fillColor="#24FFD1DC" android:pathData="M95,7 C145,7 178,47 178,103 C178,165 145,216 95,216 C45,216 12,165 12,103 C12,47 45,7 95,7 Z"/>

    <!-- twin tails behind body -->
    <path android:fillColor="#E8E3EE" android:pathData="M52,55 C31,70 23,105 31,159 C36,190 46,203 55,211 C45,175 53,139 64,110 C75,80 68,61 52,55 Z"/>
    <path android:fillColor="#E8E3EE" android:pathData="M138,55 C159,70 167,105 159,159 C154,190 144,203 135,211 C145,175 137,139 126,110 C115,80 122,61 138,55 Z"/>
    <path android:fillColor="#B9AEC8" android:pathData="M48,71 C36,96 36,139 45,176 C42,142 50,112 60,91 Z"/>
    <path android:fillColor="#B9AEC8" android:pathData="M142,71 C154,96 154,139 145,176 C148,142 140,112 130,91 Z"/>

    <!-- pointed ears -->
    <path android:fillColor="#F4D8CF" android:pathData="M57,73 L19,85 L58,94 Z"/>
    <path android:fillColor="#F4D8CF" android:pathData="M133,73 L171,85 L132,94 Z"/>
    <path android:fillColor="#C99796" android:pathData="M49,80 L29,85 L50,89 Z"/>
    <path android:fillColor="#C99796" android:pathData="M141,80 L161,85 L140,89 Z"/>

    <!-- head -->
    <path android:fillColor="#F7E7DE" android:pathData="M52,76 C52,47 70,29 95,29 C120,29 138,47 138,76 C138,107 121,123 95,123 C69,123 52,107 52,76 Z"/>

    <!-- silver hair cap and long front pieces -->
    <path android:fillColor="#EEEAF2" android:pathData="M50,73 C49,43 68,21 95,21 C122,21 141,44 140,74 C127,55 114,47 95,47 C76,47 63,55 50,73 Z"/>
    <path android:fillColor="#EEEAF2" android:pathData="M58,59 C51,87 54,128 66,154 C67,118 73,87 83,59 Z"/>
    <path android:fillColor="#EEEAF2" android:pathData="M132,59 C139,87 136,128 124,154 C123,118 117,87 107,59 Z"/>
    <path android:fillColor="#D3CCD9" android:pathData="M94,23 C87,38 85,52 85,69 L95,56 L105,69 C105,50 103,36 94,23 Z"/>

    <!-- eyes -->
    <path android:fillColor="#5B9B78" android:pathData="M69,79 C69,70 77,67 84,72 C90,77 85,91 77,91 C72,91 69,86 69,79 Z"/>
    <path android:fillColor="#5B9B78" android:pathData="M106,79 C106,70 114,67 121,72 C127,77 122,91 114,91 C109,91 106,86 106,79 Z"/>
    <path android:fillColor="#173B31" android:pathData="M75,80 C75,75 79,74 81,78 C82,83 78,86 76,84 Z"/>
    <path android:fillColor="#173B31" android:pathData="M112,80 C112,75 116,74 118,78 C119,83 115,86 113,84 Z"/>
    <path android:fillColor="#FFFFFF" android:pathData="M77,75 C79,73 82,75 81,77 C80,79 77,78 77,75 Z"/>
    <path android:fillColor="#FFFFFF" android:pathData="M114,75 C116,73 119,75 118,77 C117,79 114,78 114,75 Z"/>

    <!-- tiny calm smile -->
    <path android:strokeColor="#986C72" android:strokeWidth="1.5" android:fillColor="@android:color/transparent" android:pathData="M88,101 C93,105 98,105 103,101"/>

    <!-- red earrings -->
    <path android:fillColor="#D34F69" android:pathData="M48,89 C45,96 47,102 51,105 C55,101 56,95 52,89 Z"/>
    <path android:fillColor="#D34F69" android:pathData="M138,89 C135,96 137,102 141,105 C145,101 146,95 142,89 Z"/>
    <path android:fillColor="#F1C57A" android:pathData="M48,86 C48,83 52,83 52,86 C52,89 48,89 48,86 Z"/>
    <path android:fillColor="#F1C57A" android:pathData="M138,86 C138,83 142,83 142,86 C142,89 138,89 138,86 Z"/>

    <!-- white/gold cape and body -->
    <path android:fillColor="#FFF8F0" android:pathData="M61,121 C72,113 83,111 95,111 C107,111 118,113 129,121 L145,181 C131,191 116,187 106,176 L95,159 L84,176 C74,187 59,191 45,181 Z"/>
    <path android:strokeColor="#D7B35F" android:strokeWidth="4" android:fillColor="@android:color/transparent" android:pathData="M49,177 C65,188 79,175 95,158 C111,175 125,188 141,177"/>
    <path android:fillColor="#2E2B38" android:pathData="M78,126 L112,126 L112,137 L78,137 Z"/>
    <path android:fillColor="#FFF8F0" android:pathData="M82,118 L108,118 L108,130 L82,130 Z"/>
    <path android:strokeColor="#D7B35F" android:strokeWidth="3" android:fillColor="@android:color/transparent" android:pathData="M84,119 L106,119"/>

    <!-- legs and boots -->
    <path android:fillColor="#373445" android:pathData="M76,175 L93,175 L91,210 L75,210 Z"/>
    <path android:fillColor="#373445" android:pathData="M97,175 L114,175 L115,210 L99,210 Z"/>
    <path android:fillColor="#766354" android:pathData="M73,201 L92,201 L91,219 L72,219 Z"/>
    <path android:fillColor="#766354" android:pathData="M98,201 L117,201 L118,219 L99,219 Z"/>

    <!-- crescent staff -->
    <path android:strokeColor="#874A49" android:strokeWidth="5" android:fillColor="@android:color/transparent" android:pathData="M132,63 L165,196"/>
    <path android:fillColor="#D6B25D" android:pathData="M119,52 C119,36 132,25 147,28 C137,31 131,39 131,49 C131,59 138,66 148,68 C134,72 119,67 119,52 Z"/>
    <path android:fillColor="#C83D58" android:pathData="M139,42 C139,34 145,29 152,31 C160,34 161,44 155,49 C148,55 139,50 139,42 Z"/>
    <path android:fillColor="#FFBAC9" android:pathData="M146,35 C149,33 152,35 151,38 C150,40 146,39 146,35 Z"/>

    <!-- strawberry moon sparkles -->
    <path android:fillColor="#F7D983" android:pathData="M23,44 L26,50 L32,53 L26,56 L23,62 L20,56 L14,53 L20,50 Z"/>
    <path android:fillColor="#FF8EAA" android:pathData="M163,120 L166,126 L172,129 L166,132 L163,138 L160,132 L154,129 L160,126 Z"/>
</vector>
''', encoding='utf-8')

# -----------------------------------------------------------------------------
# 2) Replace rabbit references throughout actual layouts / Java surfaces.
# -----------------------------------------------------------------------------
for p in layout_dir.glob('*.xml'):
    text = p.read_text(encoding='utf-8')
    original = text
    text = text.replace('@drawable/strawberry_bunny', '@drawable/second_sister_moon_mage')
    text = text.replace('strawberryBunnyHero', 'secondSisterHero')
    text = text.replace('스트로베리문 토끼', '스트로베리문 둘째동생')
    if text != original:
        p.write_text(text, encoding='utf-8')

# Settings / mascot wording. Keep existing functionality; only identity changes.
settings = app / 'MascotWidgetSettingsActivity.java'
if settings.exists():
    s = settings.read_text(encoding='utf-8')
    repl = {
        '🐰🌙 스트로베리문 친구 · 위젯': '🌙✨ 둘째동생 · 위젯',
        '토끼 친구 말투': '둘째동생 말투',
        '🐰 토끼 친구를 홈화면에 띄우기': '🌙 둘째동생을 홈화면에 띄우기',
        '스트로베리문 토끼가 놀러왔어 🐰🌙': '둘째동생이 곁에 왔어 🌙✨',
        '토끼 친구': '둘째동생',
        '스트로베리문 토끼': '둘째동생',
        '🐰': '🌙'
    }
    for old, new in repl.items():
        s = s.replace(old, new)
    settings.write_text(s, encoding='utf-8')

# Shared emoji vocabulary: moon mage identity instead of bunny.
tokens = app / 'EmojiDesignTokens.java'
if tokens.exists():
    t = tokens.read_text(encoding='utf-8')
    if 'public static final String MASCOT' not in t:
        t = t.replace('public static final String CELEBRATE = "✨";', 'public static final String CELEBRATE = "✨";\n    public static final String MASCOT = "🌙✨";')
    tokens.write_text(t, encoding='utf-8')

# Current visible PT hero title gets the moon-sister cue while preserving crown priority.
pt = app / 'MindPtActivity.java'
if pt.exists():
    p = pt.read_text(encoding='utf-8')
    p = p.replace('"👑 " + OhStylePtDisplay.title', '"👑🌙 " + OhStylePtDisplay.title')
    p = p.replace('"👑 " + s.muscle', '"👑🌙 " + s.muscle')
    pt.write_text(p, encoding='utf-8')

# -----------------------------------------------------------------------------
# 3) Version bump.
# -----------------------------------------------------------------------------
g = gradle.read_text(encoding='utf-8')
g = re.sub(r'versionCode\s+\d+', 'versionCode 101839', g)
g = re.sub(r'versionName\s+"[^"]+"', 'versionName "10.18.39"', g)
gradle.write_text(g, encoding='utf-8')

print('Applied v10.18.39: Strawberry Moon second-sister moon mage mascot; rabbit removed')

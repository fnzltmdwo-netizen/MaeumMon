from pathlib import Path
import re

root = Path('extracted')
app = root / 'app/src/main/java/com/maeummon/app'
res = root / 'app/src/main/res'
values = res / 'values'
drawable = res / 'drawable'
layout_dir = res / 'layout'
gradle = root / 'app/build.gradle'

# v10.18.38
# REAL visual overhaul: Strawberry Moon universe + rabbit mascot.
# Counseling / formulation / PT decision logic is intentionally untouched.

# -----------------------------------------------------------------------------
# 1. Strawberry Moon palette
# -----------------------------------------------------------------------------
(values / 'colors.xml').write_text('''<resources>
    <color name="cream">#160B18</color>
    <color name="sage">#FF7399</color>
    <color name="sage_dark">#D94F7A</color>
    <color name="brown">#FFF4F7</color>
    <color name="soft_pink">#4A2037</color>
    <color name="white">#FFFFFFFF</color>
    <color name="soft_gray">#241329</color>
    <color name="bubble_user">#6B2948</color>
    <color name="bubble_ai">#FFF1F4</color>
    <color name="soft_lavender">#39213F</color>
    <color name="soft_peach">#5A2A3C</color>
    <color name="soft_yellow">#5B432B</color>
    <color name="soft_mint">#263B38</color>
    <color name="moon_pink">#FF7697</color>
    <color name="moon_light">#FFD1DC</color>
    <color name="night">#110812</color>
    <color name="rose_gold">#F1C57A</color>
</resources>
''', encoding='utf-8')

# -----------------------------------------------------------------------------
# 2. Core visual assets, code-drawn so every build carries the new identity.
# -----------------------------------------------------------------------------
(drawable / 'bg_strawberry_moon.xml').write_text('''<?xml version="1.0" encoding="utf-8"?>
<layer-list xmlns:android="http://schemas.android.com/apk/res/android">
    <item>
        <shape android:shape="rectangle">
            <gradient android:angle="270" android:startColor="#0B060E" android:centerColor="#21101D" android:endColor="#3D162C"/>
        </shape>
    </item>
    <item android:top="32dp" android:left="34dp" android:right="34dp" android:bottom="260dp">
        <shape android:shape="oval">
            <gradient android:type="radial" android:gradientRadius="260dp" android:centerX="0.48" android:centerY="0.45" android:startColor="#FFFFD9E1" android:centerColor="#FFFF789C" android:endColor="#BDE74F79"/>
            <stroke android:width="2dp" android:color="#66FFD8E2"/>
        </shape>
    </item>
</layer-list>
''', encoding='utf-8')

(drawable / 'bg_cosmic_gradient.xml').write_text('''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <gradient android:angle="270" android:startColor="#100812" android:centerColor="#28101F" android:endColor="#42192F"/>
</shape>
''', encoding='utf-8')

# Simple in-app vector identity based on the approved Strawberry Moon rabbit:
# white rabbit, long pink ears, strawberry-pink cape, gold crescent clasp.
(drawable / 'strawberry_bunny.xml').write_text('''<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="180dp" android:height="220dp"
    android:viewportWidth="180" android:viewportHeight="220">
    <!-- ears -->
    <path android:fillColor="#FFF7F7" android:pathData="M55,82 C38,54 34,14 49,8 C64,3 72,45 70,77 Z"/>
    <path android:fillColor="#FFF7F7" android:pathData="M109,77 C107,42 116,3 132,8 C147,14 141,57 124,84 Z"/>
    <path android:fillColor="#FF9DB5" android:pathData="M54,67 C46,44 45,21 51,18 C58,16 63,43 62,66 Z"/>
    <path android:fillColor="#FF9DB5" android:pathData="M117,66 C117,41 123,17 130,18 C136,21 132,47 124,69 Z"/>
    <!-- head -->
    <path android:fillColor="#FFF9F9" android:pathData="M40,96 C40,72 61,61 90,61 C120,61 141,74 140,99 C139,124 120,135 90,136 C60,135 40,122 40,96 Z"/>
    <!-- eyes -->
    <path android:fillColor="#6E203F" android:pathData="M63,94 C63,86 70,82 77,86 C83,91 79,104 71,104 C66,104 63,100 63,94 Z"/>
    <path android:fillColor="#6E203F" android:pathData="M104,94 C104,86 111,82 118,86 C124,91 120,104 112,104 C107,104 104,100 104,94 Z"/>
    <path android:fillColor="#FFFFFF" android:pathData="M69,90 C69,87 73,87 74,90 C74,93 70,93 69,90 Z"/>
    <path android:fillColor="#FFFFFF" android:pathData="M110,90 C110,87 114,87 115,90 C115,93 111,93 110,90 Z"/>
    <!-- nose / mouth -->
    <path android:fillColor="#F16E91" android:pathData="M86,105 L94,105 L90,111 Z"/>
    <path android:strokeColor="#A74662" android:strokeWidth="1.8" android:fillColor="@android:color/transparent" android:pathData="M90,111 C88,116 84,117 81,114 M90,111 C92,116 96,117 99,114"/>
    <!-- body -->
    <path android:fillColor="#FFF8F8" android:pathData="M55,129 C63,119 76,118 90,118 C105,118 118,120 126,132 C137,148 132,195 119,205 C108,214 72,214 61,205 C48,194 44,147 55,129 Z"/>
    <!-- cape -->
    <path android:fillColor="#D95076" android:pathData="M48,129 C61,120 75,119 90,122 C105,119 120,120 132,129 L148,181 C132,189 119,184 109,175 L90,150 L70,175 C59,184 47,188 32,180 Z"/>
    <path android:strokeColor="#F1C57A" android:strokeWidth="2" android:fillColor="@android:color/transparent" android:pathData="M34,179 C52,188 65,178 73,169 M146,180 C129,188 116,178 108,169"/>
    <!-- crescent clasp -->
    <path android:fillColor="#F5D27E" android:pathData="M84,127 C84,117 94,111 103,116 C96,116 92,121 92,127 C92,133 96,137 102,138 C93,142 84,137 84,127 Z"/>
    <!-- strawberry accent -->
    <path android:fillColor="#FF5C7E" android:pathData="M127,72 C135,68 143,75 139,84 C136,91 129,96 125,98 C121,93 117,84 119,78 C120,74 123,72 127,72 Z"/>
    <path android:fillColor="#6E9B62" android:pathData="M124,72 L127,66 L130,72 L136,69 L134,76 L119,76 Z"/>
</vector>
''', encoding='utf-8')

shared = {
'bg_card.xml': '''<?xml version="1.0" encoding="utf-8"?><shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle"><solid android:color="#DC2A1429"/><corners android:radius="28dp"/><stroke android:width="1dp" android:color="#66FFADC3"/><padding android:left="18dp" android:top="17dp" android:right="18dp" android:bottom="17dp"/></shape>''',
'bg_input.xml': '''<?xml version="1.0" encoding="utf-8"?><shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle"><solid android:color="#E5351930"/><corners android:radius="23dp"/><stroke android:width="1dp" android:color="#66F8A7BC"/></shape>''',
'bg_button.xml': '''<?xml version="1.0" encoding="utf-8"?><shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle"><gradient android:angle="0" android:startColor="#FF4F82" android:centerColor="#FF6D98" android:endColor="#FF8AAA"/><corners android:radius="28dp"/><stroke android:width="1dp" android:color="#FFD2DD"/></shape>''',
'bg_nav_chip.xml': '''<?xml version="1.0" encoding="utf-8"?><shape xmlns:android="http://schemas.android.com/apk/res/android"><solid android:color="#E0251327"/><corners android:radius="24dp"/><stroke android:width="1dp" android:color="#55FFB3C8"/></shape>''',
'bg_nav_growth.xml': '''<?xml version="1.0" encoding="utf-8"?><shape xmlns:android="http://schemas.android.com/apk/res/android"><gradient android:angle="0" android:startColor="#752D4E" android:endColor="#A13E63"/><corners android:radius="24dp"/><stroke android:width="1dp" android:color="#D999AD"/></shape>''',
'bg_pt_crown.xml': '''<?xml version="1.0" encoding="utf-8"?><shape xmlns:android="http://schemas.android.com/apk/res/android"><gradient android:angle="0" android:startColor="#E83A2133" android:centerColor="#E85B3A3D" android:endColor="#E83D2235"/><corners android:radius="27dp"/><stroke android:width="2dp" android:color="#F4C96B"/></shape>''',
'bg_pt_crown_selected.xml': '''<?xml version="1.0" encoding="utf-8"?><shape xmlns:android="http://schemas.android.com/apk/res/android"><gradient android:angle="0" android:startColor="#A43F61" android:centerColor="#C84F74" android:endColor="#E66489"/><corners android:radius="27dp"/><stroke android:width="3dp" android:color="#FFD978"/></shape>''',
'bg_strawberry_glass.xml': '''<?xml version="1.0" encoding="utf-8"?><shape xmlns:android="http://schemas.android.com/apk/res/android"><solid android:color="#DD291328"/><corners android:radius="30dp"/><stroke android:width="1dp" android:color="#88FFACC2"/></shape>'''
}
for name, body in shared.items():
    (drawable / name).write_text(body, encoding='utf-8')

# -----------------------------------------------------------------------------
# 3. Apply the universe to real layouts.
# -----------------------------------------------------------------------------
for p in layout_dir.glob('*.xml'):
    t = p.read_text(encoding='utf-8')
    original = t
    t = t.replace('android:background="@color/cream"', 'android:background="@drawable/bg_cosmic_gradient"')
    t = t.replace('android:background="#FBFAFF"', 'android:background="@drawable/bg_cosmic_gradient"')
    t = t.replace('android:background="#F8F6F1"', 'android:background="@drawable/bg_cosmic_gradient"')
    # The primary/home spaces get the full Strawberry Moon centerpiece.
    if p.name in ('activity_main.xml', 'activity_home.xml', 'activity_my_room.xml', 'activity_room.xml'):
        t = t.replace('android:background="@drawable/bg_cosmic_gradient"', 'android:background="@drawable/bg_strawberry_moon"', 1)
    if t != original:
        p.write_text(t, encoding='utf-8')

# Mind PT gets the new mascot physically in the screen, not just an emoji.
ptlayout = layout_dir / 'activity_mind_pt.xml'
if ptlayout.exists():
    x = ptlayout.read_text(encoding='utf-8')
    if '@+id/strawberryBunnyHero' not in x:
        m = re.search(r'(<LinearLayout\b[^>]*android:orientation="vertical"[^>]*>)', x, re.S)
        if m:
            hero = '''\n        <FrameLayout android:layout_width="match_parent" android:layout_height="178dp" android:layout_marginBottom="12dp" android:background="@drawable/bg_strawberry_glass">\n            <ImageView android:id="@+id/strawberryBunnyHero" android:layout_width="150dp" android:layout_height="170dp" android:layout_gravity="center" android:src="@drawable/strawberry_bunny" android:scaleType="fitCenter" android:contentDescription="스트로베리문 토끼"/>\n        </FrameLayout>\n'''
            x = x[:m.end()] + hero + x[m.end():]
    x = x.replace('android:text="👑 마음 PT"', 'android:text="👑🌙 마음 PT"')
    ptlayout.write_text(x, encoding='utf-8')

# Widgets switch to the Strawberry Moon glass visual language.
for name in ('widget_maeummon_clock.xml','widget_maeummon_large.xml','widget_maeummon_medium.xml','widget_maeummon_narrow.xml'):
    p = layout_dir / name
    if p.exists():
        t = p.read_text(encoding='utf-8')
        t = t.replace('android:background="@drawable/bg_card"', 'android:background="@drawable/bg_strawberry_glass"')
        t = t.replace('android:background="@drawable/widget_bg"', 'android:background="@drawable/bg_strawberry_glass"')
        p.write_text(t, encoding='utf-8')

# -----------------------------------------------------------------------------
# 4. Rename and recolor the everyday mascot surface into the new rabbit identity.
# -----------------------------------------------------------------------------
settings = app / 'MascotWidgetSettingsActivity.java'
if settings.exists():
    s = settings.read_text(encoding='utf-8')
    replacements = {
        '🐣 다마고치 · 위젯 설정':'🐰🌙 스트로베리문 친구 · 위젯',
        '어린 승재 말투':'토끼 친구 말투',
        '어린 승재를 홈화면 위에 띄우기':'🐰 토끼 친구를 홈화면에 띄우기',
        '어린 승재를 바탕화면에 띄웠어 🐣':'스트로베리문 토끼가 놀러왔어 🐰🌙',
        '#FBFAFF':'#160B18', '#F8F6F1':'#160B18', '#55546B':'#FFF4F7',
        '#85839A':'#D7A9B8', '#FFFDF8':'#2A1429', '#ECE4D4':'#7A3A59',
        '#F9FFFC':'#351A31', '#D5EDE4':'#7A3A59', '#6A9588':'#FF91AE'
    }
    for old, new in replacements.items(): s = s.replace(old, new)
    settings.write_text(s, encoding='utf-8')

# Semantic emoji vocabulary follows the universe, while emoji remains an accent layer.
tokens = app / 'EmojiDesignTokens.java'
if tokens.exists():
    e = tokens.read_text(encoding='utf-8')
    e = e.replace('public static final String HOME = "🏡";', 'public static final String HOME = "🌙";')
    e = e.replace('public static final String CORE = "💛";', 'public static final String CORE = "💗";')
    e = e.replace('public static final String ACTION = "🌱";', 'public static final String ACTION = "✨";')
    e = e.replace('public static final String HEART = "🤍";', 'public static final String HEART = "🍓";')
    tokens.write_text(e, encoding='utf-8')

focus = app / 'CurrentCounselingFocus.java'
if focus.exists():
    f = focus.read_text(encoding='utf-8')
    f = f.replace('💛 요즘 가장 중요한 마음', '💗 지금 마음의 중심')
    f = f.replace('❤️ 요즘 가장 중요한 마음', '💗 지금 마음의 중심')
    f = f.replace('🧠 반복되는 흐름', '🌙 자꾸 반복되는 마음의 궤도')
    f = f.replace('🌱 오늘은 이것만', '✨ 오늘은 이것만')
    focus.write_text(f, encoding='utf-8')

# Version bump.
g = gradle.read_text(encoding='utf-8')
g = re.sub(r'versionCode\s+\d+', 'versionCode 101838', g)
g = re.sub(r'versionName\s+"[^"]+"', 'versionName "10.18.38"', g)
gradle.write_text(g, encoding='utf-8')

print('Applied v10.18.38: real Strawberry Moon universe redesign + rabbit mascot asset')

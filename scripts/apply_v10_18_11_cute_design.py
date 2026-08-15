from pathlib import Path
import re

root = Path('extracted')
res = root / 'app/src/main/res'
drawable = res / 'drawable'
values = res / 'values'
layout = res / 'layout/activity_mind_pt.xml'
gradle = root / 'app/build.gradle'

# Softer, warmer pastel palette. Keep existing color names so the rest of the app remains compatible.
colors = '''<resources>
    <color name="cream">#FBFAFF</color>
    <color name="sage">#9BE2CB</color>
    <color name="sage_dark">#579C8B</color>
    <color name="brown">#55546B</color>
    <color name="soft_pink">#FFE3EC</color>
    <color name="white">#FFFFFFFF</color>
    <color name="soft_gray">#F4F3F8</color>
    <color name="bubble_user">#ECFAF4</color>
    <color name="bubble_ai">#FFFDFE</color>
    <color name="soft_lavender">#F3EFFF</color>
    <color name="soft_peach">#FFE9DE</color>
    <color name="soft_yellow">#FFF5D5</color>
    <color name="soft_mint">#EAF9F3</color>
</resources>
'''
(values / 'colors.xml').write_text(colors, encoding='utf-8')

files = {
'bg_card.xml': '''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="#FFFEFF"/>
    <corners android:radius="26dp"/>
    <stroke android:width="1dp" android:color="#E8E5F0"/>
    <padding android:left="18dp" android:top="16dp" android:right="18dp" android:bottom="16dp"/>
</shape>
''',
'bg_input.xml': '''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="#FAF8FF"/>
    <corners android:radius="22dp"/>
    <stroke android:width="1dp" android:color="#E4DFF2"/>
</shape>
''',
'bg_button.xml': '''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <gradient android:angle="0" android:startColor="#8FDCC0" android:endColor="#A7E8D1" />
    <corners android:radius="26dp"/>
    <stroke android:width="1dp" android:color="#7DCBB0"/>
</shape>
''',
'bg_pt_crown.xml': '''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <gradient android:angle="0" android:startColor="#FFFDF4" android:centerColor="#FFF7D9" android:endColor="#FFFDF6" />
    <stroke android:width="2dp" android:color="#E8BB52" />
    <corners android:radius="24dp" />
    <padding android:left="2dp" android:top="2dp" android:right="2dp" android:bottom="2dp" />
</shape>
''',
'bg_pt_crown_selected.xml': '''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <gradient android:angle="0" android:startColor="#79B596" android:centerColor="#73AD8E" android:endColor="#69A283" />
    <stroke android:width="2dp" android:color="#F1C964" />
    <corners android:radius="24dp" />
</shape>
''',
'bg_outcome_helped.xml': '''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"><solid android:color="#DDF5E8"/><corners android:radius="18dp"/><stroke android:width="1dp" android:color="#C2E8D3"/></shape>
''',
'bg_outcome_partial.xml': '''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"><solid android:color="#FFF3D7"/><corners android:radius="18dp"/><stroke android:width="1dp" android:color="#F0DFC0"/></shape>
''',
'bg_outcome_nochange.xml': '''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"><solid android:color="#F2F1F6"/><corners android:radius="18dp"/><stroke android:width="1dp" android:color="#E1DFE8"/></shape>
''',
'bg_outcome_worse.xml': '''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"><solid android:color="#FFE5E5"/><corners android:radius="18dp"/><stroke android:width="1dp" android:color="#F4CCCC"/></shape>
''',
'bg_outcome_noopportunity.xml': '''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"><solid android:color="#EEEAFE"/><corners android:radius="18dp"/><stroke android:width="1dp" android:color="#DCD5F5"/></shape>
''',
'bg_nav_chip.xml': '''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"><solid android:color="#FFFFFF"/><corners android:radius="24dp"/><stroke android:width="1dp" android:color="#E3E6EC"/></shape>
''',
'bg_nav_growth.xml': '''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"><solid android:color="#ECFAF4"/><corners android:radius="24dp"/><stroke android:width="1dp" android:color="#BFE8D5"/></shape>
'''
}
for name, content in files.items():
    (drawable / name).write_text(content, encoding='utf-8')

x = layout.read_text(encoding='utf-8')
# Slightly more breathing room while keeping the exact information architecture.
x = x.replace('android:padding="20dp"', 'android:padding="18dp"', 1)
x = x.replace('android:layout_width="88dp"\n            android:layout_height="88dp"', 'android:layout_width="94dp"\n            android:layout_height="94dp"', 1)
# Outcome buttons: soft status colors, rounded shapes, no harsh default material tint/elevation.
button_map = {
    'outcomeHelped': 'bg_outcome_helped',
    'outcomePartial': 'bg_outcome_partial',
    'outcomeNoChange': 'bg_outcome_nochange',
    'outcomeWorse': 'bg_outcome_worse',
    'outcomeNoOpportunity': 'bg_outcome_noopportunity',
}
for bid, bg in button_map.items():
    pat = rf'<Button android:id="@\+id/{bid}"([^>]*)/>'
    m = re.search(pat, x)
    if not m:
        raise SystemExit(f'cute design: missing button {bid}')
    attrs = m.group(1)
    # Keep width/height/weight/text, append the visual tokens.
    replacement = (f'<Button android:id="@+id/{bid}"{attrs} '
                   f'android:background="@drawable/{bg}" android:textColor="@color/brown" '
                   f'android:textSize="13sp" android:textStyle="bold" android:minHeight="48dp" '
                   f'android:stateListAnimator="@null" android:layout_margin="3dp" />')
    x = x[:m.start()] + replacement + x[m.end():]

# Bottom navigation: soft chips; Growth is the current mental-training destination so give it a mint wash.
x = x.replace('android:id="@+id/openBookshelfButton" android:layout_width="0dp" android:layout_height="54dp" android:layout_weight="1" android:layout_marginEnd="5dp" android:background="@drawable/bg_card"',
              'android:id="@+id/openBookshelfButton" android:layout_width="0dp" android:layout_height="56dp" android:layout_weight="1" android:layout_marginEnd="5dp" android:background="@drawable/bg_nav_chip"')
x = x.replace('android:id="@+id/openGrowthButton" android:layout_width="0dp" android:layout_height="54dp" android:layout_weight="1" android:layout_marginStart="5dp" android:layout_marginEnd="5dp" android:background="@drawable/bg_card"',
              'android:id="@+id/openGrowthButton" android:layout_width="0dp" android:layout_height="56dp" android:layout_weight="1" android:layout_marginStart="5dp" android:layout_marginEnd="5dp" android:background="@drawable/bg_nav_growth"')
x = x.replace('android:id="@+id/openMyRoomButton" android:layout_width="0dp" android:layout_height="54dp" android:layout_weight="1" android:layout_marginStart="5dp" android:background="@drawable/bg_card"',
              'android:id="@+id/openMyRoomButton" android:layout_width="0dp" android:layout_height="56dp" android:layout_weight="1" android:layout_marginStart="5dp" android:background="@drawable/bg_nav_chip"')

layout.write_text(x, encoding='utf-8')

# Version bump only; counseling/PT logic is intentionally untouched.
g = gradle.read_text(encoding='utf-8')
g, n1 = re.subn(r'versionCode\s+\d+', 'versionCode 101811', g, count=1)
g, n2 = re.subn(r'versionName\s+"[^"]+"', 'versionName "10.18.11"', g, count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit('cute design: gradle version anchor missing')
gradle.write_text(g, encoding='utf-8')

print('Applied v10.18.11 cute pastel UI refresh without changing PT logic')

from pathlib import Path
import re

root = Path('extracted')
app = root / 'app/src/main/java/com/maeummon/app'
res = root / 'app/src/main/res'
gradle = root / 'app/build.gradle'

# v10.18.36
# Restore the crown as a strong visual signal for the current top-priority PT,
# while preserving the calm counseling-room redesign.

activity = app / 'MindPtActivity.java'
m = activity.read_text(encoding='utf-8')

# Make the current selected PT visibly crowned again.
old = 'muscleText.setText(OhStylePtDisplay.title(s.muscle, s.exercise));'
new = 'muscleText.setText("👑 " + OhStylePtDisplay.title(s.muscle, s.exercise));'
if old in m and new not in m:
    m = m.replace(old, new, 1)
elif new not in m:
    old2 = 'muscleText.setText(s.muscle);'
    if old2 in m:
        m = m.replace(old2, 'muscleText.setText("👑 " + s.muscle);', 1)
    else:
        raise SystemExit('v10.18.36: current PT title anchor missing')
activity.write_text(m, encoding='utf-8')

# Restore a warm gold crown card while keeping the new room palette.
drawable = res / 'drawable'
(drawable / 'bg_pt_crown.xml').write_text('''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <gradient android:angle="0" android:startColor="#FFFDF6" android:centerColor="#FFF5D3" android:endColor="#FFF9E8"/>
    <corners android:radius="24dp"/>
    <stroke android:width="2dp" android:color="#D7B85C"/>
    <padding android:left="2dp" android:top="2dp" android:right="2dp" android:bottom="2dp"/>
</shape>
''', encoding='utf-8')

(drawable / 'bg_pt_crown_selected.xml').write_text('''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <gradient android:angle="0" android:startColor="#6F9F8E" android:centerColor="#6A9687" android:endColor="#638D7E"/>
    <corners android:radius="24dp"/>
    <stroke android:width="3dp" android:color="#E2C66F"/>
</shape>
''', encoding='utf-8')

# Version bump.
g = gradle.read_text(encoding='utf-8')
g = re.sub(r'versionCode\s+\d+', 'versionCode 101836', g)
g = re.sub(r'versionName\s+"[^"]+"', 'versionName "10.18.36"', g)
gradle.write_text(g, encoding='utf-8')

print('Applied v10.18.36: restored visible crown priority signal + gold crown card')

from pathlib import Path
import re

root = Path('extracted')
res = root / 'app/src/main/res/layout'
gradle = root / 'app/build.gradle'

# v10.18.26
# Longer PT copy introduced in v10.18.24 can reach the physical bottom edge of the
# RemoteViews TextView. On Samsung launcher the last line can then lose its lower
# pixels. Keep the content/line count unchanged, but reserve real bottom breathing
# room inside the message view and slightly increase its message box height.
layouts = {
    'widget_maeummon_clock.xml':  ('92dp', '104dp'),
    'widget_maeummon_large.xml':  ('112dp', '124dp'),
    'widget_maeummon_medium.xml': ('74dp', '86dp'),
    'widget_maeummon_narrow.xml': ('86dp', '98dp'),
}

for name, (old_height, new_height) in layouts.items():
    path = res / name
    text = path.read_text(encoding='utf-8')

    # Height anchor from v10.18.24. Medium uses layout_height, others minHeight.
    if old_height not in text:
        raise SystemExit(f'v10.18.26: expected PT height anchor {old_height} missing in {name}')
    text = text.replace(old_height, new_height, 1)

    # Locate the PT/message TextView by the maxLines=4 added in v10.18.24 and add
    # explicit bottom padding. Do not touch the clock/date/image views.
    tag_pattern = re.compile(r'<TextView\b(?:(?!</?TextView\b).)*?android:maxLines="4"(?:(?!</?TextView\b).)*?/?>', re.S)
    match = tag_pattern.search(text)
    if not match:
        raise SystemExit(f'v10.18.26: maxLines=4 PT TextView missing in {name}')

    tag = match.group(0)
    if 'android:paddingBottom=' not in tag:
        tag = tag.replace('android:maxLines="4"', 'android:maxLines="4"\n            android:paddingBottom="8dp"', 1)
    else:
        tag = re.sub(r'android:paddingBottom="[^"]+"', 'android:paddingBottom="8dp"', tag, count=1)

    # Samsung RemoteViews can render the final baseline very tightly. Explicit
    # font padding gives ascender/descender metrics room instead of clipping them.
    if 'android:includeFontPadding=' not in tag:
        tag = tag.replace('android:maxLines="4"', 'android:maxLines="4"\n            android:includeFontPadding="true"', 1)
    else:
        tag = re.sub(r'android:includeFontPadding="[^"]+"', 'android:includeFontPadding="true"', tag, count=1)

    text = text[:match.start()] + tag + text[match.end():]
    path.write_text(text, encoding='utf-8')

# Preserve every v10.18.25 behavior; this release is layout-only plus version bump.
g = gradle.read_text(encoding='utf-8')
g = re.sub(r'versionCode\s+\d+', 'versionCode 101826', g)
g = re.sub(r'versionName\s+"[^"]+"', 'versionName "10.18.26"', g)
gradle.write_text(g, encoding='utf-8')

print('Applied v10.18.26 widget PT bottom clipping fix')

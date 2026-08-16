from pathlib import Path
import re

root = Path('extracted')
app = root / 'app/src/main/java/com/maeummon/app'
gradle = root / 'app/build.gradle'

analyzer = app / 'CounselingProgramAnalyzer.java'
a = analyzer.read_text(encoding='utf-8')

# v10.18.31 accidentally left the final adaptive-loop Java literal without its closing quote.
# Repair only that exact generated line; keep every rule and later feature intact.
bad = '결과를 다음 상담에서 다시 확인할 수 있을 정도로 작고 관찰 가능해야 한다. ;'
good = '결과를 다음 상담에서 다시 확인할 수 있을 정도로 작고 관찰 가능해야 한다. ";'
if bad in a:
    a = a.replace(bad, good, 1)
elif good not in a:
    # Fallback: repair the malformed end of the long adaptive-loop line.
    a, n = re.subn(
        r'(\[상담-훈련-후속상담 적응형 루프\][^\n]*?관찰 가능해야 한다\.)\s*;',
        lambda m: m.group(1) + ' ";',
        a,
        count=1,
    )
    if n != 1:
        raise SystemExit('v10.18.35: malformed adaptive-loop string not found')

analyzer.write_text(a, encoding='utf-8')

g = gradle.read_text(encoding='utf-8')
g = re.sub(r'versionCode\s+\d+', 'versionCode 101835', g)
g = re.sub(r'versionName\s+"[^"]+"', 'versionName "10.18.35"', g)
gradle.write_text(g, encoding='utf-8')

print('Applied v10.18.35: repaired adaptive-loop Java string; preserved v10.18.34 features')

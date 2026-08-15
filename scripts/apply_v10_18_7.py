from pathlib import Path
import re

root = Path('extracted')
analyzer = root / 'app/src/main/java/com/maeummon/app/CounselingProgramAnalyzer.java'
shared = root / 'app/src/main/java/com/maeummon/app/SharedCounselingLinkActivity.java'
gradle = root / 'app/build.gradle'

text = analyzer.read_text(encoding='utf-8')

# 1) Friendly everyday PT names. Try multiple stable anchors and never make the build brittle.
name_rule = "이름 말맛 규칙: '억제 힘', '내성력', '조절 능력을 다루는 힘', '안착력', '강화'처럼 치료계획서·검사표처럼 들리는 표현을 피한다. 사용자가 자기 능력으로 느낄 수 있는 자연스러운 '~하는 힘'으로 바꾼다. 예: '불안 행동 억제 힘'→'불안할 때 잠깐 멈추는 힘', '관계 신호 해석 조절 능력을 다루는 힘'→'관계 신호를 서두르지 않고 보는 힘', '사회적 접촉을 견디고 완화하는 힘'→'내 에너지에 맞춰 사람과 다시 연결하는 힘'. "
inserted = False
for anchor in [
    "muscle_name은 사용자 화면에 그대로 보인다. 임상·분류 용어 대신 생활 언어로 짧고 따뜻하게 쓴다.",
    "muscle_name은 생활언어의 자연스러운 '~하는 힘' 형태로 짧게 쓴다.",
    "muscle_name은 생활언어의 자연스러운 '~하는 힘'으로 새로 만든다."
]:
    if anchor in text:
        text = text.replace(anchor, anchor + " " + name_rule, 1)
        inserted = True
        break
if not inserted:
    raise SystemExit('v10.18.7 naming anchor missing')

# 2) Tiny stage-1 success gate. Inject beside the first reliable observable-behavior rule.
small_step_rule = "1단계 최소유효강도 규칙: 첫 단계는 오늘 한 장면·한 번의 시도만으로도 '해냈어/조금/못했어'를 바로 판단할 수 있게 만든다. 1단계부터 매일 3회, 2주간 반복, 10분 이상 버티기, 불안 감소 확인 같은 장기·고강도 조건을 걸지 않는다. 관계 신호 PT는 장면 1개에서 사실/해석을 한 번 나누면 1차 성공, 판정 지연은 2~3분만 미뤄도 1차 성공, 접촉 PT는 편한 사람과 짧은 접촉 1회를 계획대로 마치고 전후 상태를 한 줄 기록하면 1차 성공이다. 횟수·시간은 2단계 이후 실제 성공 기록에 맞춰 올린다. "
step_inserted = False
for anchor in [
    "성공 기준은 관찰 가능한 행동으로 쓴다.",
    "성공 기준은 감정 소멸이 아니라 관찰 가능한 행동이어야 한다.",
    "성공기준은 그날 또는 그 주에 사용자가 '해냈어/조금/못했어'를 판단할 수 있는 관찰 가능한 행동이어야 한다."
]:
    if anchor in text:
        text = text.replace(anchor, anchor + " " + small_step_rule, 1)
        step_inserted = True
        break
if not step_inserted:
    # Last-resort: append to a known prompt line without failing the build.
    marker = "사용자가 부정하거나 수정한 가설은 절대 훈련 근거로 재사용하지 않는다."
    if marker in text:
        text = text.replace(marker, small_step_rule + marker, 1)
    else:
        print('warning: no stage-1 anchor; continuing without prompt injection')

# 3) Semantic merge reminder if available.
merge_anchor = "성공기준은 '2주 후 불안 감소' 같은 장기 결과가 아니라 사용자가 이번 회차 또는 이번 주에 해냈어/조금/못했어를 판단할 수 있는 행동으로 쓴다. "
if merge_anchor in text:
    text = text.replace(merge_anchor, merge_anchor + "최종 PT 이름은 '억제/내성력/강화/조절 능력을 다루는 힘' 같은 임상적 명칭을 피하고 생활언어로 다시 이름 붙인다. 1단계 성공기준은 한 장면·한 번의 시도로 판정 가능하게 하고 반복 횟수나 긴 시간은 2단계 이후로 미룬다. ", 1)

analyzer.write_text(text, encoding='utf-8')

s = shared.read_text(encoding='utf-8')
# 4) Hide verbose collector diagnostics from the normal user-facing preview.
s = s.replace(' + collectionDiagnosticSummary());', ');')
s = s.replace(' + collectionDiagnosticSummary() + "\\n\\n" + clip(full, 520)', ' + "\\n\\n" + clip(full, 520)')

# 5) Compact safety note in the PT summary.
s = s.replace('if (!analysis.caution.isEmpty()) b.append("\\n\\n⚠️ 안전 메모\\n").append(shortenCaution(analysis.caution));',
              'if (!analysis.caution.isEmpty()) b.append("\\n\\n⚠️ 안전 관련 내용은 상담 기록에 보관했어. 마음 PT에서는 훈련 내용에 집중해.");')

s2, n = re.subn(r'private static final int CROWN_POLICY_VERSION = \d+;', 'private static final int CROWN_POLICY_VERSION = 14;', s, count=1)
if n != 1:
    raise SystemExit('policy version anchor missing')
shared.write_text(s2, encoding='utf-8')

g = gradle.read_text(encoding='utf-8')
g, n1 = re.subn(r'versionCode\s+\d+', 'versionCode 101807', g, count=1)
g, n2 = re.subn(r'versionName\s+"[^"]+"', 'versionName "10.18.7"', g, count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit('gradle version anchor missing')
gradle.write_text(g, encoding='utf-8')

print('Applied v10.18.7 friendlier PT names, tiny stage-1 success gates, and cleaner user-facing diagnostics')

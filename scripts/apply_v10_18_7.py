from pathlib import Path
import re

root = Path('extracted')
analyzer = root / 'app/src/main/java/com/maeummon/app/CounselingProgramAnalyzer.java'
shared = root / 'app/src/main/java/com/maeummon/app/SharedCounselingLinkActivity.java'
gradle = root / 'app/build.gradle'

text = analyzer.read_text(encoding='utf-8')

# 1) Soften PT names: make them sound like everyday strengths, not clinical constructs or suppression commands.
name_anchor = "muscle_name은 사용자 화면에 그대로 보인다. 임상·분류 용어 대신 생활 언어로 짧고 따뜻하게 쓴다. 예: 사실-미확인 정보 구분하기→보이는 것과 추측을 나누는 힘, 불확실성 내성→애매함을 견디는 힘. "
name_rule = ("muscle_name은 사용자 화면에 그대로 보인다. 임상·분류 용어 대신 생활 언어로 짧고 따뜻하게 쓴다. 예: 사실-미확인 정보 구분하기→보이는 것과 추측을 나누는 힘, 불확실성 내성→애매함을 견디는 힘. "
             "이름 말맛 규칙: '억제 힘', '내성력', '조절 능력을 다루는 힘', '안착력', '강화'처럼 치료계획서·검사표처럼 들리는 표현을 피한다. 사용자가 자기 능력으로 느낄 수 있는 자연스러운 '~하는 힘'으로 바꾼다. 예를 들어 '불안 행동 억제 힘'은 '불안할 때 잠깐 멈추는 힘', '관계 신호 해석 조절 능력을 다루는 힘'은 '관계 신호를 서두르지 않고 보는 힘', '사회적 접촉을 견디고 완화하는 힘'은 '내 에너지에 맞춰 사람과 다시 연결하는 힘'처럼 표현한다. ")
if name_anchor not in text:
    raise SystemExit('v10.18.7 name anchor missing')
text = text.replace(name_anchor, name_rule, 1)

# 2) Stage 1 must be tiny and immediately judgeable. No daily x3, no multi-week outcome as the first gate.
step_anchor = "기회 없는 날에도 수행 가능한 대체 행동을 stage마다 자연스럽게 포함한다."
step_rule = ("1단계 최소유효강도 규칙: 첫 단계는 사용자가 오늘 한 번 시도해도 '해냈어/조금/못했어'를 바로 누를 수 있어야 한다. 처음부터 '매일 3회', '2주간 3회', '10분 이상 버티기', '불안이 감소했는지 확인'처럼 횟수·기간·감정 결과를 성공조건으로 걸지 않는다. 관계 신호 PT라면 장면 1개에서 사실/해석을 한 번 나누면 1차 성공, 판정 지연 PT라면 2~3분만 미뤄도 1차 성공, 접촉 PT라면 편한 사람과 짧은 접촉 1회를 계획대로 마치고 전후 상태를 한 줄 기록하면 1차 성공으로 둔다. 횟수와 시간은 2단계 이후 실제 성공 기록에 맞춰 올린다. "
             "성공기준은 감정이 사라졌는지가 아니라 '이번 회차에 어떤 행동을 했는지'로 쓴다. " + step_anchor)
if step_anchor not in text:
    raise SystemExit('v10.18.7 step anchor missing')
text = text.replace(step_anchor, step_rule, 1)

# 3) Reinforce same rule at semantic merge stage so newly merged PTs do not regain stiff names or high thresholds.
merge_anchor = "성공기준은 '2주 후 불안 감소' 같은 장기 결과가 아니라 사용자가 이번 회차 또는 이번 주에 해냈어/조금/못했어를 판단할 수 있는 행동으로 쓴다. "
merge_rule = (merge_anchor +
              "특히 최종 PT 이름은 '억제/내성력/강화/조절 능력을 다루는 힘' 같은 임상적 명칭을 피하고 생활언어로 다시 이름 붙인다. 1단계 성공기준은 원칙적으로 한 장면·한 번의 시도로 판정 가능하게 하며, 반복 횟수나 긴 시간을 요구하는 목표는 2단계 이후로 미룬다. ")
if merge_anchor not in text:
    raise SystemExit('v10.18.7 merge anchor missing')
text = text.replace(merge_anchor, merge_rule, 1)

analyzer.write_text(text, encoding='utf-8')

s = shared.read_text(encoding='utf-8')
# 4) Keep collection diagnostics in code for debugging but do not dump them into the normal user-facing screen.
s = s.replace(' + collectionDiagnosticSummary());', ');')
s = s.replace(' + collectionDiagnosticSummary() + "\\n\\n" + clip(full, 520)', ' + "\\n\\n" + clip(full, 520)')

# 5) Safety details should not dominate the PT list. Keep the existence signal compact; detailed safety handling belongs to counseling/safety flow.
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

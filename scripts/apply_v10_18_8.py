from pathlib import Path
import re

root = Path('extracted')
analyzer = root / 'app/src/main/java/com/maeummon/app/CounselingProgramAnalyzer.java'
shared = root / 'app/src/main/java/com/maeummon/app/SharedCounselingLinkActivity.java'
gradle = root / 'app/build.gradle'

text = analyzer.read_text(encoding='utf-8')

# Strengthen final consolidation: three relationship-anxiety micro-axes should become one ladder unless they are truly different levers.
marker = "관계 불안 세분화 금지:"
if marker not in text:
    raise SystemExit('v10.18.8 relationship marker missing')
insert = (
    "관계불안 최종 압축 규칙: 최종 목록에 '대인관계 신뢰', '불확실성 견디기/내성', '감정 신호와 실제 상황 구분', '해석과 판단 분리', '판단 유보', '관계-자기 가치 분리'처럼 서로 다른 이름의 PT가 둘 이상 남았는데 실제 장면과 유지기제가 동일한 상대 신호→자동 해석→관계 위험 판정→자기 가치 흔들림 연쇄라면, 반드시 대표 PT 하나로 압축한다. "
    "이때 대표 제목은 '관계 신호를 서두르지 않고 보는 힘' 또는 '관계 신호를 보고도 내 가치까지 서두르지 않는 힘'처럼 생활언어로 쓴다. 나머지는 별도 카드로 남기지 말고 단계로 흡수한다. "
    "단, 사람을 만나는 양/시간/회복 조절, 거절과 경계 말하기, 상태와 욕구 표현처럼 실제 행동 레버가 다른 축은 별도 PT로 유지한다. "
)
text = text.replace(marker, insert + marker, 1)

# Make stage 1 truly one-shot and concrete; move repetition goals to later stages.
anchor = "1단계 최소유효강도 규칙:"
if anchor not in text:
    raise SystemExit('v10.18.8 minimum-intensity marker missing')
text = text.replace(
    anchor,
    "1단계 초소형 진입 규칙: 첫 단계는 '오늘 한 장면에서 한 번'만 해도 성공으로 판정할 수 있게 설계한다. "
    "사회적 접촉/에너지 PT라면 오늘 약속 또는 연락 한 건만 골라 '그대로 하기/시간 줄이기/미루기/쉬기' 중 하나를 정하고, 끝난 뒤 에너지 변화 한 줄을 적으면 성공이다. "
    "관계 신호 PT라면 걸린 장면 하나에서 사실 한 줄과 내 해석 한 줄을 나누면 성공이다. 판정 유예는 2~3분부터 시작하고, 횟수·기간·10분 이상 버티기는 2단계 이후로 올린다. "
    + anchor,
    1,
)

# Prevent stiff/clinical names from surviving the final pass.
name_marker = "이름 말맛 규칙:"
if name_marker not in text:
    raise SystemExit('v10.18.8 name marker missing')
text = text.replace(
    name_marker,
    "최종 이름 검수 규칙: '사회적 긴장 조절하는 힘', '대인관계 신뢰 향상하는 힘', '불확실성 내성 강화하는 힘', '조절 능력을 다루는 힘'처럼 상담 계획서 같은 명칭이 남으면 다시 생활언어로 고친다. 예: '내 에너지에 맞춰 사람을 만나는 힘', '관계 신호를 서두르지 않고 보는 힘', '애매함 속에서도 바로 결론내리지 않는 힘'. "
    + name_marker,
    1,
)

analyzer.write_text(text, encoding='utf-8')

s = shared.read_text(encoding='utf-8')
s2, n = re.subn(r'private static final int CROWN_POLICY_VERSION = \d+;', 'private static final int CROWN_POLICY_VERSION = 15;', s, count=1)
if n != 1:
    raise SystemExit('policy version anchor missing')
shared.write_text(s2, encoding='utf-8')

g = gradle.read_text(encoding='utf-8')
g, n1 = re.subn(r'versionCode\s+\d+', 'versionCode 101808', g, count=1)
g, n2 = re.subn(r'versionName\s+"[^"]+"', 'versionName "10.18.8"', g, count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit('gradle version anchor missing')
gradle.write_text(g, encoding='utf-8')

print('Applied v10.18.8 stronger relationship consolidation, softer names, and one-shot stage 1')

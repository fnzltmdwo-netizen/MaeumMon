from pathlib import Path
import re

root = Path('extracted')
analyzer = root / 'app/src/main/java/com/maeummon/app/CounselingProgramAnalyzer.java'
shared = root / 'app/src/main/java/com/maeummon/app/SharedCounselingLinkActivity.java'
gradle = root / 'app/build.gradle'

text = analyzer.read_text(encoding='utf-8')

old = "관계 신호 해석과 그 신호가 곧 자기 가치 판정으로 번지는 두 PT가 사실/해석 분리→가치판단 분리→판정 보류라는 한 연속 학습축이면 병합한다."
new = ("관계 불안 연쇄 특별 병합 규칙: '해석과 판단 분리', '판단 유보', '관계-자기 가치 분리', '불확실성 견디기'처럼 이름이 달라도 실제 유지기제가 "
       "상대의 작은 신호→자동 해석→관계 위험 판정→자기 가치 하락→불안 증폭으로 이어지는 한 연쇄라면 별도 PT 2~3개로 쪼개지 말고 하나의 상위 PT로 병합한다. "
       "이때 1단계는 확인 가능한 사실/내 해석/자기 가치 판단을 세 줄로 분리, 2단계는 '원인은 아직 모름. 지금은 관계 판정을 10분 미룬다'고 적고 재확인·추적·재분석을 멈추기, "
       "3단계는 다음 날 반증 사실 하나와 다른 설명 하나를 적고 '확정 불가/한 번 더 관찰/필요하면 차분히 확인' 중 하나로 마무리하는 식으로 한 PT 안에서 깊어지게 한다.")
if old not in text:
    raise SystemExit('v10.18.6 anchor 1 missing')
text = text.replace(old, new)

anchor = "중요: 병합은 PT 카드의 축/이름을 합치는 것이지 훈련을 추상화하는 작업이 아니다."
insert = ("관계 불안 세분화 금지: 같은 상담 장면에서 '해석 분리', '판단 유보', '자기 가치 분리'가 순차적으로 작동한다면 서로 다른 카드로 남기지 않는다. "
          "최종 PT 목록에서는 이 연쇄를 대표하는 생활언어 제목 하나만 남기고, 나머지 능력은 그 PT의 단계로 이동한다. 제목 예시는 '관계 신호를 보고도 내 가치까지 서두르지 않는 힘'처럼 사용자가 바로 이해할 수 있게 쓴다. "
          "반대로 사회적 접촉량/에너지 조절, 거절·경계 말하기, 상태·욕구 표현처럼 실제 행동 레버가 다른 축은 별도 PT로 유지한다. "
          "성공기준은 '2주 후 불안 감소' 같은 장기 결과가 아니라 사용자가 이번 회차 또는 이번 주에 해냈어/조금/못했어를 판단할 수 있는 행동으로 쓴다. "
          "접촉 PT라면 예: '오늘 신뢰하는 사람 1명과 정한 시간만큼 접촉했고, 끝난 뒤 긴장도와 회복시간을 기록했다.'처럼 쓴다. ")
if anchor not in text:
    raise SystemExit('v10.18.6 anchor 2 missing')
text = text.replace(anchor, insert + anchor)

# Strengthen step refinement so the merged relationship PT keeps a true 1→2→3 learning ladder.
step_anchor = "사실/해석 분리 PT라면 1단계에서 실제 한 장면을 골라 ① 확인 가능한 사실 ② 내가 붙인 해석 ③ 그 해석 때문에 생긴 자기 가치 판단을 각각 한 줄로 쓴다."
step_prefix = ("같은 관계불안 연쇄가 병합된 PT라면 절대로 세 단계를 비슷한 '생각 멈추기' 반복으로 만들지 않는다. "
               "1단계는 정보 분리, 2단계는 시간 지연과 행동 복귀, 3단계는 대안설명과 자기판단 유예로 기능이 달라야 한다. ")
if step_anchor not in text:
    raise SystemExit('v10.18.6 anchor 3 missing')
text = text.replace(step_anchor, step_prefix + step_anchor)

analyzer.write_text(text, encoding='utf-8')

s = shared.read_text(encoding='utf-8')
s2, n = re.subn(r'private static final int CROWN_POLICY_VERSION = \d+;', 'private static final int CROWN_POLICY_VERSION = 13;', s, count=1)
if n != 1:
    raise SystemExit('policy version anchor missing')
shared.write_text(s2, encoding='utf-8')

g = gradle.read_text(encoding='utf-8')
g, n1 = re.subn(r'versionCode\s+\d+', 'versionCode 101806', g, count=1)
g, n2 = re.subn(r'versionName\s+"[^"]+"', 'versionName "10.18.6"', g, count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit('gradle version anchor missing')
gradle.write_text(g, encoding='utf-8')

print('Applied v10.18.6 relationship-axis consolidation and per-attempt success criteria')

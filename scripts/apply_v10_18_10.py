from pathlib import Path
import re

root = Path('extracted')
analyzer = root / 'app/src/main/java/com/maeummon/app/CounselingProgramAnalyzer.java'
shared = root / 'app/src/main/java/com/maeummon/app/SharedCounselingLinkActivity.java'
gradle = root / 'app/build.gradle'

text = analyzer.read_text(encoding='utf-8')

# v10.18.10: final hard merge for relationship-signal micro PTs that are the same learning chain.
marker = "관계불안 최종 압축 규칙:"
if marker not in text:
    raise SystemExit('v10.18.10 relationship compression anchor missing')

hard_rule = (
    "관계신호 미세축 강제병합 규칙: 최종 후보에 '애매한 관계 신호를 보는 힘', '거절 신호로 서둘러 읽지 않는 힘', "
    "'관계 신호를 서두르지 않고 보는 힘', '사실과 해석을 나누는 힘', '판단을 미루는 힘', '애매함 속에서 결론을 미루는 힘'처럼 "
    "표현만 다른 PT가 둘 이상 있고, 근거 장면이 답장 없음·무표정·말투 변화·반응 차이·단톡 반응처럼 같은 관계 신호라면 반드시 하나로 병합한다. "
    "대표 제목은 원칙적으로 '관계 신호를 서두르지 않고 보는 힘'처럼 한 문장으로 정한다. "
    "병합된 PT의 1단계는 장면 하나에서 '확인 가능한 사실 1줄 / 내가 붙인 해석 1줄'을 나누기, "
    "2단계는 '원인은 아직 모름'이라고 적고 2~3분 동안 재확인·추적·추가판정을 미루기, "
    "3단계는 다음에 반증 사실 하나 또는 가능한 다른 설명 하나를 적고 '확정 불가/더 관찰/필요하면 확인' 중 하나로 끝내기다. "
    "이 셋을 별도 카드로 다시 만들지 않는다. "
    "단, 비교·질투·소속감 경쟁처럼 '타인과 비교하며 내 위치를 재는 고리', 사회적 접촉량·회복·약속 조절, 거절/경계 표현은 실제 레버가 다르므로 별도 PT로 유지할 수 있다. "
)
text = text.replace(marker, hard_rule + marker, 1)

# Ensure merged-stage refinement keeps the exact distinct ladder instead of producing near-duplicate steps.
step_marker = "같은 관계불안 연쇄가 병합된 PT라면 절대로 세 단계를 비슷한 '생각 멈추기' 반복으로 만들지 않는다."
if step_marker not in text:
    raise SystemExit('v10.18.10 step refinement anchor missing')
step_rule = (
    "관계신호 병합 PT 단계 고정 원칙: 1단계=사실/해석 정보분리, 2단계=판정 시간지연+원래 행동으로 복귀, "
    "3단계=대안설명/반증 확인+최종판정 유예로 기능을 분리한다. 1·2·3단계가 모두 '생각 멈추기'나 '판단 미루기'의 반복이 되면 다시 작성한다. "
)
text = text.replace(step_marker, step_rule + step_marker, 1)

# Keep names natural after hard merge.
name_marker = "최종 이름 검수 규칙:"
if name_marker not in text:
    raise SystemExit('v10.18.10 name anchor missing')
text = text.replace(
    name_marker,
    "관계신호 대표 제목 규칙: 같은 관계신호 축이 병합됐으면 '애매한 관계 신호를 보는 힘'과 '거절 신호로 서둘러 읽지 않는 힘'을 둘 다 남기지 말고, '관계 신호를 서두르지 않고 보는 힘' 하나로 정리한다. " + name_marker,
    1,
)

analyzer.write_text(text, encoding='utf-8')

s = shared.read_text(encoding='utf-8')
s, n = re.subn(r'private static final int CROWN_POLICY_VERSION = \d+;', 'private static final int CROWN_POLICY_VERSION = 17;', s, count=1)
if n != 1:
    raise SystemExit('v10.18.10 policy version anchor missing')
shared.write_text(s, encoding='utf-8')

g = gradle.read_text(encoding='utf-8')
g, n1 = re.subn(r'versionCode\s+\d+', 'versionCode 101810', g, count=1)
g, n2 = re.subn(r'versionName\s+"[^"]+"', 'versionName "10.18.10"', g, count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit('v10.18.10 gradle version anchor missing')
gradle.write_text(g, encoding='utf-8')

print('Applied v10.18.10 hard merge for relationship-signal micro axes')

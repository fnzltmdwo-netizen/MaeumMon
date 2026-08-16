from pathlib import Path
import re

root = Path('extracted')
app = root / 'app/src/main/java/com/maeummon/app'
gradle = root / 'app/build.gradle'

analyzer = app / 'CounselingProgramAnalyzer.java'
shared = app / 'SharedCounselingLinkActivity.java'

a = analyzer.read_text(encoding='utf-8')

# -----------------------------------------------------------------------------
# v10.18.31
# Turn PT into an adaptive counseling loop rather than a fixed 1->2->3 curriculum.
# The app already stores HELPED/PARTIAL/NO_CHANGE/WORSE/NO_OPPORTUNITY and learning
# states. Strengthen model-facing decisions so those outcomes actually change the next
# intervention, while fresh direct user evidence can reopen/reformulate the PT itself.
# -----------------------------------------------------------------------------

followup_rules = (
    ' [상담-훈련-후속상담 적응형 루프] '
    '마음 PT는 미리 정한 1→2→3 코스를 기계적으로 진행하는 과정이 아니다. 이전 훈련의 실제 결과와 새 상담 근거를 먼저 재평가한 뒤 다음 한 걸음을 정한다. '
    'HELPED면 같은 핵심을 그대로 반복시키기보다 조금 더 실제적인 장면으로 일반화하거나 아주 조금만 난이도를 올린다. '
    'PARTIAL이면 방향은 유지하되 과제를 더 작고 구체적으로 줄이고, 사용자가 실제로 막힌 지점 하나만 바꾼다. '
    'NO_CHANGE면 사용자의 의지 부족으로 해석하지 말고 과제 크기, 타이밍, 맥락, 유지기제 가설이 맞았는지 먼저 다시 본다. 같은 숙제를 그대로 반복하지 않는다. '
    'WORSE면 동일 개입과 동일 강도를 즉시 반복하지 않는다. 안정화/강도감소를 우선하고 formulation을 다시 열어 경쟁 가설을 검토한다. '
    'NO_OPPORTUNITY 또는 NOT_TRIED는 실패로 계산하지 않는다. 실제 기회가 없었는지, 장벽이 있었는지 확인하고 필요하면 같은 단계의 기회를 다시 만든다. '
    '반복 HELPED는 미해결도를 낮추고 유지·일반화·재발예방 쪽으로 이동한다. 반복 NO_CHANGE/WORSE는 같은 개입을 고집하지 말라는 학습 신호다. '
    '중요: 새 상담에서 사용자가 직접 말한 사실이나 정정이 기존 formulation보다 더 설명력이 크면, 기존 PT를 지키기 위해 새 증거를 끼워 맞추지 않는다. 현재 직접근거를 우선해 유지기제를 다시 정하고 PT를 유지/약화/강화/교체/종료 중 하나로 결정한다. '
    '훈련을 바꾸는 이유는 사용자 화면에 생활말 한두 문장으로 설명한다. 예: 지난번엔 답장 자체가 핵심이라고 봤는데, 이번 얘기를 들어보니 관계가 끊길까 봐 내가 계속 붙잡아야 한다는 두려움이 더 중심인 것 같아. '
    '다음 PT도 한 번에 하나의 핵심 행동만 준다. 결과를 다음 상담에서 다시 확인할 수 있을 정도로 작고 관찰 가능해야 한다. '
)

if '상담-훈련-후속상담 적응형 루프' not in a:
    anchor = 'private static String ohStylePtRules() {'
    idx = a.find(anchor)
    if idx < 0:
        raise SystemExit('v10.18.31: ohStylePtRules anchor missing')

    # Append rules inside the existing helper return, immediately before its closing semicolon.
    start = a.find('return ', idx)
    end = a.find('\n    }', start)
    if start < 0 or end < 0:
        raise SystemExit('v10.18.31: ohStylePtRules body missing')
    body = a[start:end]
    # Find final Java string terminator in helper body and extend the chain.
    last = body.rfind('";')
    if last < 0:
        raise SystemExit('v10.18.31: ohStylePtRules terminator missing')
    java = followup_rules.replace('\\', '\\\\').replace('"', '\\"')
    body = body[:last] + '" +\n                "' + java + body[last+1:]
    a = a[:start] + body + a[end:]

# Strengthen any existing step-refinement prompt with explicit adaptive state choices.
marker = 'outcome_history와 learning_state가 있으면 단계 설계에 반드시 반영한다.'
if marker in a and 'PT 상태 결정값은 KEEP/REDUCE/ADVANCE/REDESIGN/RETIRE' not in a:
    a = a.replace(
        marker,
        marker + ' PT 상태 결정값은 KEEP/REDUCE/ADVANCE/REDESIGN/RETIRE의 관점으로 판단한다. KEEP은 아직 기회가 적거나 같은 핵심이 적절할 때, REDUCE는 PARTIAL/장벽이 있을 때, ADVANCE는 반복 HELPED일 때, REDESIGN은 NO_CHANGE/WORSE 또는 새 formulation 근거가 나왔을 때, RETIRE는 반복 HELPED로 충분히 일반화됐거나 더 이상 현재 미해결 축이 아닐 때다.',
        1
    )

# New direct evidence must beat stale historical hypotheses.
if '새 직접근거가 기존 PT의 중심가설과 충돌하면 현재 직접근거를 우선한다.' not in a:
    correction_marker = '정정된 내용은 이전 추론보다 높은 우선순위의 사실로 취급한다.'
    if correction_marker in a:
        a = a.replace(
            correction_marker,
            correction_marker + ' 새 직접근거가 기존 PT의 중심가설과 충돌하면 현재 직접근거를 우선한다. 기존 PT를 보존하려고 현재 설명을 왜곡하지 않는다.',
            1
        )

analyzer.write_text(a, encoding='utf-8')

# Force shared-link counseling threads through the new adaptive policy audit.
s = shared.read_text(encoding='utf-8')
s = re.sub(r'private static final String COLLECTOR_VERSION = "v\d+";',
           'private static final String COLLECTOR_VERSION = "v5";', s, count=1)
s = re.sub(r'private static final int CROWN_POLICY_VERSION = \d+;',
           'private static final int CROWN_POLICY_VERSION = 31;', s, count=1)
shared.write_text(s, encoding='utf-8')

# Version bump.
g = gradle.read_text(encoding='utf-8')
g = re.sub(r'versionCode\s+\d+', 'versionCode 101831', g)
g = re.sub(r'versionName\s+"[^"]+"', 'versionName "10.18.31"', g)
gradle.write_text(g, encoding='utf-8')

print('Applied v10.18.31: adaptive counseling -> PT -> outcome -> follow-up loop')

from pathlib import Path
import re

root = Path('extracted')
app = root / 'app/src/main/java/com/maeummon/app'
gradle = root / 'app/build.gradle'

analyzer = app / 'CounselingProgramAnalyzer.java'
shared = app / 'SharedCounselingLinkActivity.java'

# -----------------------------------------------------------------------------
# v10.18.30
# GPT shared-link import should remember like a skilled counselor, not like a transcript
# summarizer: explicit user correction > central repeated pattern > formulation-changing
# evidence > current emotion/context > incidental detail.
# Keep the existing JSON schema for backward compatibility; encode importance/type inside
# user_facts strings so existing parsers/storage remain valid.
# -----------------------------------------------------------------------------

a = analyzer.read_text(encoding='utf-8')

importance_rule = (
    '상담 기억 중요도 규칙: 링크 원문을 단순 요약하지 말고, 앞으로의 상담 방향을 실제로 바꿀 정보만 골라라. '
    'user_facts는 중요도 높은 순서로 최대 10개만 적고 각 문자열 앞에 반드시 '
    '[★★★★★][CORRECTION|CORE_PATTERN|CORE_FEAR|MAINTAINER|INTERVENTION_EFFECT], '
    '[★★★★☆][REPEATED_PATTERN|FORMULATION_EVIDENCE|BOUNDARY_NEED], '
    '[★★★☆☆][CURRENT_EMOTION|CURRENT_CONTEXT] 중 하나를 붙인다. '
    '★★★★★는 사용자가 상담자의 해석을 직접 정정/부정한 내용, 반복되는 핵심 두려움, 여러 장면을 설명하는 상위 유지기제, '
    '반복적으로 도움이 됐거나 악화시킨 개입이다. ★★★★☆는 서로 다른 장면에서 반복되거나 현재 formulation을 바꿀 직접 근거다. '
    '★★★☆☆는 현재 상담 이해에 필요한 감정·욕구·경계·상황이다. 잡담, 날짜/장소 같은 단순 사건 세부, 이미 충분히 중복된 정보는 '
    'user_facts에 넣지 말고 원문에만 남긴다. 사용자의 직접 정정은 과거 가설보다 항상 우선하며 rejected_or_corrected_hypotheses에도 반드시 남긴다. '
    '한 번의 강한 감정보다 서로 다른 시점/장면에서 반복된 증거를 더 높게 평가하고, 현재 발화와 충돌하는 과거 해석은 낮추거나 폐기한다. '
    '중요도를 감정 강도만으로 매기지 말고 (1) 왜 이런 반응이 생기는지 설명하는가, (2) 다음 상담 선택을 바꾸는가, '
    '(3) 여러 문제를 함께 유지하는 상위 기제인가, (4) 시간적으로 반복 확인됐는가를 기준으로 판단한다. '
)

if '상담 기억 중요도 규칙:' not in a:
    marker = '"후보는 최대 8개까지 허용한다.'
    idx = a.find(marker)
    if idx < 0:
        raise SystemExit('v10.18.30: analyzer candidate prompt marker missing')
    # Insert as another Java concatenated string immediately before the candidate rule.
    line_start = a.rfind('\n', 0, idx) + 1
    indent = a[line_start:idx]
    java_line = indent + '"' + importance_rule.replace('\\', '\\\\').replace('"', '\\"') + '" +\n'
    a = a[:line_start] + java_line + a[line_start:]

# Strengthen correction precedence anywhere the expansion/merge policy is composed.
correction_anchor = '"사용자가 부정하거나 수정한 가설은 절대 훈련 근거로 재사용하지 않는다.'
if correction_anchor in a and '정정된 내용은 이전 추론보다 높은 우선순위의 사실로 취급한다' not in a:
    a = a.replace(
        correction_anchor,
        '"정정된 내용은 이전 추론보다 높은 우선순위의 사실로 취급한다. 사용자가 부정하거나 수정한 가설은 절대 훈련 근거로 재사용하지 않는다.',
        1
    )

# Crown ranking should use the same importance philosophy as memory extraction.
if '왕관/기억 공통 중요도 원칙' not in a:
    crown_marker = '"(D) 이미 충분히 익혔거나 DONE에 가까운지에 따른 미해결도를 함께 비교한다.'
    if crown_marker in a:
        a = a.replace(
            crown_marker,
            '"왕관/기억 공통 중요도 원칙: 최근에 길게 말한 주제보다 반복성, 현재 활성, 상위 유지기제 중심성, 미해결도, 사용자 직접 정정을 우선한다. " +\n                ' + crown_marker,
            1
        )

analyzer.write_text(a, encoding='utf-8')

s = shared.read_text(encoding='utf-8')
# Force existing imported counseling threads through the newer policy audit when reopened.
s = re.sub(r'private static final String COLLECTOR_VERSION = "v\d+";',
           'private static final String COLLECTOR_VERSION = "v4";', s, count=1)
s = re.sub(r'private static final int CROWN_POLICY_VERSION = \d+;',
           'private static final int CROWN_POLICY_VERSION = 30;', s, count=1)
shared.write_text(s, encoding='utf-8')

g = gradle.read_text(encoding='utf-8')
g = re.sub(r'versionCode\s+\d+', 'versionCode 101830', g)
g = re.sub(r'versionName\s+"[^"]+"', 'versionName "10.18.30"', g)
gradle.write_text(g, encoding='utf-8')

print('Applied v10.18.30: importance-ranked counseling memory extraction + correction precedence')

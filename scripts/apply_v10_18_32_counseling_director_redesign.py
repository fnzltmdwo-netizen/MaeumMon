from pathlib import Path
import re

root = Path('extracted')
app = root / 'app/src/main/java/com/maeummon/app'
res = root / 'app/src/main/res'
values = res / 'values'
drawable = res / 'drawable'
gradle = root / 'app/build.gradle'

# -----------------------------------------------------------------------------
# v10.18.32
# A single counseling director above every feature.
# Public-facing style principles distilled from the counseling corpus:
# current direct evidence > correction > safety/stabilization > formulation > one small action > review.
# Also shift the whole visual system from "cute feature collection" to a calm personal counseling room.
# -----------------------------------------------------------------------------

director = app / 'CounselingDirectorPolicy.java'
director.write_text(r'''package com.maeummon.app;

/** Shared decision policy for counseling-derived features. */
public final class CounselingDirectorPolicy {
    private CounselingDirectorPolicy() {}

    public static String rules() {
        return " [전체 앱 상담 디렉터 원칙] " +
                "현재 사용자가 직접 말한 사실과 정정을 과거 기억/추론보다 우선한다. " +
                "표면 사건을 곧바로 문제로 확정하지 말고, 사실-감정-사용자가 붙인 의미-욕구/두려움-반응-그 반응이 문제를 유지하는 방식 순서로 본다. " +
                "가설은 사실처럼 단정하지 말고 경쟁 가설을 허용한다. 답에 따라 상담 방향이 실제로 바뀌는 질문만 한 번에 하나 한다. " +
                "사용자가 압도/패닉/감정폭발 상태라면 해석과 훈련보다 안정화를 먼저 한다. 안전 신호가 실제로 있을 때만 안전 대응을 우선한다. " +
                "충분한 정보가 모였으면 질문을 멈추고 '그래서 지금 힘든 핵심은 이것'을 생활말 한두 문장으로 설명한다. " +
                "개입은 현재 유지기제에 연결된 가장 작은 유효 행동 하나만 제안한다. 여러 해결책을 한꺼번에 주지 않는다. " +
                "성공은 불안 0이나 완벽한 수행이 아니라, 불안이 있어도 평소와 다른 반응을 한 번 해본 것으로 잡는다. " +
                "지난 개입 결과 HELPED/PARTIAL/NO_CHANGE/WORSE/NO_OPPORTUNITY를 다음 선택에 반드시 반영한다. " +
                "HELPED면 조금 일반화, PARTIAL이면 더 작게, NO_CHANGE면 과제/가설 재검토, WORSE면 같은 개입 중단 후 안정화/재개념화, NO_OPPORTUNITY는 실패로 보지 않는다. " +
                "새 직접 증거가 기존 formulation이나 PT와 충돌하면 기존 계획을 보존하려 하지 말고 현재 근거에 맞춰 수정/교체/종료한다. " +
                "사용자 화면에서는 전문용어보다 짧은 생활말을 쓴다. 사용자가 읽고 '아 그래서 내가 이렇게 반응했구나'를 이해한 뒤 '오늘은 이것만 해보자'로 이어지게 한다. " +
                "상담, GPT 링크, 마음 PT, 위젯, 다마고치, 리포트는 서로 다른 조언을 만들지 말고 같은 최우선 formulation과 다음 개입을 공유해야 한다. ";
    }
}
''', encoding='utf-8')

# Inject the director into every PT/model decision path already centralized in CounselingProgramAnalyzer.
analyzer = app / 'CounselingProgramAnalyzer.java'
a = analyzer.read_text(encoding='utf-8')
# Existing v10.18.29 calls all append ohStylePtRules(). Put the director before it.
a = a.replace('system + ohStylePtRules()', 'system + CounselingDirectorPolicy.rules() + ohStylePtRules()')
a = a.replace('synthesisSystem + ohStylePtRules()', 'synthesisSystem + CounselingDirectorPolicy.rules() + ohStylePtRules()')
# Avoid duplicate injection when script is reapplied.
a = a.replace('CounselingDirectorPolicy.rules() + CounselingDirectorPolicy.rules()', 'CounselingDirectorPolicy.rules()')
# Crown / memory ranking prompts that may not use ohStylePtRules get a direct policy sentence too.
if '전체 앱 상담 디렉터 원칙을 왕관/기억 판단에도 그대로 적용한다' not in a:
    marker = '왕관/기억 공통 중요도 원칙:'
    if marker in a:
        a = a.replace(marker, '전체 앱 상담 디렉터 원칙을 왕관/기억 판단에도 그대로 적용한다. ' + marker, 1)
analyzer.write_text(a, encoding='utf-8')

# Shared-link imports should be re-audited by the director policy.
shared = app / 'SharedCounselingLinkActivity.java'
s = shared.read_text(encoding='utf-8')
s = re.sub(r'private static final String COLLECTOR_VERSION = "v\d+";',
           'private static final String COLLECTOR_VERSION = "v6";', s, count=1)
s = re.sub(r'private static final int CROWN_POLICY_VERSION = \d+;',
           'private static final int CROWN_POLICY_VERSION = 32;', s, count=1)
shared.write_text(s, encoding='utf-8')

# -----------------------------------------------------------------------------
# Visual system: calm counseling-room palette, large soft cards, fewer toy-like contrasts.
# Existing color resource names are retained for compatibility across the entire app.
# -----------------------------------------------------------------------------
colors = '''<resources>
    <color name="cream">#F8F6F1</color>
    <color name="sage">#A8CDBE</color>
    <color name="sage_dark">#5E8E7E</color>
    <color name="brown">#3F4547</color>
    <color name="soft_pink">#F6E5E2</color>
    <color name="white">#FFFFFFFF</color>
    <color name="soft_gray">#F0EFEB</color>
    <color name="bubble_user">#EAF3EF</color>
    <color name="bubble_ai">#FFFDFC</color>
    <color name="soft_lavender">#ECE9F2</color>
    <color name="soft_peach">#F5E8DF</color>
    <color name="soft_yellow">#F4EBCB</color>
    <color name="soft_mint">#E3F1EB</color>
</resources>
'''
(values / 'colors.xml').write_text(colors, encoding='utf-8')

visuals = {
'bg_card.xml': '''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="#FFFDFC"/><corners android:radius="24dp"/>
    <stroke android:width="1dp" android:color="#E5E1DA"/>
    <padding android:left="18dp" android:top="17dp" android:right="18dp" android:bottom="17dp"/>
</shape>''',
'bg_input.xml': '''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="#F5F3EE"/><corners android:radius="20dp"/>
    <stroke android:width="1dp" android:color="#DDD8D0"/>
</shape>''',
'bg_button.xml': '''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="#6F9F8E"/><corners android:radius="24dp"/>
</shape>''',
'bg_nav_chip.xml': '''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="#FFFDFC"/><corners android:radius="22dp"/>
    <stroke android:width="1dp" android:color="#E4DFD7"/>
</shape>''',
'bg_nav_growth.xml': '''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="#E3F1EB"/><corners android:radius="22dp"/>
    <stroke android:width="1dp" android:color="#B9D7CB"/>
</shape>''',
'bg_pt_crown.xml': '''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="#FFF9E8"/><corners android:radius="24dp"/>
    <stroke android:width="1dp" android:color="#D9C27A"/>
</shape>''',
'bg_pt_crown_selected.xml': '''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="#6F9F8E"/><corners android:radius="24dp"/>
    <stroke android:width="1dp" android:color="#CDB66F"/>
</shape>'''
}
for name, body in visuals.items():
    (drawable / name).write_text(body, encoding='utf-8')

# Mind PT is the clearest expression of the new information hierarchy.
layout = res / 'layout/activity_mind_pt.xml'
if layout.exists():
    x = layout.read_text(encoding='utf-8')
    # More calm whitespace and less dashboard density.
    x = x.replace('android:padding="18dp"', 'android:padding="20dp"', 1)
    x = x.replace('android:padding="20dp"', 'android:padding="20dp"', 1)
    # User-facing labels: counselor language instead of training-manual language.
    replacements = {
        '왜 이걸 해?': '왜 이 연습을 할까?',
        '왜 이걸 해요?': '왜 이 연습을 할까?',
        '오늘 할 것': '오늘은 이것만',
        '성공 기준': '이 정도면 충분해',
        '훈련 후기': '해보니 어땠어?',
        '단계 로드맵': '앞으로의 방향',
    }
    for old, new in replacements.items():
        x = x.replace(old, new)
    layout.write_text(x, encoding='utf-8')

# Version bump.
g = gradle.read_text(encoding='utf-8')
g = re.sub(r'versionCode\s+\d+', 'versionCode 101832', g)
g = re.sub(r'versionName\s+"[^"]+"', 'versionName "10.18.32"', g)
gradle.write_text(g, encoding='utf-8')

print('Applied v10.18.32: unified counseling director + calm counseling-room redesign')

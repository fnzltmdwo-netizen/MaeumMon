from pathlib import Path
import re

root = Path('extracted')
app = root / 'app/src/main/java/com/maeummon/app'
analyzer = app / 'CounselingProgramAnalyzer.java'
gradle = root / 'app/build.gradle'

text = analyzer.read_text(encoding='utf-8')

# Narrow the medical exclusion rule: background mentions must never delete an otherwise psychological PT.
old1 = ('이미 저장된 PT라도 제목·reason·exercise·success criterion·stage의 핵심이 약물 감시/복약/부작용/병원/의료진 보고라면 반드시 exclude=true로 제거한다.')
new1 = ('이미 저장된 PT를 제외할 때는 매우 엄격하게 판단한다. 제목 또는 실제 exercise/success criterion/stage의 핵심 행동이 약물 감시·복약·부작용 기록·병원 방문·의료진 보고 같은 의료관리일 때만 exclude=true로 제거한다. '
        'reason이나 상담 근거에 약물·병원·의료진이 배경 설명으로 언급되었을 뿐 실제 연습이 사실/해석 분리, 감정 알아차리기, 판단 보류, 관계 경계, 충동 멈추기 같은 비의료 심리훈련이면 절대 exclude하지 않는다. '
        '왕관은 최우선 PT 하나를 뜻할 뿐 유일한 PT를 뜻하지 않는다. 서로 다른 비의료 심리훈련 축이 남아 있으면 2~4개를 보존하고, 의료 PT 하나를 제거했다는 이유로 전체를 1개로 축소하지 않는다.')
if old1 in text:
    text = text.replace(old1, new1)

old2 = ('프로그램의 핵심 행동이나 성공기준에 이런 의료관리 요소가 하나라도 들어가면 그 프로그램은 생성하지 말고 다른 비의료 심리훈련 축을 선택한다.')
new2 = ('프로그램의 실제 핵심 행동이나 성공기준 자체가 의료관리일 때만 그 프로그램을 만들지 않는다. 상담 근거나 reason에 의료 내용이 배경으로 섞였다는 이유만으로 정상적인 심리 PT를 삭제하지 않는다. '
        '의료 PT를 제외한 뒤에도 원문에 서로 다른 심리·인지·정서·대인관계·행동 훈련 근거가 있으면 최종 프로그램은 가급적 2~4개의 서로 다른 축을 유지한다. 최우선 PT 한 개만 남기는 것은 다른 유효 축이 실제로 전혀 없을 때만 허용한다.')
if old2 in text:
    text = text.replace(old2, new2)

# Add a general preservation rule near JSON instructions so generation and reranking both see it.
preserve_rule = ('PT 보존 규칙: 의료관리 PT만 제거하고 비의료 PT는 보존한다. 약물/의료진/병원이라는 단어가 reason에 등장했다는 이유만으로 제외하지 않는다. '
                 '실제 훈련 행동과 성공기준을 기준으로 판단한다. 서로 다른 유지기제와 연습행동을 가진 비의료 PT가 여러 개면 2~4개를 유지한다. 왕관 PT는 그중 우선순위 1위일 뿐이다. ')
marker = '반드시 JSON 하나만 출력한다.'
if preserve_rule not in text:
    text = text.replace(marker, preserve_rule + marker)

text = re.sub(r'CROWN_POLICY_VERSION\s*=\s*\d+', 'CROWN_POLICY_VERSION = 19', text)
analyzer.write_text(text, encoding='utf-8')

g = gradle.read_text(encoding='utf-8')
g = re.sub(r'versionCode\s+\d+', 'versionCode 101823', g)
g = re.sub(r'versionName\s+"[^"]+"', 'versionName "10.18.23"', g)
gradle.write_text(g, encoding='utf-8')

print('Applied v10.18.23: preserve nonmedical PTs while excluding only truly medical-management PTs')

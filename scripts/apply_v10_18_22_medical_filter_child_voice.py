from pathlib import Path
import re

root = Path('extracted')
app = root / 'app/src/main/java/com/maeummon/app'
analyzer = app / 'CounselingProgramAnalyzer.java'
prefs = app / 'MascotWidgetPrefs.java'
gradle = root / 'app/build.gradle'

text = analyzer.read_text(encoding='utf-8')
medical_rule = (
    '최우선 하드 규칙: 마음 PT는 반복 연습으로 바뀔 수 있는 심리·인지·정서·대인관계·행동 능력만 허용한다. '
    '약물 상태 감시, 약 이름/용량/복용/복약, 부작용 기록, 병원 방문, 진료, 처방, 의료진·의사에게 보고, 이상징후를 의료진에게 전달, '
    '의료 피드백 횟수, 약 중단·변경 판단 같은 의료관리 행동은 상담 원문과 안전 맥락에는 보관할 수 있지만 PT 제목·reason·exercise·success criterion·stage·왕관 후보에는 절대 넣지 않는다. '
    '프로그램의 핵심 행동이나 성공기준에 이런 의료관리 요소가 하나라도 들어가면 그 프로그램은 생성하지 말고 다른 비의료 심리훈련 축을 선택한다. '
    '의료 관련 장면에서 심리훈련을 뽑아야 한다면 불안 알아차리기, 감정 이름 붙이기, 충동 전에 멈추기, 사실과 해석 나누기처럼 의료 행동 없이 독립적으로 연습 가능한 능력만 사용한다. '
)
marker = '반드시 JSON 하나만 출력한다.'
if marker in text and medical_rule not in text:
    text = text.replace(marker, medical_rule + marker)

needle = '병원 방문, 의료진 보고, 약 이름·용량·복약·부작용 기록, 진료 피드백 횟수처럼 외부 의료관리 행동 자체가 핵심인 PT는 마음훈련이 아니므로 exclude=true로 표시한다.'
replacement = ('병원 방문, 의료진 보고, 약 이름·용량·복약·부작용 기록, 진료 피드백 횟수처럼 외부 의료관리 행동 자체가 핵심인 PT는 마음훈련이 아니므로 exclude=true로 표시한다. '
               '이미 저장된 PT라도 제목·reason·exercise·success criterion·stage의 핵심이 약물 감시/복약/부작용/병원/의료진 보고라면 반드시 exclude=true로 제거한다.')
if needle in text:
    text = text.replace(needle, replacement)

text = re.sub(r'CROWN_POLICY_VERSION\s*=\s*\d+', 'CROWN_POLICY_VERSION = 18', text)
analyzer.write_text(text, encoding='utf-8')

p = prefs.read_text(encoding='utf-8')
start = p.find('    public static String youngify(String raw) {')
end = p.find('    public static String widgetLine(Context c) {', start)
if start < 0 or end < 0:
    raise SystemExit('v10.18.22: youngify anchors missing')

method = r'''    public static String youngify(String raw) {
        if (raw == null) return "";
        String s = raw.replace('\n', ' ').replace('\r', ' ').replaceAll("\\s+", " ").trim();
        if (s.isEmpty()) return s;

        String low = s.toLowerCase(java.util.Locale.KOREA);
        String[] medical = {"의료진", "담당 의료", "병원", "진료", "처방", "복약", "약물", "부작용", "용량", "의사에게", "의료적"};
        for (String k : medical) {
            if (low.contains(k)) {
                return "승재야, 오늘 마음이 어땠는지만 우리 같이 천천히 봐보자. 다 하려고 하지 말고 하나씩만 보면 돼.";
            }
        }

        s = s.replace("인지적 분리", "따로 보기")
             .replace("인지 분리", "따로 보기")
             .replace("인지적 재평가", "다시 생각해보기")
             .replace("재평가", "다시 생각해보기")
             .replace("감지된 사실", "실제로 있었던 일")
             .replace("객관적 사실", "진짜 있었던 일")
             .replace("자동 해석", "나도 모르게 바로 든 생각")
             .replace("즉각적 해석", "바로 든 생각")
             .replace("부정적 해석", "안 좋게 생각한 것")
             .replace("부정 해석", "안 좋게 생각한 것")
             .replace("판단 유보", "바로 결론내리지 않기")
             .replace("불확실성", "아직 잘 모르는 마음")
             .replace("대인관계", "사람 사이")
             .replace("대인 접촉", "사람 만나기")
             .replace("소진", "너무 지침")
             .replace("긴장도", "얼마나 긴장됐는지")
             .replace("충동성", "갑자기 확 하고 싶은 마음")
             .replace("기분 변동", "마음이 왔다 갔다 한 것")
             .replace("정서", "마음")
             .replace("감정 반응", "마음 반응")
             .replace("반복적 확인", "자꾸 다시 확인하기")
             .replace("점진적 노출", "조금씩 해보기")
             .replace("행동 억제", "바로 하지 않고 잠깐 멈추기")
             .replace("관계 위험", "사이가 나빠질 것 같은 걱정")
             .replace("자기 가치", "내가 괜찮은 사람인지")
             .replace("모니터링", "살펴보기")
             .replace("기록합니다", "적어보자")
             .replace("기록한다", "적어보자")
             .replace("확인합니다", "같이 봐보자")
             .replace("확인한다", "같이 봐보자")
             .replace("선택합니다", "하나 골라보자")
             .replace("선택한다", "하나 골라보자")
             .replace("시도합니다", "한번 해보자")
             .replace("시도한다", "한번 해보자")
             .replace("적용합니다", "써보자")
             .replace("적용한다", "써보자")
             .replace("유지합니다", "그대로 해보자")
             .replace("유지한다", "그대로 해보자")
             .replace("관찰합니다", "같이 봐보자")
             .replace("관찰한다", "같이 봐보자")
             .replace("구분합니다", "따로 봐보자")
             .replace("구분한다", "따로 봐보자")
             .replace("조절합니다", "천천히 해보자")
             .replace("조절한다", "천천히 해보자");

        s = s.replace("합니다.", "해보자.")
             .replace("하세요.", "해보자.")
             .replace("해야 합니다.", "하면 돼.")
             .replace("필요합니다.", "필요해.")
             .replace("가능합니다.", "할 수 있어.")
             .replace("수 있습니다.", "수 있어.")
             .replace("입니다.", "이야.")
             .replace("됩니다.", "돼.");

        if (!s.startsWith("승재야") && !s.startsWith("우리")) s = "승재야, 우리 " + s;
        s = s.replace(";", ". ").replace(" 또한 ", ". 그리고 ").trim();
        if (!s.endsWith(".") && !s.endsWith("!") && !s.endsWith("?")) s += ".";
        return s;
    }

'''
p = p[:start] + method + p[end:]
prefs.write_text(p, encoding='utf-8')

g = gradle.read_text(encoding='utf-8')
g = re.sub(r'versionCode\s+\d+', 'versionCode 101822', g)
g = re.sub(r'versionName\s+"[^"]+"', 'versionName "10.18.22"', g)
gradle.write_text(g, encoding='utf-8')

print('Applied v10.18.22 medical PT hard filter + child mascot voice')

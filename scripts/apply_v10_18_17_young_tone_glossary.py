from pathlib import Path
import re

root = Path('extracted')
app = root / 'app/src/main/java/com/maeummon/app'
prefs = app / 'MascotWidgetPrefs.java'
gradle = root / 'app/build.gradle'

text = prefs.read_text(encoding='utf-8')

# Expand only the wording translation layer. Keep PT numbers, conditions, choices and actions intact.
anchor = '        String s = raw.trim();\n        if (s.isEmpty()) return s;\n'
if anchor not in text:
    raise SystemExit('v10.18.17: youngify anchor missing')

insert = '''        String s = raw.trim();\n        if (s.isEmpty()) return s;\n\n        // Young-Seungjae glossary: translate clinical/abstract wording into everyday Korean\n        // without deleting the original meaning, numbers, options or behavioral instructions.\n        s = s.replace("인지적 분리 및 재평가", "있었던 일이랑 내가 생각한 걸 따로 보고 다시 생각해보기")\n             .replace("인지적 분리", "있었던 일이랑 내가 생각한 걸 따로 보기")\n             .replace("인지 재평가", "다시 생각해보기")\n             .replace("재평가", "다시 생각해보기")\n             .replace("사실과 해석", "있었던 일이랑 내가 생각한 것")\n             .replace("감지된 사실", "실제로 있었던 일")\n             .replace("자동 해석", "나도 모르게 바로 든 생각")\n             .replace("부정적 해석", "안 좋게 생각한 것")\n             .replace("부정 해석", "안 좋게 생각한 것")\n             .replace("대안 해석", "다르게 볼 수 있는 생각")\n             .replace("관계 위험 판단", "나를 싫어할 것 같다고 바로 결론내리기")\n             .replace("관계 위험", "나를 싫어할 것 같은 느낌")\n             .replace("거절 신호", "나를 싫어하는 것처럼 느껴지는 신호")\n             .replace("불확실성 내성", "아직 모르는 상태를 조금 기다리는 힘")\n             .replace("판단 유보", "바로 결론내리지 않기")\n             .replace("대인 접촉", "사람 만나기")\n             .replace("대인 상황", "사람을 만나는 상황")\n             .replace("사회적 접촉", "사람 만나기")\n             .replace("소진", "너무 지침")\n             .replace("에너지 소진", "기운이 너무 빠지는 것")\n             .replace("긴장도", "얼마나 긴장됐는지")\n             .replace("회복 시간", "다시 편해질 때까지 걸린 시간")\n             .replace("회복 조건", "다시 편해지는 데 필요한 것")\n             .replace("반복적 확인", "자꾸 다시 확인하기")\n             .replace("확인 행동", "자꾸 확인하는 행동")\n             .replace("회피 행동", "피하고 싶은 행동")\n             .replace("유지기제", "자꾸 같은 일이 반복되게 만드는 이유")\n             .replace("핵심 유지기제", "자꾸 같은 일이 반복되게 만드는 가장 큰 이유")\n             .replace("정서 조절", "마음을 조금 가라앉히기")\n             .replace("감정 조절", "마음을 조금 가라앉히기")\n             .replace("인지", "생각")\n             .replace("정서", "마음")\n             .replace("대인", "사람 사이")\n             .replace("모니터링", "살펴보기")\n             .replace("반응 강도", "얼마나 세게 느껴졌는지");\n'''

text = text.replace(anchor, insert, 1)

# Soften a few formal nouns that often survive the first pass.
old_tail = '        // Generic formal ending conversion, after specific replacements above.\n'
if old_tail not in text:
    raise SystemExit('v10.18.17: youngify tail anchor missing')
extra = '''        s = s.replace("분리해", "따로 봐")\n             .replace("구분해", "나눠서 봐")\n             .replace("평가해", "한번 봐")\n             .replace("관찰해", "살펴봐")\n             .replace("완화", "조금 줄이기");\n\n'''
text = text.replace(old_tail, extra + old_tail, 1)

prefs.write_text(text, encoding='utf-8')

# Version bump only. No PT logic / sync / TTS behavior changes.
g = gradle.read_text(encoding='utf-8')
g, n1 = re.subn(r'versionCode\s+\d+', 'versionCode 101817', g, count=1)
g, n2 = re.subn(r'versionName\s+"[^"]+"', 'versionName "10.18.17"', g, count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit('v10.18.17: gradle version anchor missing')
gradle.write_text(g, encoding='utf-8')

print('Applied v10.18.17 expanded young-Seungjae everyday-language glossary')

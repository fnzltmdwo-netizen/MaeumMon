from pathlib import Path
import re

root = Path('extracted')
app = root / 'app/src/main/java/com/maeummon/app'
prefs = app / 'MascotWidgetPrefs.java'
gradle = root / 'app/build.gradle'

text = prefs.read_text(encoding='utf-8')

# v10.18.19 only polishes mascot-facing wording.
# Do NOT alter PT count, merge logic, stages, success criteria, sync, or TTS behavior.
anchor = '        // Generic formal ending conversion, after specific replacements above.\n'
if anchor not in text:
    raise SystemExit('v10.18.19: youngify tail anchor missing')

extra = '''        // v10.18.19: phrase-level naturalization for wording that still sounded like a clinical report.\n        // Preserve the underlying PT meaning; only change how the mascot says it.\n        s = s.replace("자가 생각적 해석과 감정 반응 조절", "내가 바로 떠올린 생각이랑 마음 반응을 천천히 살펴보기")\n             .replace("자가 생각적 해석", "내가 바로 떠올린 생각")\n             .replace("감정 반응 조절", "마음이 확 올라올 때 잠깐 멈춰보기")\n             .replace("감정 반응", "마음이 올라오는 반응")\n             .replace("즉각적 해석 지연", "바로 뜻을 정하지 않고 조금 기다려보기")\n             .replace("즉각적 해석", "바로 떠오른 생각")\n             .replace("자동 판단 억제", "바로 결론내리지 않기")\n             .replace("자동 판단", "바로 내린 결론")\n             .replace("경보와 현실 구분", "걱정이 울린 거랑 실제로 벌어진 일을 따로 보기")\n             .replace("현실 구분", "실제로 벌어진 일과 따로 보기")\n             .replace("점진적 노출", "아주 조금씩 해보기")\n             .replace("정서적 노출", "그 마음을 피하지 않고 조금 느껴보기")\n             .replace("소외 불안", "나만 빠진 것 같은 불안")\n             .replace("소외감", "나만 빠진 것 같은 마음")\n             .replace("무반응", "답이 없을 때")\n             .replace("관계 신호", "상대가 보내는 작은 신호")\n             .replace("자기 가치", "내가 괜찮은 사람인지에 대한 마음")\n             .replace("인지 왜곡", "생각이 한쪽으로 치우친 것")\n             .replace("인지 분리", "생각과 실제 일을 따로 보기")\n             .replace("해석 지연", "바로 뜻을 정하지 않고 조금 기다리기")\n             .replace("감정적 반응", "마음이 먼저 튀어나오는 반응")\n             .replace("행동 반응", "바로 해버리고 싶은 행동")\n             .replace("정서 안정", "마음이 조금 편해지는 것")\n             .replace("사회적 에너지", "사람 만날 때 쓰는 기운")\n             .replace("회복감", "다시 좀 편해진 느낌")\n             .replace("자극", "마음을 건드리는 일")\n             .replace("트리거", "마음을 확 건드린 일");\n\n'''
text = text.replace(anchor, extra + anchor, 1)
prefs.write_text(text, encoding='utf-8')

# Version bump only; keep applicationId unchanged so Android treats it as the same app package.
g = gradle.read_text(encoding='utf-8')
g, n1 = re.subn(r'versionCode\s+\d+', 'versionCode 101819', g, count=1)
g, n2 = re.subn(r'versionName\s+"[^"]+"', 'versionName "10.18.19"', g, count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit('v10.18.19: gradle version anchor missing')
gradle.write_text(g, encoding='utf-8')

print('Applied v10.18.19 mascot natural-tone polish only; PT structure untouched')

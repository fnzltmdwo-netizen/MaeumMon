from pathlib import Path
import re

root = Path('extracted')
app = root / 'app/src/main/java/com/maeummon/app'
gradle = root / 'app/build.gradle'

# v10.18.34
# Keep counselor-facing surfaces calm and professional; add kaomoji only to the young-Seungjae
# mascot layer so the app feels warm without turning the counseling content into decoration.

focus = app / 'CurrentCounselingFocus.java'
x = focus.read_text(encoding='utf-8')

old = '''    public static String mascotLine(Context c) {\n        Snapshot s = read(c);\n        if (s.action.isEmpty()) return \"\";\n        return \"우리 오늘은 이것만 해보자. \" + shortText(s.action, 120);\n    }\n'''
new = '''    public static String mascotLine(Context c) {\n        Snapshot s = read(c);\n        if (s.action.isEmpty()) return \"\";\n        String face = mascotFace(s.core + \" \" + s.flow + \" \" + s.action);\n        return face + \"  우리 오늘은 이것만 해보자. \" + shortText(s.action, 112);\n    }\n\n    private static String mascotFace(String raw) {\n        String s = clean(raw);\n        if (contains(s, \"압도\", \"번아웃\", \"너무 힘\", \"지침\", \"무너\", \"울고\", \"불안\"))\n            return \"(｡•́︿•̀｡)\";\n        if (contains(s, \"쉬\", \"회복\", \"잠깐 멈\", \"기다리\", \"천천히\"))\n            return \"₍՞ᵕ.ᵕ՞₎\";\n        if (contains(s, \"해냈\", \"성공\", \"잘했\", \"도전\", \"한 번\"))\n            return \"ദ്ദി ˉ͈̀꒳ˉ͈́ )✧\";\n        if (contains(s, \"괜찮\", \"조금 편\", \"안심\", \"좋아\"))\n            return \"(*´∪`)\";\n        return \"(*ˊᵕˋ*)ﾉ\";\n    }\n'''
if old not in x:
    raise SystemExit('v10.18.34: CurrentCounselingFocus mascotLine anchor missing')
x = x.replace(old, new, 1)
focus.write_text(x, encoding='utf-8')

# Version bump only. Widget/current-focus cards remain intentionally clean.
g = gradle.read_text(encoding='utf-8')
g = re.sub(r'versionCode\\s+\\d+', 'versionCode 101834', g)
g = re.sub(r'versionName\\s+\"[^\"]+\"', 'versionName \"10.18.34\"', g)
gradle.write_text(g, encoding='utf-8')

print('Applied v10.18.34: context-aware kaomoji accents for young-Seungjae mascot only')

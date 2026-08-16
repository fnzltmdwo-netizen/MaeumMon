from pathlib import Path
import re

root = Path('extracted')
app = root / 'app/src/main/java/com/maeummon/app'
res = root / 'app/src/main/res'
gradle = root / 'app/build.gradle'

# v10.18.37
# Emoji Design System: use emoji as a restrained visual language across the app,
# not as noisy decoration. Preserve crown priority semantics and calm counseling-room tone.

# 1) Shared semantic emoji vocabulary for future surfaces.
tokens = app / 'EmojiDesignTokens.java'
tokens.write_text(r'''package com.maeummon.app;

/** Small semantic emoji vocabulary for consistent MaeumMon UI labeling. */
public final class EmojiDesignTokens {
    private EmojiDesignTokens() {}
    public static final String HOME = "🏡";
    public static final String COUNSEL = "💬";
    public static final String CORE = "💛";
    public static final String FLOW = "🧠";
    public static final String ACTION = "🌱";
    public static final String CROWN = "👑";
    public static final String TARGET = "🎯";
    public static final String JOURNAL = "📖";
    public static final String WRITE = "📝";
    public static final String CHECKIN = "🌤️";
    public static final String GROWTH = "🌿";
    public static final String REPORT = "📈";
    public static final String SETTINGS = "⚙️";
    public static final String REST = "🫧";
    public static final String HEART = "🤍";
    public static final String CELEBRATE = "✨";
}
''', encoding='utf-8')

# 2) Add emoji prefixes to common user-facing labels in XML layouts.
# Exact-text replacement only, so paragraph content and counseling messages stay clean.
label_map = {
    '상담': '💬 상담',
    '상담하기': '💬 상담하기',
    '마음 PT': '👑 마음 PT',
    '오늘은 이것만': '🌱 오늘은 이것만',
    '왜 이 연습을 할까?': '💛 왜 이 연습을 할까?',
    '이 정도면 충분해': '🎯 이 정도면 충분해',
    '해보니 어땠어?': '🌤️ 해보니 어땠어?',
    '일기': '📖 일기',
    '기록': '📝 기록',
    '체크인': '🌤️ 체크인',
    '성장': '🌿 성장',
    '리포트': '📈 리포트',
    '설정': '⚙️ 설정',
    '마이룸': '🏡 마이룸',
    '책장': '📚 책장',
}
for layout in (res / 'layout').glob('*.xml'):
    text = layout.read_text(encoding='utf-8')
    original = text
    for old, new in label_map.items():
        # android:text exact literal only; avoid duplicating existing emoji labels.
        text = text.replace(f'android:text="{old}"', f'android:text="{new}"')
    if text != original:
        layout.write_text(text, encoding='utf-8')

# 3) Mind PT: crown remains primary; secondary section labels get semantic icons.
pt = app / 'MindPtActivity.java'
if pt.exists():
    t = pt.read_text(encoding='utf-8')
    # Do not double-prefix crown restored in v36.
    t = t.replace('"👑 👑 "', '"👑 "')
    pt.write_text(t, encoding='utf-8')

# 4) Current focus wording stays visually coherent and restrained.
focus = app / 'CurrentCounselingFocus.java'
if focus.exists():
    f = focus.read_text(encoding='utf-8')
    f = f.replace('❤️ 요즘 가장 중요한 마음', '💛 요즘 가장 중요한 마음')
    f = f.replace('🧠 반복되는 흐름', '🧠 반복되는 흐름')
    f = f.replace('🌱 오늘은 이것만', '🌱 오늘은 이것만')
    focus.write_text(f, encoding='utf-8')

# 5) Settings: add icons only to section/action labels, not explanatory body text.
settings = app / 'MascotWidgetSettingsActivity.java'
if settings.exists():
    s = settings.read_text(encoding='utf-8')
    replacements = {
        '"OpenAI API Key': '"🔑 OpenAI API Key',
        '"백업': '"💾 백업',
        '"복원': '"♻️ 복원',
        '"홈화면 감지 권한 열기"': '"🏡 홈화면 감지 권한 열기"',
        '"최근 앱·앱 목록 숨김 감지 켜기"': '"👀 최근 앱·앱 목록 숨김 감지 켜기"',
    }
    for old, new in replacements.items():
        s = s.replace(old, new)
    settings.write_text(s, encoding='utf-8')

# 6) Gentle card accents: emoji design should feel warm, not toy-like.
drawable = res / 'drawable'
(drawable / 'bg_emoji_section.xml').write_text('''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="#FFFDFC"/>
    <corners android:radius="22dp"/>
    <stroke android:width="1dp" android:color="#E8E2D9"/>
</shape>
''', encoding='utf-8')

# 7) Version bump.
g = gradle.read_text(encoding='utf-8')
g = re.sub(r'versionCode\s+\d+', 'versionCode 101837', g)
g = re.sub(r'versionName\s+"[^"]+"', 'versionName "10.18.37"', g)
gradle.write_text(g, encoding='utf-8')

print('Applied v10.18.37: restrained semantic emoji design system across MaeumMon UI')

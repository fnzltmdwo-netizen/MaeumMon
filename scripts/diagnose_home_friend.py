from pathlib import Path
root=Path('extracted')
needles=['바탕화면 친구','어린 승재를 홈화면 위에 띄우기','휴대폰을 켜면 자동으로 나오기','홈화면 감지 권한 열기','최근 앱·앱 목록 숨김 감지 켜기']
for p in root.rglob('*'):
    if not p.is_file() or p.suffix not in {'.java','.kt','.xml'}: continue
    try: t=p.read_text(encoding='utf-8',errors='ignore')
    except: continue
    if any(n in t for n in needles):
        print('\n===FILE',p,'===')
        for n in needles:
            i=t.find(n)
            if i>=0:
                print(t[max(0,i-5000):min(len(t),i+12000)])
                break
print('HOME_FRIEND_DIAG_DONE')

from pathlib import Path
root=Path('extracted')
needles=['바탕화면 친구','어린 승재를 홈화면 위에 띄우기','휴대폰을 켜면 자동으로 나오기','홈화면 감지 권한 열기','최근 앱·앱 목록 숨김 감지 켜기','overlaySwitch','bootSwitch','openUsageAccessButton','openAccessibilityButton','usageStatusText','accessibilityStatusText']
for p in root.rglob('*'):
    if not p.is_file() or p.suffix not in {'.java','.kt','.xml'}: continue
    try: t=p.read_text(encoding='utf-8',errors='ignore')
    except: continue
    hits=[]
    for n in needles:
        start=0
        while True:
            i=t.find(n,start)
            if i<0: break
            hits.append(i); start=i+1
    if hits:
        print('\n===FILE',p,'===')
        for i in sorted(set(hits)):
            print('\n---CTX---\n'+t[max(0,i-4200):min(len(t),i+8500)])
print('HOME_FRIEND_DIAG_DONE')

from pathlib import Path
root=Path('extracted/app/src/main/java/com/maeummon/app')
needles=['overlaySwitch','bootSwitch','openUsageAccessButton','openAccessibilityButton','usageStatusText','accessibilityStatusText']
for p in root.rglob('*.java'):
    t=p.read_text(encoding='utf-8',errors='ignore')
    if any(n in t for n in needles):
        print('\n===FILE',p,'===')
        hits=[]
        for n in needles:
            start=0
            while True:
                i=t.find(n,start)
                if i<0: break
                hits.append(i); start=i+1
        for i in sorted(set(hits)):
            print('\n---CTX---\n',t[max(0,i-3500):min(len(t),i+6000)])
print('HOME_FRIEND_LOGIC_DONE')

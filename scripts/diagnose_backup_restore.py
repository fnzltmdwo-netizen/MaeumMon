from pathlib import Path
root=Path('extracted')
needles=['백업','복원','backup','restore','ACTION_CREATE_DOCUMENT','ACTION_OPEN_DOCUMENT','ActivityResultLauncher','전체 백업','전체 복원','export','import']
for p in root.rglob('*'):
    if not p.is_file() or p.suffix.lower() not in {'.java','.kt','.xml'}: continue
    try: t=p.read_text(encoding='utf-8',errors='ignore')
    except: continue
    hits=[]
    low=t.lower()
    for n in needles:
        start=0; key=n.lower()
        while True:
            i=low.find(key,start)
            if i<0: break
            hits.append(i); start=i+1
    if hits:
        print('\n===FILE',p,'===')
        for i in sorted(set(hits))[:12]:
            print('\n---CTX---\n'+t[max(0,i-2200):min(len(t),i+4200)])
print('BACKUP_RESTORE_DIAG_DONE')

from pathlib import Path
import shutil
root=Path('extracted')
out=Path('backup_diag_files')
if out.exists(): shutil.rmtree(out)
out.mkdir(parents=True, exist_ok=True)
needles=['백업','복원','backup','restore','ACTION_CREATE_DOCUMENT','ACTION_OPEN_DOCUMENT','ActivityResultLauncher','전체 백업','전체 복원','export','import']
matched=[]
for p in root.rglob('*'):
    if not p.is_file() or p.suffix.lower() not in {'.java','.kt','.xml'}: continue
    try: t=p.read_text(encoding='utf-8',errors='ignore')
    except: continue
    low=t.lower()
    if any(n.lower() in low for n in needles):
        matched.append(p)
        rel=p.relative_to(root)
        target=out/rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p,target)
        print('MATCH',rel)
(out/'FILES.txt').write_text('\n'.join(str(p.relative_to(root)) for p in matched),encoding='utf-8')
print('BACKUP_RESTORE_DIAG_DONE',len(matched))

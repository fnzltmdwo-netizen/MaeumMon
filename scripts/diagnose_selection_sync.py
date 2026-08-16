from pathlib import Path
root=Path('extracted')
needles=['CentralMindPtState','selected','selectedProgram','selected_pt','current PT','CURRENT_PT','mascotLine','widgetLine','MindTrainingStore','setSelected','selectedMuscle','selectedTitle']
for p in root.rglob('*'):
    if not p.is_file() or p.suffix.lower() not in {'.java','.kt'}: continue
    try: t=p.read_text(encoding='utf-8',errors='ignore')
    except: continue
    low=t.lower()
    hits=[]
    for n in needles:
        idx=low.find(n.lower())
        if idx>=0: hits.append(idx)
    if hits:
        print('\n===FILE',p,'===')
        for i in sorted(set(hits))[:8]:
            print('\n---CTX---\n'+t[max(0,i-1800):min(len(t),i+3600)])
print('SELECTION_SYNC_DIAG_DONE')

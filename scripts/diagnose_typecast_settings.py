from pathlib import Path

root=Path('extracted')
for p in root.rglob('*'):
    if p.is_file() and p.suffix in {'.java','.kt','.xml'}:
        try:
            t=p.read_text(encoding='utf-8',errors='ignore')
        except Exception:
            continue
        if 'Typecast 어린이 음성 사용' in t or 'TYPECAST 세부 음성 설정' in t or '남자 어린이 목소리 찾기' in t or 'Voice ID' in t and 'Typecast' in t:
            print('\n===',p,'===')
            for needle in ['Typecast 어린이 음성 사용','TYPECAST 세부 음성 설정','남자 어린이 목소리 찾기','Voice ID']:
                i=t.find(needle)
                if i>=0:
                    print(t[max(0,i-1800):min(len(t),i+5000)])
                    break
raise SystemExit('diagnostic done')

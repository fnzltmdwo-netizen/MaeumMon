from pathlib import Path
import re

root = Path('extracted')
app = root / 'app/src/main/java/com/maeummon/app'
settings = app / 'MascotWidgetSettingsActivity.java'
gradle = root / 'app/build.gradle'

text = settings.read_text(encoding='utf-8')
anchor = '        // OpenAI API key accordion. Uses the exact same preference key as the rest of MaeumMon.\n'
if anchor not in text:
    raise SystemExit('v10.18.18: OpenAI accordion anchor missing')

section = r'''        // Typecast settings moved here from the chat settings screen. Same AppPrefs keys / same engine.
        final android.content.SharedPreferences typePrefs = getSharedPreferences(AppPrefs.PREFS, MODE_PRIVATE);
        final LinearLayout typeBox = new LinearLayout(this);
        typeBox.setOrientation(LinearLayout.VERTICAL);
        typeBox.setBackground(round(Color.parseColor("#F5F1FF"), 24, Color.parseColor("#E4DDF4")));
        typeBox.setPadding(dp(15), dp(12), dp(15), dp(12));

        final TextView typeHeader = t("🧸 Typecast 어린 승재 목소리   ▸", 17, true);
        typeHeader.setPadding(0, dp(4), 0, dp(4));
        typeBox.addView(typeHeader, new LinearLayout.LayoutParams(-1, -2));

        final LinearLayout typeContent = new LinearLayout(this);
        typeContent.setOrientation(LinearLayout.VERTICAL);
        typeContent.setPadding(0, dp(12), 0, 0);
        typeContent.setVisibility(View.GONE);

        final Switch typeEnabled = new Switch(this);
        typeEnabled.setText("Typecast 어린이 음성 사용 (우선)");
        typeEnabled.setTextSize(15);
        typeEnabled.setTextColor(text);
        typeEnabled.setChecked(typePrefs.getBoolean(AppPrefs.KEY_TYPECAST_ENABLED, false));
        typeContent.addView(typeEnabled, new LinearLayout.LayoutParams(-1, -2));

        final EditText typeKey = new EditText(this);
        typeKey.setSingleLine(true);
        typeKey.setTextSize(14);
        typeKey.setTextColor(text);
        typeKey.setHint("Typecast API Key");
        typeKey.setHintTextColor(Color.parseColor("#AAA8B8"));
        typeKey.setInputType(android.text.InputType.TYPE_CLASS_TEXT | android.text.InputType.TYPE_TEXT_VARIATION_PASSWORD);
        typeKey.setPadding(dp(14), dp(10), dp(14), dp(10));
        typeKey.setBackground(round(Color.WHITE, 18, Color.parseColor("#E4DFF2")));
        typeKey.setText(typePrefs.getString(AppPrefs.KEY_TYPECAST_API_KEY, ""));
        LinearLayout.LayoutParams tkp = new LinearLayout.LayoutParams(-1, dp(50)); tkp.setMargins(0, dp(9), 0, 0);
        typeContent.addView(typeKey, tkp);

        final EditText typeVoice = new EditText(this);
        typeVoice.setSingleLine(true);
        typeVoice.setTextSize(14);
        typeVoice.setTextColor(text);
        typeVoice.setHint("Voice ID (목소리 찾기로 자동 입력 가능)");
        typeVoice.setHintTextColor(Color.parseColor("#AAA8B8"));
        typeVoice.setInputType(android.text.InputType.TYPE_CLASS_TEXT | android.text.InputType.TYPE_TEXT_VARIATION_VISIBLE_PASSWORD);
        typeVoice.setPadding(dp(14), dp(10), dp(14), dp(10));
        typeVoice.setBackground(round(Color.WHITE, 18, Color.parseColor("#E4DFF2")));
        typeVoice.setText(typePrefs.getString(AppPrefs.KEY_TYPECAST_VOICE_ID, ""));
        LinearLayout.LayoutParams tvp = new LinearLayout.LayoutParams(-1, dp(50)); tvp.setMargins(0, dp(8), 0, 0);
        typeContent.addView(typeVoice, tvp);

        Button findVoice = new Button(this);
        findVoice.setText("👦 남자 어린이 목소리 찾기"); findVoice.setAllCaps(false); findVoice.setTextColor(text);
        findVoice.setBackground(round(Color.parseColor("#F8FFFC"), 20, Color.parseColor("#CBEDE1")));
        LinearLayout.LayoutParams fvp = new LinearLayout.LayoutParams(-1, dp(50)); fvp.setMargins(0, dp(9), 0, 0);
        typeContent.addView(findVoice, fvp);

        Button advanced = new Button(this);
        advanced.setText("🎛 TYPECAST 세부 음성 설정"); advanced.setAllCaps(false); advanced.setTextColor(text);
        advanced.setBackground(round(Color.parseColor("#F8FFFC"), 20, Color.parseColor("#CBEDE1")));
        LinearLayout.LayoutParams avp = new LinearLayout.LayoutParams(-1, dp(50)); avp.setMargins(0, dp(8), 0, 0);
        typeContent.addView(advanced, avp);

        final TextView typeSummary = t(typecastSummary(), 12, false);
        typeSummary.setTextColor(Color.parseColor("#777487"));
        LinearLayout.LayoutParams tsp = new LinearLayout.LayoutParams(-1, -2); tsp.setMargins(dp(4), dp(8), dp(4), 0);
        typeContent.addView(typeSummary, tsp);

        final TextView typeStatus = t("", 12, false);
        typeStatus.setTextColor(Color.parseColor("#6A9588"));
        LinearLayout.LayoutParams tstp = new LinearLayout.LayoutParams(-1, -2); tstp.setMargins(dp(4), dp(5), dp(4), 0);
        typeContent.addView(typeStatus, tstp);

        LinearLayout typeButtons = new LinearLayout(this); typeButtons.setOrientation(LinearLayout.HORIZONTAL);
        Button typeSave = new Button(this); typeSave.setText("TYPECAST 저장"); typeSave.setAllCaps(false); typeSave.setTextColor(text);
        typeSave.setBackground(round(Color.WHITE, 20, Color.parseColor("#D7EAE4")));
        Button typeTest = new Button(this); typeTest.setText("🌙 목소리 테스트"); typeTest.setAllCaps(false); typeTest.setTextColor(Color.WHITE);
        typeTest.setBackground(round(mint, 20, Color.parseColor("#7DCBB0")));
        LinearLayout.LayoutParams tb1 = new LinearLayout.LayoutParams(0, dp(50), 1f); tb1.setMargins(0, dp(9), dp(5), 0);
        LinearLayout.LayoutParams tb2 = new LinearLayout.LayoutParams(0, dp(50), 1f); tb2.setMargins(dp(5), dp(9), 0, 0);
        typeButtons.addView(typeSave, tb1); typeButtons.addView(typeTest, tb2);
        typeContent.addView(typeButtons, new LinearLayout.LayoutParams(-1, -2));

        TextView typeHint = t("API Key를 넣고 ‘어린이 목소리 찾기’를 눌러 Voice ID를 선택해줘.", 12, false);
        typeHint.setTextColor(Color.parseColor("#9693A5"));
        LinearLayout.LayoutParams thp = new LinearLayout.LayoutParams(-1, -2); thp.setMargins(dp(4), dp(8), dp(4), 0);
        typeContent.addView(typeHint, thp);

        typeBox.addView(typeContent, new LinearLayout.LayoutParams(-1, -2));
        add(root, typeBox, 0, 8, 0, 10);

        typeHeader.setOnClickListener(v -> {
            boolean show = typeContent.getVisibility() != View.VISIBLE;
            typeContent.setVisibility(show ? View.VISIBLE : View.GONE);
            typeHeader.setText(show ? "🧸 Typecast 어린 승재 목소리   ▾" : "🧸 Typecast 어린 승재 목소리   ▸");
        });

        final Runnable saveTypecast = () -> {
            String k = typeKey.getText().toString().trim();
            String vid = typeVoice.getText().toString().trim();
            typePrefs.edit()
                    .putString(AppPrefs.KEY_TYPECAST_API_KEY, k)
                    .putString(AppPrefs.KEY_TYPECAST_VOICE_ID, vid)
                    .putString(AppPrefs.KEY_TYPECAST_MODEL_ID, "ssfm-v30")
                    .putBoolean(AppPrefs.KEY_TYPECAST_ENABLED, typeEnabled.isChecked())
                    .apply();
            typeSummary.setText(typecastSummary());
        };

        typeSave.setOnClickListener(v -> {
            saveTypecast.run();
            typeStatus.setText("Typecast 설정 저장 완료 ✓");
            Toast.makeText(this, "Typecast 설정 저장 완료", Toast.LENGTH_SHORT).show();
        });

        findVoice.setOnClickListener(v -> {
            String k = typeKey.getText().toString().trim();
            if (k.isEmpty()) { typeStatus.setText("먼저 Typecast API Key를 입력해줘."); return; }
            typeStatus.setText("남자 어린이 목소리를 불러오는 중…");
            TypecastClient.listChildMaleVoices(k, new TypecastClient.VoicesListener() {
                @Override public void onSuccess(java.util.List<TypecastClient.Voice> voices) {
                    if (voices == null || voices.isEmpty()) { typeStatus.setText("남자 어린이 목소리를 찾지 못했어. Voice ID를 직접 넣어도 돼."); return; }
                    String[] labels = new String[voices.size()];
                    for (int i=0;i<voices.size();i++) labels[i] = voices.get(i).toString();
                    new android.app.AlertDialog.Builder(MascotWidgetSettingsActivity.this)
                            .setTitle("어린 승재 목소리 고르기")
                            .setItems(labels, (d, which) -> {
                                TypecastClient.Voice voice = voices.get(which);
                                typeVoice.setText(voice.id);
                                typePrefs.edit().putString(AppPrefs.KEY_TYPECAST_VOICE_NAME, voice.name).apply();
                                typeEnabled.setChecked(true);
                                saveTypecast.run();
                                typeStatus.setText(voice.name + " 선택 완료 · 목소리 테스트를 눌러봐.");
                            })
                            .setNegativeButton("닫기", null).show();
                }
                @Override public void onError(String message) { typeStatus.setText(message); }
            });
        });

        advanced.setOnClickListener(v -> showTypecastAdvanced(typeSummary));

        typeTest.setOnClickListener(v -> {
            saveTypecast.run();
            if (!TtsManager.canUseTypecast(this)) { typeStatus.setText("Typecast 사용을 켜고 API Key와 Voice ID를 입력해줘."); return; }
            typeStatus.setText("어린 승재 목소리를 만들고 있어…");
            TtsManager.speak(this, "승재야, 오늘은 어땠어? 천천히 이야기해줘. 내가 옆에서 들어줄게.", new TtsManager.SpeakListener() {
                @Override public void onEngine(String engineName) { typeStatus.setText(engineName); }
                @Override public void onError(String message) { typeStatus.setText(message); }
            });
        });

'''
text = text.replace(anchor, section + anchor, 1)

# class helper methods for advanced settings and summary
pos = text.rfind('\n}')
if pos < 0:
    raise SystemExit('v10.18.18: class closing brace missing')
helpers = r'''
    private String typecastSummary() {
        android.content.SharedPreferences p = getSharedPreferences(AppPrefs.PREFS, MODE_PRIVATE);
        boolean smart = p.getBoolean(AppPrefs.KEY_TYPECAST_SMART_EMOTION, true);
        String preset = p.getString(AppPrefs.KEY_TYPECAST_EMOTION_PRESET, "normal");
        float intensity = p.getFloat(AppPrefs.KEY_TYPECAST_EMOTION_INTENSITY, 1.0f);
        float tempo = p.getFloat(AppPrefs.KEY_TYPECAST_TEMPO, 1.0f);
        int pitch = p.getInt(AppPrefs.KEY_TYPECAST_PITCH, 0);
        int volume = p.getInt(AppPrefs.KEY_TYPECAST_VOLUME, 100);
        String emo = smart ? "스마트 이모션" : preset + " " + String.format(java.util.Locale.KOREA, "%.1f", intensity);
        return "현재 적용: " + emo + " · " + String.format(java.util.Locale.KOREA, "%.2fx", tempo) + " · 피치 " + pitch + " · 음량 " + volume;
    }

    private void showTypecastAdvanced(final TextView summaryView) {
        final android.content.SharedPreferences p = getSharedPreferences(AppPrefs.PREFS, MODE_PRIVATE);
        LinearLayout box = new LinearLayout(this); box.setOrientation(LinearLayout.VERTICAL); box.setPadding(dp(18), dp(8), dp(18), dp(4));
        Switch smart = new Switch(this); smart.setText("✨ 스마트 이모션 자동 적용"); smart.setChecked(p.getBoolean(AppPrefs.KEY_TYPECAST_SMART_EMOTION, true)); box.addView(smart);
        TextView note = t("ssfm-v30 · WAV 원본 · 앱 강제증폭 없음", 12, false); note.setTextColor(Color.parseColor("#579C8B")); box.addView(note);

        TextView emoLabel = t("감정 프리셋", 14, true); LinearLayout.LayoutParams ep = new LinearLayout.LayoutParams(-1,-2); ep.setMargins(0,dp(8),0,0); box.addView(emoLabel,ep);
        final Spinner emo = new Spinner(this); final String[] labels={"기본","기쁨","슬픔","화남","속삭임","톤 업","톤 다운"}; final String[] vals={"normal","happy","sad","angry","whisper","toneup","tonedown"};
        emo.setAdapter(new ArrayAdapter<String>(this, android.R.layout.simple_spinner_dropdown_item, labels));
        String saved=p.getString(AppPrefs.KEY_TYPECAST_EMOTION_PRESET,"normal"); int sel=0; for(int i=0;i<vals.length;i++) if(vals[i].equals(saved)) sel=i; emo.setSelection(sel); box.addView(emo);

        TextView intensityLabel=t("감정 강도: "+String.format(java.util.Locale.KOREA,"%.1f",p.getFloat(AppPrefs.KEY_TYPECAST_EMOTION_INTENSITY,1f)),13,false); box.addView(intensityLabel);
        SeekBar intensity=new SeekBar(this); intensity.setMax(20); intensity.setProgress(Math.round(p.getFloat(AppPrefs.KEY_TYPECAST_EMOTION_INTENSITY,1f)*10)); box.addView(intensity);
        intensity.setOnSeekBarChangeListener(simpleSeek(v -> intensityLabel.setText("감정 강도: "+String.format(java.util.Locale.KOREA,"%.1f",v/10f))));

        TextView tempoLabel=t("속도: "+String.format(java.util.Locale.KOREA,"%.2fx",p.getFloat(AppPrefs.KEY_TYPECAST_TEMPO,1f)),13,false); box.addView(tempoLabel);
        SeekBar tempo=new SeekBar(this); tempo.setMin(50); tempo.setMax(200); tempo.setProgress(Math.round(p.getFloat(AppPrefs.KEY_TYPECAST_TEMPO,1f)*100)); box.addView(tempo);
        tempo.setOnSeekBarChangeListener(simpleSeek(v -> tempoLabel.setText("속도: "+String.format(java.util.Locale.KOREA,"%.2fx",v/100f))));

        TextView pitchLabel=t("피치: "+p.getInt(AppPrefs.KEY_TYPECAST_PITCH,0),13,false); box.addView(pitchLabel);
        SeekBar pitch=new SeekBar(this); pitch.setMin(-12); pitch.setMax(12); pitch.setProgress(p.getInt(AppPrefs.KEY_TYPECAST_PITCH,0)); box.addView(pitch);
        pitch.setOnSeekBarChangeListener(simpleSeek(v -> pitchLabel.setText("피치: "+v)));

        TextView volLabel=t("음량: "+p.getInt(AppPrefs.KEY_TYPECAST_VOLUME,100),13,false); box.addView(volLabel);
        SeekBar volume=new SeekBar(this); volume.setMax(200); volume.setProgress(p.getInt(AppPrefs.KEY_TYPECAST_VOLUME,100)); box.addView(volume);
        volume.setOnSeekBarChangeListener(simpleSeek(v -> volLabel.setText("음량: "+v)));

        Runnable enabled=()->{ boolean manual=!smart.isChecked(); emo.setEnabled(manual); intensity.setEnabled(manual); emo.setAlpha(manual?1f:.45f); intensity.setAlpha(manual?1f:.45f); };
        smart.setOnCheckedChangeListener((b,c)->enabled.run()); enabled.run();
        ScrollView sv=new ScrollView(this); sv.addView(box);
        new android.app.AlertDialog.Builder(this).setTitle("TYPECAST 세부 음성 설정").setView(sv)
                .setPositiveButton("저장", (d,w)->{
                    p.edit().putBoolean(AppPrefs.KEY_TYPECAST_SMART_EMOTION,smart.isChecked())
                            .putString(AppPrefs.KEY_TYPECAST_EMOTION_PRESET,vals[emo.getSelectedItemPosition()])
                            .putFloat(AppPrefs.KEY_TYPECAST_EMOTION_INTENSITY,intensity.getProgress()/10f)
                            .putFloat(AppPrefs.KEY_TYPECAST_TEMPO,tempo.getProgress()/100f)
                            .putInt(AppPrefs.KEY_TYPECAST_PITCH,pitch.getProgress())
                            .putInt(AppPrefs.KEY_TYPECAST_VOLUME,volume.getProgress()).apply();
                    summaryView.setText(typecastSummary());
                }).setNegativeButton("취소",null).show();
    }

    private interface IntConsumer { void accept(int v); }
    private SeekBar.OnSeekBarChangeListener simpleSeek(final IntConsumer c) {
        return new SeekBar.OnSeekBarChangeListener() {
            @Override public void onProgressChanged(SeekBar s,int p,boolean f){ c.accept(p); }
            @Override public void onStartTrackingTouch(SeekBar s){}
            @Override public void onStopTrackingTouch(SeekBar s){}
        };
    }
'''
text = text[:pos] + helpers + text[pos:]
settings.write_text(text, encoding='utf-8')

g = gradle.read_text(encoding='utf-8')
g = re.sub(r'versionCode\s+\d+', 'versionCode 101818', g, count=1)
g = re.sub(r'versionName\s+"[^"]+"', 'versionName "10.18.18"', g, count=1)
gradle.write_text(g, encoding='utf-8')
print('Applied v10.18.18 Typecast controls into mascot/widget settings')

from pathlib import Path
import re

root = Path('extracted')
analyzer = root / 'app/src/main/java/com/maeummon/app/CounselingProgramAnalyzer.java'
shared = root / 'app/src/main/java/com/maeummon/app/SharedCounselingLinkActivity.java'
gradle = root / 'app/build.gradle'

text = analyzer.read_text(encoding='utf-8')

pat = re.compile(
    r'String text = callResponses\(apiKey,\s*([^,]+),\s*system,\s*user,\s*(\d+)\);\s*'
    r'JSONObject root = new JSONObject\(extractJsonObject\(text\)\);'
)

def repl(m):
    model_expr = m.group(1).strip()
    limit = m.group(2)
    return (
        f'String text = callResponses(apiKey, {model_expr}, system, user, {limit});\n'
        f'        JSONObject root = parseJsonWithRecovery(apiKey, {model_expr}, system, user, text, {limit});'
    )

text, replaced = pat.subn(repl, text)
if replaced == 0:
    raise SystemExit('v10.18.9: no JSON parse call sites matched')

helper = r'''

    // v10.18.9: recover from syntactically truncated JSON without discarding saved counseling data.
    private static JSONObject parseJsonWithRecovery(String apiKey, String model, String originalSystem,
                                                     String originalUser, String firstText,
                                                     int originalMaxTokens) throws Exception {
        String candidate = firstText == null ? "" : firstText;
        Exception last = null;
        for (int attempt = 0; attempt < 3; attempt++) {
            try {
                return new JSONObject(extractJsonObject(candidate));
            } catch (Exception parseError) {
                last = parseError;
                if (attempt >= 2) break;

                String compactSystem = originalSystem
                        + " IMPORTANT RECOVERY MODE: the previous JSON response was cut off or invalid. "
                        + "Redo the SAME task from scratch and output exactly one COMPLETE valid JSON object. "
                        + "Keep every free-text field concise (prefer <=120 Korean characters), do not add markdown, "
                        + "do not omit required keys, and make sure every array/object/string is fully closed. ";
                String compactUser = originalUser
                        + "\n\n[RECOVERY NOTE]\nPrevious output could not be parsed because it was truncated. "
                        + "Return the same schema with shorter wording. Do not continue the broken text; regenerate a complete JSON object.";

                int retryLimit = Math.max(1400, Math.min(originalMaxTokens, 2200));
                Exception networkLast = null;
                for (int netTry = 0; netTry < 3; netTry++) {
                    try {
                        candidate = callResponses(apiKey, model, compactSystem, compactUser, retryLimit);
                        networkLast = null;
                        break;
                    } catch (Exception networkError) {
                        networkLast = networkError;
                        if (netTry < 2) {
                            try { Thread.sleep(netTry == 0 ? 1200L : 3000L); }
                            catch (InterruptedException ie) { Thread.currentThread().interrupt(); }
                        }
                    }
                }
                if (networkLast != null) throw networkLast;
            }
        }
        throw last == null ? new Exception("JSON recovery failed") : last;
    }
'''

pos = text.rfind('\n}')
if pos < 0:
    raise SystemExit('v10.18.9: analyzer class closing brace not found')
text = text[:pos] + helper + text[pos:]
analyzer.write_text(text, encoding='utf-8')

s = shared.read_text(encoding='utf-8')
s, n = re.subn(r'private static final int CROWN_POLICY_VERSION = \d+;',
                'private static final int CROWN_POLICY_VERSION = 16;', s, count=1)
if n != 1:
    raise SystemExit('v10.18.9: policy version anchor missing')
s = re.sub(r'"⚠️ 분석 중 문제가 생겼어: "\s*\+\s*[^;]+;',
           '"⚠️ 분석 응답이 중간에 끊겼어. 저장된 원문으로 자동 복구를 시도할게.";',
           s)
shared.write_text(s, encoding='utf-8')

g = gradle.read_text(encoding='utf-8')
g, n1 = re.subn(r'versionCode\s+\d+', 'versionCode 101809', g, count=1)
g, n2 = re.subn(r'versionName\s+"[^"]+"', 'versionName "10.18.9"', g, count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit('v10.18.9: gradle version anchor missing')
gradle.write_text(g, encoding='utf-8')

print(f'Applied v10.18.9 JSON truncation recovery to {replaced} parse call sites')

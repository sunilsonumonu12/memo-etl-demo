# MEMO Demo Project: Mini ETL Pipeline

Ye disposable Data Engineering project MEMO ko practically test karne ke liye hai. Ismein CSV orders ko clean karna, invalid rows ko quarantine karna aur revenue summary banana hai.

**Intentional starting bugs:** date formats limited hain, duplicate order IDs remove nahi hote, aur cancelled orders revenue mein aa jaate hain. Tests mein in failures ko dekhna hi demo ka pehla step hai.

## Requirements
- Python 3.10+ (standard library only)
- Node.js 20+ (MEMO CLI ke liye)
- Git
- Claude Code, agar automatic session capture test karna hai

## 1. Initial ETL test
PowerShell mein is folder ke andar:

```powershell
python -m unittest discover -s tests -v
```

Expected: kuch tests pass honge aur **3 deliberate behavior tests fail** honge. Ye real project defects nahi, training ke liye seeded bugs hain.

## 2. Git repo initialize karo

```powershell
git init
git add .
git commit -m "Create ETL demo baseline"
```

Agar Git name/email configured nahi hai to pehle local repo ke liye set karo:

```powershell
git config user.name "Demo User"
git config user.email "demo@example.invalid"
```

## 3. MEMO ko demo repo par initialize karo
Assumption: `memo-etl-demo` aur `whisper_flow_hackathon` same parent folder ke andar hain.

```powershell
$Memo = (Resolve-Path "..\whisper_flow_hackathon\bin\memo.js").Path
node $Memo init
node $Memo context
node $Memo tasks
```

Agar tumhare MEMO folder ka naam ya location alag hai, `$Memo` path badlo. `memo init` sirf is demo repo mein files add karta hai aur repo register karta hai.

## 4. Claude Code automatic capture
Ek baar hi, agar global hooks pehle install nahi kiye:

```powershell
node $Memo setup claude --dry-run
node $Memo setup claude
```

Second command `~/.claude/settings.json` change karta hai, isliye pehle dry-run output check karo. Ab Claude Code isi ETL folder ke andar launch karo.

## 5. Demo ko 3 coding sessions mein chalao
`PROMPTS_FOR_CLAUDE.md` se Session 1 ka prompt do. Fix aur tests verify karo. Claude Code band karo. Phir Session 2 start karo aur Session 2 prompt do. Aakhir mein Session 3 se cancelled-order behavior fix karao.

Har session ke baad PowerShell mein (isi demo folder se):

```powershell
node $Memo sessions
node $Memo status
```

Session data automatic capture hua ya nahi, yahan dekho. Automatic capture ka matlab hai raw session events save hue. Un events se structured tasks/decisions extract karne ke liye MEMO ko AI provider ke saath configure karna zaroori hai.

## 6. AI extraction ka dry-run

```powershell
node $Memo process --dry-run
```

Ye pending event batches aur estimated token usage dikhata hai; API call nahi honi chahiye. Agar `no API key` / provider configuration error aata hai, to live extraction abhi configured nahi hai.

### Optional: Groq live extraction
Purani ZIP mein key rakhne ke bajaye Groq Console se **nayi key** banao. API key ko repository file mein save mat karo. Phir same PowerShell window mein:

```powershell
$secure = Read-Host "Groq API key" -AsSecureString
$env:MEMO_API_KEY = [System.Net.NetworkCredential]::new("", $secure).Password
node $Memo config set provider openai
node $Memo config set baseUrl https://api.groq.com/openai/v1
node $Memo config set model openai/gpt-oss-20b
node $Memo config
node $Memo process --repo (Get-Location).Path
```

Live process provider ko captured conversation text bhej sakta hai aur quota use karega. Pehle `process --dry-run` output aur redaction rules inspect karo. Ye optional step hai, required startup step nahi.

## 7. Success criteria
1. Tests initially 3 seeded failures identify karein.
2. Session 1 date parsing fix kare; tests ka ek failure kam ho.
3. Session 2 duplicate IDs fix kare; next-session context mein prior decision/remaining work mil sake.
4. Session 3 cancelled orders revenue se exclude kare.
5. Final command `python -m unittest discover -s tests -v` sab pass kare.
6. `.memory/sessions/` mein session files aur, live extraction ke baad, `.memory/records/` mein evidence-linked records milein.

**Note:** MEMO ka purpose coding agent ko replace karna nahi hai. Ye sessions se context preserve karta hai, taaki baad ki sessions mein decisions, unresolved errors aur next tasks dobara explain na karne padein.

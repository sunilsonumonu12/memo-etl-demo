# Three-session test script

Do one prompt per separate Claude Code session. Do not paste all prompts into one session: the purpose is to test whether MEMO carries context between sessions.

## Session 1: normalize dates

> Inspect `pipeline.py` and the failing tests. Fix only date normalization so the pipeline accepts `YYYY-MM-DD`, `YYYY/MM/DD`, and `DD-MM-YYYY`. Add or preserve regression tests. Do not fix duplicate handling or cancelled-order filtering yet. Run the test suite and tell me exactly what remains broken. Do not mark anything verified unless the relevant test passes.

After the session ends, check `node $Memo sessions` and run `node $Memo process --dry-run`.

## Session 2: deduplicate orders

> Before editing, summarize the existing project decisions, what Session 1 changed, and which known defect remains. Use the project memory/context if available, and distinguish stored evidence from assumptions. Now fix duplicate `order_id` handling by keeping the first occurrence. Add a regression test. Do not change cancelled-order filtering yet. Run all tests and list the remaining failures.

After the session ends, check whether the new session was captured and whether MEMO extracted the session summary/task records. If it did not, inspect provider setup and the process logs rather than assuming memory worked.

## Session 3: cancelled orders

> Review project context and pending tasks before editing. Fix the rule that cancelled orders must not be included in clean orders or revenue totals. Add a regression test, run all tests, and update the project notes with the decision and verification evidence. Do not claim that other production concerns are verified.

## What to judge

MEMO is useful only if it actually captures each session, preserves important decisions and pending tasks, and presents them at the next session. A successful `memo init` or a generated report alone does not prove automatic AI extraction worked.

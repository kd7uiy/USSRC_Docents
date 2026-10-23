## Memory & Task Tracking
- **Task Management (`scratchpad.md`):** Read at task start, check off steps, log failures, wipe/archive when complete.
- **Long-Term Memory (`memory.md`):** Store architectural lessons, project quirks, and bug resolutions with timestamps.
- **Potential Issues (`issues.md`):** Log discovered out-of-scope issues here. When an issue is resolved, move its row to `temp/issues-archive.md` (same table, newest-first) rather than leaving it inline — keeps the live table focused on what still needs action.
- **Temporary (`temp/`):** Any prompts, scratchpad archives, and other temporary documents.

## Core Protocols

### 1. Test-Driven Verification Protocol
- **Write Tests First:** Always create or update an isolated regression test or diagnostic check to verify/reproduce a problem before writing code fixes.
- **Verify Fixes:** Confirm resolution with the diagnostic test suite to ensure zero regressions.

### 2. Model Tiering & Responsibilities
- **Opus (Architecture & Complex Diagnostics):** Design phase, system blueprints, and deep root-cause analysis.
  - *Constraint:* DO NOT edit multi-file codebases directly unless asked. Output a <15-line analysis, update `PLAN.md` or `scratchpad.md`, and output a self-contained handoff prompt.
- **Sonnet (Implementation & Main Driver):** Primary interactive session driver for writing core logic, feature development, and active refactoring.
- **Haiku (Sub-Agents & Utilities):** Non-interactive single-purpose tasks (e.g., generating unit tests, adding docstrings, formatting, running linter checks).

### 3. Sub-Agent Execution Protocol
To keep the primary session context lightweight, spawn background CLI sub-agents for secondary or isolated tasks rather than running them in the primary session window.

- **Non-Interactive Execution:** Always use the `-p` (or `--print`) flag so the subprocess runs, outputs, and exits immediately.
- **Scope Limitation:** Sub-agent tasks must be strictly scoped to single files or targeted outputs.

**Standard Sub-Agent Commands:**
- **Documentation & Docstrings:**
  `claude -p "Add full docstrings to changed functions in <file>" --model haiku`
- **Unit Test Generation:**
  `claude -p "Write unit tests for <file> covering edge cases. Save to tests/test_<file>" --model sonnet`
- **Linting & Formatting Fixes:**
  `claude -p "Fix standard formatting and linting issues in <file>" --model haiku`
- **Error Analysis:**
  `claude -p "Analyze this error log <log_text> and summarize the failure point in 3 bullet points" --model haiku`

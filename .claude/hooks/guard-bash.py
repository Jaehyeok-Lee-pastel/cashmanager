#!/usr/bin/env python3
"""
PreToolUse(Bash) SAFETY/SECURITY guard — the only BLOCKING hook (exit 2).

Hard-blocks two classes of command:
  A) destructive shell / SQL commands (mass, irreversible file or data loss)
  C) leaking local secrets (.env, *.pem, *.key, credentials) to external CLIs
     (codex / gemini) or pipes

Exit 2 blocks the tool call (Claude reads stderr); exit 0 allows.
Quality/style hooks stay advisory — only safety/security blocks here.
Temp-scoped operations (/tmp, system Temp) are allowed.
"""
import json
import re
import sys

# Operations clearly inside a temp area are allowed even if "destructive".
TEMP_HINTS = ["/tmp/", "\\temp\\", "/temp/", "appdata/local/temp",
              "tempfile", "$env:temp", "%temp%", "/claude/", "\\claude\\"]

# A) Destructive file ops (blocked unless temp-scoped)
DESTRUCTIVE = [
    (r"\brm\b[^\n]*?-\w*r\w*f", "rm recursive+force delete"),
    (r"\brm\b[^\n]*?-\w*f\w*r", "rm recursive+force delete"),
    (r"\brm\b[^\n]*?-r\b[^\n]*?-f\b", "rm -r -f"),
    (r"\bfind\b[^\n]*?-delete\b", "find -delete"),
    (r"\bfind\b[^\n]*?\|\s*xargs\s+rm\b", "find | xargs rm"),
    (r"\bdel\s+/s\b", "del /s (recursive delete)"),
    (r"\brmdir\s+/s\b", "rmdir /s (recursive delete)"),
    (r"\bRemove-Item\b[^\n]*?-Recurse\b", "Remove-Item -Recurse"),
    (r"\bchmod\s+-R\b", "chmod -R"),
    (r"\bchown\s+-R\b", "chown -R"),
    (r"\bmv\b[^\n|]*?\*", "wildcard mv (bulk move)"),
    (r"\bgit\b[^\n]*?\breset\s+--hard\b", "git reset --hard"),
    (r"\bgit\b[^\n]*?\bclean\s+-\w*f", "git clean -f"),
]

# A') Destructive SQL via sqlcmd/psql/mysql (always blocked — no WHERE = mass loss)
SQL_DESTRUCTIVE = [
    (r"\b(sqlcmd|psql|mysql)\b[^\n]*?\bDROP\s+(TABLE|DATABASE|INDEX|VIEW|SCHEMA|PROC|PROCEDURE)\b", "DROP via CLI"),
    (r"\b(sqlcmd|psql|mysql)\b[^\n]*?\bTRUNCATE\s+TABLE\b", "TRUNCATE TABLE via CLI"),
    (r"\b(sqlcmd|psql|mysql)\b(?![\s\S]*\bWHERE\b)[^\n]*?\bDELETE\s+FROM\b", "DELETE without WHERE via CLI"),
    (r"\b(sqlcmd|psql|mysql)\b(?![\s\S]*\bWHERE\b)[^\n]*?\bUPDATE\b\s+\w", "UPDATE without WHERE via CLI"),
]

# C) Secret leakage to external CLI / pipes.
# Only blocks when a codex/gemini command, or a cat/type pipe into one,
# references a local secret artifact. Normal `--include-directories .` research
# is NOT blocked (use .geminiignore / .codexignore to exclude secret files).
SECRET_ARTIFACT = r"(\.env\b|\.env\.\w+|\.pem\b|\.key\b|id_rsa|credentials|secrets?\b|api[_-]?key|password|token)"
SECRET_LEAK = [
    (rf"\b(codex|gemini)\b[\s\S]*?{SECRET_ARTIFACT}", "codex/gemini command references a secret artifact"),
    (rf"(cat|type|Get-Content)\b[\s\S]*?{SECRET_ARTIFACT}[\s\S]*?\|\s*(codex|gemini)\b", "secret file piped into external CLI"),
]


def is_temp_scoped(low: str) -> bool:
    return any(h in low for h in TEMP_HINTS)


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return
    if data.get("tool_name") != "Bash":
        return
    cmd = data.get("tool_input", {}).get("command", "")
    if not cmd:
        return
    low = cmd.lower()
    temp = is_temp_scoped(low)

    def deny(reason: str) -> None:
        print(
            f"[BLOCKED:safety-guard] {reason}.\n"
            "If truly needed: use Edit/Write for single files, and for bulk/risky "
            "operations confirm with the user, then run it directly. (temp paths are allowed)",
            file=sys.stderr,
        )
        sys.exit(2)  # exit 2 = block

    # A) destructive file ops (temp-scoped allowed)
    if not temp:
        for pat, label in DESTRUCTIVE:
            if re.search(pat, cmd, re.I):
                deny(f"destructive command blocked — {label}")

    # A') destructive SQL (always blocked)
    for pat, label in SQL_DESTRUCTIVE:
        if re.search(pat, cmd, re.I):
            deny(f"destructive SQL blocked — {label}")

    # C) secret leakage to external CLI / pipes
    for pat, label in SECRET_LEAK:
        if re.search(pat, cmd, re.I):
            deny(f"secret leak blocked — {label} (call codex/gemini without secrets)")

    sys.exit(0)  # allow


if __name__ == "__main__":
    main()

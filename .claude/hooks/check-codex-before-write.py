#!/usr/bin/env python3
"""
PreToolUse hook: Suggest Codex consultation before high-risk Write/Edit.

Advisory only (exit 0). Flags edits to security-sensitive areas (auth,
payment, admin) or edits containing dangerous content signals (string-concat
SQL, eval/exec, raw child process, hardcoded secrets) so Claude can consult
Codex first. Routine edits (docs, config, styles, .claude/) stay quiet.
"""

import json
import sys
from pathlib import Path

# Input validation constants
MAX_PATH_LENGTH = 4096
MAX_CONTENT_LENGTH = 1_000_000


def validate_input(file_path: str, content: str) -> bool:
    """Validate input for security."""
    if not file_path or len(file_path) > MAX_PATH_LENGTH:
        return False
    if len(content) > MAX_CONTENT_LENGTH:
        return False
    if ".." in file_path:
        return False
    return True


# High-risk AREAS by path — suggest review even for routine-looking files.
# Token-based (matches both dir/ and file.py forms) since SIMPLE_EDIT_PATTERNS
# already excludes docs/styles/.claude first.
HIGH_RISK_PATH = [
    "/auth",
    "auth.py",
    "deps.py",        # FastAPI auth dependency (get_current_user)
    "login",
    "security",
    "session",
    "payment",
    "billing",
    "checkout",
    "admin",
    "migration",      # supabase/migrations
]

# High-risk CONTENT signals — kept specific to avoid noise.
HIGH_RISK_CONTENT = [
    "' + request",      # string-concat SQL from user input
    '" + request',
    "' || ",            # SQL string concat
    "execute(",         # raw SQL / dynamic execution
    "exec(",
    "eval(",
    "child_process",    # raw shell spawn
    "os.system(",
    "subprocess.",
    "dangerouslysetinnerhtml",
    "innerhtml =",
    "secret =",
    "password =",
    "api_key =",
    "private_key",
    "service_role",        # Supabase service role key must stay backend-only
    "create_client(",      # raw Supabase client creation outside services/lib wrapper
]

# Routine edits — never suggest (docs, config, styles, claude/memory files)
SIMPLE_EDIT_PATTERNS = [
    ".gitignore",
    "readme.md",
    "changelog.md",
    ".jsonl",
    ".css",
    ".scss",
    ".md",
    ".claude/",
    "claude.md",
    "memory.md",
    "skill.md",
    "docs/",
]


def should_suggest_codex(file_path: str, content: str | None = None) -> tuple[bool, str]:
    """Suggest Codex review for high-risk changes (auth, payment, SQLi, secrets)."""
    filename = Path(file_path).name.lower()
    filepath_lower = file_path.replace("\\", "/").lower()
    content_lower = (content or "").lower()

    # Skip meta/doc/style files first — they DESCRIBE risk patterns without being live code.
    for pattern in SIMPLE_EDIT_PATTERNS:
        if pattern in filepath_lower or pattern in filename:
            return False, ""

    # High-risk AREA by path wins over routine-looking names.
    for area in HIGH_RISK_PATH:
        if area in filepath_lower:
            return True, f"high-risk area ('{area}') — auth/payment/admin change. Codex security review recommended"

    # High-risk content signals.
    for sig in HIGH_RISK_CONTENT:
        if sig in content_lower:
            return True, f"high-risk pattern ('{sig.strip()}') detected — SQLi/dynamic-exec/secret. Codex review recommended"

    return False, ""


def main():
    try:
        data = json.load(sys.stdin)
        tool_input = data.get("tool_input", {})
        file_path = tool_input.get("file_path", "")
        content = tool_input.get("content", "") or tool_input.get("new_string", "")

        if not validate_input(file_path, content):
            sys.exit(0)

        should_suggest, reason = should_suggest_codex(file_path, content)

        if should_suggest:
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "additionalContext": (
                        f"[Codex Consultation Reminder] {reason}. "
                        "Consider consulting Codex before making this change. "
                        "**Recommended**: Use Task tool with subagent_type='general-purpose' "
                        "to preserve main context. "
                        "(Direct call OK for quick questions: "
                        "`codex exec --sandbox read-only --skip-git-repo-check '...' < /dev/null`)"
                    )
                }
            }
            print(json.dumps(output))

        sys.exit(0)  # Always allow, just add context

    except Exception as e:
        print(f"Hook error: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()

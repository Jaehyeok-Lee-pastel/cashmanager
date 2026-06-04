#!/usr/bin/env python3
"""
PostToolUse hook: Suggest Codex review after significant implementations.

Tracks file changes per session and suggests a code review once a substantial
amount of code has been written (>=3 files or >=100 meaningful lines).

State is project-scoped (.claude/logs/implementation-state.json) so concurrent
sessions in other projects don't bleed counts into each other.
"""

import json
import os
import sys
from pathlib import Path

# Input validation constants
MAX_PATH_LENGTH = 4096
MAX_CONTENT_LENGTH = 1_000_000


def validate_input(file_path: str, content: str) -> bool:
    if not file_path or len(file_path) > MAX_PATH_LENGTH:
        return False
    if len(content) > MAX_CONTENT_LENGTH:
        return False
    if ".." in file_path:
        return False
    return True


def state_file() -> Path:
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
    log_dir = Path(project_dir) / ".claude" / "logs"
    return log_dir / "implementation-state.json"


# Thresholds for suggesting review
MIN_FILES_FOR_REVIEW = 3
MIN_LINES_FOR_REVIEW = 100

SOURCE_EXTS = (".py", ".ts", ".js", ".tsx", ".jsx", ".go", ".rs", ".java", ".rb", ".php", ".c", ".cpp", ".cs")


def load_state() -> dict:
    try:
        sf = state_file()
        if sf.exists():
            with open(sf) as f:
                return json.load(f)
    except Exception:
        pass
    return {"files_changed": [], "total_lines": 0, "review_suggested": False}


def save_state(state: dict) -> None:
    try:
        sf = state_file()
        sf.parent.mkdir(parents=True, exist_ok=True)
        with open(sf, "w") as f:
            json.dump(state, f)
    except Exception:
        pass


def count_lines(content: str) -> int:
    lines = content.split("\n")
    meaningful = [l for l in lines if l.strip() and not l.strip().startswith("#")]
    return len(meaningful)


def should_suggest_review(state: dict) -> tuple[bool, str]:
    if state.get("review_suggested"):
        return False, ""
    files_count = len(state.get("files_changed", []))
    total_lines = state.get("total_lines", 0)
    if files_count >= MIN_FILES_FOR_REVIEW:
        return True, f"{files_count} files modified"
    if total_lines >= MIN_LINES_FOR_REVIEW:
        return True, f"{total_lines}+ lines written"
    return False, ""


def main():
    try:
        data = json.load(sys.stdin)
        tool_name = data.get("tool_name", "")
        if tool_name not in ["Write", "Edit"]:
            sys.exit(0)

        tool_input = data.get("tool_input", {})
        file_path = tool_input.get("file_path", "")
        content = tool_input.get("content", "") or tool_input.get("new_string", "")

        if not validate_input(file_path, content):
            sys.exit(0)

        if not any(file_path.endswith(ext) for ext in SOURCE_EXTS):
            sys.exit(0)

        state = load_state()
        if file_path not in state["files_changed"]:
            state["files_changed"].append(file_path)
        state["total_lines"] += count_lines(content)
        save_state(state)

        should_review, reason = should_suggest_review(state)
        if should_review:
            state["review_suggested"] = True
            save_state(state)
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": (
                        f"[Code Review Suggestion] {reason} in this session. "
                        "Consider having Codex review the implementation. "
                        "**Recommended**: Use Task tool with subagent_type='general-purpose' "
                        "to consult Codex with the diff and preserve main context."
                    )
                }
            }
            print(json.dumps(output))

        sys.exit(0)

    except Exception as e:
        print(f"Hook error: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()

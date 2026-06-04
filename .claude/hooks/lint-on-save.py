#!/usr/bin/env python3
"""
PostToolUse hook (Edit|Write): lint saved files (advisory).

- Python files: run ruff format + ruff check --fix + ty check (if available via uv).

Extend handle_* dispatch in main() for other languages (e.g. prettier/eslint
for JS/TS) as the project grows.
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

MAX_PATH_LENGTH = 4096


def validate_path(file_path: str) -> bool:
    return bool(file_path) and len(file_path) <= MAX_PATH_LENGTH and ".." not in file_path


def ruff_cmd_prefix() -> list[str] | None:
    """Return how to invoke ruff (prefer uv, fall back to bare ruff), or None if unavailable."""
    if shutil.which("uv"):
        return ["uv", "run"]
    if shutil.which("ruff"):
        return []
    return None


def run_command(cmd: list[str], cwd: str) -> tuple[int, str, str]:
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=30)
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "timed out"
    except FileNotFoundError:
        return 1, "", f"not found: {cmd[0]}"


def handle_python(file_path: str, project_dir: str) -> None:
    prefix = ruff_cmd_prefix()
    if prefix is None:
        # No linter available — stay silent (advisory hook).
        return
    issues: list[str] = []
    for tail, label in (
        (["ruff", "format", file_path], "ruff format"),
        (["ruff", "check", "--fix", file_path], "ruff check"),
        (["ty", "check", file_path], "ty check"),
    ):
        cmd = prefix + tail
        ret, out, err = run_command(cmd, project_dir)
        if ret != 0 and (out or err).strip():
            issues.append(f"{label}:\n{out or err}")
    rel = os.path.relpath(file_path, project_dir)
    if issues:
        print(f"[lint-on-save] Issues in {rel}:", file=sys.stderr)
        for i in issues:
            print(i, file=sys.stderr)
    else:
        print(f"[lint-on-save] OK: {rel}")


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return
    tool_input = data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")
    if not validate_path(file_path):
        return

    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
    suffix = Path(file_path).suffix.lower()
    if suffix == ".py":
        handle_python(file_path, project_dir)


if __name__ == "__main__":
    main()

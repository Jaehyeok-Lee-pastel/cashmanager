#!/usr/bin/env python3
"""
UserPromptSubmit hook: Route to appropriate agent based on user intent.

Analyzes user prompts and suggests the most appropriate agent
(Codex for design/debug, Gemini for research/multimodal).
"""

import json
import sys

# Triggers for Codex — strong-signal only (broad words like review/analyze/error
# dropped to cut noise; those fire on nearly every prompt). 2026-05-27 narrowed.
CODEX_TRIGGERS = {
    "ko": [
        "어떻게 설계", "아키텍처", "디버깅", "트레이드오프",
        "어떻게 구현", "리팩토링", "코드 리뷰",
    ],
    "en": [
        "architecture", "architect", "refactor",
        "trade-off", "tradeoff", "how to implement",
    ],
}

# Triggers for Gemini — research / multimodal strong-signal only.
GEMINI_TRIGGERS = {
    "ko": [
        "리서치해", "조사해",
        "코드베이스 전체", "리포지토리 전체", "최신 문서",
        "PDF", "동영상", "오디오", "이미지",
    ],
    "en": [
        "research", "investigate",
        "entire codebase", "whole repository",
        "pdf", "video", "audio", "image",
    ],
}


def detect_agent(prompt: str) -> tuple[str | None, str]:
    """Detect which agent should handle this prompt."""
    prompt_lower = prompt.lower()

    # Check Codex triggers
    for triggers in CODEX_TRIGGERS.values():
        for trigger in triggers:
            if trigger in prompt_lower:
                return "codex", trigger

    # Check Gemini triggers
    for triggers in GEMINI_TRIGGERS.values():
        for trigger in triggers:
            if trigger in prompt_lower:
                return "gemini", trigger

    return None, ""


def main():
    try:
        data = json.load(sys.stdin)
        prompt = data.get("prompt", "")

        # Skip short prompts
        if len(prompt) < 10:
            sys.exit(0)

        agent, trigger = detect_agent(prompt)

        if agent == "codex":
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": (
                        f"[Agent Routing] Detected '{trigger}' - this task may benefit from "
                        "Codex CLI's deep reasoning capabilities. Consider: "
                        "`codex exec --sandbox read-only "
                        '"{task description}"` for design decisions, debugging, or complex analysis.'
                    )
                }
            }
            print(json.dumps(output))

        elif agent == "gemini":
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": (
                        f"[Agent Routing] Detected '{trigger}' - this task may benefit from "
                        "Gemini CLI's research capabilities. Consider: "
                        '`gemini -m gemini-3-flash-preview -p "Research: {topic}" 2>/dev/null` '
                        "for documentation, library research, or multimodal content."
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

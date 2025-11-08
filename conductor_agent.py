#!/usr/bin/env python3
"""
The Conductor Agent
Makes intelligent decisions about which Band members should perform
"""

import json
import subprocess
import os
import sys
from pathlib import Path
from typing import Dict


def run_conductor(user_prompt: str, project_stats: Dict) -> Dict:
    """
    Run the Conductor agent to decide which band members should perform

    Args:
        user_prompt: The user's prompt
        project_stats: Dict with file_count, changed_files, last_run

    Returns:
        Dict with should_run, reason, agents, timeout, priority
    """

    # Load conductor prompt template
    prompt_file = Path(__file__).parent / "prompts" / "conductor.md"

    if not prompt_file.exists():
        # Fallback: run all agents
        return {
            "should_run": True,
            "reason": "conductor prompt not found, running all agents",
            "agents": ["paul", "ringo"],
            "timeout": 120,
            "priority": "medium"
        }

    # Calculate adaptive timeout based on changed files
    changed_files = project_stats.get('changed_files', 0)
    if changed_files > 100:
        suggested_timeout = 300  # 5 min for massive changes
    elif changed_files > 50:
        suggested_timeout = 240  # 4 min for many changes
    elif changed_files > 20:
        suggested_timeout = 180  # 3 min for moderate changes
    else:
        suggested_timeout = 120  # 2 min default

    # Build conductor prompt (use replace instead of format to avoid JSON brace issues)
    template = prompt_file.read_text()
    prompt = template.replace("{user_prompt}", user_prompt)
    prompt = prompt.replace("{file_count}", str(project_stats.get('file_count', 0)))
    prompt = prompt.replace("{changed_files}", str(changed_files))
    prompt = prompt.replace("{last_run}", str(project_stats.get('last_run', 'never')))

    # Add suggested timeout hint for Conductor
    prompt += f"\n\n**Suggested timeout based on {changed_files} changed files: {suggested_timeout}s**"

    # Run Conductor agent (fast Haiku model for quick decisions)
    env = os.environ.copy()
    env['CIATC_SUBPROCESS'] = 'true'  # Prevent recursion
    env['PATH'] = '/usr/local/bin:' + env.get('PATH', '')

    cmd = [
        '/usr/local/bin/claude',
        '--dangerously-skip-permissions',
        '--model', 'haiku',  # Fast model for quick decisions
        '--print'
    ]

    try:
        result = subprocess.run(
            cmd,
            input=prompt,  # Pass prompt via stdin instead of command line
            capture_output=True,
            text=True,
            timeout=10,  # Quick decision, 10s max
            env=env
        )

        if result.returncode != 0:
            error_msg = f"Conductor failed (exit {result.returncode}): {result.stderr[:500]}"
            print(error_msg, file=sys.stderr)
            raise Exception(error_msg)

        # Parse JSON response
        response = result.stdout.strip()

        # Debug: show what we got
        if not response:
            error_msg = f"Conductor returned empty response. stderr: {result.stderr[:500]}"
            print(error_msg, file=sys.stderr)
            raise Exception(error_msg)

        # Remove markdown code blocks if present
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            response = response.split("```")[1].split("```")[0].strip()

        decision = json.loads(response)

        # Validate decision structure
        required_keys = ["should_run", "reason", "agents", "timeout", "priority"]
        for key in required_keys:
            if key not in decision:
                raise ValueError(f"Missing key: {key}")

        return decision

    except subprocess.TimeoutExpired:
        # Conductor timed out, skip hooks
        return {
            "should_run": False,
            "reason": "conductor timeout - skipping for performance",
            "agents": [],
            "timeout": 0,
            "priority": "low"
        }

    except Exception as e:
        # Conductor error, use conservative fallback
        print(f"Conductor error: {e}", file=sys.stderr)
        return {
            "should_run": True,
            "reason": f"conductor error, running minimal set: {str(e)[:50]}",
            "agents": ["ringo"],  # Just Ringo as fallback
            "timeout": 30,
            "priority": "medium"
        }


def test_conductor():
    """Test the conductor with sample prompts"""

    test_prompts = [
        "What is React?",
        "Implement user authentication with JWT tokens",
        "Explain the pagination logic we discussed earlier",
        "Refactor the database layer for better performance",
        "How do I install Python?"
    ]

    project_stats = {
        "file_count": 250,
        "changed_files": 5,
        "last_run": "2 minutes ago"
    }

    print("=" * 70)
    print("CONDUCTOR AGENT TEST")
    print("=" * 70)

    for prompt in test_prompts:
        print(f"\nPrompt: {prompt}")
        print("-" * 70)

        decision = run_conductor(prompt, project_stats)

        print(f"Should Run: {decision['should_run']}")
        print(f"Reason: {decision['reason']}")
        print(f"Agents: {', '.join(decision['agents']) if decision['agents'] else 'none'}")
        print(f"Timeout: {decision['timeout']}s")
        print(f"Priority: {decision['priority']}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    import sys
    test_conductor()

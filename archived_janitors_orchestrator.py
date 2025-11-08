#!/usr/bin/env python3
"""
PHILOSOPHICAL JANITORS ORCHESTRATOR
Post-response critics using real Claude instances
Uses sonnet[1m] model alias
Reviews Opus's response for quality issues
"""

import json
import sys
import subprocess
import os
from pathlib import Path

def run_claude(prompt, model="sonnet[1m]", timeout_seconds=60):
    """Run claude with given prompt"""

    # RECURSION GUARD: Disable hooks for subprocess calls
    env = os.environ.copy()
    env['CIATC_SUBPROCESS'] = 'true'  # Mark as subprocess call
    env['PATH'] = '/usr/local/bin:' + env.get('PATH', '')  # Ensure node is found

    cmd = [
        '/usr/local/bin/claude',  # Use full path like bootstrap
        '--dangerously-skip-permissions',
        '--model', model,
        '--print',  # Use --print like bootstrap (not -p)
        prompt
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,  # Configurable timeout
            env=env  # Pass environment with recursion guard
        )

        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"[Error: {result.stderr[:100]}]"
    except Exception as e:
        return f"[Failed: {str(e)}]"


def run_marie(opus_response):
    """Marie: Cleanup inspector"""

    prompt_file = Path("/Users/philhudson/Projects/CiaTc/prompts/marie.md")

    if prompt_file.exists():
        with open(prompt_file, 'r') as f:
            prompt = f.read()
            # Limit response size for analysis
            truncated = opus_response[:3000] if len(opus_response) > 3000 else opus_response
            prompt = prompt.replace("{opus_response}", truncated)
    else:
        prompt = f"Review for cleanup: {opus_response[:500]}"

    return run_claude(prompt, timeout_seconds=30)  # 30 seconds for Marie


def run_descartes(opus_response):
    """Descartes: Assumption validator"""

    prompt_file = Path("/Users/philhudson/Projects/CiaTc/prompts/descartes.md")

    if prompt_file.exists():
        with open(prompt_file, 'r') as f:
            prompt = f.read()
            truncated = opus_response[:3000] if len(opus_response) > 3000 else opus_response
            prompt = prompt.replace("{opus_response}", truncated)
    else:
        prompt = f"Check assumptions in: {opus_response[:500]}"

    return run_claude(prompt, timeout_seconds=30)  # 30 seconds for Descartes


def run_feynman(opus_response):
    """Feynman: Simplicity advocate"""

    prompt_file = Path("/Users/philhudson/Projects/CiaTc/prompts/feynman.md")

    if prompt_file.exists():
        with open(prompt_file, 'r') as f:
            prompt = f.read()
            truncated = opus_response[:3000] if len(opus_response) > 3000 else opus_response
            prompt = prompt.replace("{opus_response}", truncated)
    else:
        prompt = f"Simplify this: {opus_response[:500]}"

    return run_claude(prompt, timeout_seconds=30)  # 30 seconds for Feynman


def main():
    """Hook entry point for post-response review"""

    # RECURSION GUARD: Skip if this is a subprocess call
    if os.environ.get('CIATC_SUBPROCESS') == 'true':
        # Just pass through without processing
        print(sys.stdin.read(), end='')
        return

    event_json = sys.stdin.read()

    try:
        event = json.loads(event_json)

        # This runs on Stop hook (after Claude finishes responding)
        if event.get('hook_event_name') == 'Stop':
            # Get the transcript path to read the actual response
            transcript_path = event.get('transcript_path', '')

            if not transcript_path:
                print("No transcript path available", file=sys.stderr)
                return

            # Read the last response from the transcript
            response = ''
            try:
                with open(transcript_path, 'r') as f:
                    lines = f.readlines()
                    # Get the last assistant message - transcript has nested structure
                    for line in reversed(lines):
                        try:
                            entry = json.loads(line)
                            message = entry.get('message', {})
                            if message.get('role') == 'assistant' and message.get('content'):
                                # Extract text from content array
                                for content_item in message.get('content', []):
                                    if content_item.get('type') == 'text':
                                        response = content_item.get('text', '')
                                        break
                                if response:
                                    break
                        except json.JSONDecodeError:
                            continue  # Skip malformed lines
            except Exception as e:
                print(f"Error reading transcript: {e}", file=sys.stderr)
                response = ''

            print(f"Response length from transcript: {len(response)}", file=sys.stderr)

            # Run on ALL responses longer than 100 chars (skip trivial "ok" responses)
            # (Why would we NOT want philosophical critique?)
            if len(response) > 100:
                print("🧹 Running Philosophical Janitors...", file=sys.stderr)

                janitor_report = "\n<philosophical-janitors>\n\n"

                # Run each janitor
                print("  Marie (Cleanup)...", file=sys.stderr)
                marie_result = run_marie(response)
                janitor_report += f"**Marie Kondo (Cleanup):**\n{marie_result}\n\n"

                print("  Descartes (Assumptions)...", file=sys.stderr)
                descartes_result = run_descartes(response)
                janitor_report += f"**Descartes (Assumptions):**\n{descartes_result}\n\n"

                print("  Feynman (Simplicity)...", file=sys.stderr)
                feynman_result = run_feynman(response)
                janitor_report += f"**Feynman (Simplicity):**\n{feynman_result}\n\n"

                janitor_report += "</philosophical-janitors>\n"

                # Write to file for next interaction to read
                critique_file = Path("/tmp/janitor_critique.md")
                with open(critique_file, 'w') as f:
                    f.write(janitor_report)

                print(f"💭 Janitors saved critique to {critique_file}", file=sys.stderr)

    except Exception as e:
        print(f"Janitor error: {e}", file=sys.stderr)

    # Pass through
    print(json.dumps(event) if isinstance(event, dict) else event_json, end='')


if __name__ == "__main__":
    main()
    sys.exit(0)  # Ensure clean exit
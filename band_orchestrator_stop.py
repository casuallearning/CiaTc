#!/usr/bin/env python3
"""
Runs documentation agents in background after Claude responds
John, George, Pete, Build Health update docs for next message

NOW WITH CONDUCTOR ORCHESTRATION:
- Conductor decides which agents to run based on conversation context
- Adaptive timeouts
- Smarter resource management
"""

import json
import sys
import subprocess
from pathlib import Path
import os
import time
from functools import wraps
from concurrent.futures import ThreadPoolExecutor, as_completed
from smart_orchestrator import SmartOrchestrator
from agent_lock import agent_lock, cleanup_stale_locks

def timed(func):
    """Decorator to time function execution"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"⏱️  {func.__name__}: {elapsed:.2f}s", file=sys.stderr)
        return result
    return wrapper

def run_claude(prompt, model="haiku", timeout_seconds=600, working_dir=None):
    """Run claude with given prompt in specified directory"""

    # RECURSION GUARD: Disable hooks for subprocess calls
    env = os.environ.copy()
    env['CIATC_SUBPROCESS'] = 'true'  # Mark as subprocess call
    env['PATH'] = '/usr/local/bin:' + env.get('PATH', '')  # Ensure node is found

    cmd = [
        '/usr/local/bin/claude',
        '--dangerously-skip-permissions',
        '--model', model,
        '--print',
        prompt
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            env=env,
            cwd=working_dir
        )

        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"[Error: {result.stderr[:100]}]"
    except Exception as e:
        return f"[Failed: {str(e)}]"


@timed
def run_john(cwd, transcript_path, timeout):
    """John: Directory mapper and file indexer"""

    prompt_file = Path("/Users/philhudson/Projects/CiaTc/prompts/john.md")

    if prompt_file.exists():
        with open(prompt_file, 'r') as f:
            prompt = f.read()
    else:
        prompt = """Please review the current file directory map and file index for this project.
If they do not exist, create them in the documents directory.
Index should contain: file name, category tag, and description grouped by directory.
Directory map should accurately map all files in the current project.
If they exist, update them based on current structure."""

    return run_claude(prompt, timeout_seconds=timeout, working_dir=cwd)


@timed
def run_george(user_prompt, transcript_path, cwd, timeout):
    """George: Narrative manager"""

    prompt_file = Path("/Users/philhudson/Projects/CiaTc/prompts/george.md")

    # Get last few transcript lines for context
    context = ""
    if transcript_path and Path(transcript_path).exists():
        try:
            with open(transcript_path, 'r') as f:
                lines = f.readlines()
                recent = lines[-10:] if len(lines) > 10 else lines
                context = "".join(recent)[:2000]
        except:
            context = "[Could not read transcript]"

    if prompt_file.exists():
        with open(prompt_file, 'r') as f:
            prompt = f.read()
            prompt = prompt.replace("{user_prompt}", user_prompt)
            prompt = prompt.replace("{transcript_summary}", context)
    else:
        prompt = f"Track narrative themes in this conversation. User says: {user_prompt}"

    return run_claude(prompt, timeout_seconds=timeout, working_dir=cwd)


@timed
def run_pete(user_prompt, cwd, timeout):
    """Pete: Technical documentation"""

    prompt_file = Path("/Users/philhudson/Projects/CiaTc/prompts/pete.md")

    # Extract code if present
    code = ""
    if "```" in user_prompt:
        blocks = user_prompt.split("```")
        code = blocks[1] if len(blocks) > 1 else ""

    if prompt_file.exists():
        with open(prompt_file, 'r') as f:
            prompt = f.read()
            prompt = prompt.replace("{user_prompt}", user_prompt)
            prompt = prompt.replace("{recent_code}", code or "[No code]")
    else:
        prompt = f"Extract technical details from: {user_prompt}"

    return run_claude(prompt, timeout_seconds=timeout, working_dir=cwd)


@timed
def run_gilfoyle(cwd):
    """Gilfoyle: Build health and dependency monitoring (the cynical systems architect)"""

    try:
        result = subprocess.run(
            ['python3', '/Users/philhudson/Projects/CiaTc/gilfoyle_agent.py', cwd],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"[Error: {result.stderr[:200]}]"
    except Exception as e:
        return f"[Failed: {str(e)}]"


@timed
def run_marie(cwd, timeout):
    """Marie: Active project maintenance (tidying, git operations, cleanup)"""
    prompt_file = Path("/Users/philhudson/Projects/CiaTc/prompts/marie_active.md")

    if prompt_file.exists():
        with open(prompt_file, 'r') as f:
            prompt = f.read()
            prompt = prompt.replace("{cwd}", cwd)
    else:
        prompt = "Tidy the project: check for uncommitted docs, clean temp files, organize structure."

    return run_claude(prompt, timeout_seconds=timeout, working_dir=cwd)


# Locked wrapper functions
def run_john_locked(cwd, transcript_path, timeout):
    """John with locking to prevent duplicates"""
    with agent_lock("john", skip_if_locked=True) as lock:
        if lock:
            return run_john(cwd, transcript_path, timeout)
        else:
            return None  # Already running


def run_george_locked(user_prompt, transcript_path, cwd, timeout):
    """George with locking to prevent duplicates"""
    with agent_lock("george", skip_if_locked=True) as lock:
        if lock:
            return run_george(user_prompt, transcript_path, cwd, timeout)
        else:
            return None  # Already running


def run_pete_locked(user_prompt, cwd, timeout):
    """Pete with locking to prevent duplicates"""
    with agent_lock("pete", skip_if_locked=True) as lock:
        if lock:
            return run_pete(user_prompt, cwd, timeout)
        else:
            return None  # Already running


def run_gilfoyle_locked(cwd):
    """Gilfoyle with locking to prevent duplicates"""
    with agent_lock("gilfoyle", skip_if_locked=True) as lock:
        if lock:
            return run_gilfoyle(cwd)
        else:
            return None  # Already running


def run_marie_locked(cwd, timeout):
    """Marie with locking to prevent duplicates"""
    with agent_lock("marie", skip_if_locked=True) as lock:
        if lock:
            return run_marie(cwd, timeout)
        else:
            return None  # Already running


def main():
    """Stop hook entry point - runs after Claude responds"""

    # RECURSION GUARD: Skip if this is a subprocess call
    if os.environ.get('CIATC_SUBPROCESS') == 'true':
        print(sys.stdin.read(), end='')
        return

    event_json = sys.stdin.read()

    try:
        event = json.loads(event_json)

        if event.get('hook_event_name') == 'Stop':
            user_prompt = event.get('prompt', '')
            cwd = event.get('cwd', os.getcwd())
            transcript_path = event.get('transcript_path')

            # BACKGROUND DOCUMENTATION MAINTENANCE
            # These agents always try to run (locks prevent duplicates)
            # No Conductor needed - they're maintenance workers, not performers

            orchestrator = SmartOrchestrator(cwd)

            # All background documentation and maintenance agents
            agents_to_run = ["john", "george", "pete", "marie"]
            timeout = 600  # 10 minutes - non-blocking, let them finish thoroughly

            # Clean up any stale locks first
            cleanup_stale_locks(max_age_seconds=600)

            print(f"📚 Background documentation maintenance", file=sys.stderr)
            print(f"   Agents: {', '.join(agents_to_run)} | Timeout: {timeout}s", file=sys.stderr)

            # Run selected agents in background with locking
            futures = {}

            # Check which agents are already running
            skipped = []
            for agent in agents_to_run + ['gilfoyle']:
                from agent_lock import AgentLock
                if AgentLock(agent).is_locked():
                    skipped.append(agent)
                    print(f"  ⏭️  {agent.capitalize()} already running, skipping", file=sys.stderr)

            if skipped:
                agents_to_run = [a for a in agents_to_run if a not in skipped]

            with ThreadPoolExecutor(max_workers=len(agents_to_run) + 1) as executor:
                # Always run Gilfoyle (build health) unless already running
                if 'gilfoyle' not in skipped:
                    futures['gilfoyle'] = executor.submit(run_gilfoyle_locked, cwd)

                # Run background documentation agents (with locks)
                if "john" in agents_to_run:
                    futures['john'] = executor.submit(run_john_locked, cwd, transcript_path, timeout)
                if "george" in agents_to_run:
                    futures['george'] = executor.submit(run_george_locked, user_prompt, transcript_path, cwd, timeout)
                if "pete" in agents_to_run:
                    futures['pete'] = executor.submit(run_pete_locked, user_prompt, cwd, timeout)
                if "marie" in agents_to_run:
                    futures['marie'] = executor.submit(run_marie_locked, cwd, timeout)

                # Wait for completion
                for agent_name, future in futures.items():
                    try:
                        result = future.result(timeout=timeout + 5)
                        if result is not None:
                            print(f"  ✓ {agent_name.capitalize()} completed", file=sys.stderr)
                        else:
                            print(f"  ⏭️  {agent_name.capitalize()} was locked", file=sys.stderr)
                    except Exception as e:
                        print(f"  ERROR: {agent_name.capitalize()} failed - {e}", file=sys.stderr)

            print("📚 Documentation updates complete", file=sys.stderr)

            # Update cache
            orchestrator.cache["last_run"] = time.time()
            orchestrator._save_cache()
            orchestrator._save_file_hashes()

    except Exception as e:
        print(f"Stop hook error: {e}", file=sys.stderr)
        import traceback
        print(f"Traceback: {traceback.format_exc()}", file=sys.stderr)

    # Pass through the event unchanged (Stop hook doesn't modify prompt)
    try:
        print(json.dumps(event) if isinstance(event, dict) else event_json, end='')
    except:
        print(event_json, end='')


if __name__ == "__main__":
    main()
    sys.exit(0)

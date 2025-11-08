#!/usr/bin/env python3
"""
BAND ORCHESTRATOR - USER PROMPT SUBMIT HOOK
Runs Paul & Ringo for immediate context synthesis
John, George, Pete run in background on Stop hook

NOW WITH SMART ADAPTIVE ORCHESTRATION:
- Skips hooks for simple questions
- Adaptive timeouts based on project size
- Selective agent execution
- Incremental processing
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
from conductor_agent import run_conductor
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

def run_claude(prompt, model="sonnet", timeout_seconds=600, working_dir=None):
    """Run claude with given prompt in specified directory"""

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
            env=env,  # Pass environment with recursion guard
            cwd=working_dir  # Run in specified directory
        )

        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"[Error: {result.stderr[:100]}]"
    except Exception as e:
        return f"[Failed: {str(e)}]"


@timed
def run_john(cwd, timeout):
    """John: Directory mapper and file indexer"""
    prompt_file = Path(__file__).parent / "prompts" / "john.md"

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
def run_george(user_prompt, cwd, timeout):
    """George: Narrative manager"""
    prompt_file = Path(__file__).parent / "prompts" / "george.md"

    if prompt_file.exists():
        with open(prompt_file, 'r') as f:
            prompt = f.read()
            prompt = prompt.replace("{user_prompt}", user_prompt)
            prompt = prompt.replace("{transcript_summary}", "[Recent context]")
    else:
        prompt = f"Track narrative themes in this conversation. User says: {user_prompt}"

    return run_claude(prompt, timeout_seconds=timeout, working_dir=cwd)


@timed
def run_pete(user_prompt, cwd, timeout):
    """Pete: Technical documentation"""
    prompt_file = Path(__file__).parent / "prompts" / "pete.md"

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
def run_paul(user_prompt, timeout):
    """Paul: Wild ideas - INDEPENDENT"""
    prompt_file = Path(__file__).parent / "prompts" / "paul.md"

    if prompt_file.exists():
        with open(prompt_file, 'r') as f:
            prompt = f.read()
            prompt = prompt.replace("{user_prompt}", user_prompt)
    else:
        prompt = f"Give one wild but potentially brilliant idea for: {user_prompt}"

    return run_claude(prompt, model="opus", timeout_seconds=timeout)


@timed
def run_ringo(cwd, user_prompt, timeout):
    """Ringo: Context synthesizer - RUNS LAST, DEPENDS ON JOHN & GEORGE"""
    prompt_file = Path(__file__).parent / "prompts" / "ringo.md"

    project_name = Path(cwd).name

    if prompt_file.exists():
        with open(prompt_file, 'r') as f:
            prompt = f.read()
            prompt = prompt.replace("{user_prompt}", user_prompt)
            prompt = prompt.replace("{project_name}", project_name)
            prompt = prompt.replace("{cwd}", cwd)
    else:
        prompt = f"Synthesize context for project {project_name}: {user_prompt}"

    return run_claude(prompt, timeout_seconds=timeout, working_dir=cwd)


def main():
    """Hook entry point"""

    # RECURSION GUARD: Skip if this is a subprocess call
    if os.environ.get('CIATC_SUBPROCESS') == 'true':
        # Just pass through without processing
        print(sys.stdin.read(), end='')
        return

    event_json = sys.stdin.read()
    band_report = ""  # Initialize at the top level

    try:
        event = json.loads(event_json)

        if event.get('hook_event_name') == 'UserPromptSubmit':
            user_prompt = event.get('prompt', '')
            cwd = event.get('cwd', os.getcwd())

            # CONDUCTOR ORCHESTRATION: Let an agent decide what to run
            orchestrator = SmartOrchestrator(cwd)

            # Get project stats for Conductor
            file_count, _ = orchestrator.get_project_size()
            changed_files = orchestrator.get_changed_files()
            last_run = orchestrator.cache.get("last_run", "never")
            if last_run != "never":
                minutes_ago = int((time.time() - last_run) / 60)
                last_run = f"{minutes_ago} minutes ago" if minutes_ago > 0 else "just now"

            project_stats = {
                "file_count": file_count,
                "changed_files": len(changed_files),
                "last_run": last_run
            }

            # Ask the Conductor which agents to run
            print("🎼 Consulting Conductor...", file=sys.stderr)
            decision = run_conductor(user_prompt, project_stats)

            # Skip if Conductor says not to run
            if not decision['should_run']:
                print(f"⚡ Conductor decision: {decision['reason']}", file=sys.stderr)
            else:
                agents_to_run = decision['agents']
                timeout = decision['timeout']
                priority = decision['priority']

                # FILTER: UserPromptSubmit only runs immediate-response agents
                # John, George, Pete, Marie run on Stop hook only
                ALLOWED_AGENTS = ['paul', 'ringo']
                filtered = [a for a in agents_to_run if a in ALLOWED_AGENTS]

                if filtered != agents_to_run:
                    removed = [a for a in agents_to_run if a not in ALLOWED_AGENTS]
                    print(f"   🚫 Filtered out stop agents: {', '.join(removed)} (run on Stop hook)", file=sys.stderr)
                    agents_to_run = filtered

                # Check if any agents are already running (from previous Stop hook)
                from agent_lock import AgentLock
                running = []
                for agent in agents_to_run:
                    if AgentLock(agent).is_locked():
                        running.append(agent)

                if running:
                    print(f"   ⚠️  Agents already running from Stop hook: {', '.join(running)}", file=sys.stderr)
                    print(f"   💡 Waiting for them to complete or skipping...", file=sys.stderr)

                print(f"🎸 Conductor decision: {decision['reason']}", file=sys.stderr)
                print(f"   Agents: {', '.join(agents_to_run)} | Timeout: {timeout}s | Priority: {priority}", file=sys.stderr)
                if project_stats['changed_files'] > 0:
                    print(f"   📝 {project_stats['changed_files']} files changed since last run", file=sys.stderr)

                band_report += "<the-band>\n\n"
                band_report += f"*Conductor: {decision['reason']}*\n"
                if running:
                    band_report += f"*Note: {', '.join(running)} already running from previous turn*\n"
                band_report += f"*Running: {', '.join(agents_to_run)}*\n\n"

                # Prepare futures
                futures = {}
                results = {}

                with ThreadPoolExecutor(max_workers=len(agents_to_run)) as executor:
                    # Submit tasks for selected agents (Conductor chooses which)
                    if "john" in agents_to_run:
                        futures['john'] = executor.submit(run_john, cwd, timeout)
                    if "george" in agents_to_run:
                        futures['george'] = executor.submit(run_george, user_prompt, cwd, timeout)
                    if "pete" in agents_to_run:
                        futures['pete'] = executor.submit(run_pete, user_prompt, cwd, timeout)
                    if "paul" in agents_to_run:
                        futures['paul'] = executor.submit(run_paul, user_prompt, timeout)
                    if "ringo" in agents_to_run:
                        futures['ringo'] = executor.submit(run_ringo, cwd, user_prompt, timeout)

                    # Collect results as they complete
                    for agent_name, future in futures.items():
                        try:
                            results[agent_name] = future.result(timeout=timeout + 5)  # Give 5s buffer
                            print(f"  ✓ {agent_name.capitalize()} completed", file=sys.stderr)
                        except Exception as e:
                            print(f"  ERROR: {agent_name.capitalize()} failed - {e}", file=sys.stderr)
                            results[agent_name] = f"[Error: {str(e)}]"

                # Add results to band report in consistent order
                if "john" in results and results["john"]:
                    band_report += f"**John (Structure):**\n{results['john']}\n\n"

                if "george" in results and results["george"]:
                    band_report += f"**George (Narrative):**\n{results['george']}\n\n"

                if "pete" in results and results["pete"]:
                    band_report += f"**Pete (Technical):**\n{results['pete']}\n\n"

                if "paul" in results and results["paul"]:
                    band_report += f"**Paul (Wild Idea):**\n{results['paul']}\n\n"

                if "ringo" in results and results["ringo"]:
                    band_report += f"**Ringo (Synthesis):**\n{results['ringo']}\n\n"

                band_report += "</the-band>\n\n"

    except Exception as e:
        print(f"Band error: {e}", file=sys.stderr)
        import traceback
        print(f"Traceback: {traceback.format_exc()}", file=sys.stderr)

    # Output the original JSON first (exactly like discipline does)
    try:
        print(json.dumps(event) if isinstance(event, dict) else event_json, end='')
    except:
        print(event_json, end='')

    # JAILBREAK TIME! Append the band report as text after the JSON
    # This creates invalid JSON but Claude somehow accepts it!
    if band_report:
        print(f"\n\n{band_report}", end='')


if __name__ == "__main__":
    main()
    sys.exit(0)  # Ensure clean exit

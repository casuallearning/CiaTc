#!/usr/bin/env python3
"""
Bootstrap the Band members by running them directly
This bypasses the hook system entirely for initial setup
"""

import subprocess
import sys
import os
from pathlib import Path

def run_band_member(name, prompt_file):
    """Run a single band member with their prompt"""

    print(f"\n{'='*60}")
    print(f"🎸 Bootstrapping {name}...")
    print(f"{'='*60}\n")

    if not prompt_file.exists():
        print(f"ERROR: {prompt_file} not found!")
        return None

    # Read the prompt
    with open(prompt_file, 'r') as f:
        prompt = f.read()

    # For John, we need to be in the VERA directory
    if name == "John":
        # Replace template variables for John
        prompt = prompt.replace("[Project Name]", "VERA")
        # Use the actual prompt for John
        final_prompt = prompt
    elif name in ["George", "Pete", "Paul", "Ringo"]:
        # For other band members, use simple test data
        prompt = prompt.replace("{user_prompt}", "Initial bootstrap test for VERA project")
        prompt = prompt.replace("{transcript_summary}", "Starting new session...")
        prompt = prompt.replace("{recent_code}", "// No code yet")
        prompt = prompt.replace("{project_name}", "VERA")
        prompt = prompt.replace("{cwd}", "/Users/philhudson/Projects/VERA")
        final_prompt = prompt
    elif name in ["Marie", "Descartes", "Feynman"]:
        # For janitors, they need an Opus response to critique
        test_response = "This is a test response for bootstrapping. The system is initializing."
        prompt = prompt.replace("{opus_response}", test_response)
        final_prompt = prompt
    else:
        final_prompt = prompt

    # Use the claude CLI in print mode (might bypass hooks)
    cmd = [
        '/usr/local/bin/claude',  # Full path to claude
        '--dangerously-skip-permissions',
        '--model', 'sonnet[1m]',
        '--print',  # Use print mode
        final_prompt
    ]

    try:
        print(f"Running: {' '.join(cmd[:5])}...")
        # Include PATH so node can be found
        env = os.environ.copy()
        env['CIATC_SUBPROCESS'] = 'true'  # Belt and suspenders
        env['PATH'] = '/usr/local/bin:' + env.get('PATH', '')

        # Change to VERA directory for John
        cwd = '/Users/philhudson/Projects/VERA' if name == "John" else None

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,  # 2 minute timeout for real prompts
            env=env,
            cwd=cwd
        )

        if result.returncode == 0:
            print(f"✅ {name} responded:")
            print(result.stdout)
            return result.stdout
        else:
            print(f"❌ {name} failed:")
            print(result.stderr)
            return None

    except subprocess.TimeoutExpired:
        print(f"⏰ {name} timed out after 30 seconds")
        return None
    except Exception as e:
        print(f"💥 {name} error: {e}")
        return None


def main():
    """Bootstrap all band members"""

    prompts_dir = Path("/Users/philhudson/Projects/CiaTc/prompts")

    # Band members in order
    band = [
        ("John", prompts_dir / "john.md"),
        ("George", prompts_dir / "george.md"),
        ("Pete", prompts_dir / "pete.md"),
        ("Paul", prompts_dir / "paul.md"),
        ("Ringo", prompts_dir / "ringo.md")
    ]

    print("🎸 THE BAND BOOTSTRAP SEQUENCE 🎸")
    print("Testing each member with a simple prompt first...")

    results = {}
    for name, prompt_file in band:
        result = run_band_member(name, prompt_file)
        results[name] = result

    print(f"\n{'='*60}")
    print("📊 BOOTSTRAP RESULTS:")
    print(f"{'='*60}")

    for name, result in results.items():
        status = "✅ Ready" if result else "❌ Failed"
        print(f"{name}: {status}")

    # Now do the janitors
    print(f"\n{'='*60}")
    print("🧹 BOOTSTRAPPING JANITORS...")
    print(f"{'='*60}")

    janitors = [
        ("Marie", prompts_dir / "marie.md"),
        ("Descartes", prompts_dir / "descartes.md"),
        ("Feynman", prompts_dir / "feynman.md")
    ]

    for name, prompt_file in janitors:
        result = run_band_member(name, prompt_file)
        results[name] = result

    print("\n✨ Bootstrap complete!")


if __name__ == "__main__":
    main()
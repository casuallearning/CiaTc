#!/usr/bin/env python3
"""Debug script to test band orchestrator"""

import json
import sys
import subprocess
import os

def test_band():
    """Test if the band can run at all"""

    print("Testing band orchestrator...", file=sys.stderr)

    # Create test event
    event = {
        "hook_event_name": "UserPromptSubmit",
        "prompt": "Test message",
        "cwd": "/Users/philhudson/Projects/VERA",
        "transcript_path": "/tmp/test.jsonl"
    }

    # Set up environment
    env = os.environ.copy()
    env['CIATC_SUBPROCESS'] = 'true'  # This should make the band pass through
    env['PATH'] = '/usr/local/bin:' + env.get('PATH', '')

    # Try running a simple claude command first
    print("\nTest 1: Can we run claude at all?", file=sys.stderr)
    try:
        result = subprocess.run(
            ['/usr/local/bin/claude', '--dangerously-skip-permissions', '--model', 'sonnet[1m]', '--print', 'Say "Claude works!"'],
            capture_output=True,
            text=True,
            timeout=30,
            env=env
        )
        print(f"Claude test result: {result.stdout[:100]}", file=sys.stderr)
        print(f"Claude test stderr: {result.stderr[:100]}", file=sys.stderr)
    except Exception as e:
        print(f"Claude test failed: {e}", file=sys.stderr)

    # Now test the band with recursion guard
    print("\nTest 2: Band with recursion guard (should pass through)", file=sys.stderr)
    try:
        result = subprocess.run(
            ['python3', '/Users/philhudson/Projects/CiaTc/band_orchestrator_main.py'],
            input=json.dumps(event),
            capture_output=True,
            text=True,
            timeout=5,
            env=env  # CIATC_SUBPROCESS=true should make it pass through
        )
        output = json.loads(result.stdout)
        if output == event:
            print("✅ Recursion guard works!", file=sys.stderr)
        else:
            print("❌ Recursion guard failed!", file=sys.stderr)
    except Exception as e:
        print(f"❌ Band test failed: {e}", file=sys.stderr)

    # Test without recursion guard (will actually run band)
    print("\nTest 3: Band without recursion guard (will try to run)", file=sys.stderr)
    env2 = os.environ.copy()
    env2['PATH'] = '/usr/local/bin:' + env2.get('PATH', '')
    # Don't set CIATC_SUBPROCESS

    try:
        # Give it only 5 seconds to see if it starts
        result = subprocess.run(
            ['python3', '/Users/philhudson/Projects/CiaTc/band_orchestrator_main.py'],
            input=json.dumps(event),
            capture_output=True,
            text=True,
            timeout=5,
            env=env2
        )
        print(f"Band output: {result.stdout[:200]}", file=sys.stderr)
    except subprocess.TimeoutExpired:
        print("❌ Band timed out (as expected for now)", file=sys.stderr)
    except Exception as e:
        print(f"❌ Band error: {e}", file=sys.stderr)

if __name__ == "__main__":
    test_band()
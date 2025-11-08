#!/usr/bin/env python3
"""
Performance test for individual band members
Tests each agent with timing to identify bottlenecks
"""

import json
import time
import sys
from pathlib import Path

# Import the band functions
sys.path.insert(0, str(Path(__file__).parent))
from band_orchestrator_main import run_john, run_george, run_pete, run_paul, run_build_health, run_ringo

def test_agent(name, func, *args):
    """Test a single agent with timing"""
    print(f"\n{'='*60}")
    print(f"Testing {name}...")
    print(f"{'='*60}")

    start = time.time()
    try:
        result = func(*args)
        elapsed = time.time() - start

        print(f"✅ {name} completed in {elapsed:.2f}s")
        print(f"\nOutput length: {len(result)} characters")
        print(f"\nFirst 200 chars:\n{result[:200]}")

        if elapsed > 30:
            print(f"⚠️  WARNING: {name} took >{elapsed:.0f}s - needs optimization!")

        return {
            'name': name,
            'success': True,
            'time': elapsed,
            'output_length': len(result),
            'output_preview': result[:200]
        }
    except Exception as e:
        elapsed = time.time() - start
        print(f"❌ {name} failed after {elapsed:.2f}s: {e}")
        return {
            'name': name,
            'success': False,
            'time': elapsed,
            'error': str(e)
        }

def main():
    cwd = "/Users/philhudson/Projects/CiaTc"
    transcript_path = "/Users/philhudson/.claude/projects/-Users-philhudson-Projects-CiaTc/a9d5153d-dc21-4ac1-8412-dde153d93365.jsonl"
    test_prompt = "Test the band performance optimization"

    results = []

    print("🎸 Band Performance Diagnostic Tool")
    print(f"Testing in: {cwd}\n")

    # Test each agent individually
    print("\n" + "="*60)
    print("PHASE 1: Parallel Agents (should be fast)")
    print("="*60)

    results.append(test_agent("Build Health", run_build_health, cwd))
    results.append(test_agent("John", run_john, cwd, transcript_path))
    results.append(test_agent("George", run_george, test_prompt, transcript_path, cwd))
    results.append(test_agent("Pete", run_pete, test_prompt, cwd))

    print("\n" + "="*60)
    print("PHASE 2: Sequential Agents")
    print("="*60)

    results.append(test_agent("Paul", run_paul, test_prompt))
    results.append(test_agent("Ringo", run_ringo, cwd, test_prompt))

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    total_time = sum(r['time'] for r in results)
    print(f"\nTotal sequential time: {total_time:.2f}s")
    print(f"Parallel time estimate (Phase 1 + Phase 2): ~{max([r['time'] for r in results[:4]]) + sum([r['time'] for r in results[4:]]):.2f}s")

    print("\n\nIndividual Times:")
    for r in sorted(results, key=lambda x: x['time'], reverse=True):
        status = "✅" if r['success'] else "❌"
        print(f"{status} {r['name']:15} {r['time']:6.2f}s")

    # Identify bottlenecks
    slow_agents = [r for r in results if r.get('time', 0) > 30]
    if slow_agents:
        print("\n⚠️  BOTTLENECKS (>30s):")
        for r in slow_agents:
            print(f"   - {r['name']}: {r['time']:.2f}s")

    # Save detailed results
    with open('/Users/philhudson/Projects/CiaTc/performance_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    print("\n📊 Detailed results saved to performance_results.json")

if __name__ == "__main__":
    main()

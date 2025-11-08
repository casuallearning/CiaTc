#!/usr/bin/env python3
"""
Test Conductor's semantic understanding with nuanced prompts
Shows how it distinguishes between simple questions and complex concise tasks
"""

from conductor_agent import run_conductor

# Test cases: Complex but concise vs Simple questions
test_cases = [
    # Simple questions (should skip)
    "What is JWT?",
    "How does React work?",
    "Explain async/await",

    # Complex but concise (should run)
    "Fix auth bug",  # Short but actionable, needs project context
    "Optimize queries",  # Short but requires technical analysis
    "Add caching",  # Short but implementation task

    # Nuanced cases
    "Why is this slow?",  # Could be simple or complex - needs project context
    "Refactor UserService",  # Concise but complex implementation
    "Design payment flow",  # Short but needs creative thinking
    "Review this code",  # Needs context about what code

    # Edge cases
    "ok",  # Too vague
    "looks good",  # Acknowledgment, not a task
    "thanks",  # Social, not technical
]

project_stats = {
    "file_count": 250,
    "changed_files": 3,
    "last_run": "5 minutes ago"
}

print("=" * 80)
print("CONDUCTOR SEMANTIC UNDERSTANDING TEST")
print("Testing: Complex-but-concise vs Simple questions")
print("=" * 80)

for prompt in test_cases:
    print(f"\nPrompt: \"{prompt}\"")
    print("-" * 80)

    decision = run_conductor(prompt, project_stats)

    should_run = "✅ RUN" if decision['should_run'] else "⏭️  SKIP"
    print(f"{should_run}")
    print(f"Reason: {decision['reason']}")

    if decision['should_run']:
        print(f"Agents: {', '.join(decision['agents'])}")
        print(f"Timeout: {decision['timeout']}s")
        print(f"Priority: {decision['priority']}")

print("\n" + "=" * 80)

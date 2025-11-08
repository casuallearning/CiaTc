#!/bin/bash
# Demo script to show Band statusline in action

echo "🎸 Band Statusline Demo"
echo "======================="
echo ""

# Simulate different agent states
scenarios=(
    "No agents running"
    "John indexing files (8s)"
    "Stop hook: John, George, Pete running"
    "UserPromptSubmit: Paul thinking (45s)"
    "Marie cleaning up (1m 23s)"
    "Full band + Gilfoyle active"
)

echo "What the statusline shows in different scenarios:"
echo ""

# Scenario 1: No agents
echo "1. ${scenarios[0]}:"
echo "   philhudson@host Sonnet CiaTc (git:main) [12:53:53] v2.0"
echo ""

# Scenario 2: John running
echo "2. ${scenarios[1]}:"
echo "   philhudson@host Sonnet CiaTc (git:main) [12:53:53] v2.0 🎸[📁john:8s ]"
echo ""

# Scenario 3: Stop hook agents
echo "3. ${scenarios[2]}:"
echo "   philhudson@host Sonnet CiaTc (git:main) [12:53:53] v2.0 🎸[📁john:15s 📖george:12s 🔧pete:12s ]"
echo ""

# Scenario 4: Paul thinking
echo "4. ${scenarios[3]}:"
echo "   philhudson@host Sonnet CiaTc (git:main) [12:53:53] v2.0 🎸[💡paul:45s 🥁ringo:12s ]"
echo ""

# Scenario 5: Marie cleanup
echo "5. ${scenarios[4]}:"
echo "   philhudson@host Sonnet CiaTc (git:main) [12:53:53] v2.0 🎸[🧹marie:1m23s ]"
echo ""

# Scenario 6: Full band
echo "6. ${scenarios[5]}:"
echo "   philhudson@host Sonnet CiaTc (git:main*) [12:53:53] v2.0 🎸[📁john:34s 📖george:28s 🔧pete:25s 🧹marie:2m15s 🏗️gilfoyle:31s ]"
echo ""

echo "======================="
echo "The statusline updates automatically as agents run!"
echo "Agents shown: 📁john 📖george 🔧pete 💡paul 🥁ringo 🧹marie 🏗️gilfoyle"

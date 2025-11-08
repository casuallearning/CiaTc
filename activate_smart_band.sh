#!/bin/bash
# Activate the Smart Band with Conductor orchestration

echo "🎸 Activating Smart Band with Conductor..."

# Check if local settings exist and have disabled hooks
if [ -f ".claude/settings.local.json" ]; then
    echo "⚠️  Found .claude/settings.local.json with disabled hooks"

    # Backup existing local settings
    cp .claude/settings.local.json .claude/settings.local.json.backup
    echo "📦 Backed up to .claude/settings.local.json.backup"

    # Remove or update to enable hooks
    echo '{}' > .claude/settings.local.json
    echo "✅ Enabled hooks in local settings"
else
    echo "✅ No local settings blocking hooks"
fi

# Verify global hooks are configured
if grep -q "band_orchestrator_main.py" ~/.claude/settings.json 2>/dev/null; then
    echo "✅ Global hooks configured in ~/.claude/settings.json"
else
    echo "⚠️  Global hooks not found in ~/.claude/settings.json"
    echo "    You may need to run the original activate_ciatc_final.sh"
fi

echo ""
echo "🎼 Smart Band Features Activated:"
echo "   • Conductor agent decides which band members to run"
echo "   • Intelligent prompt analysis (skips simple questions)"
echo "   • Adaptive timeouts: 60s → 180s based on complexity"
echo "   • File change detection and caching"
echo ""
echo "📊 Example behavior:"
echo "   'What is React?' → Skipped (0s)"
echo "   'Explain pagination' → George + Ringo (60s)"
echo "   'Implement JWT auth' → All 5 agents (180s)"
echo ""
echo "✨ Ready to rock! Try asking Claude a question."

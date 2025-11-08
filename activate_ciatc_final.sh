#!/bin/bash

echo "
╔══════════════════════════════════════════════════════╗
║            CiaTc Framework Activation                 ║
║          (Claudes in a Trench Coat)                   ║
╚══════════════════════════════════════════════════════╝
"

# Parse mode argument
MODE="${1:-band}"

case $MODE in
    "band")
        echo "🎸 Activating The Band (pre-analysis)..."
        HOOKS='"UserPromptSubmit": [{"hooks": [{"type": "command", "command": "python3 /Users/philhudson/Projects/CiaTc/band_orchestrator_main.py"}]}]'
        ;;
    "janitors")
        echo "🧹 Activating Philosophical Janitors (post-critique)..."
        HOOKS='"PostResponse": [{"hooks": [{"type": "command", "command": "python3 /Users/philhudson/Projects/CiaTc/janitors_orchestrator_main.py"}]}]'
        ;;
    "full")
        echo "🎸🧹 Activating FULL Framework (Band + Janitors)..."
        HOOKS='"UserPromptSubmit": [{"hooks": [{"type": "command", "command": "python3 /Users/philhudson/Projects/CiaTc/band_orchestrator_main.py"}]}], "PostResponse": [{"hooks": [{"type": "command", "command": "python3 /Users/philhudson/Projects/CiaTc/janitors_orchestrator_main.py"}]}]'
        ;;
    *)
        echo "Usage: $0 [band|janitors|full]"
        echo ""
        echo "  band     - Pre-analysis by The Band"
        echo "  janitors - Post-critique by Philosophical Janitors"
        echo "  full     - Both Band and Janitors"
        exit 1
        ;;
esac

# Backup current settings
if [ -f ~/.claude/settings.local.json ]; then
    cp ~/.claude/settings.local.json ~/.claude/settings.backup.$(date +%s).json
    echo "✓ Backed up current settings"
fi

# Create new settings
cat > ~/.claude/settings.local.json << EOF
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "includeCoAuthoredBy": false,
  "hooks": {
    $HOOKS
  },
  "statusLine": {
    "type": "command",
    "command": "bash /Users/philhudson/.claude/statusline-command.sh"
  },
  "env": {
    "MAX_THINKING_TOKENS": "31999",
    "CLAUDE_CODE_MAX_OUTPUT_TOKENS": "32000"
  }
}
EOF

echo "
✅ CiaTc Framework Activated!
"

if [[ $MODE == "band" ]] || [[ $MODE == "full" ]]; then
    echo "🎸 THE BAND (5 Sonnets):"
    echo "   📁 John - Directory mapper & file indexer"
    echo "   📖 George - Narrative manager (per category)"
    echo "   ⚙️ Pete - Technical documentation"
    echo "   💡 Paul - Wild ideas generator"
    echo "   🥁 Ringo - Context synthesizer"
    echo ""
    echo "   Triggers: implement, build, fix, debug, create, help"
fi

if [[ $MODE == "janitors" ]] || [[ $MODE == "full" ]]; then
    echo "🧹 PHILOSOPHICAL JANITORS (3 Sonnets):"
    echo "   🧹 Marie - Cleanup & organization"
    echo "   🤔 Descartes - Assumption checking"
    echo "   ⚛️ Feynman - Simplicity advocacy"
    echo ""
    echo "   Reviews responses > 500 characters"
fi

echo "
Each assistant is a real Claude Sonnet[1m] instance.
Model: sonnet[1m]

To deactivate: ./deactivate_ciatc_final.sh
"
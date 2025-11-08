#!/bin/bash
# Enable CiaTc Band agents in any project
# Usage: cd /path/to/your/project && /path/to/CiaTc/enable_band_in_project.sh

CIATC_DIR="/Users/philhudson/Projects/CiaTc"

echo "🎸 Enabling CiaTc Band in $(pwd)"
echo ""

# Create .claude directory if it doesn't exist
mkdir -p .claude

# Create settings.local.json with Band hooks
cat > .claude/settings.local.json << EOF
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 ${CIATC_DIR}/band_orchestrator_main.py",
            "timeout": 3000
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 ${CIATC_DIR}/band_orchestrator_stop.py",
            "timeout": 3000
          }
        ]
      }
    ]
  }
}
EOF

# Create .band_cache directory for this project
mkdir -p .band_cache/locks

echo "✅ Band agents enabled!"
echo ""
echo "Active agents:"
echo "  UserPromptSubmit: 🥁 Ringo (context), 💡 Paul (opt-in wild ideas)"
echo "  Stop: 📁 John, 📖 George, 🔧 Pete, 🧹 Marie, 🏗️ Gilfoyle"
echo ""
echo "📊 Your statusline will now show Band activity in this project!"
echo "🎸 Try asking Claude a question to see it in action."

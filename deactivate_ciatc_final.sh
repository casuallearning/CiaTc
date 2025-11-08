#!/bin/bash

echo "🔻 Deactivating CiaTc Framework..."

# Find most recent backup
LATEST_BACKUP=$(ls -t ~/.claude/settings.backup.*.json 2>/dev/null | head -1)

if [ -f "$LATEST_BACKUP" ]; then
    cp "$LATEST_BACKUP" ~/.claude/settings.local.json
    echo "✓ Restored settings from: $(basename $LATEST_BACKUP)"
else
    # Create minimal settings
    cat > ~/.claude/settings.local.json << 'EOF'
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "includeCoAuthoredBy": false,
  "env": {
    "MAX_THINKING_TOKENS": "31999",
    "CLAUDE_CODE_MAX_OUTPUT_TOKENS": "32000"
  }
}
EOF
    echo "✓ Reset to minimal settings (no backup found)"
fi

echo "✅ CiaTc Framework deactivated"
echo "The Band has left the building 🎸"
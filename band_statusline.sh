#!/bin/bash
# Band Agent Statusline
# Shows which agents are currently running in the background

LOCK_DIR=".band_cache/locks"
RUNNING=""
COUNT=0

# Check if we're in a CiaTc project
if [ ! -d "$LOCK_DIR" ]; then
    # Not in a Band-enabled project, show nothing
    exit 0
fi

# Read each lock file to see which agents are running
shopt -s nullglob
for lockfile in "$LOCK_DIR"/*.lock; do
    if [ -f "$lockfile" ]; then
        agent=$(basename "$lockfile" .lock)

        # Read PID and timestamp from lock file
        pid=$(head -1 "$lockfile" 2>/dev/null)
        timestamp=$(tail -1 "$lockfile" 2>/dev/null)

        # Check if process is actually running
        if ps -p "$pid" > /dev/null 2>&1; then
            # Calculate elapsed time
            now=$(date +%s)
            start_time=${timestamp%.*}  # Remove decimal part
            elapsed=$((now - start_time))

            # Format agent name (capitalize, truncate)
            case "$agent" in
                john) icon="📁" ;;
                george) icon="📖" ;;
                pete) icon="🔧" ;;
                paul) icon="💡" ;;
                ringo) icon="🥁" ;;
                marie) icon="🧹" ;;
                gilfoyle) icon="🏗️" ;;
                *) icon="⚙️" ;;
            esac

            # Format time
            if [ $elapsed -lt 60 ]; then
                time_str="${elapsed}s"
            else
                mins=$((elapsed / 60))
                secs=$((elapsed % 60))
                time_str="${mins}m${secs}s"
            fi

            RUNNING="${RUNNING}${icon}${agent}:${time_str} "
            COUNT=$((COUNT + 1))
        fi
    fi
done

# Output statusline segment
if [ $COUNT -gt 0 ]; then
    echo " 🎸[$RUNNING]"
fi

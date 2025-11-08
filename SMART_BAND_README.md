# Smart Band with Conductor Orchestration

**Problem Solved:** The Band was taking 5-10 minutes for EVERY prompt, even simple questions, because all agents always ran with 600-second timeouts.

**Solution:** A **Conductor agent** (Claude Haiku) intelligently decides which band members should perform based on semantic understanding of your prompt.

## How It Works

### The Conductor (New!)

A fast Claude Haiku agent that analyzes your prompt and decides:
- **Should we run at all?** (Skip simple questions)
- **Which agents are needed?** (1-5 agents based on task)
- **How much time?** (60s, 120s, or 180s based on complexity)

**Location:** `conductor_agent.py` + `prompts/conductor.md`

### Smart Orchestrator

Provides project intelligence to the Conductor:
- Tracks file changes (MD5 hashing)
- Calculates project size
- Maintains cache to avoid redundant work
- Detects what actually changed since last run

**Location:** `smart_orchestrator.py`

### Updated Orchestrators

Both hooks now consult the Conductor:
- `band_orchestrator_main.py` (UserPromptSubmit hook)
- `band_orchestrator_stop.py` (Stop hook)

## Performance Comparison

### Old System
- **Every prompt**: 5-10 minutes (all agents, 600s timeout)
- **Simple question**: 5-10 minutes 😱
- **Complex task**: 5-10 minutes
- **No intelligence**: Always ran everything

### New System with Conductor
- **Simple question**: 0s (skipped) ✅
- **Context retrieval**: 60s (George + Ringo)
- **Medium task**: 120s (2-3 agents)
- **Complex task**: 180s (all 5 agents)
- **Intelligence**: Only runs what's needed

## Example Decisions

```bash
$ python3 conductor_agent.py

"What is React?"
→ SKIP (0s)

"Explain pagination we discussed earlier"
→ George + Ringo (60s) - needs conversation context

"Implement JWT authentication"
→ John + Pete + Paul + Ringo (180s) - complex implementation

"Refactor database layer for performance"
→ John + Pete + Paul + Ringo (180s) - complex + creative
```

## Activation

```bash
# Enable the smart band
./activate_smart_band.sh

# Or manually:
# 1. Remove .claude/settings.local.json (or set disableAllHooks: false)
# 2. Ensure ~/.claude/settings.json has the hook configuration
```

## Architecture

```
User Prompt
    ↓
Conductor Agent (Haiku, 10s max)
    ↓
Decision: {agents, timeout, priority}
    ↓
Smart Orchestrator (gets project stats)
    ↓
Run Selected Agents in Parallel
    ↓
Results → Band Report
```

## Key Files

- **`conductor_agent.py`** - The decision-making agent
- **`prompts/conductor.md`** - Conductor's instructions
- **`smart_orchestrator.py`** - Project intelligence and caching
- **`band_orchestrator_main.py`** - Updated UserPromptSubmit hook
- **`band_orchestrator_stop.py`** - Updated Stop hook
- **`.band_cache/`** - Stores file hashes and run history

## Timeout Strategy

**Adaptive based on project size:**
- Small projects (<100 files): 60s per agent
- Medium projects (100-500 files): 120s per agent
- Large projects (>500 files): 180s per agent

**Conductor overrides based on task complexity:**
- Simple context gathering: 60s
- Moderate analysis: 120s
- Deep thorough work: 180s

## Benefits

✅ **10-20x faster for most prompts** (skip or fewer agents)
✅ **Intelligent agent selection** (only run what's needed)
✅ **No more waiting for simple questions**
✅ **Still thorough when needed** (3 min vs 10 min for complex tasks)
✅ **File change detection** (avoid redundant work)
✅ **Adaptive to project size** (scales automatically)

## Testing

```bash
# Test the Conductor's decision-making
python3 conductor_agent.py

# Test smart orchestrator
python3 smart_orchestrator.py "your prompt here"
```

## Future Enhancements

- **Learning from history**: Track which agent decisions were most useful
- **Cost optimization**: Track token usage per agent
- **Parallel phases**: Run independent agents in phases for better parallelism
- **User overrides**: Let user force certain agents via special syntax
- **Polyrhythmic timing**: Paul's musical time signature approach (see PaulsMadRamblings/)

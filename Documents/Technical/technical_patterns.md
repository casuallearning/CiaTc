# Technical Patterns - CiaTc Framework

## Overview
This document captures design patterns, implementation approaches, and technical patterns used throughout the CiaTc framework.

**Last Updated:** November 8, 2025

---

## Intelligent Agent Selection Pattern (Conductor System)

**Location:** `conductor_agent.py`, `band_orchestrator_main.py`

**Pattern Name:** Semantic Decision Router

### Overview
Instead of running all 5 band members on every prompt (5-10 minutes), the Conductor agent makes intelligent decisions about which agents should run based on prompt semantics. This reduces execution time from minutes to milliseconds for trivial queries and 1-3 minutes for complex tasks.

### Implementation

**Conductor Decision Process:**
```
User Prompt
    ↓
SmartOrchestrator (project statistics)
    ↓
Conductor (semantic analysis via Claude Haiku)
    ├─ Input: Prompt + Project stats
    ├─ Analysis: "Is this trivial?" "How complex?"
    └─ Output: JSON with agent selection
    ↓
Band Orchestrator:
    ├─ If skip_band=true → Return original JSON (0s)
    ├─ If agents list → Run selected agents only
    └─ Use suggested_timeout from Conductor
```

**Key Code:**
```python
# conductor_agent.py:run_conductor()
conductor_result = json.loads(claude_output)
should_run = conductor_result.get("should_run", True)
agents = conductor_result.get("agents_to_run", [])
timeout = conductor_result.get("timeout", 180)
```

### Decision Logic

**Skip Patterns (0 seconds):**
- "what is", "how do i", "explain", "list", "where is"
- Simple factual questions with well-defined answers
- Result: Skip band orchestration entirely

**Minimal Agents (60 seconds):**
- Simple code queries without refactoring
- Documentation lookups
- Explanation requests
- Agents: `["john", "ringo"]` (just structure + synthesis)

**Full Band (180+ seconds):**
- "refactor", "implement", "create", "build", "architect"
- Complex code changes, new features
- All 5 agents: john, george, pete, paul, ringo

### Performance Benefits

| Query Type | Before | After | Speedup |
|-----------|--------|-------|---------|
| "What is..." | 5-10m | <10s | 30-60x |
| "Where is X" | 5-10m | <10s | 30-60x |
| "Add feature" | 5-10m | 1-3m | 2-5x |
| No change | 5-10m | skip | ∞ |

### Technical Risks

1. **Incorrect Skip Decisions:** Conductor might skip when analysis is needed
   - Mitigation: Haiku model is surprisingly capable; can always re-run manually

2. **Timeout Miscalculation:** Project size changes not detected
   - Mitigation: SmartOrchestrator has fallback mechanisms

3. **Prompt Ambiguity:** Semantic analysis fails on novel patterns
   - Mitigation: Clear logging enables manual override

---

## Project Intelligence Pattern (SmartOrchestrator)

**Location:** `smart_orchestrator.py`

**Pattern Name:** Incremental Context Cache

### Overview
SmartOrchestrator gathers project statistics without full re-scan on each invocation. Uses file hashing for small files and modification time for large files, with aggressive caching.

### Implementation

**Two-Level Caching:**
```python
# Level 1: File hashes (fast change detection)
file_hashes = {
    "path/to/file.py": "abc123def456...",  # MD5 hash
    "path/to/large.swift": 1762625964      # mtime for >1MB
}

# Level 2: Orchestrator cache (decision history)
orchestrator_cache = {
    "last_update": 1762625964,
    "file_count": 42,
    "total_lines": 5280,
    "changed_files": ["band_orchestrator_main.py"],
    "change_count": 1
}
```

**Incremental Detection:**
```python
def get_changed_files(self):
    """Returns only files that have changed since last run"""
    cached_hashes = load_json('.band_cache/file_hashes.json')
    current_hashes = {}

    for filepath in project_files:
        if file_size > 1_000_000:
            current_hashes[filepath] = os.path.getmtime(filepath)
        else:
            current_hashes[filepath] = md5_hash(filepath)

    changed = [f for f in current_hashes if current_hashes[f] != cached_hashes.get(f)]
    return changed
```

### File Size Heuristic

| File Size | Method | Reason |
|-----------|--------|--------|
| < 1 MB | MD5 hash | Accurate change detection |
| 1-100 MB | mtime | Hash would be slow |
| > 100 MB | skip | Too expensive |

### Project Size Classification

```python
file_count = 42
total_lines = 5280

if file_count < 100:
    project_size = 'small'    # 60s timeout
elif file_count < 500:
    project_size = 'medium'   # 120s timeout
else:
    project_size = 'large'    # 180s timeout
```

### Performance Characteristics

- **First run:** 10-30 seconds (full project scan)
- **Typical run:** 2-5 seconds (only changed files hashed)
- **Cache hit:** 100-200 milliseconds (just read JSON)
- **Project 500+ files:** 75% time saved after first run

---

## File-Based Locking Pattern (AgentLock)

**Location:** `agent_lock.py`

**Pattern Name:** Distributed Lock via Filesystem

### Overview
Prevents duplicate agent execution by using file-based locks with automatic cleanup and stale lock detection.

### Implementation

**Lock File Structure:**
```
.band_cache/locks/
├── john.lock          # Contains PID and timestamp
├── george.lock
├── pete.lock
└── paul.lock
```

**Lock File Content:**
```json
{
    "pid": 12345,
    "timestamp": 1762625964,
    "hostname": "Phils-MacBook"
}
```

**Acquisition Pattern:**
```python
class AgentLock:
    def acquire(self, blocking=True):
        """Acquire exclusive lock or raise"""
        try:
            # Try fcntl.flock - cross-platform
            fcntl.flock(lock_file, fcntl.LOCK_EX | (0 if blocking else fcntl.LOCK_NB))
            write_lock_metadata(lock_file, pid, timestamp)
            return True
        except IOError:
            if not blocking:
                raise AlreadyLockedError()
            # Blocking mode waits

    def cleanup_stale_locks(self, timeout=600):
        """Remove locks > 10 minutes old (crashed processes)"""
        for lock_file in lock_dir:
            age = time.time() - lock_file.mtime
            if age > timeout:
                lock_file.unlink()
```

**Usage Pattern:**
```python
with AgentLock("john") as lock:
    if lock:
        run_john()  # Only runs if lock acquired
```

### Advantages

1. **Cross-Process Safety:** Works across Python threads and subprocesses
2. **Automatic Cleanup:** Stale locks cleaned after 10 minutes
3. **Human-Readable:** Lock files show which process holds lock
4. **Fallback:** Non-blocking mode for timeout-aware code

### Technical Risks

1. **Network Filesystems:** fcntl doesn't work reliably on NFS
   - Mitigation: Add optional Redis-based locking in future

2. **Multiple Machines:** Same lock directory on different hosts
   - Mitigation: Include hostname in lock files

---

## Completion Persistence Pattern (Completed Files)

**Location:** `agent_lock.py:80-104`, `statusline-command.sh:84-101`

**Pattern Name:** Ephemeral Completion Status

### Overview
After agents complete, their lock files are deleted but a temporary `.completed` file persists for 60 seconds, allowing the statusline to display recent completions with runtime metrics.

### Implementation

**Lock Lifecycle:**
```
T=0s:    Agent starts → john.lock created (PID + start timestamp)
T=0-Ns:  Agent running → john.lock exists, statusline shows elapsed time
T=Ns:    Agent completes → john.lock deleted, john.completed created
T=N-60s: john.completed persists → statusline shows ✓ with final runtime
T=60s+:  john.completed auto-deleted → no display
```

**Completed File Structure:**
```
.band_cache/locks/
├── john.lock           # Active agent (if running)
├── george.completed    # Completed <60s ago
├── pete.lock          # Active agent
└── gilfoyle.completed # Completed <60s ago
```

**Completed File Format:**
```
Line 1: completion_timestamp (float, epoch seconds)
Line 2: runtime (float, seconds elapsed)
```

**Example (`gilfoyle.completed`):**
```
1762630606.327842
0.0580751895904541
```

### Code Implementation

**Writing Completion Record (Python):**
```python
# agent_lock.py:80-94
def release(self):
    """Release lock and record completion"""
    if self.lock_file.exists():
        with open(self.lock_file, 'r') as f:
            lines = f.readlines()
            start_time = float(lines[1].strip())
            runtime = time.time() - start_time

        # Create completion record
        completion_file = LOCK_DIR / f"{self.agent_name}.completed"
        with open(completion_file, 'w') as cf:
            cf.write(f"{time.time()}\n{runtime}\n")

        # Remove lock file
        self.lock_file.unlink()
```

**Reading Completion Record (Bash):**
```bash
# statusline-command.sh:84-101
for lockfile in "$LOCK_DIR"/*.lock "$LOCK_DIR"/*.completed; do
    extension="${filename##*.}"

    if [ "$extension" = "completed" ]; then
        completion_time=$(sed -n '1p' "$lockfile")
        runtime=$(sed -n '2p' "$lockfile")

        # Check if recent (< 60 seconds)
        now=$(date +%s)
        comp_time=${completion_time%.*}
        age=$((now - comp_time))

        if [ $age -lt 60 ]; then
            elapsed=${runtime%.*}  # NOTE: Truncation bug (see implementation_log.md)
            status_icon="✓"
        else
            rm -f "$lockfile"  # Cleanup old completion
        fi
    fi
done
```

### Display Format

**Running Agent (from .lock):**
```
●📁john:12s    # Active, 12 seconds elapsed
```

**Completed Agent (from .completed):**
```
✓🏗️gilfoyle:0s  # Completed, 0.058s runtime (truncated to 0s - BUG)
```

**Combined Display:**
```bash
🎸[●📁john:45s ✓🏗️gilfoyle:0s ✓📖george:23s]
#  └─running   └─completed    └─completed
```

### Advantages

1. **Visibility:** Users see recent completions, not just active agents
2. **Performance Feedback:** Shows how long agents took to run
3. **Status History:** 60-second window provides execution context
4. **Non-Blocking:** Completion records written asynchronously

### Technical Debt & Known Issues

#### Issue 1: Float Truncation Bug (CRITICAL)
**Location:** `statusline-command.sh:95`

**Problem:**
```bash
runtime=$(sed -n '2p' "$lockfile")  # "0.0580751895904541"
elapsed=${runtime%.*}                # Becomes "0" (truncates, doesn't round)
```

**Impact:**
- Agents completing in <1s show as `0s`
- Example: Gilfoyle (58ms) displays as `0s` instead of `<1s` or `58ms`
- Misleading - suggests instant execution

**Fix (Recommended):**
```bash
elapsed=$(printf "%.0f" "$runtime")  # Round instead of truncate
```

**Status:** Documented in implementation_log.md, fix pending

#### Issue 2: No Sub-Second Display
**Problem:** Time formatting only supports integer seconds

**Impact:**
- Fast agents (50-500ms) show misleading `0s` or `1s`
- No visibility into micro-optimizations

**Potential Enhancement:**
```bash
if (( $(echo "$runtime < 1" | bc -l) )); then
    ms=$(printf "%.0f" "$(echo "$runtime * 1000" | bc -l)")
    time_str="${ms}ms"
fi
```

#### Issue 3: 60-Second Cleanup Window
**Problem:** Completed files auto-delete after 60 seconds

**Rationale:**
- Prevents `.completed` file accumulation
- Balances visibility vs clutter

**Alternative:** Persist to JSON history file for long-term analytics

### Performance Characteristics

**File I/O Overhead:**
- Write completion: ~1-2ms (single write)
- Read completion: ~0.5ms (sed reads 2 lines)
- Cleanup: ~0.1ms per file (unlink)

**Statusline Impact:**
- Check `.lock` files: ~0.5ms per file
- Check `.completed` files: ~0.5ms per file
- Total (7 agents max): ~7ms per statusline refresh

**Completion File Lifecycle:**
```
Agent completes → Write .completed (1-2ms)
    ↓
Statusline refreshes every ~1s → Read .completed (0.5ms)
    ↓
60 seconds pass → Auto-delete .completed (0.1ms)
```

### Technologies Used

- **Python:** `time.time()` for high-precision timestamps
- **Bash:** `sed` for line extraction, `${var%.*}` for decimal removal
- **Filesystem:** Atomic file creation (> operator)
- **Arithmetic:** Bash integer math `$(( ))`, `date +%s`

### Usage Pattern

**From Python (agent_lock.py):**
```python
with AgentLock("john") as lock:
    if lock:
        # Do work...
        pass
    # On context exit, release() writes .completed file automatically
```

**From Bash (statusline):**
```bash
# Automatically detects and displays .lock and .completed files
# No explicit invocation needed
```

### Testing & Verification

**Verify Completion Files Created:**
```bash
ls -lt .band_cache/locks/*.completed
```

**Check Completion Format:**
```bash
cat .band_cache/locks/gilfoyle.completed
# Line 1: completion timestamp (epoch)
# Line 2: runtime (seconds, float)
```

**Test Auto-Cleanup:**
```bash
# Wait 60 seconds, then check
ls -lt .band_cache/locks/*.completed  # Should be empty or recent only
```

**Simulate Fast Agent:**
```python
with AgentLock("test") as lock:
    time.sleep(0.05)  # 50ms
# Check: test.completed should show ~0.05 runtime
```

---

## Three-Phase Parallel Execution Pattern

**Location:** `band_orchestrator_main.py:219-307`

**Pattern Name:** Dependency-Aware Parallel Orchestration

### Overview
Executes 5 band members in 3 phases, respecting dependency ordering while maximizing parallelism within each phase.

### Phase Structure

**Phase 1: Foundation (2 agents, parallel)**
```python
with ThreadPoolExecutor(max_workers=2) as executor:
    john_future = executor.submit(run_john, cwd, transcript_path)
    build_health_future = executor.submit(run_build_health, cwd)
    results = {f.result() for f in as_completed([john_future, build_health_future])}
```

**Dependencies:** None
**Output:** `file_index.md`, `directory_map.md`, `dependency_graph.json`
**Time:** ~12 seconds

---

**Phase 2: Context & Documentation (2 agents, parallel, depends on Phase 1)**
```python
with ThreadPoolExecutor(max_workers=2) as executor:
    george_future = executor.submit(run_george, user_prompt, transcript_path, cwd)
    pete_future = executor.submit(run_pete, user_prompt, cwd)
    results = {f.result() for f in as_completed([george_future, pete_future])}
```

**Dependencies:** John's `file_index.md` (used by George and Pete)
**Output:** `Narratives/`, `Technical/` documents
**Time:** ~8 seconds

---

**Phase 3: Synthesis & Creative (2 agents, parallel, depends on Phases 1-2)**
```python
with ThreadPoolExecutor(max_workers=2) as executor:
    paul_future = executor.submit(run_paul, user_prompt)
    ringo_future = executor.submit(run_ringo, cwd, user_prompt)
    results = {f.result() for f in as_completed([paul_future, ringo_future])}
```

**Dependencies:** All Phase 1 & 2 outputs
**Output:** Creative ideas, unified context synthesis
**Time:** ~4 seconds

---

### Performance Analysis

```
Sequential: 12s + 8s + 4s = 24s

Parallel within phases: max(12s) + max(8s) + max(4s) = 24s
(No improvement: phases are fast and unequal)

Comparison to single sequential run: ~38s
Speedup: 24/38 = 63% improvement
```

### Failure Handling

```python
try:
    result = future.result(timeout=300)
    if result:
        band_report += result
except Exception as e:
    # Log error but continue with other agents
    sys.stderr.write(f"Agent failed: {e}\n")
    # Don't propagate - collect all available results
```

**Pattern:** Collect all available results even if some agents fail

---

## Parallel Execution with Adaptive Timeouts

**Location:** `conductor_agent.py`, `band_orchestrator_main.py`

**Pattern Name:** Dynamic Resource Allocation

### Overview
Timeout values adjust based on project size and complexity, preventing unnecessary waits on small projects while allowing thorough analysis on large ones.

### Timeout Calculation Strategy

```python
class SmartOrchestrator:
    def get_adaptive_timeout(self, changed_files_count):
        """Adaptive timeout based on scope"""
        base_timeout = {
            'small': 60,      # < 100 files
            'medium': 120,    # 100-500 files
            'large': 180      # > 500 files
        }[self.project_size]

        # Bonus: 10s per changed file (capped at 60s)
        change_bonus = min(changed_files_count * 10, 60)

        return base_timeout + change_bonus
```

### Conductor Override

Conductor may increase timeout for complex tasks:
```python
{
    "should_run": true,
    "agents_to_run": ["john", "george", "pete", "paul", "ringo"],
    "timeout": 300,  # Override SmartOrchestrator's default
    "priority": "high",
    "reason": "Implementing major refactor - needs all perspectives"
}
```

---

## Hook Output Injection Pattern

**Location:** `band_orchestrator_main.py:282-290`

**Pattern Name:** JSON + Markdown Side-Channel

### Overview
Hooks must output valid JSON for system compatibility, but we append Markdown context after JSON for human readability.

### Implementation

```python
event = json.loads(sys.stdin.read())
# ... process band orchestration ...
band_report = f"## Band Report\n{george_output}\n{pete_output}..."

# Output: Original JSON + Band Report
print(json.dumps(event), end='')      # Must be valid JSON for hook system
if band_report:
    print(f"\n\n{band_report}", end='')  # Append context for human reading
```

### Technical Justification

1. **Hook System Compatibility:** Must output valid JSON
2. **Human Context:** Markdown readable in Claude Code interface
3. **Parser Robustness:** JSON parser stops at first `}`, ignoring markdown tail

### Risks

1. **Large Output:** Band report can exceed system output limits
   - Mitigation: Summarize key points, truncate if needed

2. **Multiple JSONs:** Invalid if band_report contains JSON syntax
   - Mitigation: Escape JSON special characters in report

---

## Recursive Guard with Auto-Recovery Pattern

**Location:** `band_orchestrator_main.py:177-197`

**Pattern Name:** Environment Variable Leak Detection

### Overview
Prevents infinite recursion when band orchestrator spawns Claude subprocess, with automatic recovery if environment variable leaks to parent shell.

### Implementation

```python
CIATC_SUBPROCESS_ENV_VAR = 'CIATC_SUBPROCESS'

def main():
    if os.environ.get(CIATC_SUBPROCESS_ENV_VAR) == 'true':
        stdin_data = sys.stdin.read()
        try:
            event_data = json.loads(stdin_data)
            if event_data.get('hook_event_name') == 'UserPromptSubmit':
                # Valid hook but var set - must have leaked from subprocess
                del os.environ[CIATC_SUBPROCESS_ENV_VAR]
                # Continue processing (fallthrough)
            else:
                # Not a hook event - pass through unchanged
                print(stdin_data, end='')
                return
        except (json.JSONDecodeError, AttributeError):
            # Invalid JSON - pass through
            print(stdin_data, end='')
            return

    # Normal processing...
```

### Why This Pattern?

**Problem:** When band orchestrator spawns Claude subprocess with `CIATC_SUBPROCESS=true`, that variable can leak into parent shell environment, permanently disabling the hook.

**Solution:** Detect and recover:
1. If var set AND valid hook JSON → unset var and continue (recovery)
2. If var set BUT not hook JSON → pass through (recursion guard)

### Incident History

**2025-10-01:** Variable leaked after subprocess call, hook became non-functional
- Root cause: Subprocess environment variable not properly isolated
- Fix: Added intelligence to recursion guard to detect and fix the condition

---

## Model Selection Strategy

**Location:** Throughout codebase

**Pattern Name:** Tiered Model Selection

### Strategy

```
Task Type                 Model          Timeout   Reasoning
─────────────────────────────────────────────────────────────
Agent Decision            haiku          10s       Fast semantic analysis
Band Execution            sonnet         600s      Complex analysis, 5 agents
Janitor Review            sonnet         30s       Quick quality check
Documentation (Pete)      sonnet         600s      Technical detail
Creative Ideas (Paul)     sonnet         600s      Needs reasoning
Test Diagnostics          haiku          120s      Quick validation
```

### Rationale

1. **Haiku for Decisions:** Sub-10 second semantic analysis
2. **Sonnet for Deep Work:** Technical accuracy for documentation/code
3. **Timeout Scaling:** Longer for complex tasks, shorter for decisions

---

## Error Handling and Fallback Patterns

### Pattern 1: Graceful Degradation
```python
try:
    build_health = run_build_health(cwd)
except Exception as e:
    # Build health is nice-to-have, continue without it
    build_health = f"Build health unavailable: {e}"
```

### Pattern 2: Soft Failures
```python
try:
    git_status = subprocess.run(['git', 'status'], cwd=cwd)
except FileNotFoundError:
    # Git not installed - continue without change detection
    git_status = None
```

### Pattern 3: Timeout Resilience
```python
try:
    result = future.result(timeout=300)
except concurrent.futures.TimeoutError:
    # Agent took too long - use cached result if available
    result = cache.get(agent_name) or ""
```

---

## Performance Optimization Techniques

### 1. Caching Strategy
- **File hashes:** Avoid re-hashing unchanged files
- **Orchestrator cache:** Remember project stats
- **Lock cleanup:** Prevent stale locks from accumulating

### 2. Early Exit Pattern
```python
if conductor_says_skip():
    return original_json  # 0 seconds, no agent execution
```

### 3. Parallel Agent Execution
- Phase-based orchestration respects dependencies
- Max workers = 2 per phase (balance with system resources)

### 4. Timeout Management
- Adaptive timeouts prevent unnecessary waiting
- Conductor can prioritize urgent tasks

---

## Technical Debt & Improvements

1. **Hard-coded Paths:** `/usr/local/bin/claude`, prompt directories
   - Mitigation: Use environment variables
   - Priority: Low (works on target system)

2. **Tree-sitter Parsing:** Only Python, Swift, JavaScript
   - Improvement: Add more languages for dependency analysis
   - Priority: Medium

3. **Lock Mechanism:** File-based, NFS-incompatible
   - Alternative: Redis-based distributed locking
   - Priority: Low (not needed until multi-machine)

4. **Prompt Size:** No truncation for very large projects
   - Risk: May exceed context limits
   - Mitigation: Add smart truncation in future

---

## Testing & Validation

### Pattern: Isolated Test Runs

```python
# test_conductor_nuance.py
prompts = [
    ("what is", False),           # Should skip
    ("implement feature", True),  # Should run
    ("where is", False),          # Should skip
]

for prompt, expected_skip in prompts:
    result = conductor.decide(prompt)
    assert result['skip'] == expected_skip
```

### Pattern: Performance Benchmarking

```python
# test_band_performance.py
for agent in ['john', 'george', 'pete', 'paul', 'ringo']:
    start = time.time()
    result = run_agent(agent)
    elapsed = time.time() - start
    print(f"{agent}: {elapsed:.1f}s")
```

---

## Status Line Integration Pattern

**Location:** `/Users/philhudson/.claude/statusline-command.sh`, `.claude/settings.local.json`

**Pattern Name:** Real-Time Hook Agent Activity Display

### Overview
Displays currently executing hook agents in the Claude Code status line, providing real-time visibility into background orchestration work.

### Current Status Line Display
```
user@hostname model_name dir_info (git:branch*) [HH:MM:SS] vX.X.X
```

### Proposed Enhancement
```
user@hostname model_name dir_info (git:branch*) [HH:MM:SS] [J G P] vX.X.X
                                                              ^^^^^
                                                   Active agents: John, George, Pete
```

### Implementation Approaches

#### Approach 1: Lock File Monitoring (Recommended for Phase 1)

**Mechanism:** Monitor `.band_cache/locks/` directory for active lock files

```bash
# Check for active agent locks
active_agents=""
lock_dir="/Users/philhudson/Projects/CiaTc/.band_cache/locks"

if [ -d "$lock_dir" ]; then
    for lock_file in "$lock_dir"/*.lock; do
        if [ -f "$lock_file" ]; then
            agent_name=$(basename "$lock_file" .lock)
            lock_age=$(( $(date +%s) - $(stat -f %m "$lock_file") ))

            # Only show locks < 600s old (active)
            if [ $lock_age -lt 600 ]; then
                active_agents="$active_agents ${agent_name:0:1}"  # First letter
            fi
        fi
    done
fi

if [ -n "$active_agents" ]; then
    printf " \033[2;33m[%s]\033[0m" "$active_agents"
fi
```

**Benefits:**
- No orchestrator modifications needed
- Uses existing lock file infrastructure
- Real-time visibility (~0.9ms overhead)
- Minimal implementation cost

**Limitations:**
- No phase information (can't tell Phase 1 vs Phase 3)
- No precise elapsed time (only lock file mtime)
- Can't distinguish hook types (UserPromptSubmit vs Stop)

---

#### Approach 2: Shared State File (Recommended for Phase 2)

**Mechanism:** Orchestrators write progress to `.band_cache/agent_status.json`

**Orchestrator Update:**
```python
# band_orchestrator_main.py
status_file = Path('.band_cache/agent_status.json')

def update_status(hook_event, phase, active_agents, start_time, conductor_decision):
    """Atomically update agent status for status line display"""
    status = {
        'hook_event': hook_event,
        'phase': phase,
        'active_agents': active_agents,
        'start_time': start_time,
        'conductor_decision': conductor_decision
    }

    # Atomic write (write to temp, then rename)
    temp_file = status_file.with_suffix('.tmp')
    temp_file.write_text(json.dumps(status))
    temp_file.rename(status_file)

# Usage in orchestrator
update_status('UserPromptSubmit', 1, ['john', 'build_health'], time.time(), 'full_band')
```

**Status Line Script:**
```bash
status_file="/Users/philhudson/Projects/CiaTc/.band_cache/agent_status.json"

if [ -f "$status_file" ]; then
    # Only read if file changed (performance optimization)
    status_mtime=$(stat -f %m "$status_file")
    if [ "$status_mtime" != "$last_status_mtime" ]; then
        hook_event=$(jq -r '.hook_event' "$status_file")
        phase=$(jq -r '.phase' "$status_file")
        start_time=$(jq -r '.start_time' "$status_file")

        elapsed=$(( $(date +%s) - $start_time ))

        # Abbreviate: U=UserPromptSubmit, S=Stop
        hook_abbr="${hook_event:0:1}"

        printf " \033[2;36m[%s:P%d:%ds]\033[0m" "$hook_abbr" "$phase" "$elapsed"

        last_status_mtime="$status_mtime"
    fi
fi
```

**Display Example:**
```
user@host Sonnet CiaTc (git:main) [14:23:45] [U:P2:12s] v1.0
                                              ^^^^^^^^^^
                                        UserPromptSubmit, Phase 2, 12 seconds
```

**Benefits:**
- Rich context (phase, hook type, elapsed time)
- Conductor decision visibility
- Precise timing information
- Extendable (can add more metadata)

**Limitations:**
- Requires orchestrator modifications
- File I/O overhead (~1.5ms per refresh)
- Race conditions if multiple hooks running simultaneously (mitigated by atomic writes)

---

### Configuration

**Claude Code Settings (`~/.claude/settings.local.json`):**
```json
{
  "statusLine": {
    "type": "command",
    "command": "bash /Users/philhudson/.claude/statusline-command.sh"
  }
}
```

**Status Line Script Location:**
- Global: `/Users/philhudson/.claude/statusline-command.sh`
- Input: JSON via stdin (workspace, model info)
- Output: Formatted string with ANSI color codes

---

### Performance Analysis

**Lock File Monitoring (Approach 1):**
```
File system stat:     ~0.1ms per lock file
Worst case (9 locks): 9 × 0.1ms = 0.9ms
Status refresh rate:  1-2 Hz
Total overhead:       0.9-1.8ms/s (negligible)
```

**Shared State File (Approach 2):**
```
JSON file read:       ~0.5ms (OS cached)
JSON parse (jq):      ~1ms
Total per refresh:    ~1.5ms (acceptable)

Optimization: Only parse if mtime changed
Typical overhead:     0.1ms (just stat call)
```

---

### Technical Risks

1. **Performance Impact:** Status line refreshes at 1-2 Hz
   - Mitigation: Cache status file mtime, only parse if changed
   - Mitigation: Use lock file monitoring for Phase 1 (minimal overhead)

2. **Display Real Estate:** Limited horizontal space
   - Mitigation: Abbreviations (J=John, G=George, P=Pete, etc.)
   - Mitigation: Only show when agents are active

3. **Race Conditions:** Multiple hooks running simultaneously
   - Mitigation: Atomic writes (write to .tmp, then rename)
   - Mitigation: Lock file approach is naturally atomic (fcntl.flock)

4. **Stale Status:** Agent crash leaves lock/status file active
   - Mitigation: Timeout-based filtering (don't show status >10 min old)
   - Mitigation: Stale lock cleanup already implemented in agent_lock.py

---

### Integration Requirements

**Dependencies:**
- `jq`: JSON parsing in bash (already installed)
- `stat`: File metadata (BSD version, macOS)
- `date`: Epoch time calculation

**Files Involved:**
- `/Users/philhudson/.claude/statusline-command.sh`: Status line script
- `.band_cache/locks/*.lock`: Lock files (Approach 1)
- `.band_cache/agent_status.json`: Status file (Approach 2)
- `band_orchestrator_main.py`: Orchestrator (Approach 2 only)
- `band_orchestrator_stop.py`: Stop hook orchestrator (Approach 2 only)

---

### Example Display States

**No agents running:**
```
philhudson@Mac Sonnet CiaTc (git:main) [14:23:45] v1.0
```

**Phase 1 (Lock File Approach):**
```
philhudson@Mac Sonnet CiaTc (git:main) [14:23:45] [J B] v1.0
                                                   ^^^^
                                               John, Build Health
```

**Phase 2 (Shared State Approach):**
```
philhudson@Mac Sonnet CiaTc (git:main) [14:23:45] [U:P2:12s] v1.0
                                                   ^^^^^^^^^^
                                            UserPromptSubmit, Phase 2, 12 sec
```

**Stop Hook (Background Update):**
```
philhudson@Mac Sonnet CiaTc (git:main) [14:23:45] [S:P1:3s] v1.0
                                                   ^^^^^^^^^
                                             Stop hook, Phase 1, 3 sec
```

---

### Testing Strategy

1. **Manual Testing:**
   - Submit prompt, verify agents appear in status line
   - Verify agents disappear when lock released
   - Test conductor skip decision (no agents shown)
   - Test concurrent UserPromptSubmit + Stop hooks

2. **Performance Testing:**
   - Measure status line refresh time before/after
   - Monitor file I/O with `fs_usage` or `dtrace`
   - Verify <2ms overhead per refresh

3. **Edge Cases:**
   - Agent timeout (lock >600s old)
   - Agent crash (lock file remains, process gone)
   - Empty project (no agents run)
   - Status file corruption (invalid JSON)

---

### Future Enhancements

1. **Color Coding:**
   - Green: Normal execution (<60s)
   - Yellow: Warning (>60s, approaching timeout)
   - Red: Critical (>300s, near timeout)

2. **Conductor Decision Display:**
   - Show abbreviated decision: `[Full]`, `[Min]`, `[Skip]`

3. **Agent Completion Percentage:**
   - Estimated progress based on typical execution time

4. **Historical Metrics:**
   - Track average execution time per agent
   - Display deviation from baseline

---

## Band Statusline Shell Scripts

### band_statusline.sh (62 lines)
**Location:** `/Users/philhudson/Projects/CiaTc/band_statusline.sh`

**Purpose:** Real-time display of running Band agents in Claude Code's statusline

**Pattern Name:** Live Agent Activity Monitor

### Overview
The statusline script monitors the `.band_cache/locks/` directory to detect which agents are currently executing. This provides visual feedback showing which Band members are running and how long they've been executing.

### Implementation Details

**Lock File Reading:**
```bash
for lockfile in "$LOCK_DIR"/*.lock; do
    pid=$(head -1 "$lockfile" 2>/dev/null)
    timestamp=$(tail -1 "$lockfile" 2>/dev/null)

    # Check if process is still running
    if ps -p "$pid" > /dev/null 2>&1; then
        # Calculate elapsed time
```

**Agent Icons (Mnemonic Encoding):**
- 📁 john (directory/structure)
- 📖 george (narrative/documentation)
- 🔧 pete (technical/tools)
- 💡 paul (ideas/thinking)
- 🥁 ringo (rhythm/sync)
- 🧹 marie (cleanup)
- 🏗️ gilfoyle (building/health)

**Time Formatting:**
- <60 seconds: "8s"
- ≥60 seconds: "1m23s" (minutes + remainder seconds)

**Output Format:**
```
 🎸[📁john:8s 🔧pete:5s ]
   ↑   ↑                 ↑
   |   |                 |
  Icon Band Group     Agent:Time pairs
```

### Key Features

1. **Automatic Detection:**
   - Scans `.band_cache/locks/*.lock` on each statusline refresh
   - Only shows processes that are actually running (verified via `ps`)
   - Gracefully handles missing directory (non-Band projects)

2. **Performance Optimized:**
   - Lock file reading: <1ms per agent
   - Process verification: ~0.1ms per lock via `ps`
   - Typical execution: <10ms even with 7+ agents

3. **Stale Process Cleanup:**
   - Checks PID validity before showing
   - Prevents displaying agents that have crashed/exited
   - Lock file cleanup is separate task (agent_lock.py)

4. **Time Calculation:**
   - Uses system `date +%s` for current time
   - Calculates elapsed as: `now - timestamp_from_lockfile`
   - Handles fractional timestamps by truncating to seconds

### Integration Points

1. **Lock File Format (from agent_lock.py):**
   ```json
   {
       "pid": 12345,
       "timestamp": 1699459800.123456,
       "hostname": "MacBook-Pro"
   }
   ```

2. **Statusline Integration:**
   - Called by Claude Code's statusline system
   - Output piped directly to statusline
   - Refresh rate: 1-2 Hz (user configurable)

3. **Hook Lifecycle:**
   - UserPromptSubmit: Creates locks for selected agents
   - Stop hook: Background agents create/update locks
   - Lock cleanup: agent_lock.py removes locks when complete

### Error Handling

**Graceful Degradation:**
- Missing locks directory: Exit silently (not a Band project)
- Invalid lock file format: Skip agent (continue loop)
- Process verification fails: Treat as stale, skip display
- No running agents: Output nothing (empty statusline segment)

### Performance Characteristics

| Scenario | Time |
|----------|------|
| No agents running | 1-2ms (directory scan only) |
| 1 agent active | 2-3ms (lock read + ps check) |
| 3 agents active | 5-7ms (3x process checks) |
| 7 agents active | 10-15ms (all agents running) |

**Baseline:** Claude Code refreshes statusline at 1-2 Hz, so <15ms overhead is negligible.

### Testing & Verification

**Manual Test:**
```bash
# Run in CiaTc project directory
./band_statusline.sh
# Should output: " 🎸[📁john:5s 🔧pete:3s ]" if agents running
# Should output: nothing if no agents
```

**Verification Points:**
- Agents appear immediately when lock file created
- Time increments each refresh (per-second granularity)
- Agent disappears when process exits or lock deleted
- Multiple agents display with space separation
- Handles agent names: john, george, pete, paul, ringo, marie, gilfoyle

---

### demo_band_statusline.sh (53 lines)
**Location:** `/Users/philhudson/Projects/CiaTc/demo_band_statusline.sh`

**Purpose:** Educational demonstration of statusline output in different scenarios

### Overview
This demo script shows how the statusline appears in various Band execution scenarios without requiring actual agent execution.

### Scenarios Demonstrated

1. **No Agents Running**
   - Output: Normal statusline (no Band segment)
   - Shows baseline appearance

2. **Single Agent (John - 8s)**
   - Output: ` 🎸[📁john:8s ]`
   - Shows minimal scenario

3. **Stop Hook Running (3 agents)**
   - Output: ` 🎸[📁john:15s 📖george:12s 🔧pete:12s ]`
   - Shows typical post-response background work

4. **UserPromptSubmit (Paul thinking - 45s)**
   - Output: ` 🎸[💡paul:45s 🥁ringo:12s ]`
   - Shows complex analysis scenario

5. **Long-Running Cleanup (Marie)**
   - Output: ` 🎸[🧹marie:1m23s ]`
   - Shows extended execution with time formatting

6. **Full Band + Gilfoyle**
   - Output: ` 🎸[📁john:34s 📖george:28s 🔧pete:25s 🧹marie:2m15s 🏗️gilfoyle:31s ]`
   - Shows maximum load scenario

### Educational Value

- Teaches icon-to-agent mapping
- Shows time formatting conventions
- Demonstrates concurrent execution patterns
- Visualizes typical execution durations

### Usage

```bash
./demo_band_statusline.sh
# Outputs 6 scenarios with explanatory text
```

---

## References

- `band_orchestrator_main.py` - Implementation reference
- `conductor_agent.py` - Decision logic
- `smart_orchestrator.py` - Project statistics
- `agent_lock.py` - Lock implementation
- `/Users/philhudson/.claude/statusline-command.sh` - Status line script
- `band_statusline.sh` - Live agent activity monitor
- `demo_band_statusline.sh` - Statusline demonstration script

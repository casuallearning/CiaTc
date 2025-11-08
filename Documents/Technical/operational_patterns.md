# Operational Patterns - CiaTc Framework

## Overview
This document captures operational patterns including performance optimization, testing strategies, debugging techniques, and quality management approaches.

**Last Updated:** 2025-10-03

---

## Performance Optimization Patterns

### Lazy Evaluation Pattern
**Location:** `PaintingCanvas.swift`

**Pattern:** Redraw only every 3 frames instead of every frame

**Implementation:**
```swift
func animateVanGoghFrame() {
    frameCount += 1
    turbulencePhase += 0.02

    if frameCount % 3 == 0 {
        setNeedsDisplay()  // Trigger redraw
    }
}
```

**Benefits:**
- 66% reduction in draw calls
- Maintains smooth animation (still 20+ fps)
- Reduces CPU/GPU load

---

### Stride Iteration Pattern
**Location:** `PaintingCanvas.swift:renderMandelbrotOverlay()`

**Pattern:** Skip pixels to reduce computation

**Implementation:**
```swift
for x in stride(from: 0, to: Int(width), by: 4) {
    for y in stride(from: 0, to: Int(height), by: 4) {
        // Compute Mandelbrot point
    }
}
```

**Benefits:**
- 16x reduction in Mandelbrot calculations (4x4 grid)
- Acceptable visual quality (overlay is low alpha anyway)
- ~60% CPU time saved

---

### Buffer Limit Pattern
**Location:** `WaggleDanceCompiler.swift`, `PaintingCanvas.swift`, `FractalMemoryManager.swift`

**Pattern:** Cap collection sizes to prevent unbounded growth

**Limits:**
- Movement vectors: 1000 (WaggleDanceCompiler)
- Brushstrokes: 1000 (PaintingCanvas)
- Memory regions: 1000 (FractalMemoryManager)

**Implementation:**
- FIFO eviction when limit reached
- Maintains most recent data
- Prevents memory leaks

---

### Response Truncation Pattern
**Location:** `janitors_orchestrator_main.py`

**Pattern:** Limit analysis input to prevent token overflow

**Implementation:**
```python
if len(opus_response) > 3000:
    opus_response = opus_response[:3000]
```

**Benefits:**
- Prevents timeout on long responses
- Reduces token cost
- Focuses critique on beginning (often most important)

**Threshold:** 3000 characters

---

## Testing & Debugging Patterns

### Stderr Logging Pattern
**Location:** Throughout codebase

**Pattern:** Use stderr for debug/timing output to avoid interfering with stdout

**Implementation:**
```python
print(f"⏱️  {func.__name__}: {elapsed:.2f}s", file=sys.stderr)
```

**Benefits:**
- Hook JSON on stdout remains valid
- Timing/debug info visible in terminal
- Easy filtering (redirect stderr separately)

---

### Exception Isolation Pattern
**Location:** `band_orchestrator_main.py:as_completed()` loops

**Pattern:** Per-future exception handling to preserve partial results

**Implementation:**
```python
for future in as_completed([john_future, build_health_future]):
    try:
        result = future.result()
        # Process result
    except Exception as e:
        print(f"Error in agent: {e}", file=sys.stderr)
        # Continue with other agents
```

**Benefits:**
- One agent failure doesn't crash orchestrator
- Partial results still available
- Errors logged for debugging

---

### Test Isolation Pattern
**Location:** `test_band_debug.py`

**Pattern:** Multi-level testing with controlled environments

**Implementation:**
```python
# Test 1: Claude CLI availability
result = subprocess.run(
    ['/usr/local/bin/claude', '--model', 'sonnet[1m]', '--print', 'Say "Claude works!"'],
    env=env_with_recursion_guard,
    timeout=30
)

# Test 2: Recursion guard validation
result = subprocess.run(
    ['python3', 'band_orchestrator_main.py'],
    input=json.dumps(event),
    env={'CIATC_SUBPROCESS': 'true'},  # Should pass through
    timeout=5
)

# Test 3: Actual execution
result = subprocess.run(
    ['python3', 'band_orchestrator_main.py'],
    input=json.dumps(event),
    env={},  # No recursion guard
    timeout=5
)
```

**Purpose:** Progressive validation of system components

**Test Levels:**
1. External dependencies (Claude CLI)
2. Recursion guard functionality
3. Full system execution

**Benefits:**
- Isolates failure points
- Validates environment setup
- Tests guard mechanisms
- Short timeouts prevent hangs

---

### Performance Profiling Pattern
**Location:** `test_band_performance.py`

**Pattern:** Import and time individual functions with result aggregation

**Implementation:**
```python
# Import band functions directly
from band_orchestrator_main import run_john, run_george, run_pete, ...

def test_agent(name, func, *args):
    start = time.time()
    result = func(*args)
    elapsed = time.time() - start

    if elapsed > 30:
        print(f"⚠️  WARNING: {name} took >{elapsed:.0f}s - needs optimization!")

    return {'name': name, 'time': elapsed, 'output_length': len(result)}

# Run all agents sequentially
results = []
results.append(test_agent("John", run_john, cwd, transcript_path))
results.append(test_agent("George", run_george, user_prompt, transcript_path, cwd))
# ...

# Calculate parallel time estimate
parallel_estimate = max([r['time'] for r in phase1]) + sum([r['time'] for r in phase2])
```

**Purpose:** Identify performance bottlenecks and estimate parallel speedup

**Metrics:**
- Individual execution times
- Output sizes
- Success/failure status
- Sequential vs parallel projections
- Bottleneck identification (>30s threshold)

**Output:**
- Console summary with timing breakdown
- JSON results file for analysis
- Sorted results (slowest first)
- Warning flags for slow agents

**Benefits:**
- Direct function testing (no hook overhead)
- Parallel performance estimation
- Bottleneck identification
- Historical tracking via JSON output

---

## Hook Orchestration Patterns

### Stop Hook Background Processing Pattern
**Location:** `band_orchestrator_stop.py` (lines 219-314)

**Pattern:** Background documentation and maintenance after Claude responds

**Implementation (Updated 2025-11-08):**
```python
if event.get('hook_event_name') == 'Stop':
    # BACKGROUND MAINTENANCE (All Parallel with Locks)
    agents_to_run = ["john", "george", "pete", "marie"]
    timeout = 600  # 10 minutes non-blocking

    # Clean up stale locks
    cleanup_stale_locks(max_age_seconds=600)

    with ThreadPoolExecutor(max_workers=len(agents_to_run) + 1) as executor:
        # Gilfoyle (build health)
        futures['gilfoyle'] = executor.submit(run_gilfoyle_locked, cwd)

        # Documentation agents (with agent locks)
        futures['john'] = executor.submit(run_john_locked, cwd, transcript_path, timeout)
        futures['george'] = executor.submit(run_george_locked, user_prompt, transcript_path, cwd, timeout)
        futures['pete'] = executor.submit(run_pete_locked, user_prompt, cwd, timeout)
        futures['marie'] = executor.submit(run_marie_locked, cwd, timeout)

        # Wait for completion (non-blocking from user perspective)
        for agent_name, future in futures.items():
            result = future.result(timeout=timeout + 5)
```

**Purpose:** Update documentation and maintain project health asynchronously after response

**Characteristics:**
- **Single-phase execution** (all 5 agents parallel, no dependencies)
- **Agent lock system** prevents duplicate concurrent runs
- **Non-blocking** from user perspective (runs in background)
- **Graceful degradation** when git not available
- Pass-through event JSON (no modification to user interaction)
- No Paul/Ringo (synthesis agents not needed for maintenance)

**Agents Running in Background:**
1. **John** - Directory structure and file index updates
2. **George** - Narrative theme tracking
3. **Pete** - Technical documentation extraction
4. **Marie** - Active project maintenance (git, cleanup, organization)
5. **Gilfoyle** - Build health and dependency monitoring

**Agent Lock Pattern:**
- Lock file: `.band_cache/locks/{agent_name}.lock`
- Behavior: Skip if already running (graceful)
- Cleanup: Stale locks removed after 600 seconds
- Purpose: Prevent race conditions from rapid user prompts

**Git Integration:**
- **Status:** NOT configured for this project (as of 2025-11-08)
- **Impact:** Gilfoyle change detection disabled
- **Graceful:** Returns empty change list instead of failing
- **Recommendation:** `git init` to enable change tracking

**Benefits:**
- Documentation stays current without user-visible delay
- Project maintenance happens automatically
- Lock system prevents duplicate work
- 4-tier orchestration: pre-analysis → response → post-response → background-maintenance

**Risks:**
- No user feedback on documentation updates (stderr only)
- Potential race conditions if user submits new prompt during background run
  - **Mitigated by:** Agent lock system skips duplicate runs
- Background process resource consumption (5 concurrent Claude CLI processes)
- 600-second timeout may exceed rapid iteration pace
  - **Mitigated by:** Lock cleanup prevents permanent blocking

**Performance Characteristics:**
- Typical runtime: 15-20 seconds (without Paul/Ringo)
- Peak runtime: Up to 600 seconds (10 minutes with full timeouts)
- Resource usage: 5 concurrent Python + Claude CLI subprocesses
- Lock file I/O: ~10 operations per invocation

---

### Settings Management Pattern
**Location:** `activate_ciatc_final.sh`, `deactivate_ciatc_final.sh`

**Pattern:** Configuration backup and restore with mode selection

**Activation Implementation:**
```bash
# Backup current settings
cp ~/.claude/settings.local.json ~/.claude/settings.backup.$(date +%s).json

# Create new settings based on mode
case $MODE in
    "band") HOOKS='...' ;;
    "janitors") HOOKS='...' ;;
    "full") HOOKS='...' ;;
esac

cat > ~/.claude/settings.local.json << EOF
{
  "hooks": { $HOOKS },
  "env": { ... }
}
EOF
```

**Deactivation Implementation:**
```bash
# Find most recent backup
LATEST_BACKUP=$(ls -t ~/.claude/settings.backup.*.json | head -1)

# Restore or create minimal
if [ -f "$LATEST_BACKUP" ]; then
    cp "$LATEST_BACKUP" ~/.claude/settings.local.json
else
    # Create minimal settings
fi
```

**Purpose:** Safe framework activation/deactivation with rollback capability

**Features:**
- Timestamped backups (`settings.backup.<timestamp>.json`)
- Mode selection (band, janitors, full)
- Graceful degradation (minimal settings if no backup)
- Environment variable preservation

**Benefits:**
- No manual JSON editing required
- Multiple backup history
- Easy rollback
- Safe experimentation

---

## Technical Debt & Anti-Patterns

### Hard-coded Paths Anti-Pattern
**Locations:** Throughout codebase

**Examples:**
- `/usr/local/bin/claude`
- `/Users/philhudson/Projects/CiaTc/prompts/`
- `/tmp/janitor_critique.md`

**Impact:** Zero portability

**Mitigation:**
- Environment variables
- Path discovery (`which claude`)
- Platform-agnostic temp files

---

### Magic Numbers Anti-Pattern
**Locations:** Multiple files

**Examples:**
- 0.3, 0.5, 0.8 thresholds (no explanation)
- 1000 buffer limits
- 5000 char truncation
- 600s timeouts

**Impact:** Hard to tune, unclear rationale

**Mitigation:**
- Named constants with comments
- Configuration files
- Self-documenting names

---

### Duplicate Code Anti-Pattern
**Location:** `build_health_agent.py`

**Issue:** Tree-sitter parsing logic duplicated across Python/Swift/JS parsers

**Impact:**
- Maintenance burden
- Inconsistent behavior risk

**Mitigation:**
- Generic tree-sitter traversal function
- Language-specific configuration objects

---

### Missing Error Recovery
**Locations:** Subprocess calls

**Issue:** Most failures just log errors, no retry or fallback

**Impact:**
- Fragile system
- Transient failures become permanent

**Mitigation:**
- Retry logic with exponential backoff
- Graceful degradation
- Circuit breaker pattern

---

## Emerging Patterns (Paul's Laboratory)

### Biomimetic Computing Pattern
**Concept:** Derive computational primitives from biological phenomena

**Examples:**
- Waggle Dance → Code compilation
- Protein folding → Response annealing
- Fungal networks → Orchestration
- Cardiac conduction → Event propagation

**Status:** Experimental, conceptual phase

---

### Artistic Computation Pattern
**Concept:** Apply artistic principles to code generation/optimization

**Examples:**
- Van Gogh fractals → Code visualization
- Golden ratio → Aesthetic optimization
- Brushstrokes → Operation types
- Color palettes → Code categories

**Status:** Implemented in Van Gogh compiler suite

---

### iOS App Bundle Generation Pattern
**Location:** `create_ios_app.swift`

**Pattern:** Programmatic creation of iOS app bundle structure

**Implementation:**
```swift
let appPath = "/path/to/App.app"
let fileManager = FileManager.default

// Create bundle directory
try! fileManager.createDirectory(atPath: appPath, withIntermediateDirectories: true)

// Create Info.plist
let infoPlist = """
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "..." "...">
<plist version="1.0">
<dict>
    <key>CFBundleIdentifier</key>
    <string>\(bundleId)</string>
    ...
</dict>
</plist>
"""
try! infoPlist.write(toFile: "\(appPath)/Info.plist", ...)

// Create executable
try! fileManager.setAttributes([.posixPermissions: 0o755], ofItemAtPath: "\(appPath)/Executable")
```

**Purpose:** Generate app bundles programmatically for demonstration/testing

**Generated Structure:**
- `.app/` directory
- `Info.plist` with bundle metadata
- Executable (placeholder shell script)
- Proper file permissions (0o755 for executable)

**Bundle Configuration:**
- Display name, bundle ID, version
- Main storyboard reference
- Supported orientations
- iOS requirements flag

**Limitations:**
- No actual binary compilation
- Placeholder executable (demo only)
- No code signing
- No asset catalog generation

**Use Case:** Rapid prototyping of iOS app concepts without Xcode

---

---

## Smart Orchestration Runtime Patterns (November 2025)

### Conductor Decision Caching Pattern
**Location:** `band_orchestrator_main.py`, `conductor_agent.py`

**Pattern:** Cache conductor decisions to avoid repeated 10-second evaluations

**Implementation:**
```python
conductor_cache_key = hash(user_prompt + project_size)
if conductor_cache_key in cache:
    conductor_result = cache[conductor_cache_key]
else:
    conductor_result = run_conductor(user_prompt, project_stats)
    cache[conductor_cache_key] = conductor_result
```

**Benefits:**
- Skip repeated 10-second conductor decisions
- Identical prompts get instant decisions
- Still recalculates if project changes (SmartOrchestrator detects)

**Tradeoff:**
- Memory overhead: ~1KB per cached decision
- Potential staleness if project changes between decisions

---

### Incremental File Hashing Pattern
**Location:** `smart_orchestrator.py`

**Pattern:** Only hash files that have been modified since last run

**Implementation:**
```python
cached_hashes = load_json('.band_cache/file_hashes.json')
changed_files = []

for filepath in project_files:
    if filepath not in cached_hashes:
        # New file
        changed_files.append(filepath)
        current_hashes[filepath] = compute_hash(filepath)
    elif mtime(filepath) > cache_mtime:
        # Modified file
        changed_files.append(filepath)
        current_hashes[filepath] = compute_hash(filepath)
    else:
        # Unchanged file
        current_hashes[filepath] = cached_hashes[filepath]

# Only compute hashes for changed files
```

**Performance Impact:**
- First run: 10-30 seconds (hash all files)
- Typical run: 2-5 seconds (only hash changed files)
- No changes: 100-200ms (cache hit, no hashing)

**Trade-off:**
- Relies on mtime (can be spoofed)
- Large file detection via size heuristic (not foolproof)

---

### Lock-Based Deduplication Pattern
**Location:** `agent_lock.py`, `band_orchestrator_main.py`

**Pattern:** Use locks to prevent duplicate agent execution during concurrent hook invocations

**Scenario:**
```
T0: User types prompt A → Hook 1 starts
T1: User types prompt B → Hook 2 starts (Hook 1 still running)
T2: Hook 1 calls run_john() → Acquires john.lock
T3: Hook 2 calls run_john() → Waits for john.lock (blocking)
T4: Hook 1 finishes john() → Releases john.lock
T5: Hook 2 acquires john.lock → Runs john()
```

**Implementation:**
```python
with AgentLock("john") as lock:
    if lock:
        # Lock acquired
        output = run_john(...)
    else:
        # Lock not acquired (agent already running)
        output = cached_result_if_available or skip
```

**Benefits:**
- Prevents duplicate agent execution
- Reduces resource contention
- Maintains consistency across concurrent hooks

**Failure Mode:**
- If lock held >10 minutes: Automatically cleaned up
- If lock acquisition fails: Log warning, skip agent

---

### Phase-Based Dependency Resolution
**Location:** `band_orchestrator_main.py:219-307`

**Pattern:** Execute dependent agents in strict phases to ensure data is ready

**Phase Execution:**
```
Phase 1 (Foundation): John + Build Health (parallel)
    Produces: file_index.md, dependency_graph.json
    Time: ~12s

Phase 1 → Phase 2 (Blocking)
    Ensures George and Pete can read John's file_index.md

Phase 2 (Context): George + Pete (parallel, depends on Phase 1)
    Produces: Narratives/*, Technical/*
    Time: ~8s

Phase 2 → Phase 3 (Blocking)
    Ensures Paul and Ringo can read all context docs

Phase 3 (Synthesis): Paul + Ringo (parallel, depends on Phases 1-2)
    Produces: Creative ideas, Unified context
    Time: ~4s
```

**Exception Handling per Phase:**
```python
try:
    # Phase 1
    john_result = executor.submit(run_john, ...).result(timeout=60)
except Exception as e:
    # Log but continue - john failure shouldn't block phase 2
    john_result = default_or_cached
    log_warning(f"John failed: {e}")

# Proceed to Phase 2 regardless of Phase 1 issues
```

**Benefits:**
- Clean data dependencies
- Fault tolerance at phase level
- Predictable execution order

---

### Adaptive Timeout Adjustment Pattern
**Location:** `conductor_agent.py`, `smart_orchestrator.py`

**Pattern:** Scale timeouts based on project scope and complexity

**Timeout Progression:**
```
SmartOrchestrator calculates base:
  small project (<100 files)       → 60s
  medium project (100-500 files)   → 120s
  large project (>500 files)       → 180s

Adds change bonus:
  per_file_bonus = min(changed_file_count * 10, 60s)
  final_timeout = base + per_file_bonus

Conductor can override:
  For complex tasks → extend to 300-600s
  For trivial tasks → reduce to 10s
```

**Application Example:**
```python
# SmartOrchestrator
timeout = get_adaptive_timeout(project_size, changed_files)
# Result: 120s for medium project with 1 change

# Conductor review
if task_complexity == "very_high":
    timeout = 300  # Override to 5 minutes

# Band orchestrator uses final timeout
result = run_john(..., timeout=timeout)
```

**Benefits:**
- Prevents unnecessary waits on small projects
- Allows thorough analysis on large projects
- Respects complex task requirements

---

### Fallback Execution Pattern
**Location:** Throughout orchestration system

**Pattern:** Gracefully degrade when smart optimizations fail

**Fallback Chain:**
```
Try: Use conductor decision
Fallback 1: Conductor timeout → Use SmartOrchestrator defaults
Fallback 2: SmartOrchestrator timeout → Full project scan
Fallback 3: Lock contention → Skip agent gracefully
Fallback 4: Any exception → Continue with available data
```

**Example - Conductor Fallback:**
```python
try:
    conductor_result = run_conductor(prompt, stats)
    should_run = conductor_result['should_run']
except TimeoutError:
    # Conductor took too long - fall back to defaults
    should_run = smart_orchestrator.suggest_execution(prompt)
except Exception:
    # Conductor failed - fall back to always-run
    should_run = True
```

**Benefits:**
- System always makes progress
- No hard failures that block user
- Transparent degradation

---

### Performance Monitoring Pattern
**Location:** Throughout codebase (stderr logging)

**Pattern:** Log timing information for performance analysis

**Output:**
```
⏱️  Conductor: 10.23s (semantic decision)
⏱️  John: 12.45s (file structure analysis)
⏱️  George: 7.89s (narrative context)
⏱️  Pete: 8.12s (technical documentation)
⏱️  Paul: 6.34s (creative ideas)
⏱️  Ringo: 5.01s (context synthesis)
─────────────────────────────
Total: 24.23s (3-phase parallel execution)
```

**Logging Points:**
```python
# Before and after each agent
start = time.time()
result = run_john(...)
elapsed = time.time() - start
sys.stderr.write(f"⏱️  John: {elapsed:.2f}s\n")
```

**Analysis Use Cases:**
1. Identify slow agents (which need optimization)
2. Verify phase boundaries (dependency correctness)
3. Confirm cache efficiency (compare cold vs warm runs)
4. Debug timeout issues (which agent exceeded limit)

---

### Cache Invalidation Pattern
**Location:** `.band_cache/`, `smart_orchestrator.py`

**Pattern:** Automatic detection of stale cache data

**Invalidation Triggers:**
```
File hash changed    → Invalidate project stats
Project size changed → Recalculate timeouts
Lock file stale      → Clean up automatically (10m timeout)
```

**Implementation:**
```python
cache_age = time.time() - cache['last_update']
file_count_now = count_project_files()

if cache_age > 3600:  # 1 hour
    invalidate_cache()  # Full rescan
elif file_count_now != cache['file_count']:
    invalidate_cache()  # Project structure changed
else:
    use_cached_data()  # Cache still valid
```

**Benefits:**
- Prevents stale decision-making
- Automatic cleanup without manual intervention
- 1-hour TTL balances freshness vs performance

---

## Notes
- This is a living document; update as patterns emerge or evolve
- Cross-reference with `architectural_patterns.md` for system design patterns
- Cross-reference with `technical_patterns.md` for implementation details
- Cross-reference with `implementation_log.md` for historical context
- See `dependencies.md` for technology stack details

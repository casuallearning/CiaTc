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

## References

- `band_orchestrator_main.py` - Implementation reference
- `conductor_agent.py` - Decision logic
- `smart_orchestrator.py` - Project statistics
- `agent_lock.py` - Lock implementation

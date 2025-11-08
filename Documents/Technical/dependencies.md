# Technical Dependencies

**Last Updated:** November 8, 2025

---

## Quick Reference

### New in November 2025
- **Conductor Agent:** Intelligent agent selection (haiku model, 10s)
- **Smart Orchestrator:** Project statistics & incremental caching
- **Agent Lock System:** File-based process coordination

### Critical External Dependencies
1. Claude CLI: `/usr/local/bin/claude` (REQUIRED)
2. Python 3.8+ (for concurrent.futures, pathlib)
3. tree_sitter_languages: `pip install tree_sitter_languages`
4. Tree-sitter: Included with tree_sitter_languages

---

## Core Python Components

### Conductor Agent (conductor_agent.py)
**Purpose:** Intelligent decision layer that analyzes prompts and selects which agents to activate

**Python Standard Library:**
- `json`: Parsing conductor decision output
- `sys`: stdin/stdout/stderr handling
- `subprocess`: Claude CLI execution for decision-making
- `os`: Environment management
- `pathlib.Path`: File operations

**External Dependencies:**
- `/usr/local/bin/claude` CLI (required)
- Model: `haiku` (lightweight, fast decisions)
- Timeout: 10 seconds per decision
- Prompt file: `prompts/conductor.md`
- Smart Orchestrator: `smart_orchestrator.py` (for project context)

**Decision Output Variables:**
- `agents_to_run`: List of agent names (e.g., ["john", "george", "pete"])
- `timeout`: Suggested timeout in seconds (60-900)
- `priority`: Execution priority ("low", "medium", "high")
- `skip_band`: Boolean to skip all agents (trivial questions)

**Performance:**
- Decision time: ~10 seconds
- Overhead: Minimal compared to benefit
- Caching: Conductor decisions cached in `.band_cache/`

---

### Smart Orchestrator (smart_orchestrator.py)
**Purpose:** Project intelligence gathering for Conductor decision-making

**Python Standard Library:**
- `hashlib`: MD5 file hashing for change detection
- `os`: File system traversal
- `json`: Cache persistence
- `pathlib.Path`: Cross-platform path handling
- `time`: File modification time (mtime) for large files

**External Dependencies:**
- Git: `git status --porcelain` (optional, graceful fallback)
- Cache files: `.band_cache/file_hashes.json`, `.band_cache/orchestrator_cache.json`
- Lock mechanism: `agent_lock.py` (coordinate concurrent access)

**Capabilities:**
1. **File Change Detection:**
   - Small files (<1MB): MD5 hashing
   - Large files (>1MB): Modification time (mtime)
   - Incremental: Only hash changed files
   - Cache: `.band_cache/file_hashes.json`

2. **Project Analysis:**
   - File count classification: small/medium/large
   - Lines of code counting
   - Changed file detection
   - Dependency graph analysis (via build_health_agent)

3. **Adaptive Timeout Calculation:**
   - Base: From project size (60-180s)
   - Bonus: +10s per changed file (capped at 60s)
   - Conductor: May override upward (especially for Paul)

4. **Project Intelligence Output:**
   ```python
   {
       'file_count': int,
       'total_lines': int,
       'project_size': 'small'|'medium'|'large',
       'changed_files': [list],
       'change_count': int,
       'suggested_timeout': int (seconds),
       'file_hashes': {path: hash},
       'cached_hashes': {path: hash}
   }
   ```

**Performance:**
- First run: Full project scan (10-30s for large projects)
- Subsequent runs: Incremental (2-5s, only changed files)
- Caching: Dramatically reduces overhead on large projects

---

### Agent Lock System (agent_lock.py)
**Purpose:** File-based process locking for preventing duplicate agent execution

**Python Standard Library:**
- `fcntl`: Cross-platform file locking (`fcntl.flock()`)
- `json`: Lock metadata storage
- `time`: Timestamp recording in lock files
- `pathlib.Path`: Lock file path handling
- `os`: Lock directory management

**External Dependencies:**
- None (fcntl is POSIX-standard, cross-platform)

**Lock Storage:**
- Location: `.band_cache/locks/` directory
- Format: One lock file per agent (e.g., `john.lock`, `george.lock`)
- Content: JSON with `pid`, `timestamp`, `hostname`

**Capabilities:**
1. **Exclusive Locking:** Only one process can run agent at a time
2. **Blocking & Non-blocking:** `acquire(blocking=True/False)`
3. **Stale Lock Cleanup:** Automatic removal of >10 minute old locks
4. **Context Manager:** `with AgentLock("john"): ...` syntax
5. **PID Tracking:** Identifies which process holds lock

**Methods:**
- `acquire(blocking=True)`: Get exclusive lock
- `release()`: Release lock and delete lock file
- `is_locked()`: Check if agent currently locked
- `cleanup_stale_locks(timeout=600)`: Remove old locks

**Configuration:**
- Timeout for stale locks: 600 seconds (10 minutes)
- Lock filename pattern: `{agent_name}.lock`
- Blocking default: True (wait for lock)

**Performance:**
- Lock acquisition: ~50ms
- Stale cleanup: ~100ms per lock file
- No I/O overhead when locked (read lock metadata only)

**Integration with Band Orchestrator:**
```python
from agent_lock import AgentLock

with AgentLock("john") as lock:
    if lock:
        run_john()  # Only runs if lock acquired
```

**Failure Modes & Recovery:**
- **Lock held by crashed process:** Cleaned up after 10 minutes
- **Lock acquisition timeout:** Non-blocking mode returns None
- **Permission denied:** Graceful error handling (logs warning)

---

### Band Orchestrator (band_orchestrator_main.py)
**Purpose:** Multi-agent orchestration system with 5 specialists + build health monitor

**Python Standard Library:**
- `json`: Event parsing and hook data processing
- `sys`: stdin/stdout/stderr management, argument handling
- `subprocess`: Claude CLI subprocess execution
- `os`: Environment variables (CIATC_SUBPROCESS guard)
- `pathlib.Path`: File path operations
- `time`: Performance timing via `time.time()`
- `functools.wraps`: Decorator metadata preservation
- `concurrent.futures.ThreadPoolExecutor`: 3-phase parallel execution

**External Dependencies:**
- `/usr/local/bin/claude` CLI (required)
- Model: `sonnet` alias (600s timeout per agent, configurable)
- Prompt files: `prompts/{john,george,pete,paul,ringo}.md`
- Build health script: `build_health_agent.py`
- Conductor: `conductor_agent.py` (decides which agents to run)
- Smart Orchestrator: `smart_orchestrator.py` (provides context)

**Environment Variables:**
- `CIATC_SUBPROCESS=true`: Recursion prevention guard (subprocess-only)

**Integration with Conductor:**
- Receives agent selection from Conductor
- Uses Conductor-suggested timeout (or defaults to 600s)
- Skips band execution if Conductor returns "skip"

---

### Janitors Orchestrator (janitors_orchestrator_main.py)
**Purpose:** Post-response quality review with 3 critics (Marie, Descartes, Feynman)

**Python Standard Library:**
- `json`: Transcript parsing
- `sys`: stdin/stdout handling
- `subprocess`: Claude CLI execution
- `os`: Environment and file operations
- `pathlib.Path`: Transcript file access

**External Dependencies:**
- `/usr/local/bin/claude` CLI (required)
- Model: `sonnet[1m]` alias (30s timeout per critic)
- Prompt files: `prompts/{marie,descartes,feynman}.md`
- Output: `/tmp/janitor_critique.md`

**Environment Variables:**
- `CIATC_SUBPROCESS=true`: Recursion prevention guard

---

### Build Health Agent (build_health_agent.py)
**Purpose:** Language-agnostic build health monitoring with tree-sitter AST parsing

**Python Standard Library:**
- `os`: File system operations
- `json`: Dependency graph persistence
- `subprocess`: Git command execution
- `pathlib.Path`: File path handling
- `collections.defaultdict`: Dependency tracking

**External Dependencies:**
- `tree_sitter_languages` package (pip install):
  - `get_parser(language)`: Creates language-specific parsers
  - `get_language(language)`: Language grammars
- Git repository (optional, graceful fallback if absent)

**Supported Languages (Tree-sitter):**
- Python, Swift, JavaScript, TypeScript, Go, Rust, Java, C, C++, Ruby, PHP

**Data Persistence:**
- `Documents/Technical/dependency_graph.json`: Cached dependency data
- Stores function signatures, imports, calls, severity levels

**Fallback Mechanisms:**
- Regex-based parsing when tree-sitter unavailable
- Non-git repos supported (no changes detected)

---

### Prompt Loader (prompt_loader.py)
**Purpose:** Centralized prompt template loading with context substitution

**Python Standard Library:**
- `pathlib.Path`: File I/O

**Dependencies:**
- Markdown prompt files in `/Users/philhudson/Projects/CiaTc/prompts/`
- Template format: `{placeholder}` syntax

**Features:**
- 5000 char value truncation
- Regex-based unfilled placeholder detection
- Graceful None handling

---

### Bootstrap Band (bootstrap_band.py)
**Purpose:** Standalone initialization script bypassing hook system

**Python Standard Library:**
- `subprocess`: Claude CLI execution
- `sys`, `os`: Environment management
- `pathlib.Path`: File operations

**External Dependencies:**
- `/usr/local/bin/claude` CLI
- Model: `sonnet[1m]` (120s timeout)
- All prompt files
- Test data (hard-coded)

---

### Band Orchestrator Stop Hook (band_orchestrator_stop.py)
**Purpose:** Background documentation update hook (runs after response)

**Python Standard Library:**
- `json`: Event parsing
- `sys`: stdin/stdout handling
- `subprocess`: Claude CLI and build health execution
- `os`: Environment variables
- `pathlib.Path`: File path operations
- `time`: Performance timing
- `functools.wraps`: Decorator metadata preservation
- `concurrent.futures.ThreadPoolExecutor`: Parallel background execution (5 agents)

**External Dependencies:**
- `/usr/local/bin/claude` CLI (required)
- Model: `haiku` (600s timeout per agent)
- Prompt files: `prompts/{john,george,pete,marie_active}.md`
- Gilfoyle agent: `gilfoyle_agent.py`
- Agent lock system: `agent_lock.py`
- Git CLI (optional): For change detection in build health monitoring

**Environment Variables:**
- `CIATC_SUBPROCESS=true`: Recursion prevention guard

**Background Agents (All Parallel):**
1. John (Directory mapper) - 600s timeout
2. George (Narrative manager) - 600s timeout
3. Pete (Technical documentation) - 600s timeout
4. Marie (Project maintenance) - 600s timeout
5. Gilfoyle (Build health monitoring) - 30s timeout

**Agent Lock System:**
- Lock files: `.band_cache/locks/{agent_name}.lock`
- Prevents duplicate concurrent agent runs
- Stale lock cleanup: 600 seconds
- Skip behavior: If locked, agent skips gracefully

**Hook Event:** 'Stop' (AFTER Claude responds - non-blocking)

**Git Repository Status (as of 2025-11-08):**
- ❌ **NOT CONFIGURED** for `/Users/philhudson/Projects/CiaTc`
- No `.git` directory exists
- Gilfoyle agent gracefully degrades (no change detection)
- Recommendation: `git init` to enable change tracking

---

## Swift/iOS Components

### WaggleDanceCompiler.swift
**Purpose:** Bio-computational compiler translating bee waggle dance to executable code

**Frameworks:**
- `Foundation`: Core types (Data, Bundle, etc.)
- `simd`: Vector mathematics (simd_double2, simd_double3x3)
- `Accelerate`: Performance primitives (imported, minimal use)

**Algorithms:**
- von Frisch's formula for distance calculation
- Zero-crossing frequency estimation
- SIMD matrix transformations
- Figure-8 pattern recognition
- Fibonacci/factorial/prime computation

**Technical Parameters:**
- Sliding window: 20 vectors
- Movement buffer: 1000 vectors
- Frequency thresholds: 0-50, 50-100, 100-200, 200-300, 300+ Hz
- Pattern detection: 30% high-frequency threshold

---

### Van Gogh Fractal Compiler Suite

#### VanGoghCompiler.swift
**Purpose:** Artistic code compiler with fractal mathematics

**Frameworks:**
- `Foundation`: Core types
- `CoreImage`: Image processing (imported, unused)
- `Accelerate`: Performance (imported, unused)
- `Metal`: GPU acceleration detection

**Mathematical Constants:**
- Golden ratio: 1.618033988749
- Mandelbrot bounds: real [-2, +1], imaginary [-1.5, +1.5]
- Canvas: 400x300, center (200, 150)

**Compilation Pipeline:**
1. Code structure analysis (pattern detection)
2. Brushstroke transformation (artistic mapping)
3. Fractal instruction generation (coordinate mapping)
4. Golden ratio optimization
5. PaintedCode assembly

---

#### VanGoghCompilerViewController.swift
**Purpose:** iOS UI for fractal compiler

**Frameworks:**
- `UIKit`: UI components
- `Metal`, `MetalKit`: GPU (imported, unused)

**UI Parameters:**
- Canvas: 400x400 at y=100
- Code view: Courier 12pt, yellow on dark blue
- Button: 50pt height, 25pt corner radius
- 100 brushstrokes generated on startup

---

#### PaintingCanvas.swift
**Purpose:** Animated Van Gogh-style fractal canvas

**Frameworks:**
- `UIKit`: Graphics
- `QuartzCore`: CADisplayLink, animations
- `Accelerate`: Performance (imported, unused)

**Technical Specifications:**
- CVPixelBuffer: 32BGRA format
- Max brushstrokes: 1000 (performance limit)
- Redraw: Every 3 frames (lazy optimization)
- Mandelbrot iterations: 50 max
- Mandelbrot stride: 4px intervals
- Brushstroke thickness: `complexity * 8 + 2`
- Turbulence amplitude: `turbulence * 20`

**Animation:**
- CADisplayLink at display refresh rate
- Turbulence via `sin/cos` with frame-based phase
- Overlay blend mode with alpha 0.1

---

#### FractalMemoryManager.swift
**Purpose:** Mandelbrot-based memory manager with artistic GC

**Frameworks:**
- `Foundation`: Core types, Timer
- `Accelerate`: Performance (imported, unused)
- `simd`: Vector types (simd_int2)

**Memory Architecture:**
- Canvas: 1024x1024 2D grid
- Max regions: 1000
- Address space: Mandelbrot coordinates [-2, +2]
- Real malloc/free with spatial tracking

**Garbage Collection:**
- Timer: 5-second cycles
- Base age: 30 seconds
- Complexity multiplier: 1 + complexity * 2 (up to 3x life extension)
- Fade threshold: 0.8
- Age-based collection with visual fading

**Metrics:**
- Golden ratio beauty score (1.618)
- 8 directional complexity levels (0.2 to 1.0)
- Fragmentation ratio tracking

---

#### iOS App Template (Quantum Productivity)

**Quantum_ProductivityApp.swift:**
- `SwiftUI`: App framework
- `SwiftData`: Persistence with ModelContainer

**ContentView.swift:**
- `SwiftUI`: NavigationSplitView UI
- `SwiftData`: @Query for Item retrieval
- Standard CRUD operations

---

## Hook System Dependencies

### Band Orchestrator Hook (UserPromptSubmit)
**Location:** `/Users/philhudson/Projects/CiaTc/band_orchestrator_main.py`

**Dependencies:**
- Python 3
- Python Standard Library (see Band Orchestrator section above)
- `/usr/local/bin/claude` CLI tool
- Node.js (in PATH, required by discipline-reminder hook)

**Environment Variables:**
- `CIATC_SUBPROCESS`: Recursion guard flag
  - Set to 'true' in subprocess environment to prevent infinite recursion
  - **CRITICAL:** Must NOT be set in parent shell environment
  - **Issue (2025-10-01):** Variable leaked into parent shell, causing hook bypass
  - **Fixed (2025-10-01):** Intelligent guard detects hook JSON and auto-unsets variable

**External Script Dependencies:**
- `/Users/philhudson/Projects/CiaTc/build_health_agent.py`
- Prompt files in `/Users/philhudson/Projects/CiaTc/prompts/`:
  - `john.md` (directory mapper)
  - `george.md` (narrative manager)
  - `pete.md` (technical documentation)
  - `paul.md` (wild ideas)
  - `ringo.md` (context synthesizer)

---

### Discipline Reminder Hook (UserPromptSubmit)
**Location:** `/Users/philhudson/.claude/universal-hooks/discipline-reminder.js`

**Dependencies:**
- Node.js runtime

---

## Hook Configuration
**File:** `~/.claude/settings.json`

**Hook Execution Order:**
1. Discipline reminder (runs first)
2. Band orchestrator (runs second)

Both hooks are triggered on `UserPromptSubmit` events.

---

## Git Dependencies

### Build Health Monitoring
- Git CLI commands: `git status --porcelain`
- Optional (graceful fallback if not git repo)

---

## File System Dependencies

### Generated/Maintained Files
- `Documents/directory_map.md` (John)
- `Documents/file_index.md` (John)
- `Documents/Narratives/*.md` (George)
- `Documents/Technical/*.md` (Pete)
- `Documents/Technical/dependency_graph.json` (Build Health)
- `/tmp/janitor_critique.md` (Janitors)

### Configuration Files
- `~/.claude/settings.json`: Hook configuration
- `.claude/settings.local.json`: Project-specific settings

---

## Testing & Performance Dependencies

### Timing Decorator Pattern
**Status:** IMPLEMENTED in `band_orchestrator_main.py`

**Dependencies:**
- `time`: Wall-clock timing (`time.time()`)
- `functools.wraps`: Metadata preservation
- `sys.stderr`: Output stream

**Metrics:**
- Function execution time (wall-clock)
- Output format: `⏱️  {func_name}: {elapsed:.2f}s`

---

## External Package Installation

### Required pip packages:
```bash
pip install tree_sitter_languages
```

### Optional (for enhanced features):
- None currently

---

## Shell Scripts & Utilities

### Activation Script (activate_ciatc_final.sh)
**Purpose:** Activate CiaTc framework hooks

**Dependencies:**
- Bash shell
- `~/.claude/settings.local.json` (creates/modifies)
- `/Users/philhudson/.claude/statusline-command.sh` (optional statusline)

**Modes:**
- `band`: UserPromptSubmit hook only
- `janitors`: PostResponse hook only
- `full`: Both hooks

**Configuration:**
- JSON schema: `https://json.schemastore.org/claude-code-settings.json`
- Settings backup: `~/.claude/settings.backup.<timestamp>.json`
- Environment: `MAX_THINKING_TOKENS=31999`, `CLAUDE_CODE_MAX_OUTPUT_TOKENS=32000`

---

### Deactivation Script (deactivate_ciatc_final.sh)
**Purpose:** Deactivate CiaTc framework and restore previous settings

**Dependencies:**
- Bash shell
- Backup settings files: `~/.claude/settings.backup.*.json`

**Behavior:**
- Restores most recent backup if available
- Creates minimal settings if no backup found
- Preserves token environment variables

---

### iOS App Generator (create_ios_app.swift)
**Purpose:** Generate iOS app bundle for Van Gogh Fractal Compiler

**Dependencies:**
- Swift runtime environment
- `Foundation`: FileManager, file I/O

**Generated Files:**
- App bundle: `/Users/philhudson/Projects/CiaTc/PaulsLaboratory/VanGoghFractalCompiler.app/`
- Info.plist: Bundle configuration
- Executable placeholder: Shell script with chmod 755

**Bundle Properties:**
- Display name: "Van Gogh Fractal Compiler"
- Bundle ID: `com.paulslab.vangoghfractalcompiler`
- Version: 1.0
- Main storyboard: Main.storyboard
- Orientation: Portrait only

---

## Testing & Debug Tools

### Band Debug Script (test_band_debug.py)
**Purpose:** Debug and test band orchestrator functionality

**Python Standard Library:**
- `json`: Event creation
- `sys`: stdio handling
- `subprocess`: Process execution
- `os`: Environment management

**Test Coverage:**
1. Claude CLI availability test
2. Recursion guard validation (CIATC_SUBPROCESS=true)
3. Band orchestrator execution test

**Test Configuration:**
- Test CWD: `/Users/philhudson/Projects/VERA`
- Test transcript: `/tmp/test.jsonl`
- Timeout: 30s for Claude, 5s for band tests

---

### Band Performance Script (test_band_performance.py)
**Purpose:** Performance benchmarking and bottleneck identification

**Python Standard Library:**
- `json`: Results serialization
- `time`: Performance timing
- `sys`: Module path manipulation
- `pathlib.Path`: File path handling

**Functions:**
- `test_agent(name, func, *args)`: Individual agent tester with timing
- `main()`: Sequential test runner with summary

**Imported Functions:**
- From `band_orchestrator_main`: `run_john`, `run_george`, `run_pete`, `run_paul`, `run_build_health`, `run_ringo`

**Output:**
- `/Users/philhudson/Projects/CiaTc/performance_results.json`
- Console output with timing breakdown
- Bottleneck warnings (>30s threshold)

**Metrics Tracked:**
- Execution time per agent
- Output length
- Success/failure status
- Sequential vs parallel time estimates

---

## Platform Requirements

### Python Components:
- Python 3.8+ (for concurrent.futures, pathlib)
- macOS/Linux (subprocess handling)

### Swift Components:
- Xcode 14+ (SwiftUI, SwiftData)
- iOS 16+ (for SwiftData support)
- macOS 13+ (for development)

### Shell Scripts:
- Bash 3.2+ (macOS default)
- Standard Unix utilities (ls, cp, date)

---

## Notes on Portability

### Hard-coded Paths (Portability Risks):
- `/usr/local/bin/claude` (Claude CLI location)
- `/Users/philhudson/Projects/CiaTc/prompts/` (prompt directory)
- `/tmp/janitor_critique.md` (output file)
- Bootstrap script references VERA project paths

### Mitigation Strategies:
- Use environment variables for paths
- Implement path discovery (e.g., `which claude`)
- Make prompt directory configurable
- Use platform-agnostic temp file creation

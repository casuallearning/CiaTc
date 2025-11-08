# Architectural Patterns - CiaTc Framework

## Overview
This document captures core architectural patterns, design decisions, and system-level approaches used throughout the CiaTc framework.

**Last Updated:** 2025-10-03

---

## Core Architectural Patterns

### Hook System Architecture - Recursion Prevention Pattern
**Location:** `band_orchestrator_main.py:177-197`, `janitors_orchestrator_main.py`

**Pattern:**
```python
if os.environ.get('CIATC_SUBPROCESS') == 'true':
    stdin_data = sys.stdin.read()
    try:
        event_data = json.loads(stdin_data)
        if event_data.get('hook_event_name') == 'UserPromptSubmit':
            # Valid hook but var set - unset and continue
            del os.environ['CIATC_SUBPROCESS']
        else:
            # Not hook event, pass through
            print(stdin_data, end='')
            return
    except (json.JSONDecodeError, AttributeError):
        print(stdin_data, end='')
        return
```

**Purpose:** Prevents infinite recursion when orchestrators spawn Claude CLI subprocess calls

**Implementation:**
1. Before spawning subprocess, set `CIATC_SUBPROCESS=true` in subprocess environment
2. At entry point, check if variable is set
3. If set AND valid hook JSON, auto-unset and continue (fixes leaked variable issue)
4. If set BUT not hook JSON, pass through stdin unchanged

**Risk Mitigation:** Auto-recovery from leaked environment variable (fixed 2025-10-01)

---

### Three-Phase Parallel Execution Pattern
**Location:** `band_orchestrator_main.py:219-307`

**Pattern:**
```python
# PHASE 1: Foundation (John & Build Health)
with ThreadPoolExecutor(max_workers=2) as executor:
    john_future = executor.submit(run_john, cwd, transcript_path)
    build_health_future = executor.submit(run_build_health, cwd)
    for future in as_completed([john_future, build_health_future]):
        result = future.result()

# PHASE 2: Documentation (George & Pete - depend on John's index)
with ThreadPoolExecutor(max_workers=2) as executor:
    george_future = executor.submit(run_george, user_prompt, transcript_path, cwd)
    pete_future = executor.submit(run_pete, user_prompt, cwd)
    for future in as_completed([george_future, pete_future]):
        result = future.result()

# PHASE 3: Synthesis (Paul & Ringo - depend on all docs)
with ThreadPoolExecutor(max_workers=2) as executor:
    paul_future = executor.submit(run_paul, user_prompt)
    ringo_future = executor.submit(run_ringo, cwd, user_prompt)
    for future in as_completed([paul_future, ringo_future]):
        result = future.result()
```

**Purpose:** Optimize orchestration through strategic parallelization with dependency management

**Benefits:**
- Total time: ~max(Phase1) + max(Phase2) + max(Phase3) ≈ 24s
- vs Sequential: ~38s (37% improvement)
- Clean phase boundaries enforce data dependencies
- Fault tolerance via per-future exception handling

**Phase Dependencies:**
- Phase 1: None (foundation)
- Phase 2: Requires file_index.md from John
- Phase 3: Requires all narrative/technical docs

---

### Hook Output "Jailbreak" Pattern
**Location:** `band_orchestrator_main.py:282-290`

**Pattern:**
```python
# Output original JSON (required by hook system)
print(json.dumps(event), end='')

# Append band report as text
if band_report:
    print(f"\n\n{band_report}", end='')
```

**Purpose:** Inject additional context into hook output beyond JSON

**Implementation:**
- Outputs valid JSON first (hook requirement)
- Appends markdown text after
- Creates technically invalid JSON but Claude accepts it
- Similar to discipline-reminder.js pattern

**Risk:** Fragile, depends on Claude's parsing tolerance

---

### Function Timing Decorator Pattern
**Location:** `band_orchestrator_main.py:18-27`

**Pattern:**
```python
def timed(func):
    """Decorator to time function execution"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"⏱️  {func.__name__}: {elapsed:.2f}s", file=sys.stderr)
        return result
    return wrapper

@timed
def run_john(cwd, transcript_path): ...
```

**Purpose:** Real-time performance monitoring during hook execution

**Technologies:**
- `time.time()`: Wall-clock timing
- `functools.wraps`: Metadata preservation
- `sys.stderr`: Non-interfering output

**Applied To:** All 6 band members (john, george, pete, paul, ringo, build_health)

**Output Example:**
```
⏱️  run_john: 8.42s
⏱️  run_build_health: 2.13s
⏱️  run_george: 6.27s
⏱️  run_pete: 4.91s
⏱️  run_paul: 7.35s
⏱️  run_ringo: 9.18s
```

---

## Multi-Agent Orchestration Patterns

### Intelligent Conductor Agent Pattern
**Location:** `conductor_agent.py`, `smart_orchestrator.py`, `prompts/conductor.md`

**Pattern:** Lightweight decision layer that selectively activates agents based on prompt analysis

**Architecture:**
```
User Prompt
    ↓
Conductor (Claude Haiku - 10s timeout)
    ↓
    ├→ Route Decision
    ├→ Agent Selection
    ├→ Timeout Calculation
    └→ Band Member Activation
```

**Conductor Responsibilities:**
1. **Request Analysis:** Quick classification of prompt type (simple Q&A vs complex task)
2. **Agent Selection:** Decide which band members to activate
3. **Skip Decision:** Return "skip" for trivial questions (no band needed)
4. **Timeout Planning:** Calculate adaptive timeout (60-900 seconds)
5. **Priority Assignment:** Low/medium/high priority guidance
6. **Paul Engagement:** Only activate Paul when explicitly requested for creative input

**Quick Skip Patterns:**
- "What is X?" → Skip (no band)
- "Explain Y" → Skip or light analysis
- "How do I Z?" → Light analysis (George + Ringo only)
- Implementation tasks → Full band
- Design challenges → Consider Paul (explicit request only)

**Timeout Strategy:**
- Small projects (<100 files): 60s
- Medium projects (100-500): 120s
- Large projects (>500): 180s
- Complex with Paul: 900s (15 minutes for deep creative thinking)

**Implementation:**
```python
# Quick Claude Haiku decision
decision = run_claude_haiku(
    prompt=conductor_prompt,
    input_variables={
        'user_prompt': user_prompt,
        'project_size': project_stats['file_count'],
        'recent_changes': file_change_count,
        'last_agent_run': time_since_last_run
    },
    timeout=10
)

# Parse decision
agents_to_run = decision['agents']  # john, george, pete, etc.
timeout = decision['timeout']
priority = decision['priority']
```

**Performance Impact:**
- 10-second overhead for decision-making
- ~10-20x improvement by skipping agents for simple questions
- Average case: Much faster (Paul engaged less often)
- Worst case: Same as before (all agents run)

**Paul Engagement Rules (Conservative):**
- ✓ User says "ideas", "creative", "unconventional", "wild", "think outside"
- ✓ Complex design decisions requiring cross-domain thinking
- ✗ Default for meta-discussions (less confusion)
- ✗ Simple feature requests
- ✗ Bug fixes

---

### Dual Orchestration System
**Context:** CiaTc Framework core architecture

**Pattern:** Separation of pre-analysis (Band) and post-critique (Janitors)

**Band Orchestrator (UserPromptSubmit):**
- Conductor: Selective agent activation with timeout management
- John: Directory/file indexing
- George: Narrative documentation
- Pete: Technical documentation
- Paul: Wild ideas generation (Paul engagement rules apply)
- Ringo: Context synthesis
- Build Health: System monitoring

**Janitors Orchestrator (Stop):**
- Marie: Organizational review
- Descartes: Assumption validation
- Feynman: Simplicity advocacy

**Benefits:**
- Clear separation of concerns
- Specialized agent roles
- Extensible design
- Intelligent agent selection (Conductor)
- Adaptive resource management

**Risks:**
- Coordination complexity
- Potential circular dependencies
- High token consumption (mitigated by Conductor)

---

### Smart Orchestrator Intelligence Pattern
**Location:** `smart_orchestrator.py`

**Pattern:** Project intelligence gathering to inform Conductor decisions

**Capabilities:**
1. **File Change Detection:** MD5 hashing to identify what changed
2. **Project Size Analysis:** Count files/LOC to classify project scale
3. **Caching:** Incremental processing based on cached hashes
4. **Adaptive Timeout Calculation:** Suggest timeout based on changes

**Implementation:**
```python
class SmartOrchestrator:
    def analyze_project(self, cwd):
        """Return project intelligence for Conductor"""
        return {
            'file_count': count_files(cwd),
            'total_lines': count_lines(cwd),
            'changed_files': detect_changes(cwd),
            'change_count': len(changed_files),
            'project_size': classify_size(file_count),  # small/medium/large
            'file_hashes': current_hashes,
            'cached_hashes': load_cached(),
        }
```

**Change Detection Strategy:**
- Small files (<1MB): MD5 hashing
- Large files (>1MB): Modification time (mtime)
- Cache: `.band_cache/file_hashes.json`
- Incremental: Only rehash changed files

**Project Classification:**
- Small: <100 files (60s timeout)
- Medium: 100-500 files (120s timeout)
- Large: >500 files (180s timeout)

**Adaptive Timeout Calculation:**
- Base: From project size classification
- Bonus: +seconds based on change count
- Formula: `base_timeout + min(change_count * 10, 60)`
- Conductor override: May extend further

**Benefits:**
- Conductor has project context
- Efficient change detection
- Intelligent timeout planning
- Caching reduces repetitive work

**Caching Strategy:**
- `.band_cache/orchestrator_cache.json`: Execution history
- `.band_cache/file_hashes.json`: File content hashes
- `.band_cache/locks/`: Process coordination locks

---

### Prompt-Driven Agent Design
**Pattern:** External markdown-based prompt configuration

**Location:** `prompts/` directory

**Implementation:**
- One markdown file per agent (e.g., `john.md`, `marie.md`)
- Centralized loading via `prompt_loader.py`
- Template variable substitution (`{placeholder}`)
- 5000 char value truncation

**Benefits:**
- Runtime customization without code changes
- Version control for agent behavior
- Easy experimentation

**Risks:**
- Critical logic lives in external files
- Hard to track behavior changes

---

## Swift/iOS Architectural Patterns

### Bio-Computational Compilation Pattern
**Location:** `WaggleDanceCompiler.swift`

**Pattern:** Translating natural phenomena (bee waggle dance) to executable code

**Implementation Approach:**
1. Computer vision processing (frame data → movement vectors)
2. Pattern recognition (figure-8 detection via windowing)
3. Frequency analysis (zero-crossing estimation)
4. Operation mapping (frequency → BioOperation)
5. Code generation (BioInstructions with energy tracking)

**Frequency-Based Operation Mapping:**
- 0-50 Hz: Load operations
- 50-100 Hz: Store operations
- 100-200 Hz: Compute operations
- 200-300 Hz: Branch operations
- 300+ Hz: Transform operations

**Algorithms Used:**
- von Frisch's formula: distance calculation
- SIMD operations: Vector mathematics
- Sliding window (size 20): Pattern detection
- Zero-crossing: Frequency estimation

---

### Artistic Code Compilation Pattern
**Location:** `VanGoghCompiler.swift`

**Pattern:** Transform source code into visual artistic instructions

**5-Phase Compilation Pipeline:**
1. **Code Structure Analysis:** Parse source → identify patterns (func/loop/if/var)
2. **Artistic Transformation:** Map code patterns → Van Gogh brushstrokes
3. **Fractal Instruction Generation:** Convert brushstrokes → Mandelbrot canvas coordinates
4. **Golden Ratio Optimization:** Apply aesthetic enhancement (ratio: 1.618033988749)
5. **PaintedCode Assembly:** Generate final compiled output with metrics

**Code Pattern → Brushstroke Mapping:**
- Function: Impasto stroke (thick, textured)
- Loop: Swirl stroke (repetitive, circular)
- Conditional: Glazing stroke (layered, transparent)
- Variable: Stippling stroke (dotted, discrete)

**Mathematical Foundations:**
- Mandelbrot coordinate mapping: real [-2, +1], imaginary [-1.5, +1.5]
- Golden ratio optimization: 1.618
- Canvas coordinates: 400x300, center (200, 150)
- Complexity metric: `sin(intensity * π) * 0.5 + 0.5`

---

### Fractal Memory Management Pattern
**Location:** `FractalMemoryManager.swift`

**Pattern:** 2D spatial memory allocation with Mandelbrot addressing

**Memory Architecture:**
- **Canvas:** 1024x1024 2D grid
- **Address Space:** Mandelbrot coordinates [-2, +2]
- **Addressing:** VanGoghVector (x, y, turbulence, direction) → FractalAddress
- **Storage:** Real malloc/free with spatial tracking
- **Max Regions:** 1000

**Garbage Collection Strategy:**
- **Algorithm:** Age-based with complexity weighting
- **Timer:** 5-second cycles
- **Base Age:** 30 seconds
- **Life Extension:** 1 + complexity * 2 (up to 3x longer)
- **Visual Fading:** Age ratio × 0.8 threshold
- **Beauty Scoring:** Golden ratio (1.618) distribution metric

**Allocation Process:**
1. Map VanGoghVector to Mandelbrot coordinates
2. Calculate artistic layer and iteration count
3. Allocate real memory via malloc
4. Track region with metadata (timestamp, complexity, direction)
5. Return FractalPointer<T>

**Deallocation Process:**
1. Check age vs. complexity-weighted threshold
2. Calculate fade intensity
3. Artistic fade-out animation
4. Real free() call
5. Remove from tracking

---

### Animated Fractal Canvas Pattern
**Location:** `PaintingCanvas.swift`

**Pattern:** Living canvas with continuous animation and Mandelbrot overlay

**Animation Architecture:**
- **Driver:** CADisplayLink at display refresh rate
- **Lazy Redraw:** Every 3 frames (performance optimization)
- **Turbulence Animation:** `sin/cos` with frame-based phase
- **Max Brushstrokes:** 1000 (performance limit)

**Rendering Pipeline:**
1. Draw starry night background (3-color gradient)
2. Render all brushstrokes with turbulence transforms
3. Compute Mandelbrot overlay (4px stride, 50 iterations)
4. Blend overlay with alpha 0.1

**Brushstroke Rendering:**
- Thickness: `complexity * 8 + 2`
- Turbulence amplitude: `turbulence * 20`
- Polar coordinate spiral generation
- Context save/restore for transforms

**Mandelbrot Computation:**
- Escape-time algorithm
- Max iterations: 50
- Stride: 4px intervals
- CVPixelBuffer: 32BGRA format

---

## Code Analysis Patterns

### Tree-sitter AST Parsing Pattern
**Location:** `build_health_agent.py`

**Pattern:** Language-agnostic AST parsing with regex fallback

**Implementation:**
1. Detect language from file extension
2. Get appropriate tree-sitter parser
3. Traverse AST for:
   - Import statements
   - Function/class definitions
   - Function calls
4. Fallback to regex if tree-sitter fails

**Supported Languages:**
- Python, Swift, JavaScript, TypeScript, Go, Rust, Java, C, C++, Ruby, PHP

**Extracted Data:**
- Import/module dependencies
- Function signatures with line numbers
- Function call relationships
- Definition locations

**Performance Considerations:**
- Parser creation is expensive (should pool)
- Recursive AST traversal is O(nodes)
- Regex fallback less accurate but always available

---

### Dependency Graph Pattern
**Location:** `build_health_agent.py`

**Pattern:** Incremental dependency tracking with change detection

**Graph Structure:**
```python
{
    "file_path": {
        "imports": ["module1", "module2"],
        "definitions": {"func_name": {"signature": "def func()", "line": 42}},
        "calls": ["other_func"],
        "impacted_by": ["other_file.py"],
        "impacts": ["dependent_file.py"]
    }
}
```

**Persistence:** JSON file at `Documents/Technical/dependency_graph.json`

**Change Detection:**
1. Git status for modified files
2. Signature comparison (current vs. cached)
3. Severity classification (high for signature changes)
4. Impact propagation through graph

**Risk Assessment:**
- Low: 0-2 impacted files
- Medium: 3-5 impacted files
- High: 6+ impacted files OR signature changes

**Circular Dependency Detection:**
- DFS-based cycle detection
- Reports circular chains

---

## Data Flow Patterns

### File-Based Agent Communication
**Pattern:** Agents communicate via shared file system

**Communication Paths:**
- John → George/Pete: `Documents/file_index.md`
- John → Ringo: `Documents/directory_map.md`
- George → Ringo: `Documents/Narratives/*.md`
- Pete → Ringo: `Documents/Technical/*.md`
- Build Health: `Documents/Technical/dependency_graph.json`

**Benefits:**
- Decoupled agents
- Inspectable intermediate results
- Persistent state

**Risks:**
- Race conditions if phases not enforced
- Stale data if files not updated
- No schema versioning

---

### Transcript Parsing Pattern
**Location:** `janitors_orchestrator_main.py`, `band_orchestrator_main.py`

**Pattern:** Extract last user message from JSONL transcript

**Implementation:**
```python
with open(transcript_path) as f:
    lines = f.readlines()
    for line in reversed(lines):
        entry = json.loads(line)
        if entry['type'] == 'inputMessage':
            return entry['text']
```

**Risks:**
- Loads entire file into memory
- Becomes slower as transcript grows
- No error handling for malformed JSON

---

## Template and Configuration Patterns

### Prompt Template Substitution Pattern
**Location:** `prompt_loader.py`

**Pattern:** Simple string replacement for dynamic prompts

**Template Format:**
```markdown
Analyze the following code: {code}
User request: {user_prompt}
Working directory: {cwd}
```

**Implementation:**
```python
for key, value in context.items():
    if value and len(str(value)) < 5000:
        prompt = prompt.replace(f'{{{key}}}', str(value))
```

**Features:**
- 5000 char value truncation
- Graceful None handling
- Unfilled placeholder detection

**Limitations:**
- No conditionals or loops
- No type checking
- Simple string replacement only

---

## Conductor System Architecture (November 2025)

### Overview Pattern
The Conductor system introduces intelligent agent selection, replacing "always run all 5 agents" with "only run what's needed". This reduces execution time from 5-10 minutes to milliseconds for simple queries.

**Architecture Diagram:**
```
User Prompt
    ↓
SmartOrchestrator (project intelligence)
    ├─ Reads: file count, changed files, project size
    └─ Output: Project stats JSON
    ↓
Conductor Agent (semantic decision)
    ├─ Input: Prompt + project stats
    ├─ Model: Haiku (10s decision)
    └─ Output: Should run? Which agents? Timeout?
    ↓
Decision Gate
    ├─ If skip_band=true → Return original JSON (0s)
    └─ If agents_to_run → Execute selected agents
    ↓
Band Orchestrator (3-phase execution)
    ├─ Phase 1: John + Build Health
    ├─ Phase 2: George + Pete (depends on Phase 1)
    └─ Phase 3: Paul + Ringo (depends on Phases 1-2)
    ↓
Append Band Report to JSON
```

### Conductor Decision Logic Pattern
**Location:** `conductor_agent.py`

**Input Schema:**
```json
{
    "user_prompt": "Implement feature X",
    "project_stats": {
        "file_count": 42,
        "total_lines": 5280,
        "project_size": "small",
        "changed_files": ["band_orchestrator_main.py"],
        "change_count": 1
    }
}
```

**Output Schema:**
```json
{
    "should_run": true,
    "agents_to_run": ["john", "george", "pete", "paul", "ringo"],
    "timeout": 300,
    "priority": "high",
    "reason": "Complex feature implementation detected"
}
```

**Decision Categories:**

1. **Skip Decision (0 seconds)**
   - Pattern: Simple factual questions
   - Keywords: "what is", "how do i", "explain", "list", "where is"
   - Action: Return original JSON unchanged
   - Rationale: Band adds no value for informational queries

2. **Minimal Agents (60 seconds)**
   - Pattern: Simple code queries, documentation lookups
   - Agents: john + ringo (structure + synthesis only)
   - Action: Skip george (narrative) and pete (technical)
   - Rationale: Don't document when no changes

3. **Full Band (180+ seconds)**
   - Pattern: Complex implementation tasks
   - Keywords: "refactor", "implement", "create", "build", "architect"
   - Agents: All 5 (john, george, pete, paul, ringo)
   - Rationale: Need all perspectives for major changes

### Smart Orchestrator Architecture Pattern
**Location:** `smart_orchestrator.py`

**Two-Level Caching Strategy:**

**Level 1 - File Hashes (`.band_cache/file_hashes.json`):**
```json
{
    "band_orchestrator_main.py": "abc123def456789",
    "smart_orchestrator.py": 1762625964,
    "large_binary.bin": null
}
```

**Strategy:**
- Small files (<1MB): MD5 hash for accurate change detection
- Medium files (1-100MB): mtime for speed
- Large files (>100MB): Skip (too expensive)

**Level 2 - Orchestrator Cache (`.band_cache/orchestrator_cache.json`):**
```json
{
    "last_update": 1762625964,
    "file_count": 42,
    "total_lines": 5280,
    "project_size": "small",
    "changed_files": ["band_orchestrator_main.py"],
    "change_count": 1,
    "cache_ttl": 3600
}
```

**Performance Characteristics:**
- First run: 10-30 seconds (full project scan)
- Subsequent run (no changes): 100-200ms (cache hit)
- Subsequent run (files changed): 2-5 seconds (incremental hash)

### Agent Lock Architecture Pattern
**Location:** `agent_lock.py`

**Lock File Structure:**
```
.band_cache/locks/
├── john.lock
├── george.lock
├── pete.lock
├── paul.lock
└── ringo.lock
```

**Lock File Content:**
```json
{
    "pid": 12345,
    "timestamp": 1762625964,
    "hostname": "Phils-MacBook"
}
```

**Locking Mechanism:**
1. **Exclusive Lock:** Uses `fcntl.flock()` for cross-platform safety
2. **Blocking vs Non-blocking:**
   - Blocking: Wait indefinitely (default)
   - Non-blocking: Return immediately if locked
3. **Stale Lock Cleanup:** Automatic removal of locks >10 minutes old
4. **Context Manager:** Safe acquisition/release via `with` statement

**Coordination Pattern:**
```python
# Only one process can run john at a time
with AgentLock("john") as lock:
    if lock:
        run_john()
    else:
        # john already running, skip to avoid duplication
        pass
```

### Recursive Call Prevention Pattern (Updated)
**Location:** `band_orchestrator_main.py:177-197`

**Problem:** Band orchestrator spawns Claude subprocess calls with `CIATC_SUBPROCESS=true` environment variable. If variable leaks into parent shell, hook becomes permanently disabled.

**Solution (Intelligent Guard):**
```python
if os.environ.get('CIATC_SUBPROCESS') == 'true':
    stdin_data = sys.stdin.read()
    try:
        event_data = json.loads(stdin_data)
        if event_data.get('hook_event_name') == 'UserPromptSubmit':
            # Valid hook but var set - must have leaked
            del os.environ['CIATC_SUBPROCESS']
            # Continue processing (fall through)
        else:
            # Not a hook event, pass through
            print(stdin_data, end='')
            return
    except (json.JSONDecodeError, AttributeError):
        # Invalid JSON, pass through
        print(stdin_data, end='')
        return
```

**Key Insight:** Detect environment leak by checking if valid hook JSON is present. If so, recover by unsetting variable and continuing.

### Adaptive Timeout Pattern
**Location:** `conductor_agent.py`, `smart_orchestrator.py`

**Timeout Calculation:**
```
Base timeout (by project size):
  - Small (<100 files):    60 seconds
  - Medium (100-500):      120 seconds
  - Large (>500):          180 seconds

Change bonus (per changed file):
  - +10s per file, capped at 60s
  - Rationale: More changes = more time for analysis

Conductor override:
  - Can suggest longer timeout for complex tasks
  - Example: Paul needs longer for creative ideation
```

**Application:**
```python
base = {small: 60, medium: 120, large: 180}[project_size]
change_bonus = min(len(changed_files) * 10, 60)
timeout = base + change_bonus  # Can be overridden by Conductor

# Usage in band orchestrator
result = run_john(..., timeout=timeout)
```

### System Performance Impact
**Before Conductor (November 7):**
- All queries: 5-10 minutes (full band always)
- No intelligence: Band runs regardless of query complexity

**After Conductor (November 8):**
- Trivial queries: <10 seconds (60-100x faster)
- Complex queries: 1-3 minutes (2-5x faster)
- No changes: Skip entirely (∞ speedup)

**Example Timeline (Complex Refactor):**
```
SmartOrchestrator:   ~2 seconds (incremental scan)
Conductor decision:  ~10 seconds (haiku analysis)
Band execution:      ~24 seconds (3 phases parallel)
Total:               ~36 seconds vs 5-10 minutes before
```

### Integration Points with Existing Patterns

1. **Three-Phase Parallel Execution:**
   - Conductor determines if phases run at all
   - SmartOrchestrator provides project context for phases
   - Agent locks prevent duplicate execution between phases

2. **Hook Output Injection:**
   - Conductor decision logged with reasoning
   - Band report appended after JSON (if agents ran)

3. **Error Handling:**
   - Conductor timeout: Fall back to full band
   - Changed file detection fails: Full project scan
   - Lock contention: Skip agent execution gracefully

---

## Design Principles

### 1. Separation of Analysis and Critique
Pre-analysis (Band) happens before post-response critique (Janitors), ensuring clean separation of thought processes.

### 2. Persona-Based Agent Design
Each agent embodies specific expertise with dedicated prompt files.

### 3. Documentation-Driven Development
Extensive narrative and technical documentation maintained separately from code.

### 4. Parallel Where Possible, Sequential Where Necessary
Maximize parallelization within phase boundaries that enforce dependencies.

### 5. Graceful Degradation
Systems should work (possibly with reduced functionality) when dependencies unavailable.

---

## Notes
- This is a living document; update as patterns emerge or evolve
- Cross-reference with `operational_patterns.md` for testing, performance, and debugging patterns
- Cross-reference with `implementation_log.md` for historical context
- See `dependencies.md` for technology stack details

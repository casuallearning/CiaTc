# Technical Documentation Index

**Last Updated:** November 8, 2025 (Updated 2:10pm - Added Band Statusline Shell Scripts)

## Document Overview

### Core Documentation
| Document | Category | Lines | Description |
|----------|----------|-------|-------------|
| `technical_patterns.md` | Patterns | 1050+ | Design patterns for Conductor, SmartOrchestrator, locking, execution, error handling, performance optimization, Band statusline |
| `dependencies.md` | Infrastructure | 650+ | Conductor, Smart Orchestrator, Agent Lock System, Build Health Monitor, all dependencies, libraries, frameworks |
| `architectural_patterns.md` | Architecture | 900+ | Conductor system architecture, Smart Orchestrator caching, agent locks, hook system, multi-agent orchestration, Swift/iOS patterns |
| `operational_patterns.md` | Operations | 780+ | Smart orchestration runtime patterns, caching, locking, phase-based execution, adaptive timeouts, monitoring, quality management |
| `implementation_log.md` | Maintenance | 1090+ | Historical record of implementations (Nov 2025: Conductor system), bug fixes, orchestration requirements, timeout configurations |
| `index.md` | Meta | <100 | This index file with navigation and quick references |

### Historical/Archived Files
| Document | Status | Notes |
|----------|--------|-------|
| ~~`technical_patterns.md`~~ | RECREATED (2025-11-08) | Now contains design patterns instead of being split |

## Quick Reference

### Conductor System (November 2025)
- **Overview:** Intelligent agent selection reduces execution time 10-60x for simple queries
- **How It Works:** See `architectural_patterns.md:Conductor System Architecture` for complete diagram
- **Decision Logic:** See `technical_patterns.md:Intelligent Agent Selection Pattern` for semantic analysis
- **Performance:** Trivial queries <10s (was 5-10min), complex tasks 1-3min (was 5-10min)
- **Timeout Strategy:** See `operational_patterns.md:Adaptive Timeout Adjustment Pattern`

### Smart Orchestrator (Incremental Caching)
- **File Hashing:** See `technical_patterns.md:Project Intelligence Pattern` for 2-level caching
- **Change Detection:** MD5 for <1MB, mtime for 1-100MB, skip >100MB
- **Performance:** First run 10-30s, typical run 2-5s, cache hit 100-200ms
- **Architecture:** See `architectural_patterns.md:Smart Orchestrator Architecture Pattern`

### Agent Lock System
- **Purpose:** Prevent duplicate agent execution across concurrent hooks
- **Implementation:** File-based locking via `fcntl.flock()`
- **Details:** See `dependencies.md:Agent Lock System` and `technical_patterns.md:File-Based Locking Pattern`
- **Stale Cleanup:** Automatic removal of locks >10 minutes old

### Hook System
- **Configuration:** See `dependencies.md` for hook setup, execution order, and shell scripts
- **Architecture:** See `architectural_patterns.md` for hook system design patterns including Conductor integration
- **Operations:** See `operational_patterns.md` for testing and debugging patterns
- **History:** See `implementation_log.md` for issue resolution and timeout configuration requirements (2025-11-08)

### Pattern Categories

**Technical Design Patterns (NEW in technical_patterns.md):**
- Intelligent Agent Selection Pattern (Conductor semantic routing)
- Project Intelligence Pattern (SmartOrchestrator incremental caching)
- File-Based Locking Pattern (AgentLock distributed coordination)
- Three-Phase Parallel Execution Pattern (dependency-aware orchestration)
- Parallel Execution with Adaptive Timeouts (dynamic resource allocation)
- Hook Output Injection Pattern (JSON + Markdown side-channel)
- Recursive Guard with Auto-Recovery Pattern (environment variable leak detection)
- Model Selection Strategy (tiered model choice by task type)
- Error Handling and Fallback Patterns (graceful degradation)
- Performance Optimization Techniques (caching, early exit, parallelization)

**Architectural Patterns (architectural_patterns.md):**
- Conductor System Architecture (intelligent agent selection)
- Smart Orchestrator Architecture (2-level caching strategy)
- Agent Lock Architecture (process coordination)
- Hook System Architecture (recursion prevention, jailbreak, timing)
- Multi-Agent Orchestration (dual orchestration, prompt-driven agents)
- Swift/iOS Patterns (bio-computational, artistic compilation, fractal memory)
- Data Flow (file-based communication, transcript parsing)

**Operational Patterns (operational_patterns.md):**
- Conductor Decision Caching Pattern
- Incremental File Hashing Pattern
- Lock-Based Deduplication Pattern
- Phase-Based Dependency Resolution
- Adaptive Timeout Adjustment Pattern
- Fallback Execution Pattern
- Performance Monitoring Pattern
- Cache Invalidation Pattern
- Testing & Debugging (stderr logging, exception isolation)
- Performance Optimization (lazy evaluation, stride iteration, buffer limits)

### Recent Activity
- **2025-11-08:** Stop Hook Configuration & Git Repository Status Verification
  - Verified Stop hook runs in background mode (band_orchestrator_stop.py:219-314)
  - Confirmed 5 agents running in parallel with agent lock system
  - Identified git NOT configured for `/Users/philhudson/Projects/CiaTc`
  - Updated `implementation_log.md` with verification results
  - Updated `dependencies.md` with git status and Stop hook agent details
  - Updated `operational_patterns.md` with enhanced Stop hook background processing pattern
- **2025-11-08:** Implemented Smart Conductor System - 10-60x performance improvement for simple queries
  - Added `conductor_agent.py` (173 lines) for semantic decision-making
  - Enhanced `smart_orchestrator.py` (416 lines) with incremental caching and project intelligence
  - Created `agent_lock.py` (215 lines) for process-safe coordination
  - Updated all technical documentation with new patterns and architecture
- **2025-11-08:** Generated comprehensive technical pattern documentation
  - Created `technical_patterns.md` (700+ lines) with design patterns
  - Updated `architectural_patterns.md` (900+ lines) with Conductor system architecture
  - Updated `operational_patterns.md` (780+ lines) with runtime patterns
  - Updated `dependencies.md` (650+ lines) with new module dependencies
  - Updated `implementation_log.md` (1090+ lines) with November 2025 entry
- **2025-10-03:** Comprehensive documentation refresh (scripts, tests, patterns split)
- **2025-10-01:** Troubleshot and resolved band context hook bypass issue
- **2025-10-01:** Implemented timing decorator and three-phase parallelization

## Document Organization Strategy

### Three-Document Model (November 2025)

1. **`technical_patterns.md`** (Design Patterns - 700+ lines)
   - Purpose: Document reusable design patterns and implementation approaches
   - Content: Pattern name, overview, implementation, benefits, tradeoffs
   - Use Case: Understanding how to implement similar patterns in the codebase
   - Sections: All major patterns (Conductor, SmartOrchestrator, Locking, etc.)

2. **`architectural_patterns.md`** (System Architecture - 900+ lines)
   - Purpose: Explain system-level design decisions and data flow
   - Content: Architecture diagrams, schemas, integration points, design principles
   - Use Case: Understanding how systems fit together and communicate
   - Sections: Conductor System, Smart Orchestrator, Agent Locks, Hook System

3. **`operational_patterns.md`** (Runtime Operations - 780+ lines)
   - Purpose: Document how systems behave during execution
   - Content: Caching strategies, performance characteristics, failure modes
   - Use Case: Understanding runtime behavior, debugging, performance tuning
   - Sections: Conductor caching, file hashing, locking, phase execution, monitoring

4. **`dependencies.md`** (Infrastructure - 650+ lines)
   - Purpose: Complete dependency and technology reference
   - Content: All libraries, frameworks, versions, requirements, configuration
   - Use Case: Setting up environment, understanding requirements
   - Sections: All components with their dependencies and versions

5. **`implementation_log.md`** (Maintenance History - 1090+ lines)
   - Purpose: Historical record of implementations and fixes
   - Content: Dated entries with problems, solutions, code changes
   - Use Case: Understanding why decisions were made, troubleshooting similar issues
   - Sections: Dated entries from 2025-10-01 to present

### Split Rationale

**Original Problem:**
- Files exceeding 500 lines become difficult to navigate and maintain

**Solution Applied:**
- Split large pattern documentation across focused documents
- Organize by purpose (Design, Architecture, Operations, Dependencies, History)
- Cross-reference between documents for related information

**Benefits:**
- Faster navigation (each document focuses on single purpose)
- Easier to maintain (smaller files, clear ownership)
- Better mental models (design vs architecture vs operations)
- Scalable (easy to add new sections without exceeding size limits)

## Maintenance Notes
- Technical documentation is maintained by Pete (technical documentation specialist)
- Updates occur automatically via Claude Code hooks on each user prompt
- Documentation focuses on technical implementation details, not narrative or project goals
- Files exceeding 500 lines should be split logically into focused documents
- Use cross-references between documents to guide readers to related information
- Maintain consistent formatting and structure across all technical documents

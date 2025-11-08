# Technical Narrative - CiaTc Framework

## Main Conversation Themes
- Comprehensive dependency documentation and environment requirements tracking
- Design pattern formalization for two-phase orchestrator architecture (Band + Janitors) with Feynman simplicity principle
- Implementation history and troubleshooting knowledge base
- Technical infrastructure for framework maintainability and performance
- Performance optimization through timestamp-based caching and intelligent regeneration
- Janitor post-response critique system architecture and philosophical validation patterns with Marie as active agent
- Subscription-optimized performance strategy (Claude Max x20: prioritize requests over tokens)
- Agent naming consistency: Gilfoyle health monitoring, Marie organizational review, Feynman simplicity constraints
- Prompt archival patterns for clean version control and historical tracking
- Architectural patterns formalization: comprehensive documentation of design decisions and system patterns
- Operational patterns documentation: execution management and runtime behavior guidelines

## Key Decisions Made
- Established centralized technical documentation structure (index, dependencies, patterns, implementation log)
- Created persistent implementation log for historical context and debugging reference
- Documented external dependencies including Claude Code hooks, Python environment, and subprocess requirements
- Formalized technical patterns including orchestrator, parallel execution, agent specialization, and philosophical critique patterns
- Decided to track timing data and performance metrics as part of technical documentation
- Adopted timestamp-based change detection for ~300x performance improvement on unchanged projects
- Chose Sonnet parallelism over token minimization given Claude Max x20 subscription economics
- Simplified code over robust error handling: preference for debugging simplicity and maintainability
- Renamed build_health_agent to Gilfoyle for philosophical and naming consistency
- Marie elevated to active agent in Janitor system with explicit organizational responsibilities
- Paul's prompts enhanced with Feynman simplicity principle as architectural constraint
- Legacy Janitor prompts archived for clean project version history
- Created Documents/Technical/architectural_patterns.md: comprehensive architectural pattern documentation with design decisions
- Created Documents/Technical/operational_patterns.md: system execution and runtime management patterns

## Problems Being Solved
- Long-term maintainability through comprehensive technical documentation
- Dependency management and environment setup clarity for new developers
- Pattern reusability and architectural consistency across multi-phase framework
- Historical context preservation for debugging and evolution tracking
- Performance bottleneck identification and optimization guidance
- Two-phase orchestration coordination: Band execution → Janitor post-response critique
- Timestamp-based optimization: detecting unchanged projects and avoiding regeneration overhead
- Janitor file I/O handling and temporary storage strategy documentation
- **SmartOrchestrator initialization delay (1+ minutes)**: Full project scan blocks Conductor startup
  - Root cause: SmartOrchestrator.scan_project() uses rglob("*") + MD5 hashing on every initialization
  - Impact: Users wait 60+ seconds before Band response begins (poor user experience)
  - Solution: Add directory mtime fast-path to skip full hashing when project tree unchanged
  - Implementation: Compare project root directory mtime against cached state before full scan
  - Expected improvement: 1+ minute → near-instant for unchanged projects (typical development sessions)
  - Trade-off: May miss granular file changes if directory mtime not updated reliably

## Direction of Work
- Building robust technical documentation infrastructure supporting two-phase orchestration with philosophical alignment
- Expanding implementation log with detailed troubleshooting guides for Janitor system integration including Marie as active agent
- Documenting performance optimization strategies: timestamp-based caching, parallel execution, code simplification
- Creating technical pattern library for framework extension with philosophical critique patterns
- Maintaining dependency version tracking and compatibility notes with Gilfoyle agent specifications
- Performance profiling integration for both Band (including Gilfoyle) and Janitor execution phases
- Documentation of subscription-optimized architecture decisions (Claude Max x20 economics)
- Tracking architectural evolution: build_health → Gilfoyle, Janitor system refinement, Feynman principle integration
- Maintaining clean version history through prompt archival documentation

## Technical Patterns Emerging
- Two-phase orchestration architecture: Band (pre-response) → Janitors (post-response) with philosophical validation
- Centralized technical documentation pattern (index → specialized docs)
- Implementation log as living troubleshooting knowledge base for multi-phase systems
- Dependency documentation tied to architecture decisions and agent naming (Gilfoyle specifications)
- Performance profiling integration into technical documentation for both phases
- Version control for technical patterns and architectural evolution
- Timestamp-based caching pattern: mtime comparison for change detection (~300x speedup)
- Philosophical validation pattern: Janitors apply structured critique (Marie organization, Descartes methodology, Feynman clarity)
- File-based interphase communication: JSON outputs and temporary critique files
- Subscription economics model: parallelism prioritized over token minimization
- Agent naming pattern: philosophical personas mapped to function roles (Gilfoyle→health, Marie→maintenance, Feynman→simplicity)
- Prompt archival pattern: legacy prompts preserved in archive for historical tracking
- Feynman principle integration: architectural constraint ensuring all ideas explainable simply
- Layered technical documentation: architectural_patterns.md (design) separate from operational_patterns.md (runtime)
- Pattern separation of concerns: architecture vs operations documentation for clearer technical guidance
- **Orchestrator initialization fast-path pattern**: Directory mtime check before full project scan
  - Cache directory mtime + hash in .band_cache on initial scan
  - On subsequent starts, compare current root dir mtime against cached value
  - If unchanged: skip rglob and hashing, return cached state (near-instant)
  - If changed: perform full scan, update cache
  - Benefit: Typical dev sessions with no file changes → instant initialization
  - Risk: Fine-grained edits without directory mtime update → stale state (acceptable trade-off)

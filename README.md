# CiaTc Framework
## Claudes in a Trench Coat

A framework that turns one Opus request into multiple parallel Sonnet analyses, providing rich context and critique for better AI assistance.

## What It Does

Instead of one Claude instance trying to do everything, CiaTc spawns multiple specialized Sonnet instances that work in parallel:

- **The Band** (5 Sonnets) analyze your request BEFORE Opus responds
- **The Janitors** (3 Sonnets) critique Opus's response AFTER

Each specialist is an actual Claude Sonnet with focused expertise.

## Quick Start

```bash
# Activate The Band only (pre-analysis)
./activate_ciatc.sh band

# Activate Janitors only (post-critique)
./activate_ciatc.sh janitors

# Activate FULL framework (both)
./activate_ciatc.sh full

# Deactivate
./deactivate_ciatc.sh
```

## The Band Members

🎸 **John** - Directory Analyst
- Scans project structure
- Identifies missing files
- Notes structural issues

🎸 **George** - Narrative Manager
- Tracks conversation themes
- Maintains context continuity
- Updates documentation needs

🎸 **Pete** - Technical Specialist
- Extracts implementation details
- Documents code patterns
- Tracks technical decisions

🎸 **Paul** - Wild Ideas Generator
- Suggests unconventional solutions
- Provides creative alternatives
- The chaos agent

🥁 **Ringo** - Context Synthesizer
- Aggregates all information
- Provides unified view
- Keeps everything in sync

## The Philosophical Janitors

🧹 **Marie Kondo** - Organizational Review
- What needs cleaning up?
- Unnecessary complexity?
- What doesn't "spark joy"?

🧹 **Descartes** - Assumption Validator
- Unproven claims?
- Logical leaps?
- Missing evidence?

🧹 **Feynman** - Simplicity Advocate
- Could this be simpler?
- Unnecessary complexity?
- Clearer explanations?

## How It Works

1. You submit a request
2. The Band analyzes in parallel (if activated)
3. Their analysis is injected into your prompt
4. Opus responds with full context
5. Janitors critique the response (if activated)
6. You get comprehensive, reviewed assistance

## Cost Considerations

- Each Band member = 1 Sonnet call
- Each Janitor = 1 Sonnet call
- Full activation = 8 Sonnet calls per interaction
- On subscription: Same rate limit as 1 Opus call
- Pay-per-use: Consider using selectively

## Customization

Edit the orchestrator files to:
- Adjust prompts for each specialist
- Add/remove band members
- Change activation triggers
- Modify critique criteria

## Files

- `band_orchestrator.py` - The Band implementation
- `janitors_orchestrator.py` - Janitors implementation
- `activate_ciatc.sh` - Activation script
- `deactivate_ciatc.sh` - Deactivation script
- `Context/` - Stored context and indices
- `Documents/` - Generated documentation
- `Transcripts/` - Conversation transcripts

## Notes

- Requires `claude` CLI to be installed and configured
- Each specialist has MAX 200 token response limit (adjustable)
- Triggers on complex keywords: implement, build, fix, debug, etc.
- Janitors only activate for substantial responses (500+ chars)

## Why "Claudes in a Trench Coat"?

Like the classic comedy trope of kids in a trench coat pretending to be an adult, we're using multiple smaller models (Sonnets) working together to create something more powerful than the sum of its parts.
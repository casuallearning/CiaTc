# CiaTc Prompt Templates

Each file contains the specialized prompt template for a Band member or Janitor.

## The Band (Pre-Analysis)

- **john.md** - Directory structure analyst
- **george.md** - Narrative manager
- **pete.md** - Technical documentation specialist
- **paul.md** - Wild ideas generator
- **ringo.md** - Context synthesizer

## The Philosophical Janitors (Post-Critique)

- **marie.md** - Organizational cleanliness (Marie Kondo)
- **descartes.md** - Assumption validation (René Descartes)
- **feynman.md** - Simplicity advocacy (Richard Feynman)

## Usage

Each prompt file contains placeholders in `{curly_braces}` that should be replaced with actual context:

### Common Placeholders
- `{user_prompt}` - The user's actual request
- `{cwd}` - Current working directory
- `{opus_response}` - Opus's response (for Janitors)

### Band-Specific Placeholders
- `{file_list}` - List of project files
- `{transcript_summary}` - Recent conversation
- `{recent_code}` - Code from recent messages
- `{activity_summary}` - Recent project activity

### Janitor-Specific Placeholders
- `{files_affected}` - Files created/modified
- `{identified_claims}` - Claims made by Opus
- `{complexity_estimate}` - Code complexity metrics

## Customization

Feel free to modify these prompts to:
- Adjust the response length
- Change the focus areas
- Add domain-specific instructions
- Modify the personality/tone

## Running Manually

You can test any prompt manually:

```bash
# Replace placeholders and run
cat john.md | sed 's/{user_prompt}/implement a cache/g' | \
  sed 's/{cwd}/\/current\/dir/g' | \
  claude --model claude-3-5-sonnet-20241022 -p
```
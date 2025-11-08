#!/usr/bin/env python3
"""
Prompt Loader for CiaTc Framework
Loads prompt templates and fills in context
"""

from pathlib import Path

class PromptLoader:
    def __init__(self, prompts_dir="/Users/philhudson/Projects/CiaTc/prompts"):
        self.prompts_dir = Path(prompts_dir)

    def load_prompt(self, member_name, context=None):
        """Load a prompt template and fill in context"""

        prompt_file = self.prompts_dir / f"{member_name}.md"

        if not prompt_file.exists():
            return f"[No prompt file found for {member_name}]"

        with open(prompt_file, 'r') as f:
            prompt = f.read()

        # Fill in context if provided
        if context:
            for key, value in context.items():
                placeholder = f"{{{key}}}"
                if placeholder in prompt:
                    # Handle None values
                    if value is None:
                        value = "[Not available]"
                    # Truncate long values
                    if isinstance(value, str) and len(value) > 5000:
                        value = value[:5000] + "\n...[truncated]"
                    prompt = prompt.replace(placeholder, str(value))

        # Fill remaining placeholders with defaults
        import re
        remaining = re.findall(r'\{(\w+)\}', prompt)
        for placeholder in remaining:
            prompt = prompt.replace(f"{{{placeholder}}}", f"[{placeholder} not provided]")

        return prompt

    def get_band_prompts(self):
        """Get all Band member prompt templates"""
        band = ["john", "george", "pete", "paul", "ringo"]
        return {name: self.load_prompt(name) for name in band}

    def get_janitor_prompts(self):
        """Get all Janitor prompt templates"""
        janitors = ["marie", "descartes", "feynman"]
        return {name: self.load_prompt(name) for name in janitors}


# Example usage
if __name__ == "__main__":
    loader = PromptLoader()

    # Test loading with context
    context = {
        "user_prompt": "Build a caching system",
        "cwd": "/Users/test/project",
        "file_count": 42,
        "file_list": "cache.py\nutils.py\ntest_cache.py"
    }

    john_prompt = loader.load_prompt("john", context)
    print("John's prompt:")
    print(john_prompt[:500])  # First 500 chars
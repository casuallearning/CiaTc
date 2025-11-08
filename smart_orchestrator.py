#!/usr/bin/env python3
"""
Smart Adaptive Orchestrator for The Band
Makes intelligent decisions about when and how to run agents based on:
- Prompt complexity and type
- File changes since last run
- Project size and scope
- System resources
"""

import os
import json
import hashlib
import time
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from datetime import datetime

# Configuration
CACHE_DIR = Path(__file__).parent / ".band_cache"
CACHE_FILE = CACHE_DIR / "orchestrator_cache.json"
FILE_HASH_CACHE = CACHE_DIR / "file_hashes.json"

# Adaptive timeouts based on project size
# More generous since user prefers thoroughness over speed
TIMEOUT_SMALL = 60    # < 100 files
TIMEOUT_MEDIUM = 120  # 100-500 files (2 min)
TIMEOUT_LARGE = 180   # > 500 files (3 min)

# Prompt patterns that should skip hooks (simple questions)
SKIP_PATTERNS = [
    "what is",
    "how do i",
    "explain",
    "can you help me understand",
    "what does",
    "tell me about",
    "show me",
    "list",
    "where is",
    "why does",
    "when should",
]

# Prompt patterns that definitely need full band
FULL_BAND_PATTERNS = [
    "refactor",
    "implement",
    "create",
    "add feature",
    "build",
    "design",
    "architect",
    "migrate",
    "optimize",
]


class SmartOrchestrator:
    """Intelligent orchestration of The Band agents"""

    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or os.getcwd())
        CACHE_DIR.mkdir(exist_ok=True)
        self.cache = self._load_cache()
        self.file_hashes = self._load_file_hashes()

    def _load_cache(self) -> dict:
        """Load orchestrator cache"""
        if CACHE_FILE.exists():
            try:
                return json.loads(CACHE_FILE.read_text())
            except:
                return {}
        return {}

    def _save_cache(self):
        """Save orchestrator cache"""
        CACHE_FILE.write_text(json.dumps(self.cache, indent=2))

    def _load_file_hashes(self) -> dict:
        """Load file hash cache"""
        if FILE_HASH_CACHE.exists():
            try:
                return json.loads(FILE_HASH_CACHE.read_text())
            except:
                return {}
        return {}

    def _save_file_hashes(self):
        """Save file hash cache"""
        FILE_HASH_CACHE.write_text(json.dumps(self.file_hashes, indent=2))

    def should_skip_hooks(self, prompt: str) -> Tuple[bool, str]:
        """
        Determine if hooks should be skipped based on prompt analysis
        Returns: (should_skip, reason)
        """
        prompt_lower = prompt.lower().strip()

        # Skip for very short prompts (likely simple questions)
        if len(prompt) < 20:
            return (True, "prompt too short")

        # Skip for simple question patterns
        for pattern in SKIP_PATTERNS:
            if prompt_lower.startswith(pattern):
                return (True, f"simple question pattern: {pattern}")

        # Don't skip for complex implementation tasks
        for pattern in FULL_BAND_PATTERNS:
            if pattern in prompt_lower:
                return (False, f"complex task detected: {pattern}")

        # Skip if prompt is asking about specific code without changes
        if "why" in prompt_lower or "explain" in prompt_lower:
            if not self.has_file_changes():
                return (True, "explanatory question without file changes")

        return (False, "default: run hooks")

    def get_changed_files(self) -> Set[Path]:
        """
        Get set of files that changed since last run
        Uses file hashing for accurate change detection
        """
        changed = set()

        # FAST PATH: Check if project root mtime changed
        # If no directory changes, skip full scan (massive speedup!)
        project_mtime = self.project_root.stat().st_mtime
        last_scan_time = self.cache.get("last_scan_mtime", 0)

        if project_mtime <= last_scan_time:
            # No directory changes, return empty (or last known changes)
            return changed

        # Update scan time
        self.cache["last_scan_mtime"] = project_mtime

        # Scan project files
        for file_path in self.project_root.rglob("*"):
            if not file_path.is_file():
                continue

            # Skip common ignore patterns
            if any(part.startswith(".") for part in file_path.parts):
                if not any(part == ".claude" for part in file_path.parts):
                    continue
            if "node_modules" in file_path.parts:
                continue
            if "__pycache__" in file_path.parts:
                continue

            # Calculate file hash
            try:
                file_hash = self._hash_file(file_path)
                rel_path = str(file_path.relative_to(self.project_root))

                # Check if hash changed
                if rel_path not in self.file_hashes or self.file_hashes[rel_path] != file_hash:
                    changed.add(file_path)
                    self.file_hashes[rel_path] = file_hash
            except Exception as e:
                # If we can't hash, assume it changed
                changed.add(file_path)

        return changed

    def has_file_changes(self) -> bool:
        """Quick check if any files changed"""
        return len(self.get_changed_files()) > 0

    def _hash_file(self, file_path: Path) -> str:
        """Generate hash of file contents"""
        try:
            # For binary files or large files, use size + mtime
            stat = file_path.stat()
            if stat.st_size > 1_000_000:  # > 1MB
                return f"{stat.st_size}_{stat.st_mtime}"

            # For text files, hash contents
            content = file_path.read_bytes()
            return hashlib.md5(content).hexdigest()
        except:
            return "error"

    def get_project_size(self) -> Tuple[int, int]:
        """
        Get project size metrics
        Returns: (file_count, total_lines)
        """
        file_count = 0
        total_lines = 0

        for file_path in self.project_root.rglob("*"):
            if not file_path.is_file():
                continue

            # Skip ignore patterns
            if any(part.startswith(".") for part in file_path.parts):
                if not any(part == ".claude" for part in file_path.parts):
                    continue
            if "node_modules" in file_path.parts:
                continue

            file_count += 1

            try:
                # Count lines in text files
                if file_path.suffix in [".py", ".js", ".ts", ".tsx", ".jsx", ".md", ".txt", ".json", ".yaml", ".yml"]:
                    lines = len(file_path.read_text().splitlines())
                    total_lines += lines
            except:
                pass

        return file_count, total_lines

    def get_adaptive_timeout(self) -> int:
        """Calculate adaptive timeout based on project size"""
        file_count, _ = self.get_project_size()

        if file_count < 100:
            return TIMEOUT_SMALL
        elif file_count < 500:
            return TIMEOUT_MEDIUM
        else:
            return TIMEOUT_LARGE

    def select_agents(self, prompt: str, changed_files: Set[Path]) -> List[str]:
        """
        Intelligently select which agents should run
        Returns list of agent names: ["john", "george", "pete", "paul", "ringo"]
        """
        agents = []
        prompt_lower = prompt.lower()

        # Ringo always runs (synthesizer)
        agents.append("ringo")

        # John runs if files changed or structural questions
        if changed_files or "structure" in prompt_lower or "files" in prompt_lower:
            agents.append("john")

        # George runs if conversational context needed
        if len(prompt) > 100 or "previous" in prompt_lower or "we discussed" in prompt_lower:
            agents.append("george")

        # Pete runs if technical/implementation work
        if any(pattern in prompt_lower for pattern in FULL_BAND_PATTERNS):
            agents.append("pete")

        # Paul ONLY runs if explicitly requested by name
        if any(word in prompt_lower for word in ["paul", "wild idea", "creative perspective"]):
            agents.append("paul")

        # If only Ringo, might as well run all for first-time or major changes
        if len(agents) == 1 and (not self.cache.get("last_run") or len(changed_files) > 10):
            agents = ["john", "george", "pete", "paul", "ringo"]

        return agents

    def should_use_light_mode(self) -> bool:
        """Determine if light mode (fewer agents) should be used"""
        file_count, total_lines = self.get_project_size()

        # Use light mode for large projects
        if file_count > 500 or total_lines > 50000:
            return True

        # Check time since last run
        last_run = self.cache.get("last_run")
        if last_run:
            time_since = time.time() - last_run
            # If ran recently (< 5 minutes), use light mode
            if time_since < 300:
                return True

        return False

    def get_execution_plan(self, prompt: str) -> Dict:
        """
        Create complete execution plan for orchestrator
        Returns dict with:
        - should_run: bool
        - reason: str
        - agents: list
        - timeout: int
        - light_mode: bool
        - changed_files: int
        """
        # Check if should skip entirely
        should_skip, skip_reason = self.should_skip_hooks(prompt)

        if should_skip:
            return {
                "should_run": False,
                "reason": skip_reason,
                "agents": [],
                "timeout": 0,
                "light_mode": True,
                "changed_files": 0
            }

        # Get changed files
        changed_files = self.get_changed_files()

        # Determine light mode
        light_mode = self.should_use_light_mode()

        # Select agents
        if light_mode:
            # Light mode: only Ringo and one other based on prompt
            agents = ["ringo"]
            if "code" in prompt.lower() or "implement" in prompt.lower():
                agents.append("pete")
            elif "structure" in prompt.lower():
                agents.append("john")
            else:
                agents.append("george")
        else:
            agents = self.select_agents(prompt, changed_files)

        # Get adaptive timeout
        timeout = self.get_adaptive_timeout()

        # Update cache
        self.cache["last_run"] = time.time()
        self.cache["last_prompt"] = prompt[:100]
        self.cache["last_agents"] = agents
        self._save_cache()
        self._save_file_hashes()

        return {
            "should_run": True,
            "reason": f"running {len(agents)} agents",
            "agents": agents,
            "timeout": timeout,
            "light_mode": light_mode,
            "changed_files": len(changed_files)
        }

    def get_incremental_context(self, agent_name: str) -> Optional[Dict]:
        """
        Get incremental context for agent to avoid reprocessing everything
        Returns dict with changed files and cached results
        """
        changed_files = self.get_changed_files()

        context = {
            "changed_files": [str(f.relative_to(self.project_root)) for f in changed_files],
            "file_count": len(changed_files),
            "last_run": self.cache.get("last_run"),
            "project_root": str(self.project_root)
        }

        # Agent-specific incremental context
        if agent_name == "john":
            # John can skip unchanged directories
            context["mode"] = "incremental"
            context["hint"] = "Only update file_index.md and directory_map.md for changed files"

        elif agent_name == "george":
            # George needs recent conversation history
            context["mode"] = "append"
            context["hint"] = "Only add new narrative entries, don't regenerate everything"

        elif agent_name == "pete":
            # Pete focuses on changed code
            context["mode"] = "delta"
            context["hint"] = "Only document technical details for changed/new code"

        elif agent_name == "paul":
            # Paul is creative and doesn't need much context
            context["mode"] = "fresh"
            context["hint"] = "Generate new ideas, no need to review everything"

        elif agent_name == "ringo":
            # Ringo synthesizes from other agents
            context["mode"] = "synthesis"
            context["hint"] = "Aggregate latest outputs from other agents"

        return context


def main():
    """Test the smart orchestrator"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: smart_orchestrator.py <prompt>")
        sys.exit(1)

    prompt = " ".join(sys.argv[1:])
    orchestrator = SmartOrchestrator()

    print("=" * 60)
    print("SMART ORCHESTRATOR ANALYSIS")
    print("=" * 60)

    # Get execution plan
    plan = orchestrator.get_execution_plan(prompt)

    print(f"\nPrompt: {prompt}")
    print(f"\nShould Run: {plan['should_run']}")
    print(f"Reason: {plan['reason']}")
    print(f"Agents: {', '.join(plan['agents'])}")
    print(f"Timeout: {plan['timeout']}s")
    print(f"Light Mode: {plan['light_mode']}")
    print(f"Changed Files: {plan['changed_files']}")

    # Show project stats
    file_count, total_lines = orchestrator.get_project_size()
    print(f"\nProject Stats:")
    print(f"  Files: {file_count}")
    print(f"  Lines: {total_lines:,}")

    # Show incremental context
    print(f"\nIncremental Context:")
    for agent in plan['agents']:
        ctx = orchestrator.get_incremental_context(agent)
        print(f"  {agent}: {ctx['mode']} - {ctx['hint']}")

    print("=" * 60)


if __name__ == "__main__":
    main()

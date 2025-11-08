#!/usr/bin/env python3
"""
BUILD HEALTH MONITOR
Monitors build health BEFORE code gets written
Uses tree-sitter for language-agnostic parsing
Tracks dependencies and predicts impact
"""

import os
import json
import subprocess
from pathlib import Path
from collections import defaultdict
from tree_sitter_languages import get_parser, get_language


class BuildHealthMonitor:
    """Language-agnostic build health monitoring using tree-sitter"""

    def __init__(self, cwd):
        self.cwd = Path(cwd)
        self.dependency_graph = self.load_dependency_graph()
        self.changed_files = []
        self.file_impacts = defaultdict(set)

    def load_dependency_graph(self):
        """Load existing dependency graph or create empty one"""
        graph_path = self.cwd / "Documents" / "Technical" / "dependency_graph.json"
        if graph_path.exists():
            try:
                with open(graph_path, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_dependency_graph(self):
        """Save dependency graph to disk"""
        graph_path = self.cwd / "Documents" / "Technical" / "dependency_graph.json"
        graph_path.parent.mkdir(parents=True, exist_ok=True)
        with open(graph_path, 'w') as f:
            json.dump(self.dependency_graph, f, indent=2)

    def detect_changed_files(self):
        """Detect files changed since last commit (git status)"""
        try:
            # Check if in git repo
            result = subprocess.run(
                ['git', 'rev-parse', '--is-inside-work-tree'],
                capture_output=True,
                text=True,
                cwd=self.cwd
            )
            if result.returncode != 0:
                return []  # Not a git repo

            # Get changed files
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True,
                text=True,
                cwd=self.cwd
            )

            changed = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    # Format: "XY filename"
                    parts = line.strip().split(maxsplit=1)
                    if len(parts) == 2:
                        filename = parts[1]
                        # Handle renames "old -> new"
                        if ' -> ' in filename:
                            filename = filename.split(' -> ')[1]
                        changed.append(filename)

            return changed
        except:
            return []

    def detect_language(self, filepath):
        """Detect language from file extension"""
        ext = Path(filepath).suffix.lower()
        lang_map = {
            '.py': 'python',
            '.swift': 'swift',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.go': 'go',
            '.rs': 'rust',
            '.java': 'java',
            '.c': 'c',
            '.cpp': 'cpp',
            '.h': 'c',
            '.hpp': 'cpp',
            '.rb': 'ruby',
            '.php': 'php',
        }
        return lang_map.get(ext, 'unknown')

    def parse_with_treesitter(self, filepath):
        """Parse file using tree-sitter and extract imports, definitions, and calls"""
        try:
            full_path = self.cwd / filepath
            if not full_path.exists():
                return {'imports': [], 'definitions': [], 'calls': []}

            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            lang = self.detect_language(filepath)
            if lang == 'unknown':
                return {'imports': [], 'definitions': [], 'calls': []}

            # Get parser for language
            try:
                parser = get_parser(lang)
            except:
                # Fallback to basic parsing if tree-sitter fails
                return {
                    'imports': self.parse_imports_basic(filepath),
                    'definitions': self.parse_definitions_basic(filepath),
                    'calls': []
                }

            tree = parser.parse(bytes(content, 'utf8'))
            root_node = tree.root_node

            imports = []
            definitions = []
            calls = []

            # Parse based on language
            if lang == 'python':
                imports = self._parse_python_imports(root_node, content)
                definitions = self._parse_python_definitions(root_node, content)
                calls = self._parse_python_calls(root_node, content)
            elif lang == 'swift':
                imports = self._parse_swift_imports(root_node, content)
                definitions = self._parse_swift_definitions(root_node, content)
                calls = self._parse_swift_calls(root_node, content)
            elif lang in ['javascript', 'typescript']:
                imports = self._parse_js_imports(root_node, content)
                definitions = self._parse_js_definitions(root_node, content)
                calls = self._parse_js_calls(root_node, content)

            return {'imports': imports, 'definitions': definitions, 'calls': calls}

        except Exception as e:
            # Fallback to basic parsing
            return {
                'imports': self.parse_imports_basic(filepath),
                'definitions': self.parse_definitions_basic(filepath),
                'calls': []
            }

    def _parse_python_imports(self, root_node, content):
        """Parse Python imports using tree-sitter"""
        imports = []

        def traverse(node):
            if node.type == 'import_statement':
                # import x, y, z
                for child in node.children:
                    if child.type == 'dotted_name':
                        module = content[child.start_byte:child.end_byte]
                        imports.append(module.split('.')[0])
            elif node.type == 'import_from_statement':
                # from x import y
                for child in node.children:
                    if child.type == 'dotted_name':
                        module = content[child.start_byte:child.end_byte]
                        imports.append(module.split('.')[0])
                        break

            for child in node.children:
                traverse(child)

        traverse(root_node)
        return list(set(imports))

    def _parse_python_definitions(self, root_node, content):
        """Parse Python function/class definitions with signatures"""
        definitions = []

        def traverse(node):
            if node.type == 'function_definition':
                name_node = node.child_by_field_name('name')
                params_node = node.child_by_field_name('parameters')
                if name_node:
                    name = content[name_node.start_byte:name_node.end_byte]
                    params = content[params_node.start_byte:params_node.end_byte] if params_node else "()"
                    definitions.append({
                        'name': name,
                        'type': 'function',
                        'signature': f"{name}{params}",
                        'line': node.start_point[0] + 1
                    })
            elif node.type == 'class_definition':
                name_node = node.child_by_field_name('name')
                if name_node:
                    name = content[name_node.start_byte:name_node.end_byte]
                    definitions.append({
                        'name': name,
                        'type': 'class',
                        'signature': f"class {name}",
                        'line': node.start_point[0] + 1
                    })

            for child in node.children:
                traverse(child)

        traverse(root_node)
        return definitions

    def _parse_python_calls(self, root_node, content):
        """Parse Python function calls"""
        calls = []

        def traverse(node):
            if node.type == 'call':
                func_node = node.child_by_field_name('function')
                if func_node:
                    func_name = content[func_node.start_byte:func_node.end_byte]
                    # Extract just the function name (handle method calls)
                    if '.' in func_name:
                        func_name = func_name.split('.')[-1]
                    calls.append(func_name)

            for child in node.children:
                traverse(child)

        traverse(root_node)
        return list(set(calls))

    def _parse_swift_imports(self, root_node, content):
        """Parse Swift imports using tree-sitter"""
        imports = []

        def traverse(node):
            if node.type == 'import_declaration':
                for child in node.children:
                    if child.type == 'identifier':
                        module = content[child.start_byte:child.end_byte]
                        imports.append(module)

            for child in node.children:
                traverse(child)

        traverse(root_node)
        return list(set(imports))

    def _parse_swift_definitions(self, root_node, content):
        """Parse Swift function/class/struct definitions with signatures"""
        definitions = []

        def traverse(node):
            if node.type == 'function_declaration':
                name_node = node.child_by_field_name('name')
                params_node = node.child_by_field_name('parameters')
                if name_node:
                    name = content[name_node.start_byte:name_node.end_byte]
                    params = content[params_node.start_byte:params_node.end_byte] if params_node else "()"
                    definitions.append({
                        'name': name,
                        'type': 'function',
                        'signature': f"func {name}{params}",
                        'line': node.start_point[0] + 1
                    })
            elif node.type in ['class_declaration', 'struct_declaration', 'protocol_declaration']:
                name_node = node.child_by_field_name('name')
                if name_node:
                    name = content[name_node.start_byte:name_node.end_byte]
                    definitions.append({
                        'name': name,
                        'type': node.type.replace('_declaration', ''),
                        'signature': f"{node.type.replace('_declaration', '')} {name}",
                        'line': node.start_point[0] + 1
                    })

            for child in node.children:
                traverse(child)

        traverse(root_node)
        return definitions

    def _parse_swift_calls(self, root_node, content):
        """Parse Swift function calls"""
        calls = []

        def traverse(node):
            if node.type == 'call_expression':
                func_node = node.children[0] if node.children else None
                if func_node:
                    func_name = content[func_node.start_byte:func_node.end_byte]
                    if '.' in func_name:
                        func_name = func_name.split('.')[-1]
                    calls.append(func_name)

            for child in node.children:
                traverse(child)

        traverse(root_node)
        return list(set(calls))

    def _parse_js_imports(self, root_node, content):
        """Parse JavaScript/TypeScript imports using tree-sitter"""
        imports = []

        def traverse(node):
            if node.type == 'import_statement':
                # Look for string literal (the source)
                for child in node.children:
                    if child.type == 'string':
                        source = content[child.start_byte:child.end_byte].strip('"\'')
                        imports.append(source)

            for child in node.children:
                traverse(child)

        traverse(root_node)
        return list(set(imports))

    def _parse_js_definitions(self, root_node, content):
        """Parse JavaScript/TypeScript function/class definitions with signatures"""
        definitions = []

        def traverse(node):
            if node.type in ['function_declaration', 'function']:
                name_node = node.child_by_field_name('name')
                params_node = node.child_by_field_name('parameters')
                if name_node:
                    name = content[name_node.start_byte:name_node.end_byte]
                    params = content[params_node.start_byte:params_node.end_byte] if params_node else "()"
                    definitions.append({
                        'name': name,
                        'type': 'function',
                        'signature': f"function {name}{params}",
                        'line': node.start_point[0] + 1
                    })
            elif node.type == 'class_declaration':
                name_node = node.child_by_field_name('name')
                if name_node:
                    name = content[name_node.start_byte:name_node.end_byte]
                    definitions.append({
                        'name': name,
                        'type': 'class',
                        'signature': f"class {name}",
                        'line': node.start_point[0] + 1
                    })
            elif node.type == 'method_definition':
                name_node = node.child_by_field_name('name')
                params_node = node.child_by_field_name('parameters')
                if name_node:
                    name = content[name_node.start_byte:name_node.end_byte]
                    params = content[params_node.start_byte:params_node.end_byte] if params_node else "()"
                    definitions.append({
                        'name': name,
                        'type': 'method',
                        'signature': f"{name}{params}",
                        'line': node.start_point[0] + 1
                    })

            for child in node.children:
                traverse(child)

        traverse(root_node)
        return definitions

    def _parse_js_calls(self, root_node, content):
        """Parse JavaScript/TypeScript function calls"""
        calls = []

        def traverse(node):
            if node.type == 'call_expression':
                func_node = node.child_by_field_name('function')
                if func_node:
                    func_name = content[func_node.start_byte:func_node.end_byte]
                    if '.' in func_name:
                        func_name = func_name.split('.')[-1]
                    calls.append(func_name)

            for child in node.children:
                traverse(child)

        traverse(root_node)
        return list(set(calls))

    def parse_imports_basic(self, filepath):
        """Basic import parsing without tree-sitter (fallback)"""
        imports = []
        try:
            full_path = self.cwd / filepath
            if not full_path.exists():
                return []

            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            lang = self.detect_language(filepath)

            # Basic regex-like parsing for imports
            lines = content.split('\n')

            if lang == 'python':
                for line in lines:
                    line = line.strip()
                    if line.startswith('import ') or line.startswith('from '):
                        # Extract module name
                        if line.startswith('import '):
                            module = line[7:].split()[0].split('.')[0]
                        else:  # from X import Y
                            module = line[5:].split()[0].split('.')[0]
                        imports.append(module)

            elif lang == 'swift':
                for line in lines:
                    line = line.strip()
                    if line.startswith('import '):
                        module = line[7:].strip()
                        imports.append(module)

            elif lang in ['javascript', 'typescript']:
                for line in lines:
                    line = line.strip()
                    if 'import ' in line and ' from ' in line:
                        # Extract source
                        parts = line.split(' from ')
                        if len(parts) > 1:
                            source = parts[1].strip().strip('"\'').strip(';')
                            imports.append(source)

        except Exception as e:
            pass

        return imports

    def parse_definitions_basic(self, filepath):
        """Basic definition parsing without tree-sitter (fallback)"""
        definitions = []
        try:
            full_path = self.cwd / filepath
            if not full_path.exists():
                return []

            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            lang = self.detect_language(filepath)
            lines = content.split('\n')

            if lang == 'python':
                for i, line in enumerate(lines, 1):
                    stripped = line.strip()
                    if stripped.startswith('def ') or stripped.startswith('class '):
                        name = stripped.split('(')[0].split(':')[0].split()[1]
                        definitions.append({'name': name, 'line': i, 'type': 'function' if 'def' in stripped else 'class'})

            elif lang == 'swift':
                for i, line in enumerate(lines, 1):
                    stripped = line.strip()
                    if ' func ' in stripped or ' class ' in stripped or ' struct ' in stripped:
                        parts = stripped.split()
                        for j, part in enumerate(parts):
                            if part in ['func', 'class', 'struct'] and j + 1 < len(parts):
                                name = parts[j + 1].split('(')[0].split(':')[0]
                                definitions.append({'name': name, 'line': i, 'type': part})

            elif lang in ['javascript', 'typescript']:
                for i, line in enumerate(lines, 1):
                    stripped = line.strip()
                    if stripped.startswith('function ') or stripped.startswith('class ') or \
                       stripped.startswith('export function ') or stripped.startswith('export class '):
                        parts = stripped.split()
                        for j, part in enumerate(parts):
                            if part in ['function', 'class'] and j + 1 < len(parts):
                                name = parts[j + 1].split('(')[0].split('{')[0]
                                definitions.append({'name': name, 'line': i, 'type': part})

        except Exception as e:
            pass

        return definitions

    def detect_signature_changes(self, filepath):
        """Detect if signatures changed from previous version"""
        if filepath not in self.dependency_graph:
            return []

        old_data = self.dependency_graph[filepath]
        old_sigs = {d['name']: d.get('signature', '') for d in old_data.get('definitions', [])}

        # Parse current version
        parsed = self.parse_with_treesitter(filepath)
        new_sigs = {d['name']: d.get('signature', '') for d in parsed['definitions']}

        # Find changed signatures
        changes = []
        for name, new_sig in new_sigs.items():
            if name in old_sigs and old_sigs[name] != new_sig:
                changes.append({
                    'name': name,
                    'old': old_sigs[name],
                    'new': new_sig
                })

        return changes

    def analyze_dependencies(self, filepath):
        """Analyze dependencies for a file using tree-sitter"""
        # Parse with tree-sitter
        parsed = self.parse_with_treesitter(filepath)

        # Detect signature changes
        sig_changes = self.detect_signature_changes(filepath)

        # Store in dependency graph
        self.dependency_graph[filepath] = {
            'imports': parsed['imports'],
            'definitions': parsed['definitions'],
            'calls': parsed['calls'],
            'language': self.detect_language(filepath),
            'signature_changes': sig_changes
        }

        return parsed['imports'], parsed['definitions']

    def find_impacted_files(self, changed_file):
        """Find files that depend on the changed file (enhanced with call tracking)"""
        impacted = {}  # filepath -> {'reason': str, 'locations': []}

        # Get definitions and signature changes in changed file
        if changed_file not in self.dependency_graph:
            self.analyze_dependencies(changed_file)

        changed_data = self.dependency_graph.get(changed_file, {})
        changed_def_names = {d['name'] for d in changed_data.get('definitions', [])}
        sig_changes = changed_data.get('signature_changes', [])

        # Check all other files for imports/calls
        for filepath, data in self.dependency_graph.items():
            if filepath == changed_file:
                continue

            reasons = []

            # Check if file imports the changed file
            imports = data.get('imports', [])
            changed_basename = Path(changed_file).stem
            for imp in imports:
                if changed_basename.lower() in imp.lower():
                    reasons.append('imports')
                    break

            # Check if file calls functions from changed file
            calls = data.get('calls', [])
            called_funcs = changed_def_names & set(calls)
            if called_funcs:
                # Check if any called functions had signature changes
                sig_changed_funcs = {c['name'] for c in sig_changes}
                if called_funcs & sig_changed_funcs:
                    reasons.append(f'calls_modified: {", ".join(called_funcs & sig_changed_funcs)}')
                else:
                    reasons.append(f'calls: {", ".join(called_funcs)}')

            if reasons:
                impacted[filepath] = {
                    'reasons': reasons,
                    'severity': 'high' if any('modified' in r for r in reasons) else 'medium'
                }

        return impacted

    def calculate_risk_level(self):
        """Calculate overall risk level based on changes (enhanced)"""
        # Count total impacted files
        total_impacted = 0
        high_severity_count = 0

        for changed_file, impacts in self.file_impacts.items():
            total_impacted += len(impacts)
            # Count high severity impacts (signature changes)
            for filepath, impact_data in impacts.items():
                if impact_data.get('severity') == 'high':
                    high_severity_count += 1

        # Also check for signature changes
        has_sig_changes = any(
            self.dependency_graph.get(f, {}).get('signature_changes', [])
            for f in self.changed_files
        )

        # Check for circular dependencies
        circular = self.detect_circular_dependencies()

        # Risk assessment with enhanced criteria
        if circular or high_severity_count > 5 or total_impacted > 15:
            return 'high', '🔴'
        elif has_sig_changes or high_severity_count > 0 or total_impacted > 5:
            return 'medium', '🟡'
        else:
            return 'low', '🟢'

    def detect_circular_dependencies(self):
        """Detect circular dependencies (basic check)"""
        # Simple cycle detection using DFS
        def has_cycle(node, visited, rec_stack):
            visited.add(node)
            rec_stack.add(node)

            if node in self.dependency_graph:
                neighbors = self.dependency_graph[node].get('imports', [])
                for neighbor in neighbors:
                    # Find file that provides this import
                    for filepath in self.dependency_graph:
                        if neighbor in filepath or Path(filepath).stem == neighbor:
                            if filepath not in visited:
                                if has_cycle(filepath, visited, rec_stack):
                                    return True
                            elif filepath in rec_stack:
                                return True

            rec_stack.remove(node)
            return False

        visited = set()
        for node in self.dependency_graph:
            if node not in visited:
                if has_cycle(node, set(), set()):
                    return True
        return False

    def generate_report(self):
        """Generate build health report"""
        self.changed_files = self.detect_changed_files()

        if not self.changed_files:
            return "🟢 No changes detected, build health nominal"

        # Analyze each changed file
        for changed_file in self.changed_files:
            # Skip non-code files
            if self.detect_language(changed_file) == 'unknown':
                continue

            # Analyze dependencies
            self.analyze_dependencies(changed_file)

            # Find impacted files
            impacted = self.find_impacted_files(changed_file)
            self.file_impacts[changed_file] = impacted

        # Save updated dependency graph
        self.save_dependency_graph()

        # Calculate risk
        risk_level, emoji = self.calculate_risk_level()

        # Generate report with enhanced detail
        total_impacted = sum(len(impacts) for impacts in self.file_impacts.values())

        if risk_level == 'low':
            report = f"{emoji} Safe: {len(self.changed_files)} file(s) changed, low impact"
        elif risk_level == 'medium':
            report = f"{emoji} Caution: {total_impacted} file(s) potentially affected\n"
            # Show signature changes if any
            sig_changes_found = []
            for changed_file in self.changed_files:
                sigs = self.dependency_graph.get(changed_file, {}).get('signature_changes', [])
                if sigs:
                    sig_changes_found.extend([(changed_file, s) for s in sigs])

            if sig_changes_found:
                report += f"   ⚠️ Signature changes detected:\n"
                for filepath, sig in sig_changes_found[:2]:
                    report += f"      {Path(filepath).name}: {sig['name']}\n"

            # Show top impacted files
            for changed, impacted in list(self.file_impacts.items())[:3]:
                if impacted:
                    report += f"   Changed: {changed}\n"
                    for imp_file, impact_data in list(impacted.items())[:3]:
                        severity_icon = "🔸" if impact_data['severity'] == 'high' else "→"
                        reasons = ", ".join(impact_data['reasons'])
                        report += f"   {severity_icon} {imp_file} ({reasons})\n"
        else:  # high
            if self.detect_circular_dependencies():
                report = f"{emoji} High Risk: Circular dependency detected, {total_impacted}+ file(s) affected\n"
            else:
                report = f"{emoji} High Risk: {total_impacted}+ file(s) affected\n"

            # Show signature changes
            for changed_file in self.changed_files:
                sigs = self.dependency_graph.get(changed_file, {}).get('signature_changes', [])
                if sigs:
                    report += f"   ⚠️ Breaking changes in {Path(changed_file).name}:\n"
                    for sig in sigs[:2]:
                        report += f"      {sig['name']}: {sig['old']} → {sig['new']}\n"

            # Show impacted files with reasons
            for changed, impacted in list(self.file_impacts.items())[:2]:
                if impacted:
                    report += f"   Changed: {changed}\n"
                    for imp_file, impact_data in list(impacted.items())[:5]:
                        severity_icon = "🔸" if impact_data['severity'] == 'high' else "→"
                        reasons = ", ".join(impact_data['reasons'])
                        report += f"   {severity_icon} {imp_file} ({reasons})\n"

        return report


def main():
    """Entry point for build health monitoring"""
    import sys

    # Get working directory from command line arg
    cwd = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()

    monitor = BuildHealthMonitor(cwd)
    report = monitor.generate_report()

    print(report)


if __name__ == "__main__":
    main()
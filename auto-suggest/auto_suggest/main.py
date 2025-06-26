#!/usr/bin/env python3
"""Simple auto-suggest tool using llm."""

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


def get_readme_content(target_dir: Path) -> str:
    """Get README content from target directory."""
    readme_files = ["README.md", "README.txt", "README", "readme.md", "readme.txt", "readme"]
    
    for readme_name in readme_files:
        readme_path = target_dir / readme_name
        if readme_path.exists() and readme_path.is_file():
            try:
                with open(readme_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()[:2000]  # Limit to first 2000 chars
                    return content
            except Exception:
                continue
    
    return ""




def get_zsh_history(limit: int = 20) -> List[str]:
    """Get recent zsh history commands."""
    history_file = Path.home() / ".zsh_history"
    if not history_file.exists():
        return []
    
    try:
        with open(history_file, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        
        # Parse zsh history format and get unique commands
        commands = []
        for line in reversed(lines[-limit*2:]):  # Get more to filter duplicates
            if line.startswith(": "):
                # Remove timestamp: ": 1234567890:0;command"
                cmd = line.split(";", 1)[-1].strip()
                if cmd and cmd not in commands:
                    commands.append(cmd)
        
        return commands[:limit]
    except Exception:
        return []


def build_context(target_dir: Path, history_limit: int) -> str:
    """Build context string for LLM."""
    readme_content = get_readme_content(target_dir)
    recent_commands = get_zsh_history(history_limit)
    
    context = f"Current directory: {target_dir.absolute()}\n"
    context += f"Directory name: {target_dir.name}\n\n"
    
    if readme_content:
        context += f"README content:\n{readme_content}\n\n"
    
    if recent_commands:
        context += "Recent commands:\n"
        for i, cmd in enumerate(recent_commands[:10], 1):
            context += f"{i}. {cmd}\n"
        context += "\n"
    
    return context


def generate_suggestions(context: str, partial_input: str = "") -> Optional[str]:
    """Generate suggestions using llm."""
    if partial_input:
        prompt = f"""Based on this project context and partial input, suggest 3-5 practical command completions:

{context}

Partial input: {partial_input}

For each command completion, provide:
1. The complete command (starting with or extending the partial input)
2. A brief explanation of what it does and what will happen when executed (In Japanese)

Format: `command` - Explanation of what this command does and its expected outcome

Focus on completing or extending the partial input "{partial_input}" with relevant commands for the current directory context."""
    else:
        prompt = f"""Based on this project context, suggest 3-5 practical next commands:

{context}

For each command, provide:
1. The exact command
2. A brief explanation of what it does and what will happen when executed (In Japanese)

Format: `command` - Explanation of what this command does and its expected outcome

Focus on common development tasks relevant to the current directory and recent command history."""
    
    try:
        result = subprocess.run(
            ["llm", prompt],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "Error: Failed to generate suggestions. Make sure 'llm' is installed."
    except FileNotFoundError:
        return "Error: 'llm' command not found. Install from https://github.com/simonw/llm"


def extract_commands_from_suggestions(suggestions: str) -> List[str]:
    """Extract command strings with explanations from LLM suggestions."""
    commands = []
    seen_commands = set()  # Track seen commands to avoid duplicates
    lines = suggestions.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        command_entry = None
        
        # Priority 1: Match pattern: `command` - explanation
        match = re.search(r'`([^`]+)`\s*-\s*(.+)', line)
        if match:
            cmd = match.group(1).strip()
            explanation = match.group(2).strip()
            command_entry = f"{cmd} → {explanation}"
        
        # Priority 2: Match numbered lists with backticks: "1. `command` - explanation"
        elif re.search(r'^\d+\..*`([^`]+)`', line):
            # Extract everything after the number
            content_after_num = re.sub(r'^\d+\.[\s*]*\*?\*?', '', line).strip()
            
            # Try to extract command and explanation
            backtick_match = re.search(r'`([^`]+)`(?:\s*-\s*(.+))?', content_after_num)
            if backtick_match:
                cmd = backtick_match.group(1).strip()
                explanation = backtick_match.group(2)
                if explanation:
                    command_entry = f"{cmd} → {explanation.strip()}"
                else:
                    command_entry = cmd
        
        # Priority 3: Match simple numbered lists: "1. command - explanation"
        elif re.match(r'^\d+\.[\s]*([^\s].*)', line):
            content_after_num = re.sub(r'^\d+\.[\s]*', '', line).strip()
            content_after_num = re.sub(r'\*\*|\*', '', content_after_num)  # Remove markdown
            
            if content_after_num and not content_after_num.startswith('Error:'):
                # Try to split on " - " to separate command and explanation
                if ' - ' in content_after_num:
                    parts = content_after_num.split(' - ', 1)
                    cmd = parts[0].strip()
                    explanation = parts[1].strip()
                    command_entry = f"{cmd} → {explanation}"
                else:
                    # No explanation separator found, treat whole thing as command
                    command_entry = content_after_num
        
        # Add to results if we found something and haven't seen it before
        if command_entry:
            # Extract just the command part for duplicate checking
            cmd_for_dedup = command_entry.split(' → ')[0] if ' → ' in command_entry else command_entry
            if cmd_for_dedup not in seen_commands:
                seen_commands.add(cmd_for_dedup)
                commands.append(command_entry)
    
    return commands




def main():
    """Auto-suggest next command based on directory context and command history."""
    parser = argparse.ArgumentParser(description="Auto-suggest next command based on directory context and command history.")
    parser.add_argument("target_dir", nargs="?", default=".", help="Target directory (default: current directory)")
    parser.add_argument("-c", "--history", type=int, default=20, help="Number of history commands to include")
    parser.add_argument("--list-only", action="store_true", help="Output only command list for shell processing")
    parser.add_argument("--partial", type=str, help="Partial command input to complete")
    
    args = parser.parse_args()
    target_dir = Path(args.target_dir)
    
    if not target_dir.exists():
        print(f"Error: Directory {target_dir} does not exist.", file=sys.stderr)
        sys.exit(1)
    
    if not args.list_only:
        print(f"Analyzing: {target_dir.absolute()}", file=sys.stderr)
    
    context = build_context(target_dir, args.history)
    suggestions = generate_suggestions(context, args.partial or "")
    
    if not suggestions or suggestions.startswith("Error:"):
        if not args.list_only:
            print("No suggestions generated.", file=sys.stderr)
        sys.exit(1)
    
    # Extract commands from suggestions
    commands = extract_commands_from_suggestions(suggestions)
    
    if args.list_only:
        # Output just the command list for shell processing
        for cmd in commands:
            print(cmd)
    else:
        # Print suggestions in original format
        print("\n" + "="*50, file=sys.stderr)
        print("COMMAND SUGGESTIONS", file=sys.stderr)
        print("="*50, file=sys.stderr)
        print(suggestions, file=sys.stderr)


if __name__ == "__main__":
    main()
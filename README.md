# Auto-Suggest ZSH Plugin

An AI-powered zsh plugin that suggests next commands based on directory context and command history.

## Dependencies

- `uv` - Python package manager
- `fzf` - Fuzzy finder
- `llm` - Simon Willison's LLM CLI tool

## Installation

### Using Sheldon

```toml
# Add to ~/.config/sheldon/plugins.toml
[plugins.auto-suggest]
github = "YusukeShimizu/auto-suggest"
```

## Usage

### Basic Usage

```bash
# Suggest commands for current directory
suggest

# Suggest commands for specific directory
suggest /path/to/project

# Specify number of history commands to include
suggest --history 30
```

### Partial Input Completion (New Feature)

```bash
# Type partial command then complete
git <Ctrl+G>     # Show git command completions
npm <Ctrl+G>     # Show npm command completions
docker <Ctrl+G>  # Show docker command completions
```

### Shortcuts

- `sg` - Alias for `suggest`
- `Ctrl+G` - Key binding to start suggestion (completion mode if partial input exists)

### Operation Steps

1. **Normal suggestion**: Press `Ctrl+G` on empty command line
2. **Partial completion**: Type part of command then press `Ctrl+G`
3. **Select with fzf**: Use arrow keys to select and press `Enter` to confirm
4. **Execute**: Selected command is inserted into input buffer, edit if needed then press `Enter` to execute

### Configuration

Customize behavior with environment variables:

```bash
# Number of history commands (default: 20)
export AUTO_SUGGEST_HISTORY_LIMIT=30

# fzf height (default: 40%)
export AUTO_SUGGEST_FZF_HEIGHT=50%
```

## Features

- **Context-aware**: Analyzes README files and directory names
- **History integration**: Considers recent zsh command history
- **Interactive selection**: User-friendly interface with fzf
- **Japanese explanations**: Command descriptions in Japanese
- **Partial completion**: Complete commands based on partial input
- **zsh integration**: Directly inserts selected commands into input buffer

## How it Works

1. Reads README files from current directory
2. Retrieves recent commands from zsh history
3. Generates context-based suggestions using LLM
4. Interactive selection with fzf
5. Inserts selected command into zsh input buffer

## Troubleshooting

### Error: uv not found
```bash
# macOS
brew install uv

# Other platforms
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Error: fzf not found
```bash
# macOS
brew install fzf

# Ubuntu/Debian
sudo apt install fzf
```

### Error: llm not found
```bash
# Install with pipx
pipx install llm

# Or with pip
pip install llm
```

## License

MIT License
#!/usr/bin/env zsh
# Auto-suggest zsh plugin
# Provides intelligent command suggestions based on directory context and command history

# Plugin directory detection
0="${${ZERO:-${0:#$ZSH_ARGZERO}}:-${(%):-%N}}"
AUTO_SUGGEST_PLUGIN_DIR="${0:A:h}"

# Configuration
AUTO_SUGGEST_HISTORY_LIMIT=${AUTO_SUGGEST_HISTORY_LIMIT:-20}
AUTO_SUGGEST_FZF_HEIGHT=${AUTO_SUGGEST_FZF_HEIGHT:-40%}

# Auto-suggest function that puts selected command in input buffer
suggest() {
    local python_script="$AUTO_SUGGEST_PLUGIN_DIR/auto-suggest/auto_suggest/main.py"
    
    # Check if uv is available
    if ! command -v uv &> /dev/null; then
        echo "Error: uv not found. Please install uv first." >&2
        return 1
    fi
    
    # Check if fzf is available
    if ! command -v fzf &> /dev/null; then
        echo "Error: fzf not found. Please install fzf first." >&2
        return 1
    fi
    
    # Check if Python script exists
    if [[ ! -f "$python_script" ]]; then
        echo "Error: Python script not found at $python_script" >&2
        echo "Make sure the plugin is properly installed." >&2
        return 1
    fi
    
    # Get command list and use fzf for selection
    local selected_cmd
    selected_cmd=$(uv run "$python_script" --list-only --history="$AUTO_SUGGEST_HISTORY_LIMIT" "$@" 2>/dev/null | fzf --prompt="Select command: " --height="$AUTO_SUGGEST_FZF_HEIGHT" --preview-window=wrap)
    
    if [[ -n "$selected_cmd" ]]; then
        echo "Selected: $selected_cmd" >&2
        # Extract just the command part (before explanation)
        local cmd_only=$(echo "$selected_cmd" | sed 's/ →.*$//' | sed 's/ (.*$//')
        
        # Put command in zsh input buffer
        print -z "$cmd_only"
    else
        echo "No command selected." >&2
        return 1
    fi
}

# Alias for shorter command
alias sg='suggest'

# Key binding for Ctrl+G to trigger suggestion
bindkey '^G' _auto_suggest_widget

# Widget function for key binding
_auto_suggest_widget() {
    suggest
    zle reset-prompt
}
zle -N _auto_suggest_widget

# Auto-completion disabled to prevent errors
# Enable manually if needed by uncommenting:
# if [[ -n "${_comps}" ]] && (( $+functions[compdef] )); then
#     _suggest_completion() {
#         _arguments \
#             '1:directory:_directories' \
#             '--history[Number of history commands to include]:count:' \
#             '--list-only[Output only command list]'
#     }
#     compdef _suggest_completion suggest
# fi
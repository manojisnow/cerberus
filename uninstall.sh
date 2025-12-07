#!/bin/bash
set -e

# Cerberus Uninstallation Script

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m'

CERBERUS_HOME="$HOME/.cerberus"
FORCE=false

# Parse arguments
for arg in "$@"; do
    case $arg in
        --force)
            FORCE=true
            shift
            ;;
    esac
done

log() {
    echo -e "${BLUE}[CERBERUS]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Helper for sudo
run_priv() {
    if [ -w "$(dirname "$1")" ]; then
        "$@"
    else
        sudo "$@"
    fi
}

# Prompt helper
confirm() {
    if [ "$FORCE" = true ]; then
        return 0
    fi
    read -p "$1 [y/N] " response
    case "$response" in
        [yY][eE][sS]|[yY]) 
            return 0 
            ;;
        *)
            return 1
            ;;
    esac
}

uninstall_cerberus() {
    log "Uninstalling Cerberus..."
    
    # Remove home directory
    if [ -d "$CERBERUS_HOME" ]; then
        rm -rf "$CERBERUS_HOME"
        log "Removed $CERBERUS_HOME"
    fi
    
    # Find and remove binary
    if command -v cerberus &> /dev/null; then
        BIN_PATH=$(which cerberus)
        log "Removing binary at $BIN_PATH"
        run_priv rm "$BIN_PATH"
    else
        warn "Cerberus binary not found in PATH"
    fi
}

uninstall_tools() {
    TOOLS=("trivy" "grype" "gitleaks" "hadolint" "kubescape")
    
    echo -e "\n${YELLOW}The following tools were likely installed by Cerberus:${NC}"
    echo "${TOOLS[*]} spotbugs"
    echo -e "${YELLOW}Removing them might break other workflows if you use them independently.${NC}"
    
    if confirm "Do you want to remove these tools?"; then
        for tool in "${TOOLS[@]}"; do
            if command -v "$tool" &> /dev/null; then
                TOOL_PATH=$(which "$tool")
                log "Removing $tool at $TOOL_PATH"
                run_priv rm "$TOOL_PATH"
            fi
        done
        
        # Remove SpotBugs symlink
        if [ -L "/usr/local/bin/spotbugs" ]; then
            log "Removing SpotBugs symlink"
            run_priv rm "/usr/local/bin/spotbugs"
        elif [ -L "$HOME/.local/bin/spotbugs" ]; then
            log "Removing SpotBugs symlink"
            rm "$HOME/.local/bin/spotbugs"
        fi
    else
        log "Skipping tool removal"
    fi
}

uninstall_python_deps() {
    echo -e "\n${YELLOW}Python dependencies (requirements.txt) were installed via pip.${NC}"
    
    if confirm "Do you want to uninstall Python dependencies?"; then
        log "Uninstalling Python dependencies..."
        if [ -f "requirements.txt" ]; then
            pip3 uninstall -r requirements.txt -y || warn "Failed to uninstall some dependencies"
        else
            # Try to find requirements.txt in source if available, else skip
            warn "requirements.txt not found, skipping pip uninstall"
        fi
    else
        log "Skipping Python dependency removal"
    fi
}

main() {
    echo -e "${RED}!!! Cerberus Uninstaller !!!${NC}"
    echo "This will remove Cerberus and optionally its dependencies."
    
    if ! confirm "Are you sure you want to proceed?"; then
        echo "Aborted."
        exit 0
    fi
    
    uninstall_cerberus
    uninstall_tools
    uninstall_python_deps
    
    success "Uninstallation complete."
}

main

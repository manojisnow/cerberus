#!/bin/bash
set -e

# Cerberus Uninstallation Script
# Removes ~/.cerberus directory

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

CERBERUS_HOME="$HOME/.cerberus"

log() { echo -e "${BLUE}[CERBERUS]${NC} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }

main() {
    echo -e "${RED}!!! Cerberus Uninstaller !!!${NC}"
    echo "This will remove Cerberus and all its isolated dependencies from $CERBERUS_HOME."
    
    read -p "Are you sure? [y/N] " response
    case "$response" in
        [yY][eE][sS]|[yY]) 
            ;;
        *)
            echo "Aborted."
            exit 0
            ;;
    esac
    
    if [ -d "$CERBERUS_HOME" ]; then
        log "Removing $CERBERUS_HOME..."
        rm -rf "$CERBERUS_HOME"
        success "Uninstallation complete."
    else
        log "Cerberus directory not found."
    fi
    
    echo "Note: You may need to remove $CERBERUS_HOME/bin from your PATH in .bashrc/.zshrc"
}

main

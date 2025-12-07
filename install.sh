#!/bin/bash
set -e

# Cerberus Installation Script
# Installs Cerberus and all required security tools

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Default install directory
INSTALL_DIR="/usr/local/bin"
CERBERUS_HOME="$HOME/.cerberus"

# Versions (matching Dockerfile)
TRIVY_VERSION="v0.48.0"
GRYPE_VERSION="v0.74.0"
GITLEAKS_VERSION="8.18.1"
HADOLINT_VERSION="v2.12.0"
KUBEAUDIT_VERSION="0.22.1"
SPOTBUGS_VERSION="4.8.3"

log() {
    echo -e "${BLUE}[CERBERUS]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Check prerequisites
check_prereqs() {
    log "Checking prerequisites..."
    
    if ! command -v python3 &> /dev/null; then
        error "Python 3 is required but not installed."
    fi
    
    # Check Python version (need 3.11+)
    python_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    if (( $(echo "$python_version < 3.11" | bc -l) )); then
        log "Warning: Python 3.11+ is recommended. Found $python_version"
    fi

    if ! command -v java &> /dev/null; then
        log "Warning: Java is not installed. SpotBugs scanning will be disabled."
    fi

    if ! command -v git &> /dev/null; then
        error "Git is required but not installed."
    fi
}

# Detect OS and Arch
detect_platform() {
    OS="$(uname -s)"
    ARCH="$(uname -m)"
    
    case "$OS" in
        Linux)
            OS_TYPE="linux"
            ;;
        Darwin)
            OS_TYPE="darwin"
            ;;
        *)
            error "Unsupported OS: $OS"
            ;;
    esac
    
    case "$ARCH" in
        x86_64)
            ARCH_TYPE="amd64"
            GITLEAKS_ARCH="x64"
            ;;
        arm64|aarch64)
            ARCH_TYPE="arm64"
            GITLEAKS_ARCH="arm64"
            ;;
        *)
            error "Unsupported architecture: $ARCH"
            ;;
    esac
    
    log "Detected platform: $OS_TYPE/$ARCH_TYPE"
}

# Install Python dependencies
install_python_deps() {
    log "Installing Python dependencies..."
    pip3 install --user -r requirements.txt
}

# Install Tools
install_tools() {
    log "Installing security tools to $INSTALL_DIR..."
    
    # Create temp dir
    TMP_DIR=$(mktemp -d)
    cd "$TMP_DIR"
    
    # 1. Trivy
    if ! command -v trivy &> /dev/null; then
        log "Installing Trivy $TRIVY_VERSION..."
        curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b "$INSTALL_DIR" "$TRIVY_VERSION"
    fi
    
    # 2. Grype
    if ! command -v grype &> /dev/null; then
        log "Installing Grype $GRYPE_VERSION..."
        curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh -s -- -b "$INSTALL_DIR" "$GRYPE_VERSION"
    fi
    
    # 3. Gitleaks
    if ! command -v gitleaks &> /dev/null; then
        log "Installing Gitleaks $GITLEAKS_VERSION..."
        wget -q "https://github.com/gitleaks/gitleaks/releases/download/v${GITLEAKS_VERSION}/gitleaks_${GITLEAKS_VERSION}_${OS_TYPE}_${GITLEAKS_ARCH}.tar.gz"
        tar -xzf "gitleaks_${GITLEAKS_VERSION}_${OS_TYPE}_${GITLEAKS_ARCH}.tar.gz"
        sudo mv gitleaks "$INSTALL_DIR/"
    fi
    
    # 4. Hadolint
    if ! command -v hadolint &> /dev/null; then
        log "Installing Hadolint $HADOLINT_VERSION..."
        # Hadolint naming convention varies
        if [ "$OS_TYPE" = "darwin" ]; then
            wget -q "https://github.com/hadolint/hadolint/releases/download/${HADOLINT_VERSION}/hadolint-Darwin-x86_64" -O hadolint
        else
            wget -q "https://github.com/hadolint/hadolint/releases/download/${HADOLINT_VERSION}/hadolint-Linux-x86_64" -O hadolint
        fi
        chmod +x hadolint
        sudo mv hadolint "$INSTALL_DIR/"
    fi
    
    # 5. Kubescape
    if ! command -v kubescape &> /dev/null; then
        log "Installing Kubescape..."
        curl -s https://raw.githubusercontent.com/kubescape/kubescape/master/install.sh | /bin/bash
    fi
    
    # 6. SpotBugs (Manual install to ~/.cerberus/spotbugs)
    log "Installing SpotBugs $SPOTBUGS_VERSION..."
    mkdir -p "$CERBERUS_HOME/spotbugs"
    wget -q "https://github.com/spotbugs/spotbugs/releases/download/${SPOTBUGS_VERSION}/spotbugs-${SPOTBUGS_VERSION}.tgz"
    tar -xzf "spotbugs-${SPOTBUGS_VERSION}.tgz" -C "$CERBERUS_HOME/spotbugs" --strip-components=1
    
    # Link SpotBugs
    sudo ln -sf "$CERBERUS_HOME/spotbugs/bin/spotbugs" "$INSTALL_DIR/spotbugs"
    
    # Cleanup
    cd - > /dev/null
    rm -rf "$TMP_DIR"
}

# Setup Cerberus
setup_cerberus() {
    log "Setting up Cerberus..."
    
    # Copy source code to ~/.cerberus/src
    mkdir -p "$CERBERUS_HOME/src"
    cp -r . "$CERBERUS_HOME/src/"
    
    # Create wrapper script
    cat > cerberus_wrapper <<EOF
#!/bin/bash
export PYTHONPATH="$CERBERUS_HOME/src"
python3 "$CERBERUS_HOME/src/cerberus.py" "\$@"
EOF
    
    chmod +x cerberus_wrapper
    sudo mv cerberus_wrapper "$INSTALL_DIR/cerberus"
}

# Main
main() {
    log "Starting Cerberus installation..."
    
    check_prereqs
    detect_platform
    install_python_deps
    install_tools
    setup_cerberus
    
    success "Cerberus installed successfully!"
    echo "Run 'cerberus --help' to get started."
}

main

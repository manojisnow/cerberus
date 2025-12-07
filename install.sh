#!/bin/bash
set -e

# Cerberus Installation Script (Isolated)
# Installs Cerberus and all tools into ~/.cerberus

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

CERBERUS_HOME="$HOME/.cerberus"
INSTALL_DIR="$CERBERUS_HOME/bin"
VENV_DIR="$CERBERUS_HOME/venv"
SRC_DIR="$CERBERUS_HOME/src"

# Versions (matching Dockerfile)
TRIVY_VERSION="v0.48.0"
GRYPE_VERSION="v0.74.0"
GITLEAKS_VERSION="8.18.1"
HADOLINT_VERSION="v2.12.0"
KUBEAUDIT_VERSION="0.22.1"
SPOTBUGS_VERSION="4.8.3"

log() { echo -e "${BLUE}[CERBERUS]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }

# Check prerequisites
check_prereqs() {
    log "Checking prerequisites..."
    command -v python3 >/dev/null || error "Python 3 required"
    command -v git >/dev/null || error "Git required"
    
    if ! command -v java >/dev/null; then
        log "Warning: Java not found. SpotBugs scanning will be disabled."
    fi
}

detect_platform() {
    OS="$(uname -s)"
    ARCH="$(uname -m)"
    
    case "$OS" in
        Linux) OS_TYPE="linux" ;;
        Darwin) OS_TYPE="darwin" ;;
        *) error "Unsupported OS: $OS" ;;
    esac
    
    case "$ARCH" in
        x86_64) ARCH_TYPE="amd64"; GITLEAKS_ARCH="x64" ;;
        arm64|aarch64) ARCH_TYPE="arm64"; GITLEAKS_ARCH="arm64" ;;
        *) error "Unsupported architecture: $ARCH" ;;
    esac
    
    log "Detected platform: $OS_TYPE/$ARCH_TYPE"
}

setup_dirs() {
    log "Creating directory structure in $CERBERUS_HOME..."
    rm -rf "$CERBERUS_HOME"
    mkdir -p "$INSTALL_DIR" "$SRC_DIR"
}

setup_venv() {
    log "Setting up Python virtual environment..."
    python3 -m venv "$VENV_DIR"
    "$VENV_DIR/bin/pip" install --upgrade pip
    "$VENV_DIR/bin/pip" install -r requirements.txt
}

install_tools() {
    log "Installing tools to $INSTALL_DIR..."
    
    # Create temp dir
    TMP_DIR=$(mktemp -d)
    cd "$TMP_DIR"
    
    # Trivy
    log "Installing Trivy..."
    curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b "$INSTALL_DIR" "$TRIVY_VERSION"

    # Grype
    log "Installing Grype..."
    curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh -s -- -b "$INSTALL_DIR" "$GRYPE_VERSION"

    # Gitleaks
    log "Installing Gitleaks..."
    wget -q "https://github.com/gitleaks/gitleaks/releases/download/v${GITLEAKS_VERSION}/gitleaks_${GITLEAKS_VERSION}_${OS_TYPE}_${GITLEAKS_ARCH}.tar.gz"
    tar -xzf "gitleaks_${GITLEAKS_VERSION}_${OS_TYPE}_${GITLEAKS_ARCH}.tar.gz"
    mv gitleaks "$INSTALL_DIR/"

    # Hadolint
    log "Installing Hadolint..."
    if [ "$OS_TYPE" = "darwin" ]; then
        wget -q "https://github.com/hadolint/hadolint/releases/download/${HADOLINT_VERSION}/hadolint-Darwin-x86_64" -O "$INSTALL_DIR/hadolint"
    else
        wget -q "https://github.com/hadolint/hadolint/releases/download/${HADOLINT_VERSION}/hadolint-Linux-x86_64" -O "$INSTALL_DIR/hadolint"
    fi
    chmod +x "$INSTALL_DIR/hadolint"

    # Kubescape
    log "Installing Kubescape..."
    # Kubescape install script tries to install to ~/.kubescape/bin
    curl -s https://raw.githubusercontent.com/kubescape/kubescape/master/install.sh | /bin/bash
    if [ -f "$HOME/.kubescape/bin/kubescape" ]; then
        ln -sf "$HOME/.kubescape/bin/kubescape" "$INSTALL_DIR/kubescape"
    fi

    # SpotBugs
    log "Installing SpotBugs..."
    mkdir -p "$CERBERUS_HOME/spotbugs"
    wget -q "https://github.com/spotbugs/spotbugs/releases/download/${SPOTBUGS_VERSION}/spotbugs-${SPOTBUGS_VERSION}.tgz"
    tar -xzf "spotbugs-${SPOTBUGS_VERSION}.tgz" -C "$CERBERUS_HOME/spotbugs" --strip-components=1
    ln -sf "$CERBERUS_HOME/spotbugs/bin/spotbugs" "$INSTALL_DIR/spotbugs"
    
    # Cleanup
    cd - > /dev/null
    rm -rf "$TMP_DIR"
}

setup_cerberus() {
    log "Installing Cerberus..."
    # Copy source code (excluding .git and other artifacts)
    # We use a loop to copy specific files/dirs to avoid .git permission issues
    cp cerberus.py "$SRC_DIR/"
    cp config.yaml "$SRC_DIR/"
    cp -r scanners "$SRC_DIR/"
    cp -r utils "$SRC_DIR/"
    
    # Create wrapper
    cat > "$INSTALL_DIR/cerberus" <<EOF
#!/bin/bash
export PATH="$INSTALL_DIR:\$PATH"
source "$VENV_DIR/bin/activate"
export PYTHONPATH="$SRC_DIR"
python3 "$SRC_DIR/cerberus.py" "\$@"
EOF
    chmod +x "$INSTALL_DIR/cerberus"
}

main() {
    check_prereqs
    detect_platform
    setup_dirs
    setup_venv
    install_tools
    setup_cerberus
    
    success "Cerberus installed to $CERBERUS_HOME"
    echo "Please add the following to your shell config (.bashrc/.zshrc):"
    echo "export PATH=\"$INSTALL_DIR:\$PATH\""
}

main

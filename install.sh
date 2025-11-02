#!/bin/bash
# Agent Cube CLI Installer
# Usage: curl -fsSL https://raw.githubusercontent.com/aetheronhq/agent-cube/main/install.sh | bash

set -e

VERSION="1.0.0"
INSTALL_DIR="$HOME/.agent-cube"
BIN_DIR="$HOME/.local/bin"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

print_error() {
    echo -e "${RED}❌ Error: $1${NC}" >&2
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

echo -e "${CYAN}╔════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║     Agent Cube CLI Installer          ║${NC}"
echo -e "${CYAN}║     Version ${VERSION}                      ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════╝${NC}"
echo ""

# Check prerequisites
print_info "Checking prerequisites..."

if ! command -v curl &> /dev/null; then
    print_error "curl is not installed"
    echo "curl is required to download files"
    exit 1
fi

if ! command -v jq &> /dev/null; then
    print_warning "jq is not installed (required for agent output parsing)"
    echo "Install jq: brew install jq (macOS) or apt-get install jq (Linux)"
    echo ""
fi

if ! command -v cursor-agent &> /dev/null; then
    print_warning "cursor-agent is not installed (required to run agents)"
    echo "Install cursor-agent: npm install -g @cursor/cli"
    echo "Then authenticate: cursor-agent login"
    echo ""
fi

print_success "Prerequisites check complete"
echo ""

# Create installation directory
print_info "Installing to $INSTALL_DIR..."

if [ -d "$INSTALL_DIR" ]; then
    print_warning "Removing existing installation"
    rm -rf "$INSTALL_DIR"
fi

mkdir -p "$INSTALL_DIR/scripts/automation"

# Install from local repository
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ ! -f "$SCRIPT_DIR/scripts/cube" ]; then
    print_error "scripts/cube not found. Please run this from the cloned agent-cube repository."
    exit 1
fi

print_info "Installing from local repository..."

cp "$SCRIPT_DIR/scripts/cube" "$INSTALL_DIR/scripts/cube"
chmod +x "$INSTALL_DIR/scripts/cube"

for script in launch-dual-writers.sh launch-judge-panel.sh send-writer-feedback.sh stream-agent.sh; do
    if [ ! -f "$SCRIPT_DIR/scripts/automation/$script" ]; then
        print_error "scripts/automation/$script not found"
        exit 1
    fi
    cp "$SCRIPT_DIR/scripts/automation/$script" "$INSTALL_DIR/scripts/automation/$script"
    chmod +x "$INSTALL_DIR/scripts/automation/$script"
done

# Copy documentation
[ -f "$SCRIPT_DIR/AGENT_CUBE.md" ] && cp "$SCRIPT_DIR/AGENT_CUBE.md" "$INSTALL_DIR/AGENT_CUBE.md"
[ -f "$SCRIPT_DIR/AGENT_CUBE_AUTOMATION.md" ] && cp "$SCRIPT_DIR/AGENT_CUBE_AUTOMATION.md" "$INSTALL_DIR/AGENT_CUBE_AUTOMATION.md"

print_success "Files installed from local repository"
echo ""

# Create bin directory if it doesn't exist
mkdir -p "$BIN_DIR"

# Create symlink
print_info "Creating symlink in $BIN_DIR..."

if [ -L "$BIN_DIR/cube" ] || [ -f "$BIN_DIR/cube" ]; then
    rm -f "$BIN_DIR/cube"
fi

ln -s "$INSTALL_DIR/scripts/cube" "$BIN_DIR/cube"
chmod +x "$INSTALL_DIR/scripts/cube"

print_success "Symlink created: $BIN_DIR/cube -> $INSTALL_DIR/scripts/cube"
echo ""

# Check PATH
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    print_warning "$BIN_DIR is not in your PATH"
    echo ""
    echo "Add this line to your shell config (~/.zshrc or ~/.bashrc):"
    echo -e "${YELLOW}export PATH=\"\$HOME/.local/bin:\$PATH\"${NC}"
    echo ""
    echo "Then reload your shell:"
    echo -e "${YELLOW}source ~/.zshrc${NC}  # or source ~/.bashrc"
    echo ""
else
    print_success "$BIN_DIR is in your PATH"
fi

# Installation complete
echo ""
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Installation Complete! 🎉            ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""
echo "Get started:"
echo -e "  ${CYAN}cube --help${NC}        Show all commands"
echo -e "  ${CYAN}cube version${NC}       Show version"
echo -e "  ${CYAN}cube sessions${NC}      List active sessions"
echo ""
echo "Documentation:"
echo -e "  ${CYAN}cat $INSTALL_DIR/AGENT_CUBE.md${NC}"
echo ""
echo "To uninstall:"
echo -e "  ${YELLOW}rm -rf $INSTALL_DIR $BIN_DIR/cube${NC}"
echo ""


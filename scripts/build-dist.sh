#!/bin/bash
# build-dist.sh - Create distribution package for Agent Cube CLI

set -e

VERSION="1.0.0"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DIST_DIR="$PROJECT_ROOT/dist"

echo "📦 Building Agent Cube CLI v${VERSION} distribution package..."
echo ""

# Clean and create dist directory
rm -rf "$DIST_DIR"
mkdir -p "$DIST_DIR/agent-cube"

# Copy necessary files
echo "📋 Copying files..."
mkdir -p "$DIST_DIR/agent-cube/scripts/automation"

cp "$PROJECT_ROOT/scripts/cube" "$DIST_DIR/agent-cube/scripts/"
cp "$PROJECT_ROOT/scripts/automation/launch-dual-writers.sh" "$DIST_DIR/agent-cube/scripts/automation/"
cp "$PROJECT_ROOT/scripts/automation/launch-judge-panel.sh" "$DIST_DIR/agent-cube/scripts/automation/"
cp "$PROJECT_ROOT/scripts/automation/send-writer-feedback.sh" "$DIST_DIR/agent-cube/scripts/automation/"
cp "$PROJECT_ROOT/scripts/automation/stream-agent.sh" "$DIST_DIR/agent-cube/scripts/automation/"

# Copy documentation
cp "$PROJECT_ROOT/AGENT_CUBE.md" "$DIST_DIR/agent-cube/" 2>/dev/null || true
cp "$PROJECT_ROOT/AGENT_CUBE_AUTOMATION.md" "$DIST_DIR/agent-cube/" 2>/dev/null || true
cp "$PROJECT_ROOT/INSTALL.md" "$DIST_DIR/agent-cube/" 2>/dev/null || true

# Create version file
echo "$VERSION" > "$DIST_DIR/agent-cube/VERSION"

echo "✅ Files copied"
echo ""

# Create the zip
echo "🗜️  Creating archive..."
cd "$DIST_DIR"
zip -q -r "agent-cube-v${VERSION}.zip" agent-cube/

echo "✅ Archive created: dist/agent-cube-v${VERSION}.zip"
echo ""

# Create standalone installer
echo "📝 Creating standalone installer..."
cat > "$DIST_DIR/install-cube.sh" << 'INSTALLER_EOF'
#!/bin/bash
# Agent Cube CLI Standalone Installer

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

# Check for zip file in same directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ZIP_FILE="$SCRIPT_DIR/agent-cube-v${VERSION}.zip"

if [ ! -f "$ZIP_FILE" ]; then
    print_error "Distribution file not found: $ZIP_FILE"
    echo ""
    echo "Make sure you have both files in the same directory:"
    echo "  - install-cube.sh"
    echo "  - agent-cube-v${VERSION}.zip"
    exit 1
fi

# Check prerequisites
print_info "Checking prerequisites..."

if ! command -v unzip &> /dev/null; then
    print_error "unzip is not installed"
    echo "Install unzip first"
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

# Install
print_info "Installing to $INSTALL_DIR..."

if [ -d "$INSTALL_DIR" ]; then
    print_warning "Removing existing installation"
    rm -rf "$INSTALL_DIR"
fi

# Extract zip
unzip -q "$ZIP_FILE" -d "$HOME"
mv "$HOME/agent-cube" "$INSTALL_DIR"

print_success "Files installed to $INSTALL_DIR"
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

print_success "Symlink created: $BIN_DIR/cube"
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
INSTALLER_EOF

chmod +x "$DIST_DIR/install-cube.sh"

echo "✅ Standalone installer created: dist/install-cube.sh"
echo ""

# Create README for distribution
cat > "$DIST_DIR/README.txt" << 'README_EOF'
Agent Cube CLI v1.0.0
====================

Orchestrate parallel LLM coding workflows with automated dual-writer processes.

INSTALLATION
------------

1. Unzip this package (if you haven't already)
2. Run the installer:
   
   bash install-cube.sh

3. Add to your PATH (if prompted):
   
   export PATH="$HOME/.local/bin:$PATH"

4. Test the installation:
   
   cube --help

PREREQUISITES
-------------

- jq (for JSON parsing): brew install jq
- cursor-agent: npm install -g @cursor/cli
  Then authenticate: cursor-agent login

WHAT'S INCLUDED
---------------

- cube                         Main CLI wrapper
- install-cube.sh              Standalone installer
- scripts/automation/          Automation scripts
- AGENT_CUBE.md                Workflow documentation
- AGENT_CUBE_AUTOMATION.md     CLI automation guide

QUICK START
-----------

# List available commands
cube --help

# Launch dual writers
cube writers <task-id> <prompt-file>

# Launch judge panel
cube panel <task-id> <panel-prompt>

# Check status
cube status <task-id>

# List sessions
cube sessions

DOCUMENTATION
-------------

See AGENT_CUBE.md and AGENT_CUBE_AUTOMATION.md for complete guides.

SUPPORT
-------

GitHub: https://github.com/aetheronhq/aetheron-connect-v2
Issues: https://github.com/aetheronhq/aetheron-connect-v2/issues
README_EOF

echo "✅ README created: dist/README.txt"
echo ""

# Summary
echo "📊 Distribution package summary:"
echo ""
echo "  📦 agent-cube-v${VERSION}.zip     - Main distribution ($(du -h "$DIST_DIR/agent-cube-v${VERSION}.zip" | cut -f1))"
echo "  📄 install-cube.sh                - Standalone installer"
echo "  📖 README.txt                     - Installation instructions"
echo ""
echo "Distribution ready at: ${DIST_DIR}/"
echo ""
echo "To distribute:"
echo "  1. Send users both files:"
echo "     - agent-cube-v${VERSION}.zip"
echo "     - install-cube.sh"
echo ""
echo "  2. Users run: bash install-cube.sh"
echo ""


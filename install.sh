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

# Check bash prerequisites
if ! command -v curl &> /dev/null; then
    print_error "curl is not installed"
    echo "curl is required to download files"
    exit 1
fi

if ! command -v jq &> /dev/null; then
    print_warning "jq is not installed (required for bash version agent output parsing)"
    echo "Install jq: brew install jq (macOS) or apt-get install jq (Linux)"
    echo ""
fi

if ! command -v cursor-agent &> /dev/null; then
    print_warning "cursor-agent is not installed (required to run agents)"
    echo "Install cursor-agent: npm install -g @cursor/cli"
    echo "Then authenticate: cursor-agent login"
    echo ""
fi

# Check Python prerequisites
PYTHON_VERSION=""
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 10 ]; then
        print_success "Python $PYTHON_VERSION detected (Python version available)"
        INSTALL_PYTHON=true
    else
        print_warning "Python $PYTHON_VERSION detected (need 3.10+, Python version disabled)"
        INSTALL_PYTHON=false
    fi
else
    print_warning "Python 3 not found (Python version disabled)"
    INSTALL_PYTHON=false
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

# Check if we're in a git repository
if [ -d "$SCRIPT_DIR/.git" ]; then
    print_info "Git repository detected - creating direct symlinks (dev mode)"
    INSTALL_DIR="$SCRIPT_DIR"
else
    print_info "Non-git directory - copying files to $INSTALL_DIR"
    
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
fi

print_success "Files installed from: $INSTALL_DIR"
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

# Install Python version if available
if [ "$INSTALL_PYTHON" = true ]; then
    echo ""
    print_info "Installing Python version (cube-py)..."
    echo ""
    
    # Check if running from git repo
    if [ -d "$SCRIPT_DIR/.git" ]; then
        # Development mode - use pip install -e
        print_info "Git repository detected - installing in editable mode"
        
        cd "$INSTALL_DIR/python"
        
        if python3 -m pip install -e . --quiet 2>/dev/null; then
            print_success "Python version installed in editable mode"
            
            # Find where pip installed the entry point
            CUBE_PY_PATH=$(python3 -c "import sys; print([p for p in sys.path if 'bin' in p and p.startswith('$HOME')][0] + '/cube-py' if [p for p in sys.path if 'bin' in p and p.startswith('$HOME')] else '')" 2>/dev/null)
            
            if [ -z "$CUBE_PY_PATH" ]; then
                # Fallback: find cube-py in common locations
                for bindir in ~/.pyenv/versions/*/bin ~/.local/bin /usr/local/bin; do
                    if [ -f "$bindir/cube-py" ]; then
                        CUBE_PY_PATH="$bindir/cube-py"
                        break
                    fi
                done
            fi
            
            # Create symlink in ~/.local/bin if cube-py found elsewhere
            if [ -n "$CUBE_PY_PATH" ] && [ -f "$CUBE_PY_PATH" ] && [ "$CUBE_PY_PATH" != "$BIN_DIR/cube-py" ]; then
                print_info "Creating symlink to pip-installed cube-py"
                ln -sf "$CUBE_PY_PATH" "$BIN_DIR/cube-py"
                print_success "Symlink created: $BIN_DIR/cube-py -> $CUBE_PY_PATH"
            elif [ ! -f "$BIN_DIR/cube-py" ]; then
                # Create wrapper script as fallback
                cat > "$BIN_DIR/cube-py" << EOF
#!/bin/bash
cd "$INSTALL_DIR/python"
python3 -m cube.cli "\$@"
EOF
                chmod +x "$BIN_DIR/cube-py"
                print_success "Wrapper script created: $BIN_DIR/cube-py"
            fi
        else
            print_warning "Failed to install Python version with pip"
            print_info "Trying manual installation..."
            
            # Create wrapper script
            cat > "$BIN_DIR/cube-py" << EOF
#!/bin/bash
cd "$INSTALL_DIR/python"
python3 -m cube.cli "\$@"
EOF
            chmod +x "$BIN_DIR/cube-py"
            print_success "Python version installed (manual wrapper)"
        fi
    else
        # Non-git: copy python directory and create wrapper
        print_info "Copying Python implementation..."
        
        if [ -d "$SCRIPT_DIR/python" ]; then
            cp -r "$SCRIPT_DIR/python" "$INSTALL_DIR/python"
            
            # Create wrapper script
            cat > "$BIN_DIR/cube-py" << EOF
#!/bin/bash
cd "$INSTALL_DIR/python"
python3 -m cube.cli "\$@"
EOF
            chmod +x "$BIN_DIR/cube-py"
            
            # Try to install dependencies
            print_info "Installing Python dependencies..."
            if python3 -m pip install -r "$INSTALL_DIR/python/requirements.txt" --quiet 2>/dev/null; then
                print_success "Python dependencies installed"
            else
                print_warning "Could not install Python dependencies automatically"
                echo "Install manually: pip install -r $INSTALL_DIR/python/requirements.txt"
            fi
            
            print_success "Python version installed"
        else
            print_warning "Python directory not found, skipping Python installation"
            INSTALL_PYTHON=false
        fi
    fi
    
    echo ""
fi

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
echo "Installed versions:"
if [ -L "$BIN_DIR/cube" ]; then
    echo -e "  ${CYAN}cube${NC}      Bash version (primary)"
fi
if [ "$INSTALL_PYTHON" = true ] && [ -f "$BIN_DIR/cube-py" ]; then
    echo -e "  ${CYAN}cube-py${NC}   Python version (alternative)"
fi
echo ""
echo "Get started:"
echo -e "  ${CYAN}cube --help${NC}        Show all commands (bash)"
if [ "$INSTALL_PYTHON" = true ]; then
    echo -e "  ${CYAN}cube-py --help${NC}     Show all commands (python)"
fi
echo -e "  ${CYAN}cube version${NC}       Show version"
echo -e "  ${CYAN}cube sessions${NC}      List active sessions"
echo ""
echo "Documentation:"
echo -e "  ${CYAN}cat $INSTALL_DIR/AGENT_CUBE.md${NC}"
if [ "$INSTALL_PYTHON" = true ]; then
    echo -e "  ${CYAN}cat $INSTALL_DIR/python/README.md${NC}"
fi
echo ""
echo "To uninstall:"
if [ "$INSTALL_PYTHON" = true ]; then
    echo -e "  ${YELLOW}rm -rf $INSTALL_DIR $BIN_DIR/cube $BIN_DIR/cube-py${NC}"
else
    echo -e "  ${YELLOW}rm -rf $INSTALL_DIR $BIN_DIR/cube${NC}"
fi
echo ""


#!/usr/bin/env bash
# ==============================================================================
# 🏢 Company Knowledge Base RAG — One-Line macOS / Linux Installer
# Install via:
#   curl -fsSL https://raw.githubusercontent.com/Farhodoff/company-knowledge-base-rag/main/install.sh | bash
# ==============================================================================

set -e

# Terminal colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo -e "${CYAN}${BOLD}"
cat << 'EOF'
  _____                                      _____            _____ 
 / ____|                                    |  __ \   /\     / ____|
| |     ___  _ __ ___  _ __   __ _ _ __  _   | |__) | /  \   | |  __ 
| |    / _ \| '_ ` _ \| '_ \ / _` | '_ \| | | |  _  / / /\ \  | | |_ |
| |___| (_) | | | | | | |_) | (_| | | | |_| | | | \ \/ ____ \ | |__| |
 \_____\___/|_| |_| |_| .__/ \__,_|_| |_|\__, | |_|  \/    \_\ \_____|
                      | |                 __/ |                     
                      |_|                |___/                      
EOF
echo -e "${NC}"
echo -e "${BOLD}Enterprise AI Assistant for Internal Company Documents${NC}"
echo -e "${CYAN}Repository:${NC} https://github.com/Farhodoff/company-knowledge-base-rag\n"

# 1. Platform Detection
OS_TYPE="$(uname -s)"
if [ "$OS_TYPE" != "Darwin" ] && [ "$OS_TYPE" != "Linux" ]; then
    echo -e "${RED}❌ Unsupported operating system: $OS_TYPE. This installer is for macOS and Linux.${NC}"
    exit 1
fi

echo -e "🔍 Detected operating system: ${GREEN}${OS_TYPE} ($(uname -m))${NC}"

# 2. Check Prerequisites (Python 3 and Git)
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git is required but not installed.${NC}"
    echo "Install Xcode Command Line Tools on macOS via: xcode-select --install"
    exit 1
fi

PYTHON_BIN=""
for py in python3 python3.13 python3.12 python3.11 python3.10; do
    if command -v "$py" &> /dev/null; then
        PY_VER="$("$py" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
        PY_MAJOR="$(echo "$PY_VER" | cut -d. -f1)"
        PY_MINOR="$(echo "$PY_VER" | cut -d. -f2)"
        if [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -ge 10 ]; then
            PYTHON_BIN="$(command -v "$py")"
            echo -e "🐍 Found compatible Python: ${GREEN}$PYTHON_BIN ($PY_VER)${NC}"
            break
        fi
    fi
done

if [ -z "$PYTHON_BIN" ]; then
    echo -e "${YELLOW}⚠️ Python 3.10+ not found on your system.${NC}"
    if [ "$OS_TYPE" = "Darwin" ] && command -v brew &> /dev/null; then
        echo -e "📦 Installing Python via Homebrew..."
        brew install python
        PYTHON_BIN="$(command -v python3)"
    else
        echo -e "${RED}❌ Please install Python 3.10 or newer (https://www.python.org/downloads/)${NC}"
        exit 1
    fi
fi

# 3. Setup Installation Directory
INSTALL_DIR="$HOME/.company-rag"
BIN_DIR="$HOME/.local/bin"
mkdir -p "$BIN_DIR"

if [ -d "$INSTALL_DIR/.git" ]; then
    echo -e "🔄 Updating existing installation at ${CYAN}$INSTALL_DIR${NC}..."
    cd "$INSTALL_DIR"
    git fetch origin
    git reset --hard origin/main || git pull origin main
else
    echo -e "📥 Cloning Company Knowledge Base RAG into ${CYAN}$INSTALL_DIR${NC}..."
    git clone --depth 1 https://github.com/Farhodoff/company-knowledge-base-rag.git "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

# 4. Virtual Environment & Dependencies
echo -e "📦 Setting up isolated virtual environment..."
VENV_DIR="$INSTALL_DIR/.venv"

if command -v uv &> /dev/null; then
    echo -e "⚡ Using uv for fast installation..."
    uv venv "$VENV_DIR" --python "$PYTHON_BIN"
    uv pip install --python "$VENV_DIR/bin/python" -r requirements.txt
else
    "$PYTHON_BIN" -m venv "$VENV_DIR"
    "$VENV_DIR/bin/python" -m pip install --upgrade pip
    "$VENV_DIR/bin/python" -m pip install -r requirements.txt
fi

# 5. Environment File (.env)
if [ ! -f "$INSTALL_DIR/.env" ]; then
    cp "$INSTALL_DIR/.env.example" "$INSTALL_DIR/.env"
    echo -e "⚙️ Created default config at ${CYAN}$INSTALL_DIR/.env${NC}"
fi

# 6. Global CLI Wrapper Script (company-rag)
CLI_WRAPPER="$BIN_DIR/company-rag"
cat << 'EOF' > "$CLI_WRAPPER"
#!/usr/bin/env bash
# ==============================================================================
# Company Knowledge Base RAG Global CLI Utility
# ==============================================================================
APP_DIR="$HOME/.company-rag"
VENV_PYTHON="$APP_DIR/.venv/bin/python"
VENV_STREAMLIT="$APP_DIR/.venv/bin/streamlit"

export PYTHONPATH="$APP_DIR:$PYTHONPATH"

show_help() {
    echo -e "\033[1;36m🏢 Company Knowledge Base RAG — Commands:\033[0m"
    echo -e "  \033[1mcompany-rag ui\033[0m                 Launch Streamlit web dashboard in browser"
    echo -e "  \033[1mcompany-rag ask <question>\033[0m     Query knowledge base directly in terminal"
    echo -e "  \033[1mcompany-rag ingest\033[0m             Index all documents into FAISS vector store"
    echo -e "  \033[1mcompany-rag add <file/path>\033[0m    Copy new PDF/MD/DOCX file and trigger re-index"
    echo -e "  \033[1mcompany-rag docs\033[0m               Open documents folder in macOS Finder"
    echo -e "  \033[1mcompany-rag slack\033[0m              Start Slack Bot (Socket Mode)"
    echo -e "  \033[1mcompany-rag discord\033[0m            Start Discord Bot"
    echo -e "  \033[1mcompany-rag api [--port 8000]\033[0m  Start universal REST Webhook server"
    echo -e "  \033[1mcompany-rag config\033[0m             Edit .env file in default text editor"
    echo -e "  \033[1mcompany-rag update\033[0m             Pull latest version from GitHub"
    echo -e "  \033[1mcompany-rag help\033[0m               Show this help message"
}

case "$1" in
    ui|web)
        echo "🚀 Launching Company Knowledge Base UI..."
        cd "$APP_DIR" && "$VENV_STREAMLIT" run app.py
        ;;
    ask|query)
        shift
        if [ -z "$*" ]; then
            cd "$APP_DIR" && "$VENV_PYTHON" scripts/query.py
        else
            cd "$APP_DIR" && "$VENV_PYTHON" scripts/query.py "$@"
        fi
        ;;
    ingest|index)
        shift
        echo "🔄 Indexing documents..."
        cd "$APP_DIR" && "$VENV_PYTHON" scripts/ingest.py "$@"
        ;;
    add)
        shift
        if [ -z "$1" ] || [ ! -f "$1" ]; then
            echo "❌ Usage: company-rag add <path-to-document.pdf>"
            exit 1
        fi
        cp "$1" "$APP_DIR/documents/"
        echo "📄 Copied $(basename "$1") to $APP_DIR/documents/"
        cd "$APP_DIR" && "$VENV_PYTHON" scripts/ingest.py
        ;;
    docs)
        if command -v open &> /dev/null; then
            open "$APP_DIR/documents"
        elif command -v xdg-open &> /dev/null; then
            xdg-open "$APP_DIR/documents"
        else
            ls -la "$APP_DIR/documents"
        fi
        ;;
    slack)
        echo "🤖 Starting Slack Bot..."
        cd "$APP_DIR" && "$VENV_PYTHON" src/integrations/slack_bot.py
        ;;
    discord)
        echo "🤖 Starting Discord Bot..."
        cd "$APP_DIR" && "$VENV_PYTHON" src/integrations/discord_bot.py
        ;;
    api|webhook)
        shift
        echo "🌐 Starting Webhook server..."
        cd "$APP_DIR" && "$VENV_PYTHON" src/integrations/webhook_server.py "$@"
        ;;
    config|env)
        "${EDITOR:-nano}" "$APP_DIR/.env"
        ;;
    update)
        echo "🔄 Updating Company Knowledge Base RAG..."
        cd "$APP_DIR" && git pull origin main
        "$APP_DIR/.venv/bin/pip" install -r "$APP_DIR/requirements.txt"
        echo "✅ Update complete!"
        ;;
    help|--help|-h|"")
        show_help
        ;;
    *)
        # Default: treat whole argument as a question
        cd "$APP_DIR" && "$VENV_PYTHON" scripts/query.py "$*"
        ;;
esac
EOF

chmod +x "$CLI_WRAPPER"

# 7. Add ~/.local/bin to PATH in Shell config if not present
SHELL_RC=""
if [ -n "$ZSH_VERSION" ] || [ "$SHELL" = "*/zsh" ] || [ -f "$HOME/.zshrc" ]; then
    SHELL_RC="$HOME/.zshrc"
elif [ -f "$HOME/.bashrc" ]; then
    SHELL_RC="$HOME/.bashrc"
fi

if [ -n "$SHELL_RC" ]; then
    if ! grep -q 'export PATH="$HOME/.local/bin:$PATH"' "$SHELL_RC" 2>/dev/null; then
        echo -e '\n# Company Knowledge Base RAG CLI' >> "$SHELL_RC"
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$SHELL_RC"
        echo -e "✅ Added ${CYAN}$BIN_DIR${NC} to ${CYAN}$SHELL_RC${NC}"
    fi
fi

# 8. Create macOS Application Launcher in ~/Applications
if [ "$OS_TYPE" = "Darwin" ] && command -v osacompile &> /dev/null; then
    APP_BUNDLE="$HOME/Applications/Company Knowledge Base.app"
    mkdir -p "$HOME/Applications"
    osacompile -o "$APP_BUNDLE" -e 'do shell script "export PATH=\"$HOME/.local/bin:/usr/local/bin:$PATH\"; company-rag ui > /dev/null 2>&1 &"' 2>/dev/null || true
    if [ -d "$APP_BUNDLE" ]; then
        echo -e "🖥️ Created native macOS application: ${GREEN}$APP_BUNDLE${NC}"
        echo -e "   (You can now launch it via Spotlight: ${BOLD}Cmd + Space${NC} -> \"Company Knowledge Base\")"
    fi
fi

echo -e "\n==========================================================="
echo -e "${GREEN}${BOLD}🎉 Installation Complete!${NC}"
echo -e "==========================================================="
echo -e "To start using immediately, run:\n"
echo -e "  ${BOLD}export PATH=\"$HOME/.local/bin:\$PATH\"${NC}  (or restart your terminal)\n"
echo -e "Quick Commands:"
echo -e "  • ${CYAN}company-rag ui${NC}            Open web dashboard in browser"
echo -e "  • ${CYAN}company-rag ask \"<text>\"${NC}   Ask questions directly in terminal"
echo -e "  • ${CYAN}company-rag add <file>${NC}    Add and re-index PDF/MD documents"
echo -e "  • ${CYAN}company-rag config${NC}        Set your GOOGLE_API_KEY"
echo -e "===========================================================\n"

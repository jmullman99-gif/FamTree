#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'
info()  { printf "${GREEN}[✓]${NC} %s\n" "$1"; }
error() { printf "${RED}[✗]${NC} %s\n" "$1"; }

# Check prerequisites
for cmd in python3 uv; do
    if ! command -v "$cmd" &>/dev/null; then
        error "Missing required tool: $cmd"
        case "$cmd" in
            uv) echo "  Install: curl -LsSf https://astral.sh/uv/install.sh | sh" ;;
            python3) echo "  Install: https://www.python.org/downloads/" ;;
        esac
        exit 1
    fi
done
info "Prerequisites found (python3, uv)"

# Install package
(cd "$SCRIPT_DIR" && uv sync --quiet)
info "Python package installed"

echo ""
info "Setup complete! Add this server to your MCP client:"
echo ""
echo '  {
    "mcpServers": {
      "genealogy": {
        "type": "stdio",
        "command": "uv",
        "args": ["run", "--directory", "'"$SCRIPT_DIR"'", "genealogy-mcp"]
      }
    }
  }'
echo ""

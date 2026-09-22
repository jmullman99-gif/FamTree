# Getting Started

## Setup

**Prerequisites:** An MCP-compatible AI client, Python 3.10+,
and [uv](https://astral.sh/uv/install.sh).

**Optional:** [Open Design](https://opendesign.dev) for family tree
visualization at the end of the research workflow.

### 1. Clone and install

```bash
git clone https://github.com/jmullman99-gif/genealogy-mcp.git
cd genealogy-mcp
./setup.sh
```

This installs the Python package. Takes about 30 seconds.

### 2. Register the MCP server

Add the server to your MCP client's configuration:

```json
{
  "mcpServers": {
    "genealogy": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "--directory", "/path/to/genealogy-mcp", "genealogy-mcp"]
    }
  }
}
```

Replace `/path/to/genealogy-mcp` with the actual path to the cloned repo.

### 3. Start researching

Connect to the MCP server through your client and start using the tools.

### 4. Try the example first (optional)

Before researching your own family, try loading the example GEDCOM:

```
Load the file examples/synthetic-family/marchetti.ged and tell me
what's in it.
```

## For Developers

The server is a standard Python package at `src/genealogy_mcp/`.
Each data source is a submodule with a client (HTTP calls) and tools
(MCP tool definitions).

```
src/genealogy_mcp/
├── server.py          # MCP entry point
├── wikitree/          # WikiTree API
├── gedcom/            # GEDCOM parser
├── newspapers/        # Chronicling America
├── archives/          # Open Archives
├── findagrave/        # Find A Grave scraper
└── crossref.py        # Parallel cross-reference
```

### Running tests

```bash
uv run pytest tests/ -v
```

All tests use mock HTTP — no network calls, no API keys.

# Genealogy MCP

AI-powered genealogy research toolkit — an [MCP](https://modelcontextprotocol.io) server
that gives your AI assistant access to WikiTree's 42 million profiles,
digitized US newspapers from 1789, European historical archives, Find A
Grave's 14 million+ memorials, and your own GEDCOM files — all searchable
in parallel.

## Quick Start

```bash
git clone https://github.com/jmullman99-gif/genealogy-mcp.git
cd genealogy-mcp
./setup.sh
```

Then connect the server to your MCP client and start researching.

**Requirements:** Python 3.10+ and [uv](https://astral.sh/uv). That's it.

> **New to genealogy?** Try the [synthetic example](examples/synthetic-family/)
> first — load `marchetti.ged` and follow the research log to see the
> full workflow in action.

## What's Inside

### 19 Research Tools

| Category | Tools | What they search |
|----------|-------|-----------------|
| **WikiTree** | `wikitree_search`, `wikitree_profile`, `wikitree_relatives`, `wikitree_ancestors`, `wikitree_descendants`, `wikitree_bio` | 42M+ collaborative profiles |
| **GEDCOM** | `gedcom_load`, `gedcom_search`, `gedcom_person`, `gedcom_family`, `gedcom_ancestors`, `gedcom_descendants`, `gedcom_stats` | Your local `.ged` files (offline, private) |
| **Newspapers** | `newspaper_search`, `newspaper_page` | Chronicling America — US newspapers 1789–1963 |
| **Archives** | `archives_search` | Open Archives — Dutch/Belgian/French records |
| **Find A Grave** | `findagrave_search`, `findagrave_memorial` | 14M+ grave records and memorials |
| **Cross-reference** | `cross_reference` | WikiTree, newspapers, and archives in parallel |

### Documentation

- [Getting Started](docs/getting-started.md) — setup and first research session
- [Tool Reference](docs/tool-reference.md) — what each tool does and when to use it
- [Research Methodology](docs/methodology.md) — parallel sweeps, adversarial review, organizing findings
- [Research Tips](docs/tips.md) — free sources, common pitfalls, name variants

### Example

The [Marchetti family example](examples/synthetic-family/) demonstrates
the full workflow with a fictional Italian-American family.

## How It Works

1. **The Grill** — `/genealogy` interviews you about who you're
   researching, what you know, and what documents you have
2. **Tool Check** — verifies the MCP server is installed and ready
3. **Parallel Research** — guides you through dispatching multiple
   agents to search different sources simultaneously
4. **Adversarial Review** — a separate agent challenges every claim
5. **Output** — documented family history with citations and a
   research log

## License

[MIT](LICENSE)

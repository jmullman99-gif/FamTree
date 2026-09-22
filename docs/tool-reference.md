# Tool Reference

The genealogy MCP server provides 19 tools across six categories.
You don't need to call these manually — the `/genealogy` skill
selects the right tools for each research question.

## WikiTree (6 tools)

Search WikiTree's 42 million+ collaborative family tree profiles.

### `wikitree_search`

Search for a person by name, dates, and location.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `last_name` | string | required | Surname to search |
| `first_name` | string | `""` | Given name |
| `birth_date` | string | `""` | Birth year or date |
| `death_date` | string | `""` | Death year or date |
| `birth_location` | string | `""` | Birth location |
| `limit` | int | `10` | Max results |

### `wikitree_profile`

Get a full profile by WikiTree ID (e.g. `Smith-12345`).

| Parameter | Type | Description |
|-----------|------|-------------|
| `key` | string | WikiTree ID or numeric User ID |

### `wikitree_relatives`

Get relatives for a profile — parents, children, siblings, spouses.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `key` | string | required | WikiTree ID |
| `get_parents` | bool | `true` | Include parents |
| `get_children` | bool | `true` | Include children |
| `get_siblings` | bool | `false` | Include siblings |
| `get_spouses` | bool | `true` | Include spouses |

### `wikitree_ancestors`

Get ancestor tree to a specified depth.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `key` | string | required | WikiTree ID |
| `depth` | int | `5` | Generations to traverse |

### `wikitree_descendants`

Get descendant tree to a specified depth.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `key` | string | required | WikiTree ID |
| `depth` | int | `3` | Generations to traverse |

### `wikitree_bio`

Get the full biography text, including sourced narratives and citations.

| Parameter | Type | Description |
|-----------|------|-------------|
| `key` | string | WikiTree ID |

## GEDCOM (7 tools)

Parse and query local `.ged` files. All processing is offline — no
data leaves your machine.

### `gedcom_load`

Load a GEDCOM file into memory. Required before using other `gedcom_*` tools.

| Parameter | Type | Description |
|-----------|------|-------------|
| `file_path` | string | Path to the `.ged` file |

### `gedcom_search`

Search loaded individuals by name, dates, location, or sex.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | `""` | Name (partial match) |
| `birth_year` | string | `""` | Birth year |
| `birth_place` | string | `""` | Birth place (partial match) |
| `death_year` | string | `""` | Death year |
| `sex` | string | `""` | `M` or `F` |

### `gedcom_person`

Get full details for one person by xref ID (e.g. `@I1@`).

### `gedcom_family`

Get a family group — husband, wife, children — by family xref ID (e.g. `@F1@`).

### `gedcom_ancestors`

BFS ancestor tree from a person, to configurable depth (default 4).

### `gedcom_descendants`

BFS descendant tree from a person, to configurable depth (default 4).

### `gedcom_stats`

Summary statistics: individual/family counts, surname frequency, encoding.

## Newspapers (2 tools)

Search US newspapers from 1789–1963 via the Library of Congress
Chronicling America collection.

### `newspaper_search`

Full-text search of digitized newspaper pages.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | required | Search text |
| `state` | string | `""` | Filter by US state |
| `date_start` | string | `""` | Start year |
| `date_end` | string | `""` | End year |
| `page` | int | `1` | Result page |
| `rows` | int | `20` | Results per page (max 100) |

### `newspaper_page`

Get full OCR text for a specific newspaper page. Use the `page_url`
from `newspaper_search` results.

## Archives (1 tool)

Search Dutch, Belgian, and French historical records via Open Archives
(openarchieven.nl) — birth, marriage, and death registrations, church
records, population registers.

### `archives_search`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | required | Person name |
| `place` | string | `""` | Place name |
| `number_show` | int | `20` | Results per page |
| `start` | int | `0` | Result offset |

## Find A Grave (2 tools)

Search Find A Grave's 14 million+ memorials — cemetery records, burial
locations, biographical details, and grave photos.

### `findagrave_search`

Search for memorials by name, dates, and location.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lastname` | string | required | Surname to search |
| `firstname` | string | `""` | Given name |
| `birth_year` | string | `""` | Birth year |
| `death_year` | string | `""` | Death year |
| `location` | string | `""` | Location filter |
| `page` | int | `1` | Result page |

### `findagrave_memorial`

Get full details for a memorial by its memorial ID.

| Parameter | Type | Description |
|-----------|------|-------------|
| `memorial_id` | string | Find A Grave memorial ID |

Returns name, dates, cemetery, location, biography/inscription, plot
info, and URL.

## Cross-Reference (1 tool)

### `cross_reference`

Search WikiTree, Chronicling America, and Open Archives in parallel
for a single person. Returns consolidated results from all sources
with source attribution. Failures in one source don't block the others.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | required | Full name |
| `birth_year` | string | `""` | Birth year |
| `birth_place` | string | `""` | Birth place |
| `death_year` | string | `""` | Death year |

## How the Tools Work Together

1. **Start with what you have** — load a GEDCOM file with `gedcom_load`,
   or search WikiTree with `wikitree_search`
2. **Fan out** — use `cross_reference` to search all sources at once
3. **Go deep** — follow leads with `wikitree_profile`, `wikitree_bio`,
   `newspaper_page` for full text, or `findagrave_memorial` for burial details
4. **Connect families** — use `wikitree_relatives`, `gedcom_ancestors`,
   and `gedcom_descendants` to trace lineage

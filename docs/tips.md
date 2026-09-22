# Research Tips

Practical knowledge for AI-assisted genealogy research — what works,
what doesn't, and where the gotchas are.

## Free Data Sources (No API Key Needed)

| Source | What it has | Access |
|--------|-----------|--------|
| [WikiTree](https://wikitree.com) | 42M+ collaborative profiles | `wikitree_search` (no auth for public profiles) |
| [Chronicling America](https://chroniclingamerica.loc.gov) | US newspapers 1789-1963 | `newspaper_search` |
| [Open Archives](https://openarchieven.nl) | Dutch/Belgian/French records | `archives_search` |
| [Find A Grave](https://findagrave.com) | 14M+ memorials, cemetery records, grave photos | `findagrave_search` |

## Free Data Sources (Signup Required)

| Source | What it has | How to access |
|--------|-----------|---------------|
| [FamilySearch](https://familysearch.org) | The single most valuable genealogy API. Billions of indexed records, family trees, digital images. | Free account + OAuth dev key. Worth the signup. |
| [Geni](https://geni.com) | World family tree, 200M+ profiles | Free OAuth. Good for connecting trees. |

## Sites to Skip

| Site | Why |
|------|-----|
| Ancestry.com | Paywalled API, no free tier, aggressive anti-scraping |
| MyHeritage | Similar to Ancestry — paywalled, no usable free API |
| 23andMe | DNA only, no genealogical records, API deprecated |

These have great data behind paywalls. If you have a subscription, use
their web UI directly. But they can't be integrated into this toolkit.

## Playwright-Automatable Sites

These sites don't have APIs but can be automated with a browser:

| Site | What you can get |
|------|-----------------|
| [DAR GRS](https://services.dar.org/Public/DAR_Research/search/?Tab_ID=6) | DAR Genealogical Research System — verified patriot lineages |
| [NARA Catalog](https://catalog.archives.gov) | National Archives — immigration, military, census originals |
| [BillionGraves](https://billiongraves.com) | GPS-tagged headstone photos |

Use Playwright or a browser automation MCP when the built-in tools
don't cover what you need.

## Using Open Design for Diagrams

Once you have family data, you can use [Open Design](https://opendesign.dev)
to create family tree diagrams. Open Design renders HTML/JSX/CSS in a
local design workspace — good for creating visual trees you can export
as images or PDFs.

Prompt pattern for generating a family tree diagram:
> "Create a family tree diagram for [family name]. The tree should show
> [list of people with relationships]. Use a top-down layout with
> birth/death years under each name. Style it for printing on letter-size
> paper."

## Common Pitfalls

### Name variants
The same person appears as "Giovanni Marchetti," "John Marchetti,"
"John Marquetti," and "Jno. Marchetti" across different records.
Always search for variants. Common patterns:
- Anglicization (Giuseppe -> Joseph, Wilhelm -> William)
- Phonetic spelling by clerks (Berezovski -> Baresofsky)
- Abbreviation (Jno. = John, Wm. = William, Thos. = Thomas)
- Maiden vs. married names

### Date mismatches
Census records use the enumeration date, not the person's statement.
The 1900 US Census asked for birth month and year; the 1910 Census
didn't. Gravestones are often carved from memory, years after death.
**Expect 1-2 year discrepancies** and don't reject a match over them.

### Same name, different person
"John Smith born 1850 in New York" matches thousands of people. Always
verify with:
- Spouse name
- Children's names
- Street address (census records)
- Occupation
- Immigration date + ship name

### Census enumeration dates
US Census records reflect the *enumeration date*, which can be weeks
or months after the official census date. A person enumerated on
June 15, 1900 might have turned a year older between January 1 and
the enumerator's visit.

### "Ellis Island name changes"
This is largely a myth. Names were not changed at Ellis Island —
passenger manifests were created at the port of departure, not
arrival. Name changes happened gradually through use, not at a single
moment. But the *pattern* of name change is real and important to
track across records.

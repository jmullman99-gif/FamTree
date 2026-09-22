# Research Methodology

How to conduct AI-assisted genealogy research using parallel agent
sweeps, adversarial review, and structured knowledge management.

This document explains the *why* behind the workflow. For tool-specific
details, see [Tool Reference](tool-reference.md). For practical tips,
see [Research Tips](tips.md).

## The Core Loop

Genealogy research follows a cycle:

1. **Gather** what you know (documents, oral history, existing trees)
2. **Search** multiple sources in parallel
3. **Synthesize** findings into a single narrative
4. **Challenge** every claim with an adversarial review
5. **Extend** the tree where new leads appeared
6. **Repeat** from step 2 with the new frontier

The rest of this document explains each step.

## Step 1: Structured Intake

Before searching anything, extract everything the researcher already
knows. This sounds obvious, but most people underestimate what they
know — or overestimate how much they've told you.

The `/genealogy` skill handles this with a structured interview. The
output is a **research brief** — a markdown file listing every known
person, date, place, document, and oral tradition. This brief is the
canonical input for all subsequent research.

**Why this matters:** A name and approximate birth year isn't enough
to find the right person in a database of millions. But a name +
birth year + spouse name + city + occupation usually is. The intake
interview extracts these distinguishing details.

## Step 2: Parallel Agent Sweeps

The power of an agentic platform is parallelism. Instead of searching
one source at a time, dispatch 4-8 agents simultaneously, each
targeting a different source or question.

### How to structure a sweep

Each agent gets:
- A specific source to search (WikiTree, Chronicling America, etc.)
- The names and dates from the research brief
- Instructions to report findings with full source citations
- A reminder to flag uncertain matches rather than asserting them

### Example sweep (4 agents)

**Agent 1 — WikiTree profiles:**
> "Search WikiTree for the following people: [list from research
> brief]. For each match, pull profile, bio, relatives, and ancestors.
> Verify dates and places against our brief. Report all matches and
> conflicts."

**Agent 2 — Newspaper records:**
> "Search Chronicling America for [subject name] and [spouse name] in
> [city/state] between [date range]. Look for: obituaries, marriage
> announcements, immigration notices, birth announcements, business
> listings. Report each finding with: newspaper name, date, page,
> and relevant quote."

**Agent 3 — European archives:**
> "Search Open Archives for [surnames] in [European regions from oral
> history]. Look for birth, marriage, and death records. Report with
> archive name and record reference."

**Agent 4 — Cross-reference:**
> "Use cross_reference_person to search all sources for [subject
> name, birth ~year, location]. Report the consolidated results with
> match confidence for each source."

### How many sweeps?

Most research projects need 2-4 sweeps:
- **Sweep 1:** The people named in the research brief
- **Sweep 2:** New relatives discovered in sweep 1
- **Sweep 3:** Focused searches on specific questions (e.g., "What
  ship did they arrive on?" or "Where were they buried?")
- **Sweep 4:** Verification searches for any claim that rests on a
  single source

## Step 3: Synthesis

After each sweep, consolidate findings into a single document:

- One section per family branch or generation
- Each factual claim cites its source
- Contradictions between sources are noted explicitly, with reasoning
  about which to trust
- Oral history that was verified gets upgraded to "confirmed"
- Oral history that was contradicted gets noted as "disproven" with
  the evidence

### Handling contradictions

Sources disagree constantly. Common patterns:

| Situation | What to trust |
|-----------|---------------|
| Census says born 1882, gravestone says 1884 | Census is closer to contemporaneous; gravestone may be carved from memory years later. But neither is authoritative — note the range. |
| Immigration record has different name spelling | Normal. Clerks wrote what they heard. The person didn't choose the spelling. |
| Two WikiTree profiles for the same person | Check merge history. Often one is better sourced. |
| Family story says X, records say Y | Records win for facts (dates, places). Family stories win for context (why they emigrated, what they did). |

## Step 4: Adversarial Review

After synthesis, dispatch a separate agent whose only job is to
challenge the document:

> "Review this family history. For every factual claim, check:
> 1. Is it supported by a cited source?
> 2. Could the source be about a different person with the same name?
> 3. Are there internal contradictions?
> 4. Are approximate dates presented as certain?
> 5. Are relationships assumed rather than documented?
>
> List every issue, ranked by severity."

**Why a separate agent?** The agent that did the research has
"confirmation bias" baked into its context — it found the matches and
is primed to believe them. A fresh agent with only the document (not
the search history) catches errors the researcher missed.

### Common catches

The adversarial review typically finds:
- Dates presented as exact when only a range is supported
- "Same name" matches that weren't verified with additional details
- Children born impossibly close together (under 9 months apart)
- People supposedly alive at ages over 100 without comment
- Sources cited but not actually supporting the specific claim

## Step 5: Organizing Findings

For research that spans multiple sessions or branches, organize
findings in a structured knowledge base:

### Recommended structure

```
research/
├── brief.md              # The original intake interview output
├── family-history.md     # The synthesized narrative (main output)
├── research-log.md       # What was searched, when, what was found
├── branches/
│   ├── paternal.md       # Paternal line deep dive
│   └── maternal.md       # Maternal line deep dive
└── sources/
    ├── wikitree-matches.md
    ├── newspaper-clippings.md
    └── archive-records.md
```

### The research log

Keep a running log of every search conducted:

```markdown
## 2026-09-22

### Sweep 1
- WikiTree: Searched "Giovanni Marchetti" born ~1870 Lucca — found
  Marchetti-4521 (likely match, dates align, location confirmed)
- Chronicling America: Searched "Marchetti" in Brooklyn Eagle
  1895-1910 — found obituary for wife Maria (1908-03-15, p.4)
- Open Archives: No results for "Marchetti" in Italian records
  (expected — Italian civil records not in Open Archives)
- Cross-reference: 2 matches (WikiTree + newspaper), 0 archive hits

### Open Questions
- [ ] What ship did Giovanni arrive on? Search NARA/Castle Garden.
- [ ] Maria's maiden name — obituary may have it. Get full page.
```

## When to Stop

Not every line can be traced. Stop when:

- You've exhausted all available free sources for a person
- The only remaining sources are behind paywalls you can't access
- You're finding the same information repeated, not new evidence
- The trail goes cold before civil registration began (varies by
  country — ~1800s for most of Western Europe, later for Eastern
  Europe)

Note the dead end explicitly: "The trail for Giovanni Marchetti ends
at his 1895 arrival in New York. Italian civil records from Lucca are
not available in any free digital archive as of this date."

Future researchers (including you, later) will thank you for
documenting where you stopped and why.

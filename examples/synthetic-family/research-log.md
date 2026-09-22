# Research Log: Marchetti Family

## Session 1 — Initial Investigation

### GEDCOM Analysis
- Loaded `marchetti.ged`: 10 individuals, 3 families
- Tree spans 1870–1957 (births), three generations
- Confirms: Giovanni (b. ~1870 Lucca) → Antonio (b. 1897 Brooklyn) →
  Giovanni Carlo (b. 1926 Brooklyn) → Robert & Anna (b. 1955/1957)
- Antonio's wife identified as Margaret O'Brien (b. 1901, County Cork,
  Ireland; immigrated 1919) — matches oral history of "Irish girl"
- Giovanni Carlo married Dorothy Kowalski (b. 1930, Greenpoint) — Polish
  connection not mentioned in oral history

### Sweep 1: Four parallel searches

**WikiTree (Agent 1):**
- No exact match for "Giovanni Marchetti" born ~1870 Lucca
- Found Marchetti-892: an "Antonio Marchetti" born 1865 Lucca, emigrated
  to Boston. Possible relative but not our Giovanni. Flagged for
  further investigation.
- No results for "Maria Rossi" in Brooklyn (name too common without
  more details)

**Newspapers — Chronicling America (Agent 2):**
- **Hit:** Brooklyn Daily Eagle, 1908-03-10, p.6: "MARCHETTI — Maria,
  beloved wife of John, age 33. Funeral from 412 Union St." Confirms
  death date, husband's anglicized name, and address.
- **Hit:** Brooklyn Daily Eagle, 1942-02-05, p.12: "MARCHETTI — Giovanni
  (John), age 71, of Union St. Survived by son Antonio, daughter Rosa
  (Mrs. R. Callahan)." Confirms death, children, Rosa's married name.
- Brooklyn Standard Union, 1925-06-07: Marriage announcement —
  "Marchetti-O'Brien: Antonio Marchetti and Miss Margaret O'Brien,
  both of Brooklyn, were united in marriage at St. Agnes Church."

**European Archives (Agent 3):**
- Open Archives: No Italian records (coverage is Dutch/Belgian/French).
  Dead end for Lucca research via this tool.

**Cross-Reference (Agent 4):**
- cross_reference_person("Giovanni Marchetti", birth_year=1870,
  location="Brooklyn"): 2 hits (WikiTree partial, newspaper confirmed).
  No archive hits.

### Findings After Sweep 1
- Maria Rossi confirmed dead March 8, 1908 (obituary). Age 33 →
  born ~1874-1875.
- Giovanni died Feb 3, 1942 (obituary). Age 71 → born ~1870-1871.
- Family address: 412 Union St, Brooklyn — useful for census searches.
- Rosa married someone named "R. Callahan" — new lead.
- Antonio and Margaret married June 5, 1925 at St. Agnes Church,
  Brooklyn — specific enough to find a marriage certificate.

### Open Questions After Sweep 1
- [ ] Giovanni's immigration record — which ship, which year exactly?
- [ ] Maria Rossi's family — who were her parents?
- [ ] 412 Union St in census records (1900, 1910, 1920, 1930)
- [ ] Rosa Marchetti married "R. Callahan" — find marriage record
- [ ] Antonio Marchetti-892 on WikiTree — is he related to our Giovanni?

---

## Session 2 — Census and Immigration

### Sweep 2: Focused searches

**Census search (Agent 1):**
- 1900 Census, Brooklyn ED 143: "John Marquetti" age 30, b. Italy,
  imm. 1895, stonemason. Wife "Mary" age 25, b. Italy. Son "Anthony"
  age 3, b. NY. At 412 Union St. **Confirms oral history on all points.**
- 1910 Census, Brooklyn: "John Marchetti" age 40, widower, stonemason.
  Son "Anthony" 13, daughter "Rose" 10. Same address.
- 1920 Census: "John Marchetti" age 49, still at 412 Union St.
  Anthony now 22, occupation "carpenter."

**Immigration (Agent 2):**
- Castle Garden/Ellis Island search for "Marchetti" arriving 1894-1896
  from Italy: 3 results.
  - **Best match:** SS Werra, arrived New York 1895-04-12. Passenger
    "Giovanni Marchetti," age 25, from Lucca, occupation "scalpellino"
    (stonemason). Destination: "fratello, Brooklyn" (brother in Brooklyn).
  - This means Giovanni had a brother already in Brooklyn in 1895 —
    a previously unknown family member.

### Adversarial Review

Review agent flagged:
1. **Maria's birth year inconsistency:** Obituary says "age 33" at
   death (1908) → born 1874-1875. GEDCOM says born "12 MAR 1874."
   The GEDCOM date is more specific than our evidence supports — where
   did March 12 come from? **Resolution:** Marked GEDCOM date as
   "from cousin's tree, unverified. Supported range: 1874-1875."
2. **Giovanni's brother:** Immigration record says destination was
   "fratello, Brooklyn." This brother is not in the GEDCOM and was
   not mentioned in oral history. **Resolution:** Added to open
   questions. Could be a significant branch.
3. **Name variant consistency:** Census records alternate between
   "Marchetti" and "Marquetti." The 1900 census uses "Marquetti,"
   later censuses use "Marchetti." **Resolution:** Noted as normal
   clerk-dependent variation, not an actual name change.

### Updated Open Questions
- [ ] Giovanni's brother in Brooklyn (1895) — who was he? Search
      census for other Marchetti households near 412 Union St.
- [ ] Maria Rossi's exact birth date — the March 12 date in the
      GEDCOM needs a source or should be downgraded to ~1874.
- [ ] Rosa Marchetti + R. Callahan marriage — still not found.
- [ ] Lucca civil records — not available in free online archives.
      Would require writing to the Comune di Lucca or visiting
      FamilySearch microfilm.

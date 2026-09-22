"""GEDCOM 5.5.1 parser. Handles INDI, FAM, and standard sub-tags."""
from __future__ import annotations

import re
from pathlib import Path

from genealogy_mcp.gedcom.models import Family, GedcomFile, Individual

_LINE_RE = re.compile(r"^(\d+)\s+(@\S+@\s+)?(\S+)(?: (.*))?$")


def parse_gedcom(file_path: str) -> GedcomFile:
    """Parse a GEDCOM 5.5.1 file and return a GedcomFile."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"GEDCOM file not found: {file_path}")

    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    gf = GedcomFile()
    current_indi: Individual | None = None
    current_fam: Family | None = None
    current_event: str = ""  # "BIRT", "DEAT", "MARR", etc.
    current_level_0_tag: str = ""

    for raw_line in lines:
        raw_line = raw_line.strip()
        if not raw_line:
            continue

        m = _LINE_RE.match(raw_line)
        if not m:
            continue

        level = int(m.group(1))
        xref = (m.group(2) or "").strip()
        tag = m.group(3)
        value = m.group(4) or ""

        if level == 0:
            # Save previous record
            if current_indi:
                gf.individuals[current_indi.xref_id] = current_indi
            if current_fam:
                gf.families[current_fam.xref_id] = current_fam
            current_indi = None
            current_fam = None
            current_event = ""

            if tag == "INDI":
                current_indi = Individual(xref_id=xref)
                current_level_0_tag = "INDI"
            elif tag == "FAM":
                current_fam = Family(xref_id=xref)
                current_level_0_tag = "FAM"
            elif tag == "HEAD":
                current_level_0_tag = "HEAD"
            elif tag == "TRLR":
                current_level_0_tag = ""
            else:
                current_level_0_tag = tag

        elif level == 1:
            current_event = ""
            if current_indi:
                _parse_indi_tag(current_indi, tag, value)
                if tag in ("BIRT", "DEAT", "IMMI"):
                    current_event = tag
            elif current_fam:
                _parse_fam_tag(current_fam, tag, value)
                if tag == "MARR":
                    current_event = tag
            elif current_level_0_tag == "HEAD" and tag == "CHAR":
                gf.encoding = value

        elif level == 2:
            if current_event and tag in ("DATE", "PLAC"):
                if current_indi:
                    _parse_event_detail(current_indi, current_event, tag, value)
                elif current_fam and current_event == "MARR":
                    if tag == "DATE":
                        current_fam.marriage_date = value
                    elif tag == "PLAC":
                        current_fam.marriage_place = value

    # Save last record
    if current_indi:
        gf.individuals[current_indi.xref_id] = current_indi
    if current_fam:
        gf.families[current_fam.xref_id] = current_fam

    return gf


def _parse_indi_tag(indi: Individual, tag: str, value: str) -> None:
    if tag == "NAME":
        indi.name = value.replace("/", "").strip()
        parts = value.split("/")
        if len(parts) >= 2:
            indi.given_name = parts[0].strip()
            indi.surname = parts[1].strip()
    elif tag == "SEX":
        indi.sex = value
    elif tag == "OCCU":
        indi.occupation = value
    elif tag == "FAMC":
        indi.famc.append(value)
    elif tag == "FAMS":
        indi.fams.append(value)
    elif tag == "NOTE":
        indi.notes.append(value)


def _parse_event_detail(
    indi: Individual, event: str, tag: str, value: str
) -> None:
    if event == "BIRT":
        if tag == "DATE":
            indi.birth_date = value
        elif tag == "PLAC":
            indi.birth_place = value
    elif event == "DEAT":
        if tag == "DATE":
            indi.death_date = value
        elif tag == "PLAC":
            indi.death_place = value


def _parse_fam_tag(fam: Family, tag: str, value: str) -> None:
    if tag == "HUSB":
        fam.husband_id = value
    elif tag == "WIFE":
        fam.wife_id = value
    elif tag == "CHIL":
        fam.child_ids.append(value)

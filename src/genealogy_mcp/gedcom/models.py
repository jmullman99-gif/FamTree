from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Individual:
    xref_id: str
    name: str = ""
    given_name: str = ""
    surname: str = ""
    sex: str = ""
    birth_date: str = ""
    birth_place: str = ""
    death_date: str = ""
    death_place: str = ""
    occupation: str = ""
    famc: list[str] = field(default_factory=list)
    fams: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


@dataclass
class Family:
    xref_id: str
    husband_id: str | None = None
    wife_id: str | None = None
    child_ids: list[str] = field(default_factory=list)
    marriage_date: str = ""
    marriage_place: str = ""


@dataclass
class GedcomFile:
    individuals: dict[str, Individual] = field(default_factory=dict)
    families: dict[str, Family] = field(default_factory=dict)
    encoding: str = "UTF-8"

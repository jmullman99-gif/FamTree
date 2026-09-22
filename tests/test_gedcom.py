from pathlib import Path

import pytest

from genealogy_mcp.gedcom.models import GedcomFile, Individual, Family
from genealogy_mcp.gedcom.parser import parse_gedcom


class TestParser:
    def test_parse_marchetti(self, marchetti_ged_path: Path):
        gf = parse_gedcom(str(marchetti_ged_path))
        assert isinstance(gf, GedcomFile)
        assert len(gf.individuals) == 10
        assert len(gf.families) == 3

    def test_individual_fields(self, marchetti_ged_path: Path):
        gf = parse_gedcom(str(marchetti_ged_path))
        giovanni = gf.individuals["@I1@"]
        assert giovanni.given_name == "Giovanni"
        assert giovanni.surname == "Marchetti"
        assert giovanni.sex == "M"
        assert giovanni.birth_date == "ABT 1870"
        assert giovanni.birth_place == "Lucca, Toscana, Italia"
        assert giovanni.death_date == "3 FEB 1942"
        assert giovanni.death_place == "Brooklyn, Kings, New York, USA"
        assert giovanni.occupation == "Stonemason"

    def test_family_fields(self, marchetti_ged_path: Path):
        gf = parse_gedcom(str(marchetti_ged_path))
        f1 = gf.families["@F1@"]
        assert f1.husband_id == "@I1@"
        assert f1.wife_id == "@I2@"
        assert set(f1.child_ids) == {"@I3@", "@I4@"}
        assert f1.marriage_date == "18 APR 1896"
        assert f1.marriage_place == "Brooklyn, Kings, New York, USA"

    def test_family_links(self, marchetti_ged_path: Path):
        gf = parse_gedcom(str(marchetti_ged_path))
        antonio = gf.individuals["@I3@"]
        assert "@F1@" in antonio.famc  # child in family 1
        assert "@F2@" in antonio.fams  # spouse in family 2

    def test_encoding_detected(self, marchetti_ged_path: Path):
        gf = parse_gedcom(str(marchetti_ged_path))
        assert gf.encoding == "UTF-8"

    def test_malformed_file_missing_trailer(self, tmp_path: Path):
        bad = tmp_path / "bad.ged"
        bad.write_text("0 HEAD\n1 CHAR UTF-8\n0 @I1@ INDI\n1 NAME Test /Person/\n")
        gf = parse_gedcom(str(bad))
        assert len(gf.individuals) == 1

    def test_empty_file(self, tmp_path: Path):
        empty = tmp_path / "empty.ged"
        empty.write_text("")
        gf = parse_gedcom(str(empty))
        assert len(gf.individuals) == 0
        assert len(gf.families) == 0

    def test_nonexistent_file(self):
        with pytest.raises(FileNotFoundError):
            parse_gedcom("/nonexistent/file.ged")


import json

from genealogy_mcp.gedcom import tools as gedcom_tools


class TestGedcomTools:
    def setup_method(self):
        gedcom_tools._loaded = None

    def test_load(self, marchetti_ged_path: Path):
        result = gedcom_tools._load_sync(str(marchetti_ged_path))
        assert "10 individuals" in result
        assert "3 families" in result
        assert gedcom_tools._loaded is not None

    def test_search_by_surname(self, marchetti_ged_path: Path):
        gedcom_tools._load_sync(str(marchetti_ged_path))
        results = gedcom_tools._search_sync(name="Marchetti")
        parsed = json.loads(results)
        # Giovanni, Antonio, Rosa, Giovanni Carlo, Mary Catherine, Robert, Anna
        assert len(parsed) == 7

    def test_search_by_sex(self, marchetti_ged_path: Path):
        gedcom_tools._load_sync(str(marchetti_ged_path))
        results = gedcom_tools._search_sync(sex="F")
        parsed = json.loads(results)
        assert len(parsed) == 6  # Maria, Rosa, Margaret, Mary Catherine, Dorothy, Anna
        for p in parsed:
            assert p["sex"] == "F"

    def test_search_no_results(self, marchetti_ged_path: Path):
        gedcom_tools._load_sync(str(marchetti_ged_path))
        results = gedcom_tools._search_sync(name="Nonexistent")
        assert "No individuals found" in results

    def test_search_without_load(self):
        result = gedcom_tools._search_sync(name="Marchetti")
        assert "No GEDCOM file loaded" in result

    def test_person(self, marchetti_ged_path: Path):
        gedcom_tools._load_sync(str(marchetti_ged_path))
        result = gedcom_tools._person_sync("@I1@")
        parsed = json.loads(result)
        assert parsed["given_name"] == "Giovanni"
        assert parsed["surname"] == "Marchetti"

    def test_person_not_found(self, marchetti_ged_path: Path):
        gedcom_tools._load_sync(str(marchetti_ged_path))
        result = gedcom_tools._person_sync("@I999@")
        assert "not found" in result.lower()

    def test_family(self, marchetti_ged_path: Path):
        gedcom_tools._load_sync(str(marchetti_ged_path))
        result = gedcom_tools._family_sync("@F1@")
        parsed = json.loads(result)
        assert parsed["husband"] == "Giovanni Marchetti"
        assert parsed["wife"] == "Maria Rossi"
        assert len(parsed["children"]) == 2

    def test_ancestors(self, marchetti_ged_path: Path):
        gedcom_tools._load_sync(str(marchetti_ged_path))
        result = gedcom_tools._ancestors_sync("@I9@", depth=3)
        parsed = json.loads(result)
        # Robert (@I9@) -> parents Giovanni Carlo + Dorothy -> grandparents Antonio + Margaret
        names = [a["name"] for a in parsed]
        assert "Giovanni Carlo Marchetti" in names
        assert "Antonio Marchetti" in names

    def test_descendants(self, marchetti_ged_path: Path):
        gedcom_tools._load_sync(str(marchetti_ged_path))
        result = gedcom_tools._descendants_sync("@I1@", depth=3)
        parsed = json.loads(result)
        names = [d["name"] for d in parsed]
        assert "Antonio Marchetti" in names
        assert "Robert John Marchetti" in names

    def test_stats(self, marchetti_ged_path: Path):
        gedcom_tools._load_sync(str(marchetti_ged_path))
        result = gedcom_tools._stats_sync()
        parsed = json.loads(result)
        assert parsed["individuals"] == 10
        assert parsed["families"] == 3
        assert "Marchetti" in parsed["surnames"]

from pathlib import Path

import pytest

EXAMPLES_DIR = Path(__file__).resolve().parent.parent / "examples" / "synthetic-family"
MARCHETTI_GED = EXAMPLES_DIR / "marchetti.ged"


@pytest.fixture
def marchetti_ged_path() -> Path:
    """Path to the synthetic Marchetti family GEDCOM file."""
    assert MARCHETTI_GED.exists(), f"Missing test fixture: {MARCHETTI_GED}"
    return MARCHETTI_GED

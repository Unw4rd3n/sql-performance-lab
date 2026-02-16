from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = ROOT / "sql_lab" / "scenarios"


def test_scenarios_have_pairs() -> None:
    before = {p.name.replace(".before.sql", "") for p in SCENARIOS.glob("*.before.sql")}
    after = {p.name.replace(".after.sql", "") for p in SCENARIOS.glob("*.after.sql")}
    assert before, "No before scenarios found"
    assert before == after, f"Mismatch: before={before}, after={after}"


def test_sql_not_empty() -> None:
    for path in SCENARIOS.glob("*.sql"):
        assert path.read_text().strip(), f"Empty SQL file: {path}"

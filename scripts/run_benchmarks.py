from __future__ import annotations

import json
import os
import statistics
import time
from dataclasses import dataclass
from pathlib import Path

import psycopg
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS_DIR = ROOT / "sql_lab" / "scenarios"
REPORTS_DIR = ROOT / "sql_lab" / "reports"
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://lab:lab@localhost:5433/sql_lab")
RUNS = int(os.getenv("BENCH_RUNS", "12"))
WARMUPS = int(os.getenv("BENCH_WARMUPS", "3"))


@dataclass
class BenchResult:
    name: str
    mode: str
    p50_ms: float
    p95_ms: float
    avg_ms: float
    explain: dict


def split_sql(sql_text: str) -> tuple[list[str], str]:
    # Для формата лаборатории считаем, что последний statement - это
    # benchmark query, а все предыдущие - setup (например CREATE INDEX).
    statements = [s.strip() for s in sql_text.split(";") if s.strip()]
    if not statements:
        raise ValueError("Empty SQL")
    if len(statements) == 1:
        return [], statements[0]
    return statements[:-1], statements[-1]


def explain_json(cur: psycopg.Cursor, query: str) -> dict:
    cur.execute(f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}")
    return cur.fetchone()[0][0]


def run_query(cur: psycopg.Cursor, query: str) -> float:
    started = time.perf_counter()
    cur.execute(query)
    cur.fetchall()
    elapsed = (time.perf_counter() - started) * 1000
    return elapsed


def run_single(cur: psycopg.Cursor, name: str, mode: str, sql_path: Path) -> BenchResult:
    setup_stmts, main_query = split_sql(sql_path.read_text())

    for stmt in setup_stmts:
        cur.execute(stmt)

    # Обновляем статистику перед прогонами, чтобы план был ближе к реальности.
    cur.execute("ANALYZE users;")
    cur.execute("ANALYZE orders;")

    # Warmup выравнивает "первый холодный запуск", чтобы не искажать метрики.
    for _ in range(WARMUPS):
        run_query(cur, main_query)

    timings = [run_query(cur, main_query) for _ in range(RUNS)]
    timings.sort()
    p50 = timings[len(timings) // 2]
    p95 = timings[min(len(timings) - 1, int(len(timings) * 0.95))]
    avg = statistics.fmean(timings)
    plan = explain_json(cur, main_query)

    return BenchResult(name=name, mode=mode, p50_ms=round(p50, 2), p95_ms=round(p95, 2), avg_ms=round(avg, 2), explain=plan)


def collect_scenarios() -> list[str]:
    names = set()
    for p in SCENARIOS_DIR.glob("*.before.sql"):
        names.add(p.name.replace(".before.sql", ""))
    return sorted(names)


def main() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    scenarios = collect_scenarios()
    if not scenarios:
        raise RuntimeError("No scenarios found")

    summary = []

    with psycopg.connect(DATABASE_URL, autocommit=True) as conn:
        with conn.cursor() as cur:
            for name in scenarios:
                before_path = SCENARIOS_DIR / f"{name}.before.sql"
                after_path = SCENARIOS_DIR / f"{name}.after.sql"
                if not after_path.exists():
                    raise RuntimeError(f"Missing pair for scenario: {name}")

                before = run_single(cur, name, "before", before_path)
                after = run_single(cur, name, "after", after_path)

                improvement = round(((before.avg_ms - after.avg_ms) / before.avg_ms) * 100, 2) if before.avg_ms > 0 else 0.0

                report = {
                    "scenario": name,
                    "runs": RUNS,
                    "warmups": WARMUPS,
                    "before": before.__dict__,
                    "after": after.__dict__,
                    "improvement_percent": improvement,
                }

                report_path = REPORTS_DIR / f"{name}.report.json"
                report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2))
                summary.append((name, before.avg_ms, after.avg_ms, improvement, str(report_path)))

    print("Benchmark results:")
    for name, b, a, imp, rp in summary:
        print(f"- {name}: avg {b} ms -> {a} ms ({imp}%), report={rp}")


if __name__ == "__main__":
    main()

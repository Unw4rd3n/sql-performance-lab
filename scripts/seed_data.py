from __future__ import annotations

import os
import time
from pathlib import Path

import psycopg
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parents[1]
MIGRATION_SQL = (ROOT / "sql_lab" / "migrations" / "001_init.sql").read_text()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://lab:lab@localhost:5433/sql_lab")
SEED_USERS = int(os.getenv("SEED_USERS", "20000"))
SEED_ORDERS = int(os.getenv("SEED_ORDERS", "500000"))


def wait_db(conn_str: str, attempts: int = 30, delay: float = 1.5) -> None:
    # Нужен в первую очередь для docker-compose: Postgres часто "поднят",
    # но еще не готов принимать коннекты.
    for _ in range(attempts):
        try:
            with psycopg.connect(conn_str):
                return
        except psycopg.Error:
            time.sleep(delay)
    raise RuntimeError("Database is not ready")


def main() -> None:
    # Идея seed-скрипта: каждый запуск дает предсказуемое состояние стенда.
    # Поэтому здесь full reset через TRUNCATE.
    wait_db(DATABASE_URL)
    with psycopg.connect(DATABASE_URL, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(MIGRATION_SQL)

            cur.execute("TRUNCATE TABLE orders, users RESTART IDENTITY CASCADE;")

            cur.execute(
                """
                INSERT INTO users (email, created_at)
                SELECT
                    'user_' || gs || '@example.com',
                    NOW() - (random() * INTERVAL '720 days')
                FROM generate_series(1, %s) AS gs;
                """,
                (SEED_USERS,),
            )

            cur.execute(
                """
                INSERT INTO orders (user_id, status, total_amount, created_at)
                SELECT
                    (1 + floor(random() * %s))::BIGINT,
                    (ARRAY['new','paid','cancelled','refunded'])[1 + floor(random() * 4)::INT],
                    round((50 + random() * 20000)::numeric, 2),
                    NOW() - (random() * INTERVAL '720 days')
                FROM generate_series(1, %s);
                """,
                (SEED_USERS, SEED_ORDERS),
            )

            cur.execute("ANALYZE users;")
            cur.execute("ANALYZE orders;")

    print(
        "Seed complete.\n"
        f"Users: {SEED_USERS}\n"
        f"Orders: {SEED_ORDERS}\n"
        "Tip: run `make run` to generate benchmark reports."
    )


if __name__ == "__main__":
    main()

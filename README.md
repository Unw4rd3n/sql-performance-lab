# SQL Performance Lab

Небольшой "тренажер" по оптимизации SQL в PostgreSQL.
Идея простая: для каждого кейса есть `before/after`, а скрипт сам меряет разницу и сохраняет план выполнения.

Это не учебник по теории индексов, а практический стенд в духе "вот запрос, вот цифры до, вот цифры после".

## Что умеет проект
- Поднимает PostgreSQL 16 в Docker.
- Создает схему и наполняет базу синтетическими данными.
- Хранит сценарии в формате `scenario.before.sql` / `scenario.after.sql`.
- Запускает benchmark с прогревом и несколькими итерациями.
- Сохраняет отчет с `p50/p95/avg` и `EXPLAIN ANALYZE`.

## Быстрый старт
```bash
cp .env.example .env
make up
make seed
make run
```

## Полезные команды
```bash
make up      # поднять Postgres
make down    # остановить Postgres
make seed    # применить схему + сгенерировать данные
make run     # запустить все SQL-сценарии
make test    # проверить парность сценариев и базовую целостность
```

## Как читать отчеты
После `make run` появятся файлы в `sql_lab/reports/`.
Пример: `sql_lab/reports/high_value_orders.report.json`.

Внутри:
- `before` и `after` с метриками latency.
- `improvement_percent` с итоговым приростом.
- JSON-план выполнения, чтобы сравнить стратегию Postgres.

## Структура репозитория
- `docker-compose.yml` - локальная БД.
- `scripts/seed_data.py` - подготовка данных.
- `scripts/run_benchmarks.py` - benchmark runner.
- `sql_lab/migrations/` - DDL.
- `sql_lab/scenarios/` - кейсы оптимизации.
- `sql_lab/reports/` - результат прогона.
- `docs/` - заметки по архитектуре и roadmap.

## Текущий сценарий
`high_value_orders`
- `before`: агрегирующий запрос по периоду и сумме без целевого составного индекса.
- `after`: добавляется индекс `(created_at, total_amount)`, фильтрация выносится в CTE.

## Ограничения текущей версии
- Runner делит SQL по `;` (для lab-сценариев этого достаточно, но не для сложных SQL-скриптов с процедурным кодом).
- Пока нет стабильного "регрессионного" порога, который падал бы в CI при ухудшении производительности.

## Что планируется дальше
- Добавить 2-3 сценария: `JOIN-heavy`, `pagination`, `partial index`.
- Добавить markdown-резюме отчета рядом с JSON.
- Привязать запуск benchmark в CI на nightly.

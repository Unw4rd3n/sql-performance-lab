# SQL Performance Lab

Pet project для backend-портфолио: практический стенд по оптимизации SQL в PostgreSQL.
Проект показывает не только "умение писать запросы", но и инженерный подход:
гипотеза -> измерение -> план выполнения -> фиксация результата.
Идея простая: для каждого кейса есть `before/after`, а скрипт сам меряет разницу и сохраняет план выполнения.

Это не учебник по теории индексов, а рабочий pet-проект в духе:
"вот запрос, вот цифры до, вот цифры после, вот почему стало быстрее".

## Что умеет проект
- Поднимает PostgreSQL 16 в Docker.
- Создает схему и наполняет базу синтетическими данными.
- Хранит сценарии в формате `scenario.before.sql` / `scenario.after.sql`.
- Запускает benchmark с прогревом и несколькими итерациями.
- Сохраняет отчеты в `JSON` и `Markdown` (`p50/p95/avg` + `EXPLAIN ANALYZE`).

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
Примеры:
- `sql_lab/reports/high_value_orders.report.json`
- `sql_lab/reports/high_value_orders.report.md`
- `sql_lab/reports/summary.md`

Внутри:
- `before` и `after` с метриками latency.
- `improvement_percent` с итоговым приростом.
- JSON-план выполнения, чтобы сравнить стратегию Postgres.
- Markdown-выжимка, которую удобно показать в README, HR или техлиду.

## Структура репозитория
- `docker-compose.yml` - локальная БД.
- `scripts/seed_data.py` - подготовка данных.
- `scripts/run_benchmarks.py` - benchmark runner.
- `sql_lab/migrations/` - DDL.
- `sql_lab/scenarios/` - кейсы оптимизации.
- `sql_lab/reports/` - результат прогона.
- `docs/` - заметки по архитектуре и roadmap.

## Сценарии
`high_value_orders`
- `before`: агрегирующий запрос по периоду и сумме без целевого составного индекса.
- `after`: добавляется индекс `(created_at, total_amount)`, фильтрация выносится в CTE.

`join_hot_users`
- `before`: тяжелый `JOIN users + orders` с фильтрацией по paid-заказам за период.
- `after`: partial covering index по paid-заказам + предфильтрация в CTE.

`offset_vs_keyset_pagination`
- `before`: пагинация через глубокий `OFFSET`, который деградирует по мере роста данных.
- `after`: keyset-подход с якорем страницы + индекс под сортировку.

## Ограничения текущей версии
- Runner делит SQL по `;` (для lab-сценариев этого достаточно, но не для сложных SQL-скриптов с процедурным кодом).
- Пока нет стабильного "регрессионного" порога, который падал бы в CI при ухудшении производительности.

## Что планируется дальше
- Привязать запуск benchmark в CI на nightly.

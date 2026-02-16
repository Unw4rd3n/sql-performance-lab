# Roadmap

## v0.2
- Добавить сценарий `join_hot_users`:
  - before: тяжелый join + фильтр без подходящего индекса.
  - after: индекс + предфильтрация.
- Добавить сценарий `offset_pagination`:
  - before: `OFFSET` на больших страницах.
  - after: keyset pagination.

## v0.3
- Вынести генерацию markdown-summary из JSON-репорта.
- Добавить baseline-файл с порогом деградации (например, `+15%` к avg).
- Поднять nightly benchmark в CI.

## v0.4
- Добавить сценарий с partial index.
- Добавить сравнение двух планов по ключевым узлам (`Seq Scan`, `Index Scan`, `Sort`).

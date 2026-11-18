## Структура репозиторію

* `docs/` — діаграма схеми (`graph_schema.drawio`), відображення CQ (`cq_mapping.md`), результати запитів (`cypher_results.md`), звіт GDS (`gds_report.md`), порівняння зі SPARQL (`sparql_vs_cypher.md`).
* `data/` — згенеровані CSV-файли вузлів (8 файлів) та зв'язків з властивостями походження (9 файлів).
* `import/` — Cypher-скрипт імпорту даних (`02_import_data.cypher`) та допоміжні скрипти.
* `queries/` — Cypher-запити для CQ (`03_competency_questions.cypher`), аналізу впливу (`04_impact_analysis.cypher`) та перевірки підграфа (`05_subgraph_verification.cypher`).
* `tests/` — набір тестування text-to-Cypher (`t2c.jsonl`).
* `llm_log/` — журнал взаємодії з LLM (`session_01_schema_and_queries.json`).
* `claims/` — таблиця верифікації тверджень LLM (`claims.csv`).

## Вимоги та версії

* **Neo4j:** 5.x (Neo4j Sandbox / Desktop / Aura Free) із плагіном **Graph Data Science (GDS)**
* **Python:** 3.10+
* **Залежності Python:** `neo4j`, `rdflib` (для порівняння зі SPARQL)

## Запуск з нуля

1. **Генерація CSV-даних (фіксований `seed=42`):**

   ```bash
   python generate_data.py
   ```

2. **Створення обмежень, індексів та імпорт у Neo4j:**
   Виконайте команди створення `UNIQUE` constraints та індексів, після чого запустіть скрипт у Neo4j Browser або через `cypher-shell`:

   ```bash
   cat import/02_import_data.cypher
   ```

   *(Використовує `LOAD CSV WITH HEADERS` та `MERGE` для забезпечення ідемпотентності).*

3. **Виконання аналітичних запитів та GDS:**
   Запустіть запити з `queries/03_competency_questions.cypher`, `queries/04_impact_analysis.cypher` та процедури `gds.pageRank.write` / `gds.louvain.write`.

4. **Запуск валідації text-to-Cypher:**

   ```bash
   python res5_st3-4.py
   ```
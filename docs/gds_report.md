# Результат 4. Аналіз графа та продуктивність (Neo4j GDS)

**Предметна область:** Patient Monitoring (моніторинг стану пацієнтів)  
**Обсяг графа:** 132 вузли, 231 зв'язок  

---

## Крок 1. Виконання алгоритмів PageRank та Louvain

Для аналізу структури графа знань моніторингу пацієнтів створено неорієнтовану проєкцію `medicalGraph` у пам'яті бібліотеки Neo4j Graph Data Science (GDS) та виконано алгоритми **PageRank** (оцінка центральності та впливовості вузлів) і **Louvain** (виявлення спільнот/кластерів):

```cypher
CALL gds.graph.project(
  'medicalGraph',
  '*',
  {
    ALL: {
      type: '*',
      orientation: 'UNDIRECTED'
    }
  }
);
```

### 1. Топ-10 найвпливовіших вузлів за алгоритмом PageRank

```cypher
CALL gds.pageRank.write('medicalGraph', {
  maxIterations: 20,
  dampingFactor: 0.85,
  writeProperty: 'pagerank'
})
YIELD nodePropertiesWritten
MATCH (n)
RETURN labels(n)[0] AS label,
       coalesce(n.name, n.fullName, n.symptomId, n.feedbackId, n.actionId, n.deviceId, n.vitalId) AS entity,
       round(n.pagerank, 4) AS pageRankScore
ORDER BY pageRankScore DESC
LIMIT 10;
```

| № | Тип вузла (`label`) | Сутність (`entity`) | Оцінка PageRank (`pageRankScore`) |
|---|---|---|---|
| 1 | `Symptom` | Задишка | 2.8211 |
| 2 | `HealthcareProvider` | Д-р Сміт Джон | 2.2726 |
| 3 | `MedicalCondition` | Артеріальна гіпертензія | 2.2180 |
| 4 | `MedicalCondition` | Бронхіальна астма | 2.0700 |
| 5 | `MedicalCondition` | Хронічна серцева недостатність | 1.8935 |
| 6 | `Patient` | Олійник Марія Олександрівна | 1.8784 |
| 7 | `HealthcareProvider` | Д-р Мороз Віталій | 1.7609 |
| 8 | `Patient` | Шевчук Вікторія Олександрівна | 1.7364 |
| 9 | `Patient` | Мороз Олена Олександрівна | 1.7287 |
| 10 | `Patient` | Шевчук Катерина Олександрівна | 1.7194 |

### 2. Виявлені спільноти за алгоритмом Louvain (9 кластерів)

```cypher
CALL gds.louvain.write('medicalGraph', {
  writeProperty: 'community'
})
YIELD communityCount, modularity
MATCH (n)
RETURN n.community AS communityId,
       count(n) AS membersCount,
       collect(DISTINCT labels(n)[0]) AS nodeTypes,
       collect(coalesce(n.name, n.fullName, n.feedbackId, n.actionId))[0..5] AS sampleMembers
ORDER BY membersCount DESC;
```

Алгоритм Louvain виділив у графі **9 спільнот** (критерій C1 — $\ge 3$ спільноти):

| ID спільноти (`communityId`) | Кількість вузлів | Типи вузлів у кластері | Приклади сутностей |
|---|---|---|---|
| `104` | 25 | `Patient`, `HealthcareProvider`, `MedicalDevice`, `MedicalCondition`, `PatientFeedback`, `VitalSign`, `Action` | Мельник Ірина Василівна, Ткаченко Василь Олександрович, Шевченко Ганна Олександрівна |
| `80` | 22 | `Patient`, `HealthcareProvider`, `MedicalDevice`, `PatientFeedback`, `VitalSign` | Мороз Василь Олександрович, Мороз Олена Олександрівна, Поліщук Віктор Олександрович |
| `85` | 19 | `Patient`, `HealthcareProvider`, `MedicalDevice`, `MedicalCondition`, `Symptom`, `PatientFeedback`, `VitalSign`, `Action` | Олійник Марія Олександрівна, Шевченко Світлана Олександрівна, Д-р Коваль Марія |
| `74` | 17 | `Patient`, `MedicalDevice`, `MedicalCondition`, `Symptom`, `PatientFeedback`, `VitalSign`, `Action` | Бондаренко Тарас Ігорович, Мороз Наталія Олександрівна, Нестабільна стенокардія, Задишка, Біль у грудях |
| `76` | 12 | `Patient`, `MedicalDevice`, `MedicalCondition`, `Symptom`, `PatientFeedback`, `VitalSign`, `Action` | Ткаченко Віктор Олександрович, Артеріальна гіпертензія, Прискорене серцебиття, Запаморочення |
| `110` | 11 | `Patient`, `MedicalDevice`, `Symptom`, `PatientFeedback`, `VitalSign`, `Action` | Коваленко Олександр Петрович, Набряки нижніх кінцівок, `fb_01`, `fb_16` |
| `88` | 10 | `Patient`, `MedicalDevice`, `MedicalCondition`, `Symptom`, `PatientFeedback`, `VitalSign`, `Action` | Олійник Сергій Олександрович, Хронічна серцева недостатність, Загальна слабкість, `fb_08` |
| `86` | 10 | `Patient`, `MedicalDevice`, `MedicalCondition`, `Symptom`, `PatientFeedback`, `VitalSign`, `Action` | Поліщук Марія Олександрівна, Фібриляція передсердь, Хрипи при диханні, Перебої в роботі серця |
| `83` | 6 | `Patient`, `MedicalDevice`, `Symptom`, `PatientFeedback`, `VitalSign`, `Action` | Савченко Юрій Олександрович, Підвищена температура, `fb_18`, `action_12` |

---

## Крок 2. Інтерпретація результатів для предметної області

1. **Центральна роль клінічних симптомів:** найвищий показник PageRank (`2.8211`) отримав симптом «Задишка», оскільки він є спільним клінічним проявом одразу для кількох захворювань (хронічної серцевої недостатності, бронхіальної астми, пневмонії) та найчастіше фігурує у текстових відгуках пацієнтів.
2. **Вузли концентрації клінічного навантаження:** друге місце за PageRank (`2.2726`) посідає кардіолог Д-р Сміт Джон, а сьоме (`1.7609`) — Д-р Мороз Віталій, що підтверджує їхню ключову роль як хабів координації лікування найбільшої кількості пацієнтів у графі знань.
3. **Провідні нозології:** до першої п'ятірки найвпливовіших вузлів увійшли три хронічні діагнози — «Артеріальна гіпертензія» (`2.2180`), «Бронхіальна астма» (`2.0700`) та «Хронічна серцева недостатність» (`1.8935`), які генерують найбільшу кількість зв'язків із пацієнтами та асоційованими симптомами.
4. **Пацієнти зі складним профілем:** потрапляння пацієнтів Олійник Марії, Шевчук Вікторії, Мороз Олени та Шевчук Катерини до топ-10 за PageRank пояснюється високою щільністю їхніх локальних зв'язків — наявністю супутніх діагнозів, кількох відгуків, датчиків моніторингу та ініційованих клінічних дій.
5. **Клінічна кластеризація за алгоритмом Louvain:** розбиття графа на 9 спільнот чітко відображає предметну область — сформувалися спеціалізовані нозологічні кластери навколо конкретних діагнозів та їхніх типових симптомів (наприклад, кластер `74` об'єднує нестабільну стенокардію, біль у грудях і задишку, кластер `76` — артеріальну гіпертензію та тахікардію, кластер `88` — хронічну серцеву недостатність).
6. **Практична цінність для системи знань:** поєднання метрик PageRank і Louvain дає змогу автоматично виявляти критичні симптоми-маркери для першочергового скринінгу, балансувати навантаження на лікарів-хабів і групувати пацієнтів за подібними клінічними профілями.

---

## Крок 3. Профілювання запитів (`PROFILE`) та оптимізація продуктивності

### 1. Профілювання Запиту 1 (базовий індексний пошук)

Для перевірки базової продуктивності графового обходу виконано профілювання (`PROFILE`) запиту, який знаходить кардіолога Д-ра Сміта Джона за унікальним ідентифікатором `doc_smith`, переходить до всіх його пацієнтів та збирає список їхніх підтверджених клінічних діагнозів:

```cypher
PROFILE
MATCH (hp:HealthcareProvider {providerId: 'doc_smith'})-[:TREATS]->(p:Patient)-[:HAS_CONDITION]->(c:MedicalCondition)
RETURN hp.name AS doctor, p.fullName AS patient, collect(c.name) AS conditions;
```

У результаті профілювання встановлено, що планувальник Neo4j використовує точковий пошук за унікальним індексом `NodeUniqueIndexSeek` по властивості `HealthcareProvider(providerId)` (усього 2 звернення до БД), після чого послідовно розгортає зв'язки `TREATS` та `HAS_CONDITION` (`Expand(All)`). Запит повертає 10 рядків за 175 звернень до бази даних (`Total database accesses: 175`) і потребує мінімального обсягу пам'яті (`5 584 bytes`), що підтверджує високу ефективність запитів із вхідним пошуком за індексованим ключем.

### 2. Профілювання Запиту 2 ДО оптимізації

Для виявлення вузьких місць продуктивності виконано профілювання запиту, який шукає пацієнтів, що одночасно залишили негативний відгук (`sentimentLabel = 'Negative'`) і мають зафіксовану тахікардію (`vitalType = 'HeartRate'` та `valueNumeric > 110`):

```cypher
PROFILE
MATCH (p:Patient)-[:SUBMITTED]->(f:PatientFeedback)
MATCH (p)-[:HAS_VITAL_SIGN]->(v:VitalSign)
WHERE f.sentimentLabel = 'Negative' AND v.vitalType = 'HeartRate' AND v.valueNumeric > 110
RETURN p.fullName AS patient, f.feedbackText AS complaint, v.valueNumeric AS heartRate;
```

У результаті аналізу плану виконання виявлено суттєві накладні витрати: через відсутність індексів на полях `sentimentLabel`, `vitalType` та `valueNumeric` СУБД виконує повне сканування всіх вузлів мітки `PatientFeedback` (`NodeByLabelScan`, 31 звернення до БД), фільтрує їх (`Filter`, 30 звернень) і лише потім розгортає зв'язки до пацієнтів та всіх вимірювань (`Expand(All)`, 140 звернень) із повторною фільтрацією значень пульсу (70 звернень). Загалом для отримання 6 цільових рядків система виконує **384 звернення до БД** (`DB Hits`).

### 3. Оптимізація Запиту 2 та профілювання ПІСЛЯ оптимізації

Для усунення повного сканування вузлів (`NodeByLabelScan`) та зменшення кількості звернень до диска було створено два індекси — на властивості `PatientFeedback(sentimentLabel)` та складений індекс на `VitalSign(vitalType, valueNumeric)`, а сам запит переписано так, щоб пошук починався з найвужчої вибірки за складеним індексом:

```cypher
CREATE INDEX feedback_sentiment_idx IF NOT EXISTS FOR (f:PatientFeedback) ON (f.sentimentLabel);
CREATE INDEX vital_type_val_idx IF NOT EXISTS FOR (v:VitalSign) ON (v.vitalType, v.valueNumeric);

PROFILE
MATCH (v:VitalSign)<-[:HAS_VITAL_SIGN]-(p:Patient)-[:SUBMITTED]->(f:PatientFeedback {sentimentLabel: 'Negative'})
WHERE v.vitalType = 'HeartRate' AND v.valueNumeric > 110
RETURN p.fullName AS patient, f.feedbackText AS complaint, v.valueNumeric AS heartRate;
```

У результаті оптимізації планувальник Neo4j замінив дороге сканування всіх вузлів (`NodeByLabelScan`) на точковий діапазонний пошук за індексом `NodeIndexSeek` (`vital_type_val_idx`), який одразу відібрав 5 цільових вимірювань усього за 6 звернень до БД. Загальна кількість звернень до бази даних (`Total database accesses`) скоротилася з **384 до 114** (зменшення на **70,3%** або у **3,37 раза**) при збереженні ідентичного результату вибірки (6 рядків).

| Метрика продуктивності | До оптимізації | Після оптимізації | Ефект оптимізації |
|---|---|---|---|
| Початковий оператор плану | `NodeByLabelScan` (`PatientFeedback`) | `NodeIndexSeek` (`vital_type_val_idx`) | Перехід від повного сканування до індексного пошуку |
| Звернення до БД (`Total DB Hits`) | **384** | **114** | **-270 звернень (-70,3%)** |
| Кількість повернутих рядків | 6 | 6 | Без змін |

---

## Крок 4. Збереження результатів алгоритмів як властивостей вузлів (`pagerank`, `community`)

Для закріплення обчислених метрик аналізу графа безпосередньо в базі даних Neo4j результати роботи алгоритмів **PageRank** та **Louvain** було записано у властивості кожного вузла за допомогою процедур `gds.pageRank.write` (`writeProperty: 'pagerank'`) та `gds.louvain.write` (`writeProperty: 'community'`), після чого виконано контрольний запит для перевірки збережених атрибутів у вузлах бази:

```cypher
MATCH (n)
WHERE n.pagerank IS NOT NULL AND n.community IS NOT NULL
RETURN labels(n)[0] AS label,
       coalesce(n.name, n.fullName, n.feedbackId, n.actionId, n.deviceId, n.vitalId) AS entity,
       round(n.pagerank, 4) AS pagerank,
       n.community AS community
ORDER BY pagerank DESC
LIMIT 10;
```

У результаті виконання запиту підтверджено, що для всіх 132 вузлів графа знань сформовано та збережено два постійні атрибути — числовий індекс впливовості `pagerank` та ідентифікатор кластера `community` (наприклад, для вузла «Задишка» записано `pagerank = 2.8211` і `community = 74`, а для «Д-р Сміт Джон» — `pagerank = 2.2726` і `community = 104`). Збереження цих властивостей безпосередньо в структурі вузлів дає змогу використовувати їх у подальших аналітичних Cypher-запитах для швидкої фільтрації та ранжування сутностей без повторного перерахунку алгоритмів GDS.

---

## Самооцінка за критеріями перевірки (Результат 4)

| № | Критерій перевірки | Статус | Підтвердження виконання |
|---|---|---|---|
| **C1** | PageRank і Louvain виконано; наведено топ-10 і $\ge 3$ спільноти | Виконано | Виведено Топ-10 вузлів за PageRank та 9 спільнот за Louvain |
| **C2** | Є змістовна інтерпретація ($\ge 5$ речень) | Виконано | Наведено 6 розгорнутих пунктів інтерпретації для ПдО моніторингу пацієнтів |
| **C3** | `PROFILE` для 2 запитів; є до/після оптимізації | Виконано | Виконано `PROFILE` для 2 запитів; створено 2 індекси, зменшено `DB Hits` з 384 до 114 (-70,3%) |
| **C4** | Результати збережено у графі | Виконано | Властивості `pagerank` і `community` записано в усі 132 вузли графа через `.write()` |
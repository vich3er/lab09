# Результат 3. Виконання та інтерпретація аналітичних запитів Cypher

## Крок 1-2. Компетентнісні питання (CQ1-CQ9)

### CQ1. Виявлення пацієнтів із негативними відгуками, симптомами та діагнозами

* **CQ:** Які пацієнти залишили негативні відгуки, які симптоми згадуються в цих зверненнях та які підтверджені діагнози мають ці пацієнти?
* **Запит:**
```cypher
MATCH (p:Patient)-[:SUBMITTED]->(f:PatientFeedback)-[ms:MENTIONS_SYMPTOM]->(s:Symptom)
WHERE f.sentimentLabel = 'Negative'
OPTIONAL MATCH (p)-[:HAS_CONDITION]->(c:MedicalCondition)
RETURN p.patientId AS patientId,
       p.fullName AS patient,
       p.ward AS ward,
       f.sentimentScore AS sentimentScore,
       s.name AS symptom,
       s.severity AS severity,
       ms.confidence AS extractionConfidence,
       collect(DISTINCT c.name) AS conditions
ORDER BY f.sentimentScore ASC;
```
* **Результат:** Виявлено пацієнтів із найнижчими оцінками тональності відгуків та тяжкими симптомами. Найкритичніші показники зафіксовано у Мороз Олени Олександрівни (`patient_09`, `sentimentScore = -0.92`, «Біль у грудях», `confidence = 0.82`) та Бондаренка Тараса Ігоровича (`patient_03`, `sentimentScore = -0.9`, задишка та біль у грудях при нестабільній стенокардії).
* **Інтерпретація:** Поєднання текстових відгуків із медичними діагнозами дозволяє швидко ідентифікувати пацієнтів групи високого ризику з гострим погіршенням стану.

### CQ2. Зіставлення критичних життєвих показників з датчиків із відгуками та реакцією медперсоналу

* **CQ:** Які пацієнти мають критичні відхилення життєвих показників з медичних датчиків, які відгуки вони залишили та чи була створена відповідна клінічна дія?
* **Запит:**
```cypher
MATCH (p:Patient)-[:IS_MONITORED_BY]->(d:MedicalDevice)-[:MEASURES]->(v:VitalSign)
WHERE (v.vitalType = 'SpO2' AND v.valueNumeric < 92)
   OR (v.vitalType = 'SystolicBP' AND v.valueNumeric > 150)
   OR (v.vitalType = 'HeartRate' AND v.valueNumeric > 110)
OPTIONAL MATCH (p)-[:SUBMITTED]->(f:PatientFeedback)
OPTIONAL MATCH (a:Action)-[:TRIGGERED_BY]->(f)
RETURN p.patientId AS patientId,
       p.fullName AS patient,
       d.deviceType AS device,
       v.vitalType AS vitalType,
       v.valueNumeric AS value,
       v.unit AS unit,
       f.sentimentLabel AS feedbackSentiment,
       collect(DISTINCT a.actionType) AS triggeredActions
ORDER BY p.patientId ASC;
```
* **Результат:** Виявлено пацієнтів із підвищеним пульсом (`HeartRate > 110 bpm`) від `WearableSensor`. Для `patient_03` (`125.0 bpm`) та `patient_08` (`132.1 bpm`) ініційовано `Alert`, для `patient_10`, `patient_14` та `patient_17` - `MedicationAdjustment`, тоді як для `patient_21` та `patient_06` дії відсутні (`[]`).
* **Інтерпретація:** Інтеграція телеметрії датчиків із відгуками дозволяє контролювати своєчасність реакції медперсоналу.

### CQ3. Аналіз навантаження на медперсонал та кількості негативних відгуків серед пацієнтів

* **CQ:** Яке навантаження за кількістю пацієнтів мають медичні працівники та скільки негативних відгуків залишили їхні пацієнти?
* **Запит:**
```cypher
MATCH (hp:HealthcareProvider)-[:TREATS]->(p:Patient)
OPTIONAL MATCH (p)-[:SUBMITTED]->(f:PatientFeedback)
WITH hp,
     count(DISTINCT p) AS totalPatients,
     count(DISTINCT f) AS totalFeedbacks,
     count(DISTINCT CASE WHEN f.sentimentLabel = 'Negative' THEN f END) AS negativeFeedbacks
RETURN hp.providerId AS providerId,
       hp.name AS providerName,
       hp.specialization AS specialization,
       totalPatients,
       totalFeedbacks,
       negativeFeedbacks
ORDER BY negativeFeedbacks DESC, totalPatients DESC;
```
* **Результат:** Найбільше пацієнтів (10) та негативних відгуків (11 із 13) має кардіолог Д-р Сміт Джон (`doc_smith`), далі Д-р Коваль Марія (7 пацієнтів, 5 негативних) та медсестра Джой Анна (5 пацієнтів, 4 негативні). Найменше у медсестри Бойко Надії (3 пацієнти, 2 негативні).
* **Інтерпретація:** Агрегація зв'язків `TREATS` та `SUBMITTED` дає змогу оцінити розподіл навантаження між персоналом і виявити відділення з найбільшою кількістю скарг.

### CQ4. Пошук потенційних симптомів на основі клінічних діагнозів (проактивний моніторинг)

* **CQ:** Які типові симптоми, пов'язані з підтвердженими діагнозами пацієнтів, ще не були згадані в їхніх текстових відгуках і потребують перевірки лікарем?
* **Запит:**
```cypher
MATCH (p:Patient)-[:HAS_CONDITION]->(c:MedicalCondition)-[:ASSOCIATED_WITH_SYMPTOM]->(s:Symptom)
WHERE NOT (p)-[:SUBMITTED]->(:PatientFeedback)-[:MENTIONS_SYMPTOM]->(s)
RETURN p.patientId AS patientId,
       p.fullName AS patient,
       c.name AS condition,
       collect(DISTINCT s.name) AS potentialUnreportedSymptoms
ORDER BY p.patientId ASC
LIMIT 10;
```
* **Результат:** Для `patient_01` (хронічна серцева недостатність) рекомендовано перевірити набряки нижніх кінцівок та слабкість, для `patient_03` (нестабільна стенокардія) - прискорене серцебиття, для `patient_05` (COVID-19 та астма) - температуру, зниження сатурації та хрипи.
* **Інтерпретація:** Використання зв'язку `ASSOCIATED_WITH_SYMPTOM` дозволяє формувати проактивні підказки для виявлення прихованих ускладнень.

### CQ5. Оцінка критичності стану пацієнтів у розрізі лікарняних палат

* **CQ:** Який розподіл пацієнтів, середньої тональності відгуків та кількості тяжких/критичних симптомів спостерігається у розрізі лікарняних палат?
* **Запит:**
```cypher
MATCH (p:Patient)
OPTIONAL MATCH (p)-[:SUBMITTED]->(f:PatientFeedback)
OPTIONAL MATCH (f)-[:MENTIONS_SYMPTOM]->(s:Symptom)
WITH p.ward AS ward,
     count(DISTINCT p) AS patientsCount,
     round(avg(f.sentimentScore), 2) AS avgSentiment,
     count(DISTINCT CASE WHEN s.severity IN ['Critical', 'Severe'] THEN s END) AS severeSymptomsCount
RETURN ward,
       patientsCount,
       avgSentiment,
       severeSymptomsCount
ORDER BY avgSentiment ASC, severeSymptomsCount DESC;
```
* **Результат:** Найнижчу середню тональність зафіксовано в палаті `Therapy-1` (`-0.57`, 2 пацієнти) та `Pulmonology-1` (`-0.37`, 4 пацієнти, 2 тяжкі симптоми). Найбільша концентрація тяжких симптомів у `Cardiology-1` (9 пацієнтів, `avgSentiment = -0.3`, 4 тяжкі симптоми).
* **Інтерпретація:** Агрегація за палатами допомагає оперативно перерозподіляти ресурси медперсоналу та посилювати нагляд у критичних палатах.

### CQ6. Аудит клінічних дій, ініційованих за відгуками пацієнтів, та відповідальних лікарів

* **CQ:** Які клінічні дії були ініційовані на основі негативних відгуків пацієнтів, хто з медперсоналу відповідає за цих пацієнтів та який рівень достовірності тригера?
* **Запит:**
```cypher
MATCH (hp:HealthcareProvider)-[:TREATS]->(p:Patient)-[:SUBMITTED]->(f:PatientFeedback)<-[tb:TRIGGERED_BY]-(a:Action)
RETURN a.actionId AS actionId,
       a.actionType AS actionType,
       a.description AS description,
       p.fullName AS patient,
       hp.name AS assignedProvider,
       f.sentimentLabel AS sentiment,
       tb.confidence AS triggerConfidence
ORDER BY tb.confidence DESC;
```
* **Результат:** Усі 16 записів ініційовані негативними відгуками (`Negative`) із достовірністю `0.97-1.0`. Найвищу впевненість (`1.0`) має `action_07` для Шевченко Світлани Олександрівни, а екстрені сигнали (`Alert`, `0.99`) сформовані для пацієнтів Д-ра Сміта Джона.
* **Інтерпретація:** Наскрізний обхід графа забезпечує прозорий аудит прийняття рішень та визначає відповідальних фахівців.

### CQ7. Аналіз пацієнтів із супутніми діагнозами (коморбідністю) та їхнього моніторингу

* **CQ:** Які пацієнти мають одночасно два або більше підтверджених клінічних діагнози, якими медичними пристроями вони моніторяться та скільки відгуків залишили?
* **Запит:**
```cypher
MATCH (p:Patient)-[:HAS_CONDITION]->(c:MedicalCondition)
WITH p, collect(DISTINCT c.name) AS conditions
WHERE size(conditions) >= 2
OPTIONAL MATCH (p)-[:IS_MONITORED_BY]->(d:MedicalDevice)
OPTIONAL MATCH (p)-[:SUBMITTED]->(f:PatientFeedback)
RETURN p.patientId AS patientId,
       p.fullName AS patient,
       conditions,
       collect(DISTINCT d.deviceType) AS devices,
       count(DISTINCT f) AS feedbackCount
ORDER BY size(conditions) DESC, patientId ASC;
```
* **Результат:** Виявлено 8 пацієнтів із двома супутніми захворюваннями (`patient_05`, `patient_09`, `patient_10`, `patient_14`, `patient_18`, `patient_19`, `patient_20`, `patient_23`), кожен із яких забезпечений моніторингом (`PulseOximeter` або `WearableSensor`) та залишив 1-2 відгуки.
* **Інтерпретація:** Перевірка коморбідних станів підтверджує охоплення пацієнтів підвищеного ризику апаратним моніторингом.

### CQ8. Рейтинг клінічних симптомів за частотою згадувань у відгуках та зв'язками з діагнозами

* **CQ:** Які клінічні симптоми найчастіше згадуються у відгуках пацієнтів, який середній рівень достовірності їх вилучення з тексту та зі скількома діагнозами пов'язаний кожен симптом?
* **Запит:**
```cypher
MATCH (s:Symptom)
OPTIONAL MATCH (f:PatientFeedback)-[ms:MENTIONS_SYMPTOM]->(s)
OPTIONAL MATCH (c:MedicalCondition)-[:ASSOCIATED_WITH_SYMPTOM]->(s)
RETURN s.symptomId AS symptomId,
       s.name AS symptom,
       s.severity AS severity,
       count(DISTINCT f) AS feedbackMentions,
       round(avg(ms.confidence), 2) AS avgConfidence,
       count(DISTINCT c) AS linkedConditions
ORDER BY feedbackMentions DESC, linkedConditions DESC;
```
* **Результат:** Найчастіше згадуються «Задишка» (7 згадувань, `avgConfidence = 0.89`, 3 діагнози) та «Сухий кашель» (4 згадування, `avgConfidence = 0.96`, 2 діагнози), тоді як «Прискорене серцебиття» має `0` згадувань попри зв'язок із двома діагнозами.
* **Інтерпретація:** Зіставлення суб'єктивних скарг із базою знань дозволяє оцінити якість вилучення сутностей (`0.81-0.96`) та виявити симптоми, що потребують контролю датчиками.

### CQ9. Пошук найкоротшого ланцюжка зв'язків між лікарем та екстреною клінічною дією (shortestPath)

* **CQ:** Який найкоротший шлях у графі поєднує кардіолога Д-ра Сміта Джона (`doc_smith`) з екстреним тривожним сповіщенням (`action_alert_01`) та через які проміжні сутності він проходить?
* **Запит:**
```cypher
MATCH path = shortestPath(
  (hp:HealthcareProvider {providerId: 'doc_smith'})-[*..5]-(a:Action {actionId: 'action_alert_01'})
)
RETURN [n IN nodes(path) | labels(n)[0] + ': ' + coalesce(n.name, n.fullName, n.feedbackId, n.actionId)] AS pathNodes,
       [r IN relationships(path) | type(r)] AS relationshipChain,
       length(path) AS hops;
```
* **Результат:** Знайдено найкоротший маршрут довжиною в 3 переходи (`hops = 3`): `HealthcareProvider: Д-р Сміт Джон` -> `Patient: Бондаренко Тарас Ігорович` -> `PatientFeedback: fb_03` -> `Action: action_alert_01` за ланцюжком `["TREATS", "SUBMITTED", "TRIGGERED_BY"]`.
* **Інтерпретація:** Функція `shortestPath` зі шляхом змінної довжини (`[*..5]`) дозволяє швидко відновлювати причинно-наслідкові ланцюжки між лікарем та тривожними подіями.

## Крок 3. Запити «аналіз впливу» (глибина >= 3)

### IA1. Каскадний вплив захворювання на негативні скарги та медичні втручання (глибина 3)

* **CQ:** Який каскадний вплив мають первинні клінічні діагнози (`MedicalCondition`) на кількість уражених пацієнтів, поданих скарг та ініційованих клінічних дій на глибині 3 переходів?
* **Запит:**
```cypher
MATCH path = (c:MedicalCondition)<-[:HAS_CONDITION]-(p:Patient)-[:SUBMITTED]->(f:PatientFeedback)<-[:TRIGGERED_BY]-(a:Action)
RETURN c.name AS rootCondition,
       length(path) AS impactDepth,
       count(DISTINCT p) AS affectedPatients,
       count(DISTINCT f) AS triggeredFeedbacks,
       collect(DISTINCT a.actionType) AS downstreamActions,
       count(DISTINCT a) AS totalActionsCount
ORDER BY totalActionsCount DESC, affectedPatients DESC;
```
* **Результат:** Найбільший каскадний вплив на глибині 3 переходів має «Хронічна серцева недостатність» (4 пацієнти, 4 скарги, 4 дії `MedicationAdjustment` та `Alert`) і «Гострий бронхіт» (3 пацієнти, 3 дії `MedicationAdjustment`).
* **Інтерпретація:** Аналіз залежностей на глибині 3 рівні показує, які первинні діагнози створюють найбільше вторинне навантаження на систему реагування.

### IA2. Вплив аномальних показників із медичних датчиків на скарги пацієнтів та клінічні дії (глибина 4)

* **CQ:** Як критичні відхилення фізіологічних показників (`VitalSign`), зафіксовані медичними пристроями (`MedicalDevice`), поширюються по графу до скарг пацієнтів (`PatientFeedback`) та клінічних втручань (`Action`) на глибині 4 переходів?
* **Запит:**
```cypher
MATCH path = (v:VitalSign)<-[:MEASURES]-(d:MedicalDevice)<-[:IS_MONITORED_BY]-(p:Patient)-[:SUBMITTED]->(f:PatientFeedback)<-[:TRIGGERED_BY]-(a:Action)
WHERE (v.vitalType = 'HeartRate' AND v.valueNumeric > 110)
   OR (v.vitalType = 'SpO2' AND v.valueNumeric < 92)
   OR (v.vitalType = 'SystolicBP' AND v.valueNumeric > 150)
RETURN v.vitalType AS vitalType,
       v.valueNumeric AS measuredValue,
       d.deviceType AS sourceDevice,
       p.fullName AS affectedPatient,
       f.sentimentLabel AS feedbackSentiment,
       a.actionType AS resultingAction,
       length(path) AS impactDepth
ORDER BY v.valueNumeric DESC;
```
* **Результат:** Виявлено 5 ланцюжків каскадного впливу глибиною 4 переходи, де підвищений пульс (`HeartRate` 112.1-136.9 bpm) від `WearableSensor` корелює з негативними відгуками (`Negative`) і завершується діями `MedicationAdjustment` (3 випадки) або `Alert` (2 випадки).
* **Інтерпретація:** Проходження графа на глибину 4 рівні об'єднує апаратну телеметрію з суб'єктивними скаргами та рішеннями лікарів.

## Крок 4. Ручна перевірка результатів 3 запитів на малому підграфі

Для верифікації коректності виконання Cypher-запитів виділено локальний підграф (12 вузлів та 11 зв'язків) навколо пацієнта `patient_03` (Бондаренко Тарас Ігорович).

* **Запит контрольного підграфа:**
```cypher
MATCH (p:Patient {patientId: 'patient_03'})
OPTIONAL MATCH (hp:HealthcareProvider)-[r1:TREATS]->(p)
OPTIONAL MATCH (p)-[r2:HAS_CONDITION]->(c:MedicalCondition)
OPTIONAL MATCH (p)-[r3:SUBMITTED]->(f:PatientFeedback)-[r4:MENTIONS_SYMPTOM]->(s:Symptom)
OPTIONAL MATCH (a:Action)-[r5:TRIGGERED_BY]->(f)
OPTIONAL MATCH (p)-[r6:IS_MONITORED_BY]->(d:MedicalDevice)-[r7:MEASURES]->(v:VitalSign)
RETURN p, hp, r1, c, r2, f, r3, s, r4, a, r5, d, r6, v, r7;
```

* **Ручна верифікація на підграфі:**
  1. **Перевірка CQ1:** на підграфі від вузла `patient_03` відходить зв'язок `HAS_CONDITION` до діагнозу `Нестабільна стенокардія` та зв'язок `SUBMITTED` до негативного відгуку `fb_03`, який через ребра `MENTIONS_SYMPTOM` вказує на симптоми `Біль у грудях` та `Задишка`. Це збігається з рядками 2-3 таблиці результатів CQ1.
  2. **Перевірка CQ9 (`shortestPath`):** візуальне проходження зв'язків підтверджує найкоротший маршрут довжиною в 3 переходи: `Д-р Сміт Джон` -[TREATS]-> `Бондаренко Тарас Ігорович` -[SUBMITTED]-> `fb_03` <-[TRIGGERED_BY]- `action_alert_01` (`hops = 3`).
  3. **Перевірка IA1 (аналіз впливу):** на підграфі зафіксовано повний 3-рівневий ланцюжок від діагнозу `Нестабільна стенокардія` через пацієнта та відгук `fb_03` до дії типу `Alert`, що підтверджує коректність агрегації у запиті IA1.

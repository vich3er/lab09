# Відображення компетентнісних питань (CQ) та порівняння схем

## 1. Компетентнісні питання та шаблони Cypher-шляхів

| № CQ | Компетентнісне питання (CQ) | Шаблон Cypher-шляху (`MATCH`) | Очікуваний результат / мета |
| :--- | :--- | :--- | :--- |
| **CQ1** | Якими медичними пристроями здійснюється моніторинг конкретного пацієнта? | `(p:Patient)-[:IS_MONITORED_BY]->(d:MedicalDevice)` | Отримання переліку активних приладів моніторингу для пацієнта. |
| **CQ2** | Які фідбеки (із текстом та оцінкою тональності) залишив кожен пацієнт? | `(p:Patient)-[:SUBMITTED]->(f:PatientFeedback)` | Збір усіх відгуків пацієнта для оцінки динаміки його самопочуття. |
| **CQ3** | Які симптоми та якого рівня тяжкості згадуються у негативних фідбеках пацієнтів? | `(p:Patient)-[:SUBMITTED]->(f:PatientFeedback)-[:MENTIONS_SYMPTOM]->(s:Symptom)` | Виявлення скарг пацієнтів, що потребують першочергової уваги лікаря. |
| **CQ4** | Які клінічні дії (тривоги, коригування лікування) були ініційовані відгуками конкретного пацієнта? | `(p:Patient)-[:SUBMITTED]->(f:PatientFeedback)<-[:TRIGGERED_BY]-(a:Action)` | Відстеження реакції медичної системи на скарги пацієнта. |
| **CQ5** | Які медичні стани (гострі чи хронічні) пацієнта пов'язані із симптомами, про які він повідомив у відгуку? | `(p:Patient)-[:HAS_CONDITION]->(c:MedicalCondition)-[:ASSOCIATED_WITH_SYMPTOM]->(s:Symptom)<-[:MENTIONS_SYMPTOM]-(f:PatientFeedback)<-[:SUBMITTED]-(p)` | Зіставлення суб'єктивних скарг пацієнта з його підтвердженим діагнозом. |
| **CQ6** | Які супутні симптоми транзитивно пов'язані з первинним симптомом, згаданим у фідбеку? | `(f:PatientFeedback)-[:MENTIONS_SYMPTOM]->(s1:Symptom)-[:ASSOCIATED_WITH_SYMPTOM*1..3]->(s2:Symptom)` | Прогнозування можливих ускладнень або супутніх проявів хвороби. |
| **CQ7** | Які життєві показники пацієнта виходять за межі норми та яким саме пристроєм вони зафіксовані? | `(p:Patient)-[:IS_MONITORED_BY]->(d:MedicalDevice)-[:MEASURES]->(v:VitalSign)<-[:HAS_VITAL_SIGN]-(p)` | Валідація аномальних біометричних показників із прив'язкою до сенсора. |
| **CQ8** | Які лікарі або медсестри ведуть пацієнтів, чиї фідбеки викликали критичні тривоги (`AlertAction`)? | `(hp:HealthcareProvider)-[:TREATS]->(p:Patient)-[:SUBMITTED]->(f:PatientFeedback)<-[:TRIGGERED_BY]-(a:Action)` | Визначення відповідального медперсоналу для екстреного реагування. |
| **CQ9** | Як змінюється середня тональність відгуків (`sentimentScore`) у розрізі діагнозів пацієнтів? | `(c:MedicalCondition)<-[:HAS_CONDITION]-(p:Patient)-[:SUBMITTED]->(f:PatientFeedback)` | Агрегована оцінка ефективності лікування для різних груп захворювань. |
| **CQ10** | Який найкоротший шлях зв'язку між конкретним медичним працівником та виявленим у пацієнта симптомом? | `shortestPath((hp:HealthcareProvider)-[*]-(s:Symptom))` | Аналіз ланцюжка взаємодії «лікар - пацієнт - відгук/діагноз - симптом». |

## 2. Властивості походження (Provenance) на зв'язках

Для всіх типів зв'язків у графі визначено три обов'язкові властивості походження:
- `source` (`String`) - джерело походження факту (`"patient_mobile_app"`, `"nlp_extraction_v1"`, `"iot_telemetry_stream"`, `"ehr_system"`, `"clinical_rule_engine"`, `"medical_kb_icd10"`).
- `confidence` (`Float`, `[0.0 .. 1.0]`) - рівень достовірності факту (`1.0` для верифікованих медичних записів та телеметрії; `0.75 - 0.98` для зв'язків, видобутих NLP-моделлю).
- `validFrom` (`DateTime`, ISO 8601) - часова мітка початку актуальності зв'язку.

| Тип зв'язку | Типові значення `source` | Типовий діапазон `confidence` | Семантика `validFrom` |
| :--- | :--- | :--- | :--- |
| `:SUBMITTED` | `"patient_mobile_app"` | `1.0` | Час публікації фідбеку пацієнтом. |
| `:MENTIONS_SYMPTOM` | `"nlp_extraction_v1"` | `0.75 - 0.98` | Час аналізу фідбеку та виявлення симптому. |
| `:ASSOCIATED_WITH_SYMPTOM` | `"medical_kb_icd10"` | `0.85 - 1.0` | Дата затвердження клінічного протоколу / бази знань. |
| `:HAS_CONDITION` | `"ehr_system"` | `1.0` | Дата встановлення діагнозу лікарем. |
| `:IS_MONITORED_BY` | `"ehr_system"`, `"iot_telemetry_stream"` | `1.0` | Час підключення та реєстрації приладу за пацієнтом. |
| `:MEASURES` | `"iot_telemetry_stream"` | `1.0` | Час фіксації вимірювання датчиком. |
| `:HAS_VITAL_SIGN` | `"iot_telemetry_stream"` | `1.0` | Час прив'язки виміряного показника до картки пацієнта. |
| `:TREATS` | `"ehr_system"` | `1.0` | Дата призначення лікаря / медсестри пацієнту. |
| `:TRIGGERED_BY` | `"clinical_rule_engine"` | `0.90 - 1.0` | Час автоматичного формування клінічної дії/тривоги. |

## 3. Порівняння LPG-схеми з OWL-онтологією (ЛР 7)

| Елемент OWL-онтології (`onto.owl`) | Реалізація у графовій схемі Neo4j (LPG) | Тип трансформації та обґрунтування |
| :--- | :--- | :--- |
| Клас `:Patient` | Мітка вузла `:Patient` | Пряме відображення класу в мітку вузла з додаванням унікального ключа `patientId` та демографічних атрибутів (`fullName`, `age`, `gender`, `ward`). |
| Клас `:PatientFeedback` та підкласи `:SymptomFeedback`, `:ServiceFeedback` | Мітка вузла `:PatientFeedback` + властивість `feedbackType` | Ієрархію підкласів згорнуто в єдину мітку з дискримінатором `feedbackType` (`"Symptom"` / `"Service"`) для спрощення індексації та запитів. |
| Клас `:Sentiment` (`:PositiveSentiment`, `:NegativeSentiment`, `:NeutralSentiment`) та властивість `:hasScore` | Властивості `sentimentLabel` та `sentimentScore` у вузлі `:PatientFeedback` | Клас перетворено на атрибути вузла відгуку, оскільки тональність є невід'ємною характеристикою конкретного фідбеку (усунення зайвих переходів ребрами). |
| Клас `:Symptom` (`:PainSymptom`, `:RespiratorySymptom`, `:CardiovascularSymptom`) та `:hasSeverity` | Мітка вузла `:Symptom` + властивості `category`, `severity` | Підкласи симптомів представлено через категоріальну властивість `category`, а анотацію `:hasSeverity` перенесено у властивість вузла `severity`. |
| Клас `:MedicalCondition` та підкласи `:AcuteCondition`, `:ChronicCondition` | Мітка вузла `:MedicalCondition` + властивість `conditionType` | Клас відображено у мітку вузла, а поділ на гострі та хронічні стани збережено у властивості `conditionType` (`"Acute"` / `"Chronic"`). |
| Клас `:VitalSign` (`:HeartRate`, `:OxygenSaturation`, `:BloodPressure`, `:BodyTemperature`) та `:hasValueNumeric` | Мітка вузла `:VitalSign` + властивості `vitalType`, `valueNumeric` | Усі підкласи фізіологічних показників об'єднано під міткою `:VitalSign` із типізацією через `vitalType` та числовим значенням `valueNumeric`. |
| Клас `:MedicalDevice` (`:PulseOximeter`, `:WearableSensor`) та `:hasDeviceID` | Мітка вузла `:MedicalDevice` + властивості `deviceId`, `deviceType` | Клас став міткою вузла, ідентифікатор `:hasDeviceID` став первинним ключем `deviceId`, а підкласи перенесено в атрибут `deviceType`. |
| Клас `:HealthcareProvider` та підкласи `:Doctor`, `:Nurse` | Мітка вузла `:HealthcareProvider` + властивість `role` | Персонал об'єднано в єдину мітку `:HealthcareProvider` із розмежуванням ролей через властивість `role` (`"Doctor"` / `"Nurse"`). |
| Клас `:Action` (`:AlertAction`, `:MedicationAdjustment`) | Мітка вузла `:Action` + властивість `actionType` | Клінічні дії представлено міткою `:Action`, а тип реакції (`"Alert"`, `"MedicationAdjustment"`) винесено у властивість `actionType`. |
| Об'єктні властивості `:submittedBy` / `:hasFeedback`, `:isMonitoredBy` / `:monitorsPatient` (інверсні пари в OWL) | Однонапрямлені типи зв'язків `:SUBMITTED`, `:IS_MONITORED_BY` | Інверсні властивості OWL замінено єдиними спрямованими ребрами, оскільки Neo4j забезпечує однакову швидкість обходу зв'язку в обох напрямках. |
| Об'єктні властивості `:mentionsSymptom`, `:associatedWithSymptom`, `:measuresVitalSign`, `:treatsPatient`, `:triggeredBy` | Типи зв'язків `:MENTIONS_SYMPTOM`, `:ASSOCIATED_WITH_SYMPTOM`, `:MEASURES`, `:TREATS`, `:TRIGGERED_BY` + атрибути `source`, `confidence`, `validFrom` | Об'єктні властивості перетворено на типізовані ребра LPG із додаванням метаданих походження безпосередньо на зв'язках (що неможливо в чистому RDF без реіфікації). |
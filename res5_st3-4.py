import json
import re
from pathlib import Path

base_dir = Path(r"D:\4_cry\ch_dan\lab9")
tests_dir = base_dir / "tests"
tests_dir.mkdir(parents=True, exist_ok=True)

SCHEMA_PROMPT = """
Role: READ-ONLY Cypher query generator for Neo4j.
Forbidden keywords: CREATE, MERGE, DELETE, DETACH, SET, REMOVE, DROP.
Always include a LIMIT clause (<= 50).

Allowed Node Labels:
- Patient (patientId, fullName, age, gender, pagerank, community)
- HealthcareProvider (providerId, name, specialty)
- MedicalDevice (deviceId, deviceType, status)
- MedicalCondition (conditionId, name, icdCode)
- Symptom (symptomId, name, severity)
- VitalSign (vitalId, vitalType, valueNumeric, unit, timestamp)
- PatientFeedback (feedbackId, feedbackText, sentimentLabel)
- Action (actionId, actionType, description)

Allowed Relationships:
- (Patient)-[:TREATS]-(HealthcareProvider) or (HealthcareProvider)-[:TREATS]->(Patient)
- (Patient)-[:IS_MONITORED_BY]->(MedicalDevice)
- (Patient)-[:HAS_CONDITION]->(MedicalCondition)
- (Patient)-[:REPORTS_SYMPTOM]->(Symptom)
- (Patient)-[:HAS_VITAL_SIGN]->(VitalSign)
- (Patient)-[:SUBMITTED]->(PatientFeedback)
- (HealthcareProvider)-[:PERFORMED]->(Action)
"""

ALLOWED_LABELS = {
    "Patient", "HealthcareProvider", "MedicalDevice", "MedicalCondition",
    "Symptom", "VitalSign", "PatientFeedback", "Action"
}
ALLOWED_RELS = {
    "TREATS", "IS_MONITORED_BY", "HAS_CONDITION", "REPORTS_SYMPTOM",
    "HAS_VITAL_SIGN", "SUBMITTED", "PERFORMED"
}
FORBIDDEN_OPS = {"CREATE", "MERGE", "DELETE", "DETACH", "SET", "REMOVE", "DROP"}

test_cases = [
    {
        "id": "T01",
        "question": "Вивести список пацієнтів та їхніх медичних пристроїв",
        "generated_cypher": "MATCH (p:Patient)-[:IS_MONITORED_BY]->(d:MedicalDevice) RETURN p.fullName, d.deviceId LIMIT 10;",
        "expected_valid": True
    },
    {
        "id": "T02",
        "question": "Знайти пацієнтів із пульсом понад 110 уд/хв",
        "generated_cypher": "MATCH (p:Patient)-[:HAS_VITAL_SIGN]->(v:VitalSign) WHERE v.vitalType = 'HeartRate' AND v.valueNumeric > 110 RETURN p.fullName, v.valueNumeric LIMIT 10;",
        "expected_valid": True
    },
    {
        "id": "T03",
        "question": "Показати пацієнтів лікаря doc_smith",
        "generated_cypher": "MATCH (hp:HealthcareProvider {providerId: 'doc_smith'})-[:TREATS]->(p:Patient) RETURN p.fullName LIMIT 15;",
        "expected_valid": True
    },
    {
        "id": "T04",
        "question": "Отримати пацієнтів із негативними відгуками",
        "generated_cypher": "MATCH (p:Patient)-[:SUBMITTED]->(f:PatientFeedback {sentimentLabel: 'Negative'}) RETURN p.fullName, f.feedbackText LIMIT 10;",
        "expected_valid": True
    },
    {
        "id": "T05",
        "question": "Знайти пацієнтів з діагнозом Артеріальна гіпертензія",
        "generated_cypher": "MATCH (p:Patient)-[:HAS_CONDITION]->(c:MedicalCondition {name: 'Артеріальна гіпертензія'}) RETURN p.fullName LIMIT 20;",
        "expected_valid": True
    },
    {
        "id": "T06",
        "question": "Вивести пацієнтів зі скаргою на задишку",
        "generated_cypher": "MATCH (p:Patient)-[:REPORTS_SYMPTOM]->(s:Symptom {name: 'Задишка'}) RETURN p.fullName LIMIT 10;",
        "expected_valid": True
    },
    {
        "id": "T07",
        "question": "Показати дії, виконані медичним персоналом",
        "generated_cypher": "MATCH (hp:HealthcareProvider)-[:PERFORMED]->(a:Action) RETURN hp.name, a.actionType LIMIT 10;",
        "expected_valid": True
    },
    {
        "id": "T08",
        "question": "Вивести топ-5 найвпливовіших вузлів за PageRank",
        "generated_cypher": "MATCH (n:Patient) RETURN n.fullName, n.pagerank ORDER BY n.pagerank DESC LIMIT 5;",
        "expected_valid": True
    },
    {
        "id": "T09",
        "question": "Знайти пацієнтів зі спільноти Louvain 104",
        "generated_cypher": "MATCH (p:Patient {community: 104}) RETURN p.fullName LIMIT 15;",
        "expected_valid": True
    },
    {
        "id": "T10",
        "question": "Яких пацієнтів лікує доктор Сміт?",
        "generated_cypher": "MATCH (d:Doctor {name: 'Д-р Сміт Джон'})-[:CURES]->(p:Patient) RETURN p.fullName LIMIT 10;",
        "expected_valid": False
    },
    {
        "id": "T11",
        "question": "Оновити вік пацієнта patient_01 на 50 років",
        "generated_cypher": "MATCH (p:Patient {patientId: 'patient_01'}) SET p.age = 50 RETURN p.fullName LIMIT 1;",
        "expected_valid": False
    },
    {
        "id": "T12",
        "question": "Вивести всі критичні життєві показники без обмеження",
        "generated_cypher": "MATCH (p:Patient)-[:HAS_VITAL_SIGN]->(v:VitalSign) WHERE v.valueNumeric > 130 RETURN p.fullName, v.valueNumeric;",
        "expected_valid": False
    }
]

def validate_cypher(query: str):
    errors = []
    upper_q = query.upper()
    for op in FORBIDDEN_OPS:
        if re.search(rf"\b{op}\b", upper_q):
            errors.append(f"Порушення read-only: заборонений оператор {op}")
    labels = re.findall(r"\([a-zA-Z0-9_]*:([a-zA-Z0-9_]+)", query)
    for lbl in labels:
        if lbl not in ALLOWED_LABELS:
            errors.append(f"Помилка схеми: невідома мітка вузла :{lbl}")
    rels = re.findall(r"\[:([a-zA-Z0-9_]+)", query)
    for rel in rels:
        if rel not in ALLOWED_RELS:
            errors.append(f"Помилка схеми: невідомий тип зв'язку :{rel}")
    if not re.search(r"\bLIMIT\s+\d+", upper_q):
        errors.append("Порушення політики безпеки: відсутній оператор LIMIT")
    return len(errors) == 0, errors

jsonl_path = tests_dir / "t2c.jsonl"
correct = 0
failed_cases = []

with open(jsonl_path, "w", encoding="utf-8") as f:
    for item in test_cases:
        is_valid, errs = validate_cypher(item["generated_cypher"])
        if is_valid:
            correct += 1
        else:
            failed_cases.append((item["id"], item["question"], item["generated_cypher"], errs))
        record = {
            "id": item["id"],
            "system_prompt_ref": "READ_ONLY_MEDICAL_KG_SCHEMA",
            "question": item["question"],
            "cypher": item["generated_cypher"],
            "is_valid": is_valid,
            "validation_errors": errs
        }
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

total = len(test_cases)
accuracy = (correct / total) * 100
print(f"Файл збережено: {jsonl_path}")
print(f"Усього тестових питань: {total}")
print(f"Коректних запитів: {correct}/{total} ({accuracy:.1f}%)")
print("\nАналіз 3 виявлених помилок:")
for cid, q, cyph, errs in failed_cases:
    print(f"- [{cid}] Питання: {q}")
    print(f"  Запит: {cyph}")
    print(f"  Причина відхилення: {'; '.join(errs)}")
LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/vich3er/lab9/main/lab9/data/patients.csv' AS row
MERGE (p:Patient {patientId: row.patientId})
SET p.fullName = row.fullName,
    p.age = toInteger(row.age),
    p.gender = row.gender,
    p.ward = row.ward;

LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/vich3er/lab9/main/lab9/data/providers.csv' AS row
MERGE (hp:HealthcareProvider {providerId: row.providerId})
SET hp.name = row.name,
    hp.role = row.role,
    hp.specialization = row.specialization;

LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/vich3er/lab9/main/lab9/data/devices.csv' AS row
MERGE (d:MedicalDevice {deviceId: row.deviceId})
SET d.deviceType = row.deviceType,
    d.status = row.status;

LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/vich3er/lab9/main/lab9/data/conditions.csv' AS row
MERGE (c:MedicalCondition {conditionId: row.conditionId})
SET c.name = row.name,
    c.conditionType = row.conditionType,
    c.icdCode = row.icdCode;

LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/vich3er/lab9/main/lab9/data/symptoms.csv' AS row
MERGE (s:Symptom {symptomId: row.symptomId})
SET s.name = row.name,
    s.category = row.category,
    s.severity = row.severity;

LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/vich3er/lab9/main/lab9/data/feedbacks.csv' AS row
MERGE (f:PatientFeedback {feedbackId: row.feedbackId})
SET f.feedbackText = row.feedbackText,
    f.feedbackType = row.feedbackType,
    f.sentimentLabel = row.sentimentLabel,
    f.sentimentScore = toFloat(row.sentimentScore),
    f.timestamp = datetime(row.timestamp);

LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/vich3er/lab9/main/lab9/data/vitals.csv' AS row
MERGE (v:VitalSign {vitalId: row.vitalId})
SET v.vitalType = row.vitalType,
    v.valueNumeric = toFloat(row.valueNumeric),
    v.unit = row.unit,
    v.measuredAt = datetime(row.measuredAt);

LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/vich3er/lab9/main/lab9/data/actions.csv' AS row
MERGE (a:Action {actionId: row.actionId})
SET a.actionType = row.actionType,
    a.description = row.description,
    a.createdAt = datetime(row.createdAt);

LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/vich3er/lab9/main/lab9/data/rel_submitted.csv' AS row
MATCH (p:Patient {patientId: row.patientId})
MATCH (f:PatientFeedback {feedbackId: row.feedbackId})
MERGE (p)-[r:SUBMITTED]->(f)
SET r.source = row.source,
    r.confidence = toFloat(row.confidence),
    r.validFrom = datetime(row.validFrom);

LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/vich3er/lab9/main/lab9/data/rel_mentions_symptom.csv' AS row
MATCH (f:PatientFeedback {feedbackId: row.feedbackId})
MATCH (s:Symptom {symptomId: row.symptomId})
MERGE (f)-[r:MENTIONS_SYMPTOM]->(s)
SET r.source = row.source,
    r.confidence = toFloat(row.confidence),
    r.validFrom = datetime(row.validFrom);

LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/vich3er/lab9/main/lab9/data/rel_associated_symptom.csv' AS row
MATCH (toNode:Symptom {symptomId: row.toId})
OPTIONAL MATCH (c:MedicalCondition {conditionId: row.fromId})
OPTIONAL MATCH (s:Symptom {symptomId: row.fromId})
WITH row, toNode, coalesce(c, s) AS fromNode
WHERE fromNode IS NOT NULL
MERGE (fromNode)-[r:ASSOCIATED_WITH_SYMPTOM]->(toNode)
SET r.source = row.source,
    r.confidence = toFloat(row.confidence),
    r.validFrom = datetime(row.validFrom);

LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/vich3er/lab9/main/lab9/data/rel_has_condition.csv' AS row
MATCH (p:Patient {patientId: row.patientId})
MATCH (c:MedicalCondition {conditionId: row.conditionId})
MERGE (p)-[r:HAS_CONDITION]->(c)
SET r.source = row.source,
    r.confidence = toFloat(row.confidence),
    r.validFrom = datetime(row.validFrom);

LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/vich3er/lab9/main/lab9/data/rel_monitored_by.csv' AS row
MATCH (p:Patient {patientId: row.patientId})
MATCH (d:MedicalDevice {deviceId: row.deviceId})
MERGE (p)-[r:IS_MONITORED_BY]->(d)
SET r.source = row.source,
    r.confidence = toFloat(row.confidence),
    r.validFrom = datetime(row.validFrom);

LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/vich3er/lab9/main/lab9/data/rel_measures.csv' AS row
MATCH (d:MedicalDevice {deviceId: row.deviceId})
MATCH (v:VitalSign {vitalId: row.vitalId})
MERGE (d)-[r:MEASURES]->(v)
SET r.source = row.source,
    r.confidence = toFloat(row.confidence),
    r.validFrom = datetime(row.validFrom);

LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/vich3er/lab9/main/lab9/data/rel_has_vital.csv' AS row
MATCH (p:Patient {patientId: row.patientId})
MATCH (v:VitalSign {vitalId: row.vitalId})
MERGE (p)-[r:HAS_VITAL_SIGN]->(v)
SET r.source = row.source,
    r.confidence = toFloat(row.confidence),
    r.validFrom = datetime(row.validFrom);

LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/vich3er/lab9/main/lab9/data/rel_treats.csv' AS row
MATCH (hp:HealthcareProvider {providerId: row.providerId})
MATCH (p:Patient {patientId: row.patientId})
MERGE (hp)-[r:TREATS]->(p)
SET r.source = row.source,
    r.confidence = toFloat(row.confidence),
    r.validFrom = datetime(row.validFrom);

LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/vich3er/lab9/main/lab9/data/rel_triggered_by.csv' AS row
MATCH (a:Action {actionId: row.actionId})
MATCH (f:PatientFeedback {feedbackId: row.feedbackId})
MERGE (a)-[r:TRIGGERED_BY]->(f)
SET r.source = row.source,
    r.confidence = toFloat(row.confidence),
    r.validFrom = datetime(row.validFrom);
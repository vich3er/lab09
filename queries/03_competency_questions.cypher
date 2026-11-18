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

MATCH (p:Patient)-[:HAS_CONDITION]->(c:MedicalCondition)-[:ASSOCIATED_WITH_SYMPTOM]->(s:Symptom)
WHERE NOT (p)-[:SUBMITTED]->(:PatientFeedback)-[:MENTIONS_SYMPTOM]->(s)
RETURN p.patientId AS patientId,
       p.fullName AS patient,
       c.name AS condition,
       collect(DISTINCT s.name) AS potentialUnreportedSymptoms
ORDER BY p.patientId ASC
LIMIT 10;

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

MATCH (hp:HealthcareProvider)-[:TREATS]->(p:Patient)-[:SUBMITTED]->(f:PatientFeedback)<-[tb:TRIGGERED_BY]-(a:Action)
RETURN a.actionId AS actionId,
       a.actionType AS actionType,
       a.description AS description,
       p.fullName AS patient,
       hp.name AS assignedProvider,
       f.sentimentLabel AS sentiment,
       tb.confidence AS triggerConfidence
ORDER BY tb.confidence DESC;

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

MATCH path = shortestPath(
  (hp:HealthcareProvider {providerId: 'doc_smith'})-[*..5]-(a:Action {actionId: 'action_alert_01'})
)
RETURN [n IN nodes(path) | labels(n)[0] + ': ' + coalesce(n.name, n.fullName, n.feedbackId, n.actionId)] AS pathNodes,
       [r IN relationships(path) | type(r)] AS relationshipChain,
       length(path) AS hops;

MATCH path = (c:MedicalCondition)<-[:HAS_CONDITION]-(p:Patient)-[:SUBMITTED]->(f:PatientFeedback)<-[:TRIGGERED_BY]-(a:Action)
RETURN c.name AS rootCondition,
       length(path) AS impactDepth,
       count(DISTINCT p) AS affectedPatients,
       count(DISTINCT f) AS triggeredFeedbacks,
       collect(DISTINCT a.actionType) AS downstreamActions,
       count(DISTINCT a) AS totalActionsCount
ORDER BY totalActionsCount DESC, affectedPatients DESC;

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

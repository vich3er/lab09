MATCH (p:Patient {patientId: 'patient_03'})
OPTIONAL MATCH (hp:HealthcareProvider)-[r1:TREATS]->(p)
OPTIONAL MATCH (p)-[r2:HAS_CONDITION]->(c:MedicalCondition)
OPTIONAL MATCH (p)-[r3:SUBMITTED]->(f:PatientFeedback)-[r4:MENTIONS_SYMPTOM]->(s:Symptom)
OPTIONAL MATCH (a:Action)-[r5:TRIGGERED_BY]->(f)
OPTIONAL MATCH (p)-[r6:IS_MONITORED_BY]->(d:MedicalDevice)-[r7:MEASURES]->(v:VitalSign)
RETURN p, hp, r1, c, r2, f, r3, s, r4, a, r5, d, r6, v, r7;

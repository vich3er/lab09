import csv
import os
import random
from datetime import datetime, timedelta

random.seed(42)
OUTPUT_DIR = r"D:\4_cry\ch_dan\lab9\data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def write_csv(filename, headers, rows):
    with open(os.path.join(OUTPUT_DIR, filename), mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

patients = [
    ["patient_01", "Коваленко Олександр Петрович", 64, "Male", "Cardiology-1"],
    ["patient_02", "Мельник Ірина Василівна", 52, "Female", "Therapy-2"],
    ["patient_03", "Бондаренко Тарас Ігорович", 58, "Male", "Cardiology-1"],
]
first_names_m = ["Андрій", "Максим", "Дмитро", "Сергій", "Олег", "Юрій", "Віктор", "Ігор", "Роман", "Богдан", "Василь"]
first_names_f = ["Олена", "Наталія", "Тетяна", "Марія", "Світлана", "Оксана", "Ганна", "Юлія", "Людмила", "Катерина", "Вікторія"]
last_names = ["Шевченко", "Ткаченко", "Кравченко", "Олійник", "Шевчук", "Поліщук", "Бойко", "Лисенко", "Мороз", "Савченко", "Руденко"]
wards = ["Cardiology-1", "Cardiology-2", "Pulmonology-1", "Therapy-1", "Therapy-2"]

for i in range(4, 26):
    pid = f"patient_{i:02d}"
    gender = "Male" if i % 2 == 0 else "Female"
    fname = random.choice(first_names_m if gender == "Male" else first_names_f)
    lname = random.choice(last_names)
    patronymic = "Олександрович" if gender == "Male" else "Олександрівна"
    patients.append([pid, f"{lname} {fname} {patronymic}", random.randint(25, 82), gender, random.choice(wards)])

write_csv("patients.csv", ["patientId", "fullName", "age", "gender", "ward"], patients)

providers = [
    ["doc_smith", "Д-р Сміт Джон", "Doctor", "Cardiology"],
    ["nurse_joy", "Медсестра Джой Анна", "Nurse", "General Care"],
    ["doc_koval", "Д-р Коваль Марія", "Doctor", "Pulmonology"],
    ["doc_moroz", "Д-р Мороз Віталій", "Doctor", "Internal Medicine"],
    ["nurse_savchuk", "Медсестра Савчук Олена", "Nurse", "Cardiology"],
    ["nurse_boiko", "Медсестра Бойко Надія", "Nurse", "Intensive Care"],
]
write_csv("providers.csv", ["providerId", "name", "role", "specialization"], providers)

devices = [
    ["POX-9921", "PulseOximeter", "Active"],
    ["WSR-1044", "WearableSensor", "Active"],
]
for i in range(3, 16):
    dtype = "PulseOximeter" if i % 2 == 1 else "WearableSensor"
    prefix = "POX" if dtype == "PulseOximeter" else "WSR"
    status = "Active" if i <= 13 else "Inactive"
    devices.append([f"{prefix}-{1000 + i * 37}", dtype, status])

write_csv("devices.csv", ["deviceId", "deviceType", "status"], devices)

conditions = [
    ["cond_heart_failure", "Хронічна серцева недостатність", "Chronic", "I50.9"],
    ["cond_hypertension", "Артеріальна гіпертензія", "Chronic", "I10"],
    ["cond_pneumonia", "Гостра пневмонія", "Acute", "J18.9"],
    ["cond_asthma", "Бронхіальна астма", "Chronic", "J45.9"],
    ["cond_angina", "Нестабільна стенокардія", "Acute", "I20.0"],
    ["cond_bronchitis", "Гострий бронхіт", "Acute", "J20.9"],
    ["cond_arrhythmia", "Фібриляція передсердь", "Chronic", "I48.9"],
    ["cond_covid19", "Гостра респіраторна інфекція COVID-19", "Acute", "U07.1"],
]
write_csv("conditions.csv", ["conditionId", "name", "conditionType", "icdCode"], conditions)

symptoms = [
    ["symptom_dyspnea", "Задишка", "Respiratory", "Severe"],
    ["symptom_chest_pain", "Біль у грудях", "Pain", "Critical"],
    ["symptom_fever", "Підвищена температура", "General", "Moderate"],
    ["symptom_cough", "Сухий кашель", "Respiratory", "Moderate"],
    ["symptom_tachycardia", "Прискорене серцебиття", "Cardiovascular", "Severe"],
    ["symptom_fatigue", "Загальна слабкість", "General", "Mild"],
    ["symptom_dizziness", "Запаморочення", "Neurological", "Moderate"],
    ["symptom_edema", "Набряки нижніх кінцівок", "Cardiovascular", "Moderate"],
    ["symptom_hypoxia", "Зниження сатурації", "Respiratory", "Critical"],
    ["symptom_headache", "Головний біль", "Pain", "Mild"],
    ["symptom_wheezing", "Хрипи при диханні", "Respiratory", "Severe"],
    ["symptom_palpitations", "Перебої в роботі серця", "Cardiovascular", "Severe"],
]
write_csv("symptoms.csv", ["symptomId", "name", "category", "severity"], symptoms)

feedback_templates = [
    ("Відчуваю сильну задишку навіть у спокої", "Symptom", "Negative", -0.82, "symptom_dyspnea"),
    ("З'явився різкий біль за грудиною вранці", "Symptom", "Negative", -0.92, "symptom_chest_pain"),
    ("Температура піднялась до 38.5, морозить", "Symptom", "Negative", -0.68, "symptom_fever"),
    ("Сильне серцебиття після прийому ліків", "Symptom", "Negative", -0.74, "symptom_tachycardia"),
    ("Постійний сухий кашель заважає спати", "Symptom", "Negative", -0.61, "symptom_cough"),
    ("Відчуваю запаморочення при вставанні", "Symptom", "Negative", -0.55, "symptom_dizziness"),
    ("Помітив набряки на ногах ввечері", "Symptom", "Negative", -0.58, "symptom_edema"),
    ("Важко дихати, чути хрипи в грудях", "Symptom", "Negative", -0.85, "symptom_wheezing"),
    ("Стан покращився, дихати стало значно легше", "Symptom", "Positive", 0.78, "symptom_dyspnea"),
    ("Дуже вдячний лікарям за швидку допомогу", "Service", "Positive", 0.91, None),
    ("У палаті чисто, персонал уважний", "Service", "Positive", 0.84, None),
    ("Довго чекав на огляд чергового лікаря", "Service", "Negative", -0.45, None),
    ("Нормальне самопочуття, скарг немає", "Service", "Neutral", 0.12, None),
]

base_time = datetime(2026, 10, 20, 8, 0, 0)
feedbacks = [
    ["fb_01", "Задишка посилилась під час ходьби", "Symptom", "Negative", -0.75, "2026-10-20T10:00:00Z"],
    ["fb_02", "Чудовий догляд медсестри у палаті", "Service", "Positive", 0.85, "2026-10-21T11:30:00Z"],
    ["fb_03", "Гострий біль у грудях та нестача повітря", "Symptom", "Negative", -0.90, "2026-10-22T08:15:00Z"],
]
rel_submitted = [
    ["patient_01", "fb_01", "patient_mobile_app", 1.0, "2026-10-20T10:00:00Z"],
    ["patient_02", "fb_02", "patient_mobile_app", 1.0, "2026-10-21T11:30:00Z"],
    ["patient_03", "fb_03", "patient_mobile_app", 1.0, "2026-10-22T08:15:00Z"],
]
rel_mentions = [
    ["fb_01", "symptom_dyspnea", "nlp_extraction_v1", 0.94, "2026-10-20T10:00:05Z"],
    ["fb_03", "symptom_chest_pain", "nlp_extraction_v1", 0.96, "2026-10-22T08:15:04Z"],
    ["fb_03", "symptom_dyspnea", "nlp_extraction_v1", 0.88, "2026-10-22T08:15:04Z"],
]

for i in range(4, 31):
    fid = f"fb_{i:02d}"
    pid = patients[(i - 1) % len(patients)][0]
    text, ftype, slabel, sscore, sym_id = random.choice(feedback_templates)
    ts = (base_time + timedelta(hours=i * 3)).strftime("%Y-%m-%dT%H:%M:%SZ")
    feedbacks.append([fid, text, ftype, slabel, sscore, ts])
    rel_submitted.append([pid, fid, "patient_mobile_app", 1.0, ts])
    if sym_id:
        conf = round(random.uniform(0.78, 0.98), 2)
        rel_mentions.append([fid, sym_id, "nlp_extraction_v1", conf, ts])
        if random.random() < 0.25:
            extra_sym = random.choice(symptoms)[0]
            if extra_sym != sym_id:
                rel_mentions.append([fid, extra_sym, "nlp_extraction_v1", round(random.uniform(0.75, 0.90), 2), ts])

write_csv("feedbacks.csv", ["feedbackId", "feedbackText", "feedbackType", "sentimentLabel", "sentimentScore", "timestamp"], feedbacks)
write_csv("rel_submitted.csv", ["patientId", "feedbackId", "source", "confidence", "validFrom"], rel_submitted)
write_csv("rel_mentions_symptom.csv", ["feedbackId", "symptomId", "source", "confidence", "validFrom"], rel_mentions)

vitals = [
    ["vital_spo2_01", "OxygenSaturation", 88.5, "%", "2026-10-20T09:55:00Z"],
    ["vital_hr_01", "HeartRate", 125.0, "bpm", "2026-10-22T08:10:00Z"],
]
rel_monitored = [
    ["patient_01", "POX-9921", "ehr_system", 1.0, "2026-10-19T09:00:00Z"],
    ["patient_03", "WSR-1044", "ehr_system", 1.0, "2026-10-19T09:30:00Z"],
]
rel_measures = [
    ["POX-9921", "vital_spo2_01", "iot_telemetry_stream", 1.0, "2026-10-20T09:55:00Z"],
    ["WSR-1044", "vital_hr_01", "iot_telemetry_stream", 1.0, "2026-10-22T08:10:00Z"],
]
rel_has_vital = [
    ["patient_01", "vital_spo2_01", "iot_telemetry_stream", 1.0, "2026-10-20T09:55:00Z"],
    ["patient_03", "vital_hr_01", "iot_telemetry_stream", 1.0, "2026-10-22T08:10:00Z"],
]

for idx, p in enumerate(patients[3:], start=3):
    pid = p[0]
    dev = devices[idx % len(devices)]
    did = dev[0]
    vid = f"vital_{idx:02d}"
    ts = (base_time + timedelta(hours=idx * 2)).strftime("%Y-%m-%dT%H:%M:%SZ")
    rel_monitored.append([pid, did, "ehr_system", 1.0, "2026-10-19T10:00:00Z"])
    if dev[1] == "PulseOximeter":
        val = round(random.uniform(86.0, 99.0), 1)
        vitals.append([vid, "OxygenSaturation", val, "%", ts])
    else:
        val = round(random.uniform(62.0, 138.0), 1)
        vitals.append([vid, "HeartRate", val, "bpm", ts])
    rel_measures.append([did, vid, "iot_telemetry_stream", 1.0, ts])
    rel_has_vital.append([pid, vid, "iot_telemetry_stream", 1.0, ts])

write_csv("vitals.csv", ["vitalId", "vitalType", "valueNumeric", "unit", "measuredAt"], vitals)
write_csv("rel_monitored_by.csv", ["patientId", "deviceId", "source", "confidence", "validFrom"], rel_monitored)
write_csv("rel_measures.csv", ["deviceId", "vitalId", "source", "confidence", "validFrom"], rel_measures)
write_csv("rel_has_vital.csv", ["patientId", "vitalId", "source", "confidence", "validFrom"], rel_has_vital)

actions = [
    ["action_alert_01", "Alert", "Критичний тривожний сигнал черговому кардіологу", "2026-10-22T08:15:10Z"],
    ["action_med_adj_01", "MedicationAdjustment", "Коригування дози діуретиків та киснева підтримка", "2026-10-20T10:05:00Z"],
]
rel_triggered = [
    ["action_alert_01", "fb_03", "clinical_rule_engine", 0.99, "2026-10-22T08:15:10Z"],
    ["action_med_adj_01", "fb_01", "clinical_rule_engine", 0.95, "2026-10-20T10:05:00Z"],
]

neg_feedbacks = [fb for fb in feedbacks[3:] if fb[3] == "Negative"]
for i, fb in enumerate(neg_feedbacks[:10], start=3):
    aid = f"action_{i:02d}"
    atype = "Alert" if fb[4] <= -0.75 else "MedicationAdjustment"
    desc = "Екстрене сповіщення лікаря через критичний стан" if atype == "Alert" else "Перегляд схеми медикаментозної терапії"
    ts = fb[5]
    actions.append([aid, atype, desc, ts])
    rel_triggered.append([aid, fb[0], "clinical_rule_engine", round(random.uniform(0.90, 1.0), 2), ts])

write_csv("actions.csv", ["actionId", "actionType", "description", "createdAt"], actions)
write_csv("rel_triggered_by.csv", ["actionId", "feedbackId", "source", "confidence", "validFrom"], rel_triggered)

rel_has_condition = [
    ["patient_01", "cond_heart_failure", "ehr_system", 1.0, "2026-09-01T10:00:00Z"],
    ["patient_02", "cond_bronchitis", "ehr_system", 1.0, "2026-10-18T12:00:00Z"],
    ["patient_03", "cond_angina", "ehr_system", 1.0, "2026-10-21T09:00:00Z"],
]
for p in patients[3:]:
    c1 = random.choice(conditions)[0]
    rel_has_condition.append([p[0], c1, "ehr_system", 1.0, "2026-10-01T09:00:00Z"])
    if random.random() < 0.3:
        c2 = random.choice(conditions)[0]
        if c2 != c1:
            rel_has_condition.append([p[0], c2, "ehr_system", 1.0, "2026-10-05T09:00:00Z"])

write_csv("rel_has_condition.csv", ["patientId", "conditionId", "source", "confidence", "validFrom"], rel_has_condition)

rel_assoc_symptom = [
    ["cond_heart_failure", "symptom_dyspnea", "medical_kb_icd10", 1.0, "2026-01-01T00:00:00Z"],
    ["cond_heart_failure", "symptom_edema", "medical_kb_icd10", 0.95, "2026-01-01T00:00:00Z"],
    ["cond_heart_failure", "symptom_fatigue", "medical_kb_icd10", 0.90, "2026-01-01T00:00:00Z"],
    ["cond_hypertension", "symptom_headache", "medical_kb_icd10", 0.92, "2026-01-01T00:00:00Z"],
    ["cond_hypertension", "symptom_dizziness", "medical_kb_icd10", 0.88, "2026-01-01T00:00:00Z"],
    ["cond_pneumonia", "symptom_fever", "medical_kb_icd10", 0.98, "2026-01-01T00:00:00Z"],
    ["cond_pneumonia", "symptom_cough", "medical_kb_icd10", 0.96, "2026-01-01T00:00:00Z"],
    ["cond_pneumonia", "symptom_dyspnea", "medical_kb_icd10", 0.91, "2026-01-01T00:00:00Z"],
    ["cond_asthma", "symptom_wheezing", "medical_kb_icd10", 0.99, "2026-01-01T00:00:00Z"],
    ["cond_asthma", "symptom_dyspnea", "medical_kb_icd10", 0.95, "2026-01-01T00:00:00Z"],
    ["cond_angina", "symptom_chest_pain", "medical_kb_icd10", 0.99, "2026-01-01T00:00:00Z"],
    ["cond_angina", "symptom_tachycardia", "medical_kb_icd10", 0.87, "2026-01-01T00:00:00Z"],
    ["cond_bronchitis", "symptom_cough", "medical_kb_icd10", 0.97, "2026-01-01T00:00:00Z"],
    ["cond_bronchitis", "symptom_fever", "medical_kb_icd10", 0.85, "2026-01-01T00:00:00Z"],
    ["cond_arrhythmia", "symptom_palpitations", "medical_kb_icd10", 0.98, "2026-01-01T00:00:00Z"],
    ["cond_arrhythmia", "symptom_tachycardia", "medical_kb_icd10", 0.94, "2026-01-01T00:00:00Z"],
    ["cond_covid19", "symptom_fever", "medical_kb_icd10", 0.95, "2026-01-01T00:00:00Z"],
    ["cond_covid19", "symptom_hypoxia", "medical_kb_icd10", 0.90, "2026-01-01T00:00:00Z"],
    ["symptom_dyspnea", "symptom_hypoxia", "medical_kb_icd10", 0.92, "2026-01-01T00:00:00Z"],
    ["symptom_hypoxia", "symptom_tachycardia", "medical_kb_icd10", 0.89, "2026-01-01T00:00:00Z"],
    ["symptom_chest_pain", "symptom_dyspnea", "medical_kb_icd10", 0.86, "2026-01-01T00:00:00Z"],
    ["symptom_tachycardia", "symptom_dizziness", "medical_kb_icd10", 0.84, "2026-01-01T00:00:00Z"],
]
write_csv("rel_associated_symptom.csv", ["fromId", "toId", "source", "confidence", "validFrom"], rel_assoc_symptom)

rel_treats = [
    ["doc_smith", "patient_01", "ehr_system", 1.0, "2026-10-19T08:00:00Z"],
    ["nurse_joy", "patient_02", "ehr_system", 1.0, "2026-10-19T08:00:00Z"],
    ["doc_smith", "patient_03", "ehr_system", 1.0, "2026-10-19T08:00:00Z"],
]
doctors = ["doc_smith", "doc_koval", "doc_moroz"]
nurses = ["nurse_joy", "nurse_savchuk", "nurse_boiko"]
for idx, p in enumerate(patients[3:], start=3):
    rel_treats.append([doctors[idx % len(doctors)], p[0], "ehr_system", 1.0, "2026-10-19T08:30:00Z"])
    if idx % 2 == 0:
        rel_treats.append([nurses[idx % len(nurses)], p[0], "ehr_system", 1.0, "2026-10-19T08:30:00Z"])

write_csv("rel_treats.csv", ["providerId", "patientId", "source", "confidence", "validFrom"], rel_treats)
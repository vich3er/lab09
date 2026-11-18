import time
from rdflib import Graph

g = Graph()
g.parse(r"D:\4_cry\ch_dan\lab8\data\kb.ttl", format="turtle")

prefix = """
PREFIX : <http://www.semanticweb.org/patient_monitoring#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
"""

queries = {
    "Q1 (Пацієнти та пристрої)": prefix + """
        SELECT ?patient ?device WHERE {
            ?patient rdf:type :Patient ;
                     :isMonitoredBy ?device .
        } LIMIT 10
    """,
    "Q2 (Критичні показники > 130)": prefix + """
        SELECT ?patient ?vital ?val WHERE {
            ?patient rdf:type :Patient ;
                     :hasVitalSign ?vital .
            ?vital :hasValueNumeric ?val .
            FILTER(?val > 130)
        } ORDER BY DESC(?val) LIMIT 10
    """,
    "Q3 (Кількість пацієнтів)": prefix + """
        SELECT (COUNT(DISTINCT ?patient) AS ?totalPatients) WHERE {
            ?patient rdf:type :Patient .
        }
    """,
    "Q4 (Пристрої та їхні ідентифікатори)": prefix + """
        SELECT ?device ?devId WHERE {
            ?device rdf:type :MedicalDevice ;
                    :hasDeviceID ?devId .
        } LIMIT 10
    """,
    "Q5 (Пацієнт + пристрій + показник)": prefix + """
        SELECT ?patient ?device ?val WHERE {
            ?patient rdf:type :Patient ;
                     :isMonitoredBy ?device ;
                     :hasVitalSign ?vital .
            ?vital :hasValueNumeric ?val .
        } LIMIT 10
    """
}

for name, q in queries.items():
    t0 = time.perf_counter()
    res = list(g.query(q))
    dt = (time.perf_counter() - t0) * 1000
    print(f"=== {name} | рядків: {len(res)} | час: {dt:.2f} ms ===")
    for row in res[:5]:
        print("  ", [str(x).split("#")[-1] for x in row])


fhir_to_omop_systems = {
    "http://snomed.info/sct": "SNOMED",
    "http://www.nlm.nih.gov/research/umls/rxnorm": "RxNorm",
    "http://www.ama-assn.org/go/cpt": "CPT4",
    "http://hl7.org/fhir/sid/ndc": "NDC",
    "http://hl7.org/fhir/sid/icd-10": "ICD10",
    "http://hl7.org/fhir/sid/icd-10-cm": "ICD10CM",
    "http://hl7.org/fhir/sid/icd-10-pcs": "ICD10PCS",
    "http://loinc.org": "LOINC"
}

def lookup_system(fhir_uri: str) -> str | None:
    '''
    Provide a FHIR URI to return an OMOP Vocabulary ID as a string. If system not found, returns None.
    '''
    if fhir_uri not in fhir_to_omop_systems:
        return None
    else:
        return fhir_to_omop_systems[fhir_uri]
    
def reverse_lookup_system(omop_vocabulary_id: str):
    '''
    Provide an OMOP Vocabularly ID to reverse look up the associated FHIR URI. If not found, returns None.
    '''
    for k, v in fhir_to_omop_systems.items():
        if omop_vocabulary_id == v:
            return k
    return omop_vocabulary_id
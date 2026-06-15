# Provider Entity Field Specifications

This directory contains field specification templates for static provider resources.

## Files Created

### Practitioners (3)
1. **practitioner_primary_care.json5** - Dr. Jane Smith, General Practitioner
   - NPI: 1847362915 (Type 1, verified non-existent in NPPES as of 2026-06-10)
2. **practitioner_lab_tech.json5** - James Martinez, MT(ASCP), Lab Technician
   - NPI: 1691847523 (Type 1, verified non-existent in NPPES as of 2026-06-10)
3. **practitioner_radiologist.json5** - Dr. Alex Johnson, Radiologist
   - NPI: 1539174682 (Type 1, verified non-existent in NPPES as of 2026-06-10)

### Organizations (4)
1. **organization_clinic.json5** - Metro Health Clinic
   - Identifier: ORG-METRO-001
   - Type: Healthcare Provider
2. **organization_lab.json5** - City Medical Laboratory
   - Identifier: ORG-CITYLAB-001
   - Type: Hospital Department
3. **organization_imaging.json5** - Regional Imaging Center
   - Identifier: ORG-IMAGING-001
   - Type: Hospital Department
4. **organization_pharmacy.json5** - PharmaCare Network
   - Identifier: ORG-PHARMACY-001
   - Type: Pharmacy

### PractitionerRoles (3)
1. **practitioner_role_gp.json5** - GP at Metro Health
   - Identifier: ROLE-GP-001
   - Links: Practitioner 1847362915 + Organization ORG-METRO-001
2. **practitioner_role_lab.json5** - Lab Tech at City Lab
   - Identifier: ROLE-LAB-001
   - Links: Practitioner 1691847523 + Organization ORG-CITYLAB-001
3. **practitioner_role_radiologist.json5** - Radiologist at Imaging Center
   - Identifier: ROLE-RAD-001
   - Links: Practitioner 1539174682 + Organization ORG-IMAGING-001

## Next Steps

1. **Review** each file and modify field values as needed
2. **Verify** all data is fictional and safe to use
3. **Request** full FHIR Sheets entity generation when ready
4. **Test** entities can be properly loaded and referenced

## Safety Notes

All data uses:
- ✅ Generic common names (Smith, Johnson, Martinez)
- ✅ 555 phone numbers (reserved for fiction)
- ✅ Generic addresses (Anytown, Main Street)
- ✅ Example.org email domains
- ✅ Sequential fake NPIs (not real provider numbers)
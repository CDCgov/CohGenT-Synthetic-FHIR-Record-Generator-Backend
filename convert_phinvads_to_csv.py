# convert_phinvads_to_csv.py
# Unified script to convert PHINVADS JSON files to CSVs with automatic occupation→industry mapping

import json
import csv

# Correct system URLs from PHINVADS codeSystemOID
INDUSTRY_SYSTEM = "urn:oid:2.16.840.1.114222.4.5.336"
OCCUPATION_SYSTEM = "urn:oid:2.16.840.1.114222.4.5.339"

def convert_industry_json_to_csv():
    """Convert PHINVADS_industry.json to industries.csv"""
    
    with open('data/PHINVADS_industry.json', 'r') as f:
        data = json.load(f)
    
    concepts = data['versionList'][0]['conceptList']
    
    # Create industries dict for later mapping
    industries = {}
    rows = []
    
    for concept in concepts:
        code = concept['conceptCode']
        display = concept['cdcpreferredDesignation']
        industries[code] = display
        rows.append({
            'code': code,
            'system': INDUSTRY_SYSTEM,
            'display': display
        })
    
    with open('data/industries.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['code', 'system', 'display'])
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"✓ Converted {len(concepts)} industries to data/industries.csv")
    return industries

def find_industry_by_keyword(industries):
    """
    Create keyword → industry_code mapping based on actual industry names.
    Returns dict of pattern → industry_code
    """
    mapping = {}
    
    for code, display in industries.items():
        display_lower = display.lower()
        
        # Extract key words from industry name for matching
        if 'health' in display_lower or 'hospital' in display_lower or 'medical' in display_lower:
            mapping['healthcare'] = code
        elif 'education' in display_lower or 'school' in display_lower:
            mapping['education'] = code
        elif 'construction' in display_lower:
            mapping['construction'] = code
        elif 'retail' in display_lower:
            mapping['retail'] = code
        elif 'food' in display_lower or 'accommodation' in display_lower:
            mapping['food_service'] = code
        elif 'manufacturing' in display_lower:
            mapping['manufacturing'] = code
        elif 'transportation' in display_lower or 'warehousing' in display_lower:
            mapping['transportation'] = code
        elif 'agriculture' in display_lower or 'forestry' in display_lower or 'fishing' in display_lower:
            mapping['agriculture'] = code
        elif 'public administration' in display_lower or 'government' in display_lower:
            mapping['public_admin'] = code
        elif 'professional' in display_lower or 'scientific' in display_lower or 'technical' in display_lower:
            mapping['professional'] = code
        elif 'finance' in display_lower or 'insurance' in display_lower:
            mapping['finance'] = code
        elif 'arts' in display_lower or 'entertainment' in display_lower or 'recreation' in display_lower:
            mapping['arts'] = code
        elif 'real estate' in display_lower:
            mapping['real_estate'] = code
        elif 'information' in display_lower:
            mapping['information'] = code
        elif 'utilities' in display_lower:
            mapping['utilities'] = code
        elif 'mining' in display_lower:
            mapping['mining'] = code
        elif 'wholesale' in display_lower:
            mapping['wholesale'] = code
        elif 'management' in display_lower:
            mapping['management'] = code
    
    return mapping

def guess_industry_for_occupation(occupation_name, industry_map):
    """
    Match occupation name to industry using comprehensive keyword patterns.
    Returns industry_code or None.
    """
    occ_lower = occupation_name.lower()
    
    # Healthcare (most specific patterns first)
    healthcare_keywords = [
        'nurse', 'physician', 'doctor', 'surgeon', 'dentist', 'dental', 
        'therapist', 'pharmacist', 'medical', 'health', 'clinical', 
        'veterinarian', 'optometrist', 'chiropractor', 'psychologist',
        'dietitian', 'paramedic', 'emt', 'radiologic', 'sonographer'
    ]
    if any(kw in occ_lower for kw in healthcare_keywords):
        return industry_map.get('healthcare')
    
    # Education
    education_keywords = [
        'teacher', 'professor', 'instructor', 'educator', 'librarian',
        'tutor', 'counselor', 'principal', 'dean'
    ]
    if any(kw in occ_lower for kw in education_keywords):
        return industry_map.get('education')
    
    # Public Safety / Government
    public_admin_keywords = [
        'police', 'firefighter', 'detective', 'officer', 'inspector',
        'sheriff', 'correctional', 'security guard', 'legislator',
        'judge', 'magistrate'
    ]
    if any(kw in occ_lower for kw in public_admin_keywords):
        return industry_map.get('public_admin')
    
    # Construction
    construction_keywords = [
        'carpenter', 'electrician', 'plumber', 'mason', 'roofer',
        'construction', 'installer', 'hvac', 'painter', 'drywall',
        'glazier', 'boilermaker', 'ironworker', 'laborer'
    ]
    if any(kw in occ_lower for kw in construction_keywords):
        return industry_map.get('construction')
    
    # Food Service
    food_keywords = [
        'cook', 'chef', 'waiter', 'waitress', 'bartender', 'food service',
        'dishwasher', 'host', 'hostess', 'barista'
    ]
    if any(kw in occ_lower for kw in food_keywords):
        return industry_map.get('food_service')
    
    # Retail
    retail_keywords = [
        'cashier', 'retail', 'sales clerk', 'stocker', 'merchandiser'
    ]
    if any(kw in occ_lower for kw in retail_keywords):
        return industry_map.get('retail')
    
    # Sales (could be retail or wholesale)
    if 'sales' in occ_lower and 'representative' in occ_lower:
        return industry_map.get('wholesale') or industry_map.get('professional')
    elif 'sales' in occ_lower:
        return industry_map.get('retail')
    
    # Transportation
    transportation_keywords = [
        'driver', 'pilot', 'flight attendant', 'transportation', 'locomotive',
        'bus driver', 'taxi', 'truck', 'dispatcher', 'cargo'
    ]
    if any(kw in occ_lower for kw in transportation_keywords):
        return industry_map.get('transportation')
    
    # Manufacturing
    manufacturing_keywords = [
        'assembler', 'machinist', 'welder', 'machine operator', 'fabricator',
        'production', 'packer', 'quality control', 'manufacturing'
    ]
    if any(kw in occ_lower for kw in manufacturing_keywords):
        return industry_map.get('manufacturing')
    
    # Agriculture
    agriculture_keywords = [
        'farm', 'agricultural', 'grader', 'sorter', 'logger', 'forester',
        'fisher', 'rancher'
    ]
    if any(kw in occ_lower for kw in agriculture_keywords):
        return industry_map.get('agriculture')
    
    # Finance
    finance_keywords = [
        'accountant', 'auditor', 'financial', 'actuary', 'analyst',
        'bank teller', 'loan officer', 'insurance', 'underwriter', 'claims'
    ]
    if any(kw in occ_lower for kw in finance_keywords):
        return industry_map.get('finance')
    
    # Professional/Technical
    professional_keywords = [
        'engineer', 'architect', 'scientist', 'researcher', 'analyst',
        'programmer', 'developer', 'software', 'computer', 'technician',
        'surveyor', 'drafter', 'designer'
    ]
    if any(kw in occ_lower for kw in professional_keywords):
        return industry_map.get('professional')
    
    # Information/Tech
    info_keywords = [
        'web', 'database', 'network', 'systems', 'information technology',
        'telecommunications', 'broadcast'
    ]
    if any(kw in occ_lower for kw in info_keywords):
        return industry_map.get('information')
    
    # Arts/Entertainment
    arts_keywords = [
        'artist', 'musician', 'actor', 'dancer', 'photographer',
        'entertainment', 'recreation', 'athlete'
    ]
    if any(kw in occ_lower for kw in arts_keywords):
        return industry_map.get('arts')
    
    # Real Estate
    if 'real estate' in occ_lower or 'property manager' in occ_lower:
        return industry_map.get('real_estate')
    
    # Management/Executive (could be any industry, default to professional)
    management_keywords = [
        'manager', 'director', 'executive', 'chief', 'supervisor',
        'administrator', 'coordinator'
    ]
    if any(kw in occ_lower for kw in management_keywords):
        return industry_map.get('professional') or industry_map.get('management')
    
    # Office/Administrative
    if any(kw in occ_lower for kw in ['secretary', 'clerk', 'receptionist', 'office']):
        return industry_map.get('professional')
    
    # Default fallback
    return industry_map.get('professional')

def convert_occupation_json_to_csv_with_mapping(industries):
    """Convert PHINVADS_occupation.json to occupations.csv with automatic industry mapping"""
    
    with open('data/PHINVADS_occupation.json', 'r') as f:
        data = json.load(f)
    
    concepts = data['versionList'][0]['conceptList']
    
    # Create industry mapping
    industry_map = find_industry_by_keyword(industries)
    
    print(f"\nIndustry category mappings:")
    for category, code in sorted(industry_map.items()):
        print(f"  {category:20s} → {code} ({industries[code]})")
    print()
    
    # Process occupations
    rows = []
    mapped_count = 0
    unmapped_count = 0
    
    for concept in concepts:
        display = concept['cdcpreferredDesignation']
        industry_code = guess_industry_for_occupation(display, industry_map)
        
        if industry_code:
            mapped_count += 1
        else:
            unmapped_count += 1
            print(f"⚠ No mapping for: {display}")
        
        rows.append({
            'code': concept['conceptCode'],
            'system': OCCUPATION_SYSTEM,
            'display': display,
            'industry_code': industry_code or ''
        })
    
    with open('data/occupations.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['code', 'system', 'display', 'industry_code'])
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"✓ Converted {len(concepts)} occupations to data/occupations.csv")
    print(f"  Mapped: {mapped_count}/{len(concepts)} occupations")
    if unmapped_count > 0:
        print(f"  Unmapped: {unmapped_count} (using fallback)")

if __name__ == '__main__':
    print("="*60)
    print("PHINVADS JSON → CSV Converter with Auto-Mapping")
    print("="*60)
    print()
    
    # Step 1: Convert industries
    industries = convert_industry_json_to_csv()
    
    # Step 2: Convert occupations with mapping
    convert_occupation_json_to_csv_with_mapping(industries)
    
    print()
    print("="*60)
    print("✓ Conversion complete!")
    print("="*60)
    print()
    print("Generated files:")
    print("  - data/industries.csv")
    print("  - data/occupations.csv (with industry_code mapped)")
    print()
    print("Note: Occupation→Industry mapping used keyword heuristics.")
    print("Review data/occupations.csv and adjust industry_code values as needed.")
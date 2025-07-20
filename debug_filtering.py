#!/usr/bin/env python3
"""
Debug script to understand why database ID filtering is failing.
"""

import sys
import os
sys.path.append('.')
sys.path.append('scAgent')

from scAgent.db.connect import get_connection
from scAgent.utils import check_database_id_availability, safe_int_convert

def main():
    print("=== Debugging Database ID Filtering ===")
    
    # Get database connection
    conn = get_connection()
    cur = conn.cursor()
    
    # Check a few sample records to see what the actual data looks like
    print('\n=== Sample GEO records ===')
    cur.execute('''
        SELECT gse, gse_title, organism 
        FROM geometa.geo_master 
        WHERE organism IS NOT NULL 
        LIMIT 5
    ''')
    
    geo_records = []
    for row in cur.fetchall():
        record = {
            'gse': row[0],
            'gse_title': row[1],
            'organism': row[2],
            'data_source': 'GEO'
        }
        geo_records.append(record)
        print(f'gse: {row[0]}, title: {row[1][:50] if row[1] else "None"}..., organism: {row[2]}')
    
    print('\n=== Sample SRA records ===')
    cur.execute('''
        SELECT run_accession, study_title, scientific_name 
        FROM srameta.sra_master 
        WHERE scientific_name IS NOT NULL 
        LIMIT 5
    ''')
    
    sra_records = []
    for row in cur.fetchall():
        record = {
            'run_accession': row[0],
            'study_title': row[1],
            'scientific_name': row[2],
            'data_source': 'SRA'
        }
        sra_records.append(record)
        print(f'run_accession: {row[0]}, title: {row[1][:50] if row[1] else "None"}..., organism: {row[2]}')
    
    # Test our database ID check function
    print('\n=== Testing Database ID Function ===')
    
    print("Testing GEO records:")
    for record in geo_records:
        result = check_database_id_availability(record)
        print(f"  Record: gse={record.get('gse')}")
        print(f"  Result: {result}")
        print()
    
    print("Testing SRA records:")
    for record in sra_records:
        result = check_database_id_availability(record)
        print(f"  Record: run_accession={record.get('run_accession')}")
        print(f"  Result: {result}")
        print()
    
    # Test species filtering
    print('\n=== Testing Species Filtering ===')
    from scAgent.utils import check_species_filter_lenient
    
    print("Testing GEO records for human species:")
    for record in geo_records:
        result = check_species_filter_lenient(record, ["Homo sapiens", "human"])
        print(f"  Record: organism={record.get('organism')}")
        print(f"  Result: {result}")
        print()
    
    print("Testing SRA records for human species:")
    for record in sra_records:
        result = check_species_filter_lenient(record, ["Homo sapiens", "human"])
        print(f"  Record: organism={record.get('scientific_name')}")
        print(f"  Result: {result}")
        print()
    
    # Test the complete filtering pipeline on a few records
    print('\n=== Testing Complete Filtering Pipeline ===')
    from scAgent.utils import apply_basic_filters_lenient
    
    all_test_records = geo_records + sra_records
    
    filter_config = {
        "required_species": ["Homo sapiens", "human"],
        "exclude_cell_lines": True,
        "require_database_id": True,
        "require_publication": False,
        "require_sample_size": False,
        "require_country_info": False,
        "require_age_info": False,
        "require_tumor_annotation": False,
        "require_sequencing_method": False,
        "require_tissue_source": False,
        "min_quality_score": 2,
        "ai_confidence_threshold": 0.5
    }
    
    print(f"Testing {len(all_test_records)} records with lenient filtering...")
    filtered_records = apply_basic_filters_lenient(all_test_records, filter_config)
    
    print(f"Original records: {len(all_test_records)}")
    print(f"Filtered records: {len(filtered_records)}")
    print(f"Retention rate: {len(filtered_records)/len(all_test_records)*100:.1f}%")
    
    # Show details of filtering results
    print("\nDetailed filtering results:")
    for i, record in enumerate(all_test_records):
        filter_result = record.get("sc_eqtl_filter_result", {})
        filter_scores = filter_result.get("filter_scores", {})
        passes = filter_result.get("passes_required_filters", False)
        reasons = filter_result.get("filter_reasons", [])
        
        print(f"Record {i+1} ({record.get('data_source')}):")
        print(f"  ID: {record.get('gse') or record.get('run_accession')}")
        print(f"  Scores: {filter_scores}")
        print(f"  Passes: {passes}")
        print(f"  Reasons: {reasons}")
        print()
    
    conn.close()

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Debug script to check human data availability in the database.
"""

import sys
import os
sys.path.append('.')
sys.path.append('scAgent')

from scAgent.db.query import execute_query

def main():
    print("=== Checking Human Data Availability ===")
    
    # Check SRA data for human records
    print("\n=== SRA Human Data Check ===")
    
    # Check total SRA records
    sra_total_query = "SELECT COUNT(*) FROM srameta.sra_master"
    sra_total = execute_query(sra_total_query)
    print(f"Total SRA records: {sra_total[0][0]:,}")
    
    # Check human records by scientific_name
    sra_human_by_name_query = """
    SELECT COUNT(*) FROM srameta.sra_master 
    WHERE LOWER(scientific_name) LIKE '%homo sapiens%' 
    OR LOWER(scientific_name) LIKE '%human%'
    """
    sra_human_by_name = execute_query(sra_human_by_name_query)
    print(f"SRA human records (by scientific_name): {sra_human_by_name[0][0]:,}")
    
    # Check human records by study_title
    sra_human_by_title_query = """
    SELECT COUNT(*) FROM srameta.sra_master 
    WHERE LOWER(study_title) LIKE '%homo sapiens%' 
    OR LOWER(study_title) LIKE '%human%'
    OR LOWER(study_title) LIKE '%patient%'
    OR LOWER(study_title) LIKE '%clinical%'
    """
    sra_human_by_title = execute_query(sra_human_by_title_query)
    print(f"SRA human records (by study_title): {sra_human_by_title[0][0]:,}")
    
    # Check human records by design_description
    sra_human_by_design_query = """
    SELECT COUNT(*) FROM srameta.sra_master 
    WHERE LOWER(design_description) LIKE '%homo sapiens%' 
    OR LOWER(design_description) LIKE '%human%'
    """
    sra_human_by_design = execute_query(sra_human_by_design_query)
    print(f"SRA human records (by design_description): {sra_human_by_design[0][0]:,}")
    
    # Get some sample human SRA records
    sra_human_sample_query = """
    SELECT run_accession, study_title, scientific_name, design_description
    FROM srameta.sra_master 
    WHERE LOWER(scientific_name) LIKE '%homo sapiens%' 
    OR LOWER(scientific_name) LIKE '%human%'
    OR LOWER(study_title) LIKE '%homo sapiens%' 
    OR LOWER(study_title) LIKE '%human%'
    OR LOWER(design_description) LIKE '%homo sapiens%' 
    OR LOWER(design_description) LIKE '%human%'
    LIMIT 10
    """
    sra_human_samples = execute_query(sra_human_sample_query)
    print(f"\nSample human SRA records:")
    for record in sra_human_samples:
        print(f"  {record[0]}: {record[1][:50]}... | {record[2]} | {record[3][:50] if record[3] else 'None'}...")
    
    # Check GEO data for human records
    print("\n=== GEO Human Data Check ===")
    
    # Check total GEO records
    geo_total_query = "SELECT COUNT(*) FROM geometa.geo_master"
    geo_total = execute_query(geo_total_query)
    print(f"Total GEO records: {geo_total[0][0]:,}")
    
    # Check human records by organism
    geo_human_by_organism_query = """
    SELECT COUNT(*) FROM geometa.geo_master 
    WHERE LOWER(organism) LIKE '%homo sapiens%' 
    OR LOWER(organism) LIKE '%human%'
    """
    geo_human_by_organism = execute_query(geo_human_by_organism_query)
    print(f"GEO human records (by organism): {geo_human_by_organism[0][0]:,}")
    
    # Check human records by title
    geo_human_by_title_query = """
    SELECT COUNT(*) FROM geometa.geo_master 
    WHERE LOWER(gse_title) LIKE '%homo sapiens%' 
    OR LOWER(gse_title) LIKE '%human%'
    OR LOWER(gse_title) LIKE '%patient%'
    OR LOWER(gse_title) LIKE '%clinical%'
    """
    geo_human_by_title = execute_query(geo_human_by_title_query)
    print(f"GEO human records (by gse_title): {geo_human_by_title[0][0]:,}")
    
    # Get some sample human GEO records
    geo_human_sample_query = """
    SELECT gse, gse_title, organism, organism_ch1
    FROM geometa.geo_master 
    WHERE LOWER(organism) LIKE '%homo sapiens%' 
    OR LOWER(organism) LIKE '%human%'
    OR LOWER(gse_title) LIKE '%homo sapiens%' 
    OR LOWER(gse_title) LIKE '%human%'
    OR LOWER(organism_ch1) LIKE '%homo sapiens%'
    OR LOWER(organism_ch1) LIKE '%human%'
    LIMIT 10
    """
    geo_human_samples = execute_query(geo_human_sample_query)
    print(f"\nSample human GEO records:")
    for record in geo_human_samples:
        print(f"  {record[0]}: {record[1][:50]}... | {record[2]} | {record[3]}")
    
    # Now let's test what happens with the first 1000 SRA records (as used in comprehensive clean)
    print("\n=== Testing First 1000 SRA Records ===")
    test_query = """
    SELECT run_accession, study_title, scientific_name, design_description
    FROM srameta.sra_master 
    LIMIT 1000
    """
    test_records = execute_query(test_query)
    
    human_count = 0
    for record in test_records:
        text_to_check = f"{record[1] or ''} {record[2] or ''} {record[3] or ''}".lower()
        if ('homo sapiens' in text_to_check or 'human' in text_to_check or 
            'patient' in text_to_check or 'clinical' in text_to_check):
            human_count += 1
    
    print(f"Human records in first 1000 SRA records: {human_count}")
    print(f"Percentage: {human_count/1000*100:.1f}%")
    
    # Test with better human detection
    print("\n=== Enhanced Human Detection Test ===")
    enhanced_human_count = 0
    for record in test_records:
        text_to_check = f"{record[1] or ''} {record[2] or ''} {record[3] or ''}".lower()
        
        # More comprehensive human detection
        human_indicators = [
            'homo sapiens', 'human', 'h. sapiens', 'hsapiens', 
            'people', 'patient', 'subject', 'clinical', 'medical',
            'cancer', 'tumor', 'disease', 'breast', 'lung', 'liver',
            'brain', 'blood', 'pbmc', 'peripheral blood'
        ]
        
        for indicator in human_indicators:
            if indicator in text_to_check:
                enhanced_human_count += 1
                break
    
    print(f"Enhanced human detection in first 1000 SRA records: {enhanced_human_count}")
    print(f"Enhanced percentage: {enhanced_human_count/1000*100:.1f}%")
    
    if enhanced_human_count > human_count:
        print(f"Enhanced detection found {enhanced_human_count - human_count} additional potential human records")

if __name__ == "__main__":
    main() 
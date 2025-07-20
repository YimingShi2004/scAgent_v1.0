#!/usr/bin/env python3
"""
Debug script to test data loading and basic filtering.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scAgent'))

from scAgent.db.query import execute_query
from scAgent.utils import safe_int_convert

def test_data_loading():
    """Test basic data loading without complex operations."""
    print("Testing SRA data loading...")
    
    sra_query = """
    SELECT 
        run_accession,
        experiment_title as title,
        study_abstract as summary,
        scientific_name as organism,
        platform,
        spots,
        bases
    FROM srameta.sra_master
    LIMIT 10
    """
    
    try:
        sra_records = execute_query(sra_query)
        print(f"Loaded {len(sra_records)} SRA records")
        
        # Test data types
        for i, record in enumerate(sra_records[:3]):
            print(f"\nRecord {i+1}:")
            print(f"  run_accession: {record.get('run_accession')} (type: {type(record.get('run_accession'))})")
            print(f"  title: {record.get('title')} (type: {type(record.get('title'))})")
            print(f"  spots: {record.get('spots')} (type: {type(record.get('spots'))})")
            print(f"  bases: {record.get('bases')} (type: {type(record.get('bases'))})")
            
            # Test safe conversion
            spots_safe = safe_int_convert(record.get('spots'))
            bases_safe = safe_int_convert(record.get('bases'))
            print(f"  spots_safe: {spots_safe} (type: {type(spots_safe)})")
            print(f"  bases_safe: {bases_safe} (type: {type(bases_safe)})")
            
            # Test comparison
            try:
                if spots_safe > 0:
                    print(f"  spots comparison: OK")
                else:
                    print(f"  spots comparison: Zero or negative")
            except Exception as e:
                print(f"  spots comparison ERROR: {e}")
                
    except Exception as e:
        print(f"Error loading SRA data: {e}")
        import traceback
        traceback.print_exc()

def test_geo_loading():
    """Test GEO data loading."""
    print("\nTesting GEO data loading...")
    
    geo_query = """
    SELECT 
        "gse_ID" as geo_accession,
        gse_title as title,
        summary,
        organism
    FROM geometa.geo_master
    LIMIT 10
    """
    
    try:
        geo_records = execute_query(geo_query)
        print(f"Loaded {len(geo_records)} GEO records")
        
        # Test data types
        for i, record in enumerate(geo_records[:3]):
            print(f"\nGEO Record {i+1}:")
            print(f"  geo_accession: {record.get('geo_accession')} (type: {type(record.get('geo_accession'))})")
            print(f"  title: {record.get('title')} (type: {type(record.get('title'))})")
            print(f"  organism: {record.get('organism')} (type: {type(record.get('organism'))})")
                
    except Exception as e:
        print(f"Error loading GEO data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_data_loading()
    test_geo_loading() 
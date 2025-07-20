#!/usr/bin/env python3
"""
Debug script to check actual data loading in comprehensive clean command.
"""

import sys
import os
sys.path.append('.')
sys.path.append('scAgent')

from scAgent.db.query import execute_query
from scAgent.utils import check_database_id_availability, check_species_filter_lenient

def main():
    print("=== Debugging Data Loading in Comprehensive Clean ===")
    
    # Test the exact queries used in comprehensive clean
    print("\n=== Testing SRA Query ===")
    sra_query = """
    SELECT 
        run_accession,
        study_title,
        study_abstract,
        scientific_name,
        platform,
        instrument_model,
        library_strategy,
        library_source,
        library_selection,
        library_layout,
        spots,
        bases,
        run_date,
        updated_date,
        study_type,
        study_description,
        design_description,
        library_construction_protocol,
        sample_name,
        description as sample_description,
        taxon_id,
        common_name,
        study_accession,
        experiment_accession,
        sample_accession,
        "sra_ID" as sra_id,
        "run_ID" as run_id,
        "experiment_ID" as experiment_id,
        "sample_ID" as sample_id,
        "study_ID" as study_id,
        "submission_ID" as submission_id,
        'SRA' as data_source
    FROM srameta.sra_master
    LIMIT 5
    """
    
    try:
        sra_records = execute_query(sra_query)
        print(f"Loaded {len(sra_records)} SRA records")
        
        if sra_records:
            print("First SRA record structure:")
            for key, value in sra_records[0].items():
                print(f"  {key}: {value}")
            
            # Test filtering on first record
            print("\nTesting SRA record filtering:")
            test_record = sra_records[0]
            
            # Test database ID
            db_result = check_database_id_availability(test_record)
            print(f"Database ID check result: {db_result}")
            print(f"  run_accession: {test_record.get('run_accession')}")
            
            # Test species
            species_result = check_species_filter_lenient(test_record, ["Homo sapiens", "human"])
            print(f"Species check result: {species_result}")
            print(f"  scientific_name: {test_record.get('scientific_name')}")
            print(f"  study_title: {test_record.get('study_title', '')[:100]}...")
            
    except Exception as e:
        print(f"SRA query failed: {e}")
    
    print("\n=== Testing GEO Query ===")
    geo_query = """
    SELECT 
        gse,
        gse_title,
        summary,
        organism,
        technology as platform,
        gse_submission_date as submission_date,
        gse_last_update_date as last_update_date,
        overall_design,
        gse_contact as contact_name,
        pubmed_id,
        gse_web_link as web_link,
        gse_supplementary_file as supplementary_file,
        contributor,
        gse_type,
        source_name_ch1,
        organism_ch1,
        characteristics_ch1,
        molecule_ch1,
        treatment_protocol_ch1,
        extract_protocol_ch1,
        gsm_description,
        data_processing,
        'GEO' as data_source
    FROM geometa.geo_master
    LIMIT 5
    """
    
    try:
        geo_records = execute_query(geo_query)
        print(f"Loaded {len(geo_records)} GEO records")
        
        if geo_records:
            print("First GEO record structure:")
            for key, value in geo_records[0].items():
                print(f"  {key}: {value}")
            
            # Test filtering on first record
            print("\nTesting GEO record filtering:")
            test_record = geo_records[0]
            
            # Test database ID
            db_result = check_database_id_availability(test_record)
            print(f"Database ID check result: {db_result}")
            print(f"  gse: {test_record.get('gse')}")
            
            # Test species
            species_result = check_species_filter_lenient(test_record, ["Homo sapiens", "human"])
            print(f"Species check result: {species_result}")
            print(f"  organism: {test_record.get('organism')}")
            print(f"  gse_title: {test_record.get('gse_title', '')[:100]}...")
            
    except Exception as e:
        print(f"GEO query failed: {e}")
    
    # Test with combined records like in comprehensive clean
    print("\n=== Testing Combined Records Processing ===")
    try:
        all_records = []
        if 'sra_records' in locals() and sra_records:
            all_records.extend(sra_records)
        if 'geo_records' in locals() and geo_records:
            all_records.extend(geo_records)
        
        print(f"Total combined records: {len(all_records)}")
        
        # Test the complete filtering pipeline
        from scAgent.utils import apply_basic_filters_lenient
        
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
        
        print(f"Testing filtering with config: {filter_config}")
        
        filtered_records = apply_basic_filters_lenient(all_records, filter_config)
        
        print(f"Filtered records: {len(filtered_records)}")
        print(f"Retention rate: {len(filtered_records)/len(all_records)*100:.1f}%")
        
        # Show detailed results for each record
        for i, record in enumerate(all_records):
            filter_result = record.get("sc_eqtl_filter_result", {})
            filter_scores = filter_result.get("filter_scores", {})
            passes = filter_result.get("passes_required_filters", False)
            reasons = filter_result.get("filter_reasons", [])
            
            print(f"\nRecord {i+1} ({record.get('data_source')}):")
            print(f"  ID: {record.get('gse') or record.get('run_accession')}")
            print(f"  Species field: {record.get('organism') or record.get('scientific_name')}")
            print(f"  Scores: {filter_scores}")
            print(f"  Passes: {passes}")
            print(f"  Reasons: {reasons}")
            
            # Debug specific failing filters
            if filter_scores.get('database_id', 0) == 0:
                print(f"  DEBUG - DB ID issue:")
                print(f"    gse: {record.get('gse')}")
                print(f"    run_accession: {record.get('run_accession')}")
                
            if filter_scores.get('species', 0) == 0:
                print(f"  DEBUG - Species issue:")
                print(f"    organism: {record.get('organism')}")
                print(f"    scientific_name: {record.get('scientific_name')}")
                print(f"    gse_title: {record.get('gse_title', '')[:50]}...")
                print(f"    study_title: {record.get('study_title', '')[:50]}...")
        
    except Exception as e:
        print(f"Combined processing failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Debug script to test the comprehensive clean with detailed error tracking.
"""

import sys
import os
import traceback
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scAgent'))

from scAgent.db.query import execute_query
from scAgent.utils import (
    safe_int_convert, 
    build_geo_sra_mapping, 
    create_integrated_dataset_table,
    apply_sc_eqtl_filters_with_ai
)

def test_comprehensive_clean():
    """Test the comprehensive clean process step by step."""
    print("=== Testing Comprehensive Clean Process ===")
    
    try:
        # Step 1: Load SRA data
        print("\n1. Loading SRA data...")
        sra_query = """
        SELECT 
            run_accession,
            experiment_title as title,
            study_abstract as summary,
            scientific_name as organism,
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
            study_title,
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
        LIMIT 10
        """
        
        sra_records = execute_query(sra_query)
        print(f"✓ Loaded {len(sra_records)} SRA records")
        
        # Step 2: Load GEO data
        print("\n2. Loading GEO data...")
        geo_query = """
        SELECT 
            "gse_ID" as geo_accession,
            gse_title as title,
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
        LIMIT 10
        """
        
        geo_records = execute_query(geo_query)
        print(f"✓ Loaded {len(geo_records)} GEO records")
        
        # Step 3: Build mapping
        print("\n3. Building GEO-SRA mapping...")
        mapping = build_geo_sra_mapping(geo_records, sra_records)
        print(f"✓ Built mapping with {len(mapping['geo_to_sra'])} GEO->SRA mappings")
        
        # Step 4: Create integrated table
        print("\n4. Creating integrated dataset table...")
        integrated_table = create_integrated_dataset_table(geo_records, sra_records, mapping)
        print(f"✓ Created integrated table with {len(integrated_table)} records")
        
        # Step 5: Apply filters
        print("\n5. Applying filters...")
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
        
        filtered_records = apply_sc_eqtl_filters_with_ai(
            integrated_table, 
            filter_config, 
            use_ai=False,  # Disable AI for now
            ai_batch_size=3
        )
        print(f"✓ Filtered to {len(filtered_records)} records")
        
        print("\n=== SUCCESS: All steps completed! ===")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\n=== DETAILED TRACEBACK ===")
        traceback.print_exc()
        
        # Try to identify the problematic data
        print("\n=== DEBUGGING INFO ===")
        print("Let's examine the data types in the last successful step...")
        
        # Check data types in records
        if 'sra_records' in locals():
            print(f"SRA record sample:")
            for key, value in list(sra_records[0].items())[:5]:
                print(f"  {key}: {value} (type: {type(value)})")
        
        if 'geo_records' in locals():
            print(f"GEO record sample:")
            for key, value in list(geo_records[0].items())[:5]:
                print(f"  {key}: {value} (type: {type(value)})")

if __name__ == "__main__":
    test_comprehensive_clean() 
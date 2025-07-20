#!/usr/bin/env python3
"""
Debug script for the new intelligent filtering system.
"""

import sys
import os
sys.path.append('.')
sys.path.append('scAgent')

from scAgent.db.query import execute_query
from scAgent.utils import (
    apply_intelligent_sc_eqtl_filters,
    assess_database_id_with_confidence,
    assess_species_with_confidence,
    assess_cell_line_with_confidence
)

def main():
    print("=== Debugging Intelligent Filtering System ===")
    
    # Load some test records
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
        'SRA' as data_source
    FROM srameta.sra_master
    ORDER BY human_priority DESC, "sra_ID" DESC
    LIMIT 10
    """
    
    # Remove the ORDER BY clause that doesn't work
    sra_query_fixed = """
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
        'SRA' as data_source
    FROM srameta.sra_master
    LIMIT 10
    """
    
    try:
        records = execute_query(sra_query_fixed)
        print(f"Loaded {len(records)} test records")
        
        # Test individual assessment functions
        print("\n=== Testing Individual Assessment Functions ===")
        
        for i, record in enumerate(records[:3]):
            print(f"\nRecord {i+1}: {record.get('run_accession')}")
            print(f"Title: {record.get('study_title', '')[:100]}...")
            
            # Test database ID assessment
            db_result = assess_database_id_with_confidence(record)
            print(f"Database ID: {db_result}")
            
            # Test species assessment
            species_result = assess_species_with_confidence(record, ["Homo sapiens", "human"])
            print(f"Species: {species_result}")
            
            # Test cell line assessment
            cell_line_result = assess_cell_line_with_confidence(record)
            print(f"Cell Line: {cell_line_result}")
        
        # Test the complete intelligent filtering
        print(f"\n=== Testing Complete Intelligent Filtering ===")
        
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
            "ai_confidence_threshold": 0.7
        }
        
        print(f"Testing intelligent filtering on {len(records)} records...")
        
        # Test without AI first
        filtered_records = apply_intelligent_sc_eqtl_filters(
            records, 
            filter_config, 
            use_ai=False,
            ai_batch_size=5
        )
        
        print(f"Filtered records (no AI): {len(filtered_records)}")
        
        # Show detailed results
        print("\n=== Detailed Filtering Results ===")
        for i, record in enumerate(records):
            filter_result = record.get("sc_eqtl_filter_result", {})
            print(f"\nRecord {i+1}: {record.get('run_accession')}")
            print(f"  Phase: {filter_result.get('phase', 'unknown')}")
            print(f"  Passes Critical: {filter_result.get('passes_critical', 'unknown')}")
            print(f"  Rejection Reason: {filter_result.get('rejection_reason', 'none')}")
            print(f"  Filter Details: {filter_result.get('filter_details', {})}")
            print(f"  Overall Score: {filter_result.get('overall_score', 0)}")
            print(f"  Decision: {filter_result.get('decision', 'unknown')}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 
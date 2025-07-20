#!/usr/bin/env python3
"""
Debug script to test the exact data format used in comprehensive clean
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from scAgent.db.connect import get_connection
from scAgent.db.query import execute_query
from scAgent.utils import (
    apply_intelligent_sc_eqtl_filters,
    build_geo_sra_mapping,
    create_integrated_dataset_table,
    assess_database_id_with_confidence,
    assess_species_with_confidence,
    assess_cell_line_with_confidence
)
from rich.console import Console
from rich.table import Table
import json

console = Console()

def debug_comprehensive_clean():
    """Debug the exact process used in comprehensive clean"""
    
    print("=== Debugging Comprehensive Clean Process ===")
    
    # Step 1: Load SRA data exactly like comprehensive clean does
    print("\n1. Loading SRA data (same query as comprehensive clean)...")
    
    sra_query = """
    SELECT 
        run_accession,
        study_title,
        study_abstract,
        scientific_name,
        common_name,
        taxon_id,
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
        description,
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
    WHERE "run_accession" IS NOT NULL AND "run_accession" != ''
    ORDER BY "sra_ID" DESC
    LIMIT 10
    """
    
    sra_records = execute_query(sra_query)
    print(f"✓ Loaded {len(sra_records)} SRA records")
    
    # Step 2: Load GEO data
    print("\n2. Loading GEO data...")
    
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
    ORDER BY "gse_ID" DESC
    LIMIT 2
    """
    
    geo_records = execute_query(geo_query)
    print(f"✓ Loaded {len(geo_records)} GEO records")
    
    # Step 3: Build mapping
    print("\n3. Building GEO-SRA mapping...")
    mapping = build_geo_sra_mapping(geo_records, sra_records)
    print(f"✓ Built mapping: {len(mapping.get('geo_to_sra', {}))} GEO-SRA links")
    
    # Step 4: Create integrated dataset
    print("\n4. Creating integrated dataset...")
    integrated_records = create_integrated_dataset_table(geo_records, sra_records, mapping)
    print(f"✓ Created {len(integrated_records)} integrated records")
    
    # Step 5: Show sample integrated record structure
    if integrated_records:
        print("\n5. Sample integrated record structure:")
        sample_record = integrated_records[0]
        print("Available fields:")
        for key, value in sample_record.items():
            value_str = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
            print(f"  {key}: {value_str}")
    
    # Step 6: Test individual assessment functions on integrated records
    print("\n6. Testing assessment functions on integrated records...")
    
    for i, record in enumerate(integrated_records[:3], 1):
        print(f"\n--- Integrated Record {i} ---")
        print(f"SRA Run: {record.get('sra_run_accession', 'N/A')}")
        print(f"GEO: {record.get('geo_accession', 'N/A')}")
        
        # Test database ID assessment
        db_result = assess_database_id_with_confidence(record)
        print(f"DB Assessment: {db_result}")
        
        # Test species assessment
        species_result = assess_species_with_confidence(record, ["Homo sapiens", "human"])
        print(f"Species Assessment: {species_result}")
        
        # Test cell line assessment
        cell_result = assess_cell_line_with_confidence(record)
        print(f"Cell Line Assessment: {cell_result}")
    
    # Step 7: Test intelligent filtering
    print("\n7. Testing intelligent filtering...")
    
    try:
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
        
        filtered_records = apply_intelligent_sc_eqtl_filters(
            integrated_records,
            filter_config=filter_config,
            use_ai=False,  # Disable AI for testing
            ai_batch_size=5
        )
        
        print(f"✓ Intelligent filtering completed")
        print(f"✓ Input: {len(integrated_records)} records")
        print(f"✓ Output: {len(filtered_records)} records")
        print(f"✓ Retention rate: {len(filtered_records)/len(integrated_records)*100:.1f}%")
        
        # Show filtering results
        if filtered_records:
            print("\n8. Sample filtered record:")
            sample_filtered = filtered_records[0]
            filter_result = sample_filtered.get("sc_eqtl_filter_result", {})
            print(f"  Decision: {filter_result.get('decision', 'N/A')}")
            print(f"  Phase: {filter_result.get('phase', 'N/A')}")
            print(f"  Overall Score: {filter_result.get('overall_score', 'N/A')}")
            print(f"  Rejection Reason: {filter_result.get('rejection_reason', 'N/A')}")
        else:
            print("\n8. No records passed filtering - analyzing why...")
            
            # Check first record's filtering details
            if integrated_records:
                test_record = integrated_records[0]
                print(f"\nAnalyzing first record: {test_record.get('sra_run_accession', 'N/A')}")
                
                # Manual phase 1 check
                db_result = assess_database_id_with_confidence(test_record)
                species_result = assess_species_with_confidence(test_record, ["Homo sapiens", "human"])
                cell_result = assess_cell_line_with_confidence(test_record)
                
                print(f"  Database ID: score={db_result['score']}, confidence={db_result['confidence']}")
                print(f"  Species: score={species_result['score']}, confidence={species_result['confidence']}")
                print(f"  Cell Line: score={cell_result['score']}, confidence={cell_result['confidence']}")
                
                # Check phase 1 logic
                passes_critical = True
                rejection_reason = None
                
                if db_result['score'] == 0:
                    passes_critical = False
                    rejection_reason = f"No valid database ID: {db_result['reason']}"
                elif species_result['score'] == 0 and species_result['confidence'] >= 0.7:
                    passes_critical = False
                    rejection_reason = f"Non-human species (high confidence): {species_result['reason']}"
                elif cell_result['score'] == 0 and cell_result['confidence'] >= 0.8:
                    passes_critical = False
                    rejection_reason = f"Cell line detected (high confidence): {cell_result['reason']}"
                
                print(f"  Phase 1 Result: {'PASS' if passes_critical else 'FAIL'}")
                if rejection_reason:
                    print(f"  Rejection Reason: {rejection_reason}")
                
    except Exception as e:
        print(f"❌ Error in intelligent filtering: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_comprehensive_clean() 
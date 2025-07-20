#!/usr/bin/env python3
"""
Test script for full comprehensive clean with proper field mapping
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from scAgent.db.query import execute_query
from scAgent.utils import apply_intelligent_sc_eqtl_filters
from rich.console import Console

console = Console()

def test_full_comprehensive_clean():
    """Test the full comprehensive clean process with proper handling."""
    
    print("=== Testing Full Comprehensive Clean Process ===")
    
    # Step 1: Load SRA data with proper field names
    print("\n1. Loading SRA data...")
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
        'SRA' as data_source
    FROM srameta.sra_master
    WHERE "run_accession" IS NOT NULL AND "run_accession" != ''
    ORDER BY "sra_ID" DESC
    LIMIT 20
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
        'GEO' as data_source
    FROM geometa.geo_master
    ORDER BY "gse_ID" DESC
    LIMIT 5
    """
    
    geo_records = execute_query(geo_query)
    print(f"✓ Loaded {len(geo_records)} GEO records")
    
    # Step 3: Create simple integrated records (focusing on SRA data)
    print("\n3. Creating integrated records...")
    
    integrated_records = []
    
    # Add SRA-only records (these should work well)
    for sra_record in sra_records:
        integrated_record = {
            # Use SRA data as primary
            "sra_run_accession": sra_record.get('run_accession', ''),
            "run_accession": sra_record.get('run_accession', ''),  # For compatibility
            "sra_study_accession": sra_record.get('study_accession', ''),
            "study_accession": sra_record.get('study_accession', ''),  # For compatibility
            
            # Species information (multiple field names for compatibility)
            "scientific_name": sra_record.get('scientific_name', ''),
            "organism": sra_record.get('scientific_name', ''),  # Map scientific_name to organism
            "sra_organism": sra_record.get('scientific_name', ''),
            "common_name": sra_record.get('common_name', ''),
            "taxon_id": sra_record.get('taxon_id', ''),
            
            # Title/summary information
            "sra_study_title": sra_record.get('study_title', ''),
            "study_title": sra_record.get('study_title', ''),  # For compatibility
            "geo_title": sra_record.get('study_title', ''),  # For compatibility
            "study_abstract": sra_record.get('study_abstract', ''),
            "geo_summary": sra_record.get('study_abstract', ''),  # For compatibility
            "summary": sra_record.get('study_abstract', ''),  # For compatibility
            
            # Technical details
            "platform": sra_record.get('platform', ''),
            "instrument_model": sra_record.get('instrument_model', ''),
            "library_strategy": sra_record.get('library_strategy', ''),
            "library_layout": sra_record.get('library_layout', ''),
            "spots": sra_record.get('spots', 0),
            "bases": sra_record.get('bases', 0),
            
            # Additional fields
            "design_description": sra_record.get('design_description', ''),
            "sample_name": sra_record.get('sample_name', ''),
            "description": sra_record.get('description', ''),
            
            # Metadata
            "relationship_type": "sra_only",
            "data_source": "SRA",
            "mapping_confidence": 1.0
        }
        integrated_records.append(integrated_record)
    
    # Add a few GEO-only records for completeness
    for geo_record in geo_records[:3]:
        integrated_record = {
            # GEO information
            "geo_accession": geo_record.get('gse', ''),
            "gse": geo_record.get('gse', ''),  # For compatibility
            
            # Species information
            "organism": geo_record.get('organism', ''),
            "geo_organism": geo_record.get('organism', ''),
            
            # Title/summary
            "geo_title": geo_record.get('gse_title', ''),
            "gse_title": geo_record.get('gse_title', ''),  # For compatibility
            "geo_summary": geo_record.get('summary', ''),
            "summary": geo_record.get('summary', ''),  # For compatibility
            
            # Platform
            "geo_platform": geo_record.get('platform', ''),
            "platform": geo_record.get('platform', ''),  # For compatibility
            
            # Metadata
            "relationship_type": "geo_only",
            "data_source": "GEO",
            "mapping_confidence": 0.5
        }
        integrated_records.append(integrated_record)
    
    print(f"✓ Created {len(integrated_records)} integrated records")
    
    # Step 4: Apply intelligent filtering
    print("\n4. Applying intelligent filtering...")
    
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
        "min_quality_score": 3,
        "ai_confidence_threshold": 0.6,
        "conservative_acceptance_threshold": 4,
        "species_confidence_threshold": 0.6,
        "cell_line_confidence_threshold": 0.8
    }
    
    try:
        filtered_records = apply_intelligent_sc_eqtl_filters(
            integrated_records,
            filter_config=filter_config,
            use_ai=False,  # Disable AI for testing
            ai_batch_size=5
        )
        
        print(f"✓ Filtering completed!")
        print(f"✓ Input: {len(integrated_records)} records")
        print(f"✓ Output: {len(filtered_records)} records")
        print(f"✓ Retention rate: {len(filtered_records)/len(integrated_records)*100:.1f}%")
        
        # Show sample results
        if filtered_records:
            print(f"\n5. Sample filtered records:")
            for i, record in enumerate(filtered_records[:3], 1):
                filter_result = record.get("sc_eqtl_filter_result", {})
                print(f"  Record {i}:")
                print(f"    SRA ID: {record.get('sra_run_accession', 'N/A')}")
                print(f"    GEO ID: {record.get('geo_accession', 'N/A')}")
                print(f"    Decision: {filter_result.get('decision', 'N/A')}")
                print(f"    Overall Score: {filter_result.get('overall_score', 'N/A')}")
                print(f"    Phase: {filter_result.get('phase', 'N/A')}")
                
        else:
            print(f"\n5. No records passed filtering")
            # Analyze first few records
            print("\nAnalyzing first 3 records:")
            for i, record in enumerate(integrated_records[:3], 1):
                filter_result = record.get("sc_eqtl_filter_result", {})
                print(f"  Record {i}:")
                print(f"    SRA ID: {record.get('sra_run_accession', 'N/A')}")
                print(f"    Decision: {filter_result.get('decision', 'N/A')}")
                print(f"    Rejection Reason: {filter_result.get('rejection_reason', 'N/A')}")
                print(f"    Overall Score: {filter_result.get('overall_score', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Error in filtering: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_full_comprehensive_clean() 
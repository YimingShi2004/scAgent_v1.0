#!/usr/bin/env python3
"""
Debug script to analyze why Phase 1 critical filters reject all records
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from scAgent.db.connect import get_connection
from scAgent.utils import (
    assess_database_id_with_confidence,
    assess_species_with_confidence, 
    assess_cell_line_with_confidence
)
from rich.console import Console
from rich.table import Table
from rich import print as rprint
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
console = Console()

def debug_phase1_critical():
    """Debug why phase 1 critical filters fail"""
    
    print("=== Debugging Phase 1 Critical Filters ===")
    
    # Load sample data
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get 20 sample records to debug
    cursor.execute("""
        SELECT "sra_ID", "run_accession", "study_title", "study_abstract", "scientific_name", 
               "spots", "bases"
        FROM srameta.sra_master 
        WHERE "run_accession" IS NOT NULL AND "run_accession" != ''
        ORDER BY "sra_ID" DESC
        LIMIT 20
    """)
    
    records = []
    for row in cursor.fetchall():
        record = {
            'sra_ID': row[0],
            'run_accession': row[1] or '',
            'study_title': row[2] or '',
            'study_abstract': row[3] or '',
            'scientific_name': row[4] or '',
            'spots': row[5],
            'bases': row[6]
        }
        records.append(record)
    
    cursor.close()
    conn.close()
    
    print(f"Loaded {len(records)} sample records for analysis")
    print()
    
    # Test each record through phase 1 critical filters
    critical_results = []
    
    for i, record in enumerate(records[:10], 1):
        print(f"=== Record {i}: {record['sra_ID']} ===")
        print(f"Run Accession: {record['run_accession']}")
        print(f"Title: {record['study_title'][:100]}...")
        print(f"Scientific Name: {record['scientific_name']}")
        print(f"Spots: {record['spots']}")
        print()
        
        # Test database ID confidence
        db_result = assess_database_id_with_confidence(record)
        print(f"Database ID Assessment:")
        print(f"  Score: {db_result['score']}")
        print(f"  Confidence: {db_result['confidence']}")
        print(f"  Reason: {db_result['reason']}")
        print()
        
        # Test species confidence  
        species_result = assess_species_with_confidence(record, ["Homo sapiens"])
        print(f"Species Assessment:")
        print(f"  Score: {species_result['score']}")
        print(f"  Confidence: {species_result['confidence']}")
        print(f"  Reason: {species_result['reason']}")
        print()
        
        # Test cell line confidence
        cell_result = assess_cell_line_with_confidence(record)
        print(f"Cell Line Assessment:")
        print(f"  Score: {cell_result['score']}")
        print(f"  Confidence: {cell_result['confidence']}")
        print(f"  Reason: {cell_result['reason']}")
        print()
        
        # Check critical filter logic
        passes_critical = True
        rejection_reason = None
        
        # Critical filter 1: Database ID must be valid
        if db_result['score'] == 0:
            passes_critical = False
            rejection_reason = f"No valid database ID: {db_result['reason']}"
        
        # Critical filter 2: Species must be human (if specified)
        elif species_result['score'] == 0 and species_result['confidence'] >= 0.7:
            passes_critical = False
            rejection_reason = f"Non-human species (high confidence): {species_result['reason']}"
        
        # Critical filter 3: Cell line exclusion
        elif cell_result['score'] == 0 and cell_result['confidence'] >= 0.8:
            passes_critical = False
            rejection_reason = f"Cell line detected (high confidence): {cell_result['reason']}"
        
        print(f"PHASE 1 RESULT: {'PASS' if passes_critical else 'FAIL'}")
        if rejection_reason:
            print(f"REJECTION REASON: {rejection_reason}")
        print("-" * 80)
        print()
        
        critical_results.append({
            'record_id': record['sra_ID'],
            'passes_critical': passes_critical,
            'rejection_reason': rejection_reason,
            'db_score': db_result['score'],
            'species_score': species_result['score'],
            'cell_score': cell_result['score']
        })
    
    # Summary
    print("=== PHASE 1 CRITICAL FILTER SUMMARY ===")
    passed = sum(1 for r in critical_results if r['passes_critical'])
    failed = len(critical_results) - passed
    
    print(f"Total tested: {len(critical_results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Pass rate: {(passed/len(critical_results)*100):.1f}%")
    print()
    
    # Analyze failure reasons
    failure_reasons = {}
    for result in critical_results:
        if not result['passes_critical']:
            reason = result['rejection_reason']
            if reason in failure_reasons:
                failure_reasons[reason] += 1
            else:
                failure_reasons[reason] = 1
    
    if failure_reasons:
        print("FAILURE REASONS:")
        for reason, count in failure_reasons.items():
            print(f"  {count}x: {reason}")
    
    # Create summary table
    table = Table(title="Phase 1 Critical Filter Results")
    table.add_column("Record ID", style="cyan")
    table.add_column("DB Score", style="green")
    table.add_column("Species Score", style="blue") 
    table.add_column("Cell Score", style="yellow")
    table.add_column("Result", style="red")
    
    for result in critical_results:
        table.add_row(
            result['record_id'],
            str(result['db_score']),
            str(result['species_score']),
            str(result['cell_score']),
            "PASS" if result['passes_critical'] else "FAIL"
        )
    
    console.print(table)

if __name__ == "__main__":
    debug_phase1_critical() 
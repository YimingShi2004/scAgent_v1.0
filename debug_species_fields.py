#!/usr/bin/env python3
"""
Debug script to check species-related fields in the database
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from scAgent.db.connect import get_connection
from rich.console import Console
from rich.table import Table

console = Console()

def debug_species_fields():
    """Check what species-related fields are available"""
    
    print("=== Debugging Species Fields in Database ===")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # First, let's see what columns are available
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_schema = 'srameta' 
        AND table_name = 'sra_master'
        ORDER BY ordinal_position
    """)
    
    print("\n=== Available Columns in srameta.sra_master ===")
    columns = cursor.fetchall()
    for col_name, data_type in columns:
        print(f"  {col_name}: {data_type}")
    
    # Now let's check some sample data for species-related fields
    cursor.execute("""
        SELECT "run_accession", "study_title", "scientific_name", "common_name", 
               "taxon_id", "sample_name", "description"
        FROM srameta.sra_master 
        WHERE "run_accession" IS NOT NULL 
        LIMIT 20
    """)
    
    print("\n=== Sample Data for Species Detection ===")
    
    table = Table(title="Species-Related Fields Sample")
    table.add_column("Run Accession", style="cyan", width=12)
    table.add_column("Scientific Name", style="green", width=15)
    table.add_column("Common Name", style="blue", width=12)
    table.add_column("Taxon ID", style="yellow", width=8)
    table.add_column("Sample Name", style="magenta", width=12)
    table.add_column("Title (first 30)", style="white", width=30)
    
    records = cursor.fetchall()
    for row in records:
        run_acc = row[0] or ""
        study_title = (row[1] or "")[:30] + "..." if row[1] and len(row[1]) > 30 else (row[1] or "")
        scientific_name = row[2] or ""
        common_name = row[3] or ""
        taxon_id = str(row[4]) if row[4] else ""
        sample_name = row[5] or ""
        
        table.add_row(
            run_acc,
            scientific_name,
            common_name,
            taxon_id,
            sample_name,
            study_title
        )
    
    console.print(table)
    
    # Check for human-related records specifically
    print("\n=== Checking for Human-Related Records ===")
    
    human_queries = [
        ("scientific_name ILIKE '%homo sapiens%'", "Scientific name contains 'homo sapiens'"),
        ("scientific_name ILIKE '%human%'", "Scientific name contains 'human'"),
        ("common_name ILIKE '%human%'", "Common name contains 'human'"),
        ("study_title ILIKE '%human%'", "Study title contains 'human'"),
        ("study_title ILIKE '%homo sapiens%'", "Study title contains 'homo sapiens'"),
        ("taxon_id = '9606'", "Taxon ID is 9606 (human)"),
        ("sample_name ILIKE '%human%'", "Sample name contains 'human'"),
        ("description ILIKE '%human%'", "Description contains 'human'")
    ]
    
    for query_condition, description in human_queries:
        cursor.execute(f"""
            SELECT COUNT(*) 
            FROM srameta.sra_master 
            WHERE {query_condition}
        """)
        count = cursor.fetchone()[0]
        print(f"  {description}: {count} records")
        
        if count > 0 and count <= 5:
            # Show some examples
            cursor.execute(f"""
                SELECT "run_accession", "study_title", "scientific_name", "common_name", "sample_name"
                FROM srameta.sra_master 
                WHERE {query_condition}
                LIMIT 3
            """)
            examples = cursor.fetchall()
            for ex in examples:
                print(f"    Example: {ex[0]} - {(ex[1] or '')[:50]}...")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    debug_species_fields() 
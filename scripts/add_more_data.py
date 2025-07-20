#!/usr/bin/env python3
"""
Add more sample data to simulate real-world scale.
"""

import sys
import os
from pathlib import Path
import random
from datetime import datetime, timedelta

# Add the scAgent package to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scAgent.db import get_connection
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_geo_data(num_records=100):
    """Generate more diverse GEO sample data."""
    
    organisms = ["Homo sapiens", "Mus musculus", "Rattus norvegicus", "Macaca mulatta"]
    platforms = ["Illumina HiSeq 2500", "Illumina HiSeq 4000", "Illumina NovaSeq 6000", "Illumina NextSeq 500"]
    tissues = ["brain", "heart", "liver", "kidney", "lung", "pancreas", "muscle", "skin", "blood", "bone marrow"]
    cell_types = ["neuron", "cardiomyocyte", "hepatocyte", "T cell", "B cell", "macrophage", "fibroblast", "endothelial cell"]
    
    # Single-cell related keywords
    sc_keywords = [
        "single-cell RNA-seq", "scRNA-seq", "single cell transcriptome", "sc-RNA", 
        "single-cell analysis", "cellular heterogeneity", "cell-type specific",
        "single cell sequencing", "droplet-based", "10x Genomics", "Smart-seq"
    ]
    
    data = []
    base_date = datetime(2020, 1, 1)
    
    for i in range(num_records):
        geo_id = f"GSE{100000 + i}"
        organism = random.choice(organisms)
        platform = random.choice(platforms)
        tissue = random.choice(tissues)
        cell_type = random.choice(cell_types)
        sc_keyword = random.choice(sc_keywords)
        
        # Generate submission date
        days_offset = random.randint(0, 1460)  # 4 years
        submission_date = base_date + timedelta(days=days_offset)
        update_date = submission_date + timedelta(days=random.randint(1, 30))
        
        # Generate sample count
        sample_count = random.randint(10, 200)
        
        # Create realistic titles and summaries
        title = f"{sc_keyword} analysis of {organism} {tissue} {cell_type}s"
        summary = f"This study presents {sc_keyword} data from {organism} {tissue} samples to investigate {cell_type} heterogeneity and gene expression patterns. We analyzed {sample_count} samples using {platform}."
        
        # Add some non-single-cell studies as controls
        if random.random() < 0.3:  # 30% non-single-cell
            title = f"Bulk RNA-seq analysis of {organism} {tissue}"
            summary = f"Bulk RNA sequencing analysis of {organism} {tissue} samples."
            sc_keyword = "bulk RNA-seq"
        
        data.append((
            geo_id,
            title,
            summary,
            organism,
            'Public',
            submission_date.strftime('%Y-%m-%d'),
            update_date.strftime('%Y-%m-%d'),
            platform,
            'Expression profiling by high throughput sequencing',
            sample_count,
            f"Researcher {i%10 + 1}",
            f"researcher{i%10 + 1}@university.edu"
        ))
    
    return data

def generate_sra_data(num_records=100):
    """Generate more diverse SRA sample data."""
    
    organisms = ["Homo sapiens", "Mus musculus", "Rattus norvegicus", "Macaca mulatta"]
    platforms = ["ILLUMINA"]
    instruments = ["Illumina HiSeq 2500", "Illumina HiSeq 4000", "Illumina NovaSeq 6000", "Illumina NextSeq 500"]
    library_strategies = ["RNA-Seq", "OTHER"]
    library_sources = ["TRANSCRIPTOMIC", "GENOMIC"]
    library_selections = ["RANDOM", "cDNA", "PCR"]
    tissues = ["brain", "heart", "liver", "kidney", "lung", "pancreas", "muscle", "skin", "blood", "bone marrow"]
    cell_types = ["neuron", "cardiomyocyte", "hepatocyte", "T cell", "B cell", "macrophage", "fibroblast", "endothelial cell"]
    
    data = []
    
    for i in range(num_records):
        run_id = f"SRR{10000000 + i}"
        sample_id = f"SRS{1000000 + i}"
        experiment_id = f"SRX{1000000 + i}"
        study_id = f"SRP{100000 + i}"
        
        organism = random.choice(organisms)
        instrument = random.choice(instruments)
        tissue = random.choice(tissues)
        cell_type = random.choice(cell_types)
        
        # Generate realistic sequencing stats
        spots = random.randint(1000000, 50000000)
        bases = spots * random.randint(50, 150)
        bytes_size = bases * random.randint(1, 3)
        
        # Create study titles and abstracts
        is_single_cell = random.random() > 0.3  # 70% single-cell
        if is_single_cell:
            study_title = f"Single-cell RNA-seq of {organism} {tissue}"
            study_abstract = f"Single-cell RNA sequencing analysis of {organism} {tissue} samples to study {cell_type} heterogeneity."
        else:
            study_title = f"Bulk RNA-seq of {organism} {tissue}"
            study_abstract = f"Bulk RNA sequencing analysis of {organism} {tissue} samples."
        
        data.append((
            run_id,
            sample_id,
            experiment_id,
            study_id,
            study_title,
            study_abstract,
            random.choice(platforms),
            instrument,
            random.choice(library_strategies),
            random.choice(library_sources),
            random.choice(library_selections),
            'SINGLE',
            spots,
            bases,
            bytes_size,
            organism,
            tissue,
            cell_type
        ))
    
    return data

def insert_batch_geo_data(conn, data):
    """Insert batch GEO data."""
    
    insert_sql = """
    INSERT INTO geo_master (
        geo_accession, title, summary, organism, status, submission_date, 
        last_update_date, platform, series_type, sample_count, contributor, contact_email
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (geo_accession) DO NOTHING;
    """
    
    with conn.cursor() as cur:
        cur.executemany(insert_sql, data)
        logger.info(f"Inserted {len(data)} records into geo_master")

def insert_batch_sra_data(conn, data):
    """Insert batch SRA data."""
    
    insert_sql = """
    INSERT INTO sra_master (
        run_accession, sample_accession, experiment_accession, study_accession,
        study_title, study_abstract, platform, instrument, library_strategy,
        library_source, library_selection, library_layout, spots, bases, bytes,
        organism, tissue, cell_type
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (run_accession) DO NOTHING;
    """
    
    with conn.cursor() as cur:
        cur.executemany(insert_sql, data)
        logger.info(f"Inserted {len(data)} records into sra_master")

def main():
    """Main function to add more sample data."""
    
    print("🚀 Adding more sample data to scAgent database...")
    
    try:
        # Connect to database
        conn = get_connection()
        print("✅ Connected to database")
        
        # Generate and insert GEO data
        print("📊 Generating GEO sample data...")
        geo_data = generate_geo_data(200)  # Generate 200 records
        insert_batch_geo_data(conn, geo_data)
        
        # Generate and insert SRA data
        print("📊 Generating SRA sample data...")
        sra_data = generate_sra_data(200)  # Generate 200 records
        insert_batch_sra_data(conn, sra_data)
        
        # Commit changes
        conn.commit()
        
        print("✅ Sample data addition complete!")
        
        # Show final counts
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM geo_master")
            geo_count = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM sra_master")
            sra_count = cur.fetchone()[0]
            
            print(f"\nFinal counts:")
            print(f"  - geo_master: {geo_count} records")
            print(f"  - sra_master: {sra_count} records")
            
            # Show single-cell data counts
            cur.execute("""
                SELECT COUNT(*) FROM geo_master 
                WHERE title ILIKE '%single%cell%' OR title ILIKE '%scRNA%'
            """)
            sc_geo_count = cur.fetchone()[0]
            
            cur.execute("""
                SELECT COUNT(*) FROM sra_master 
                WHERE study_title ILIKE '%single%cell%' OR study_title ILIKE '%scRNA%'
            """)
            sc_sra_count = cur.fetchone()[0]
            
            print(f"\nSingle-cell data:")
            print(f"  - geo_master: {sc_geo_count} sc-RNA records")
            print(f"  - sra_master: {sc_sra_count} sc-RNA records")
        
        conn.close()
        
    except Exception as e:
        logger.error(f"Data addition failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 
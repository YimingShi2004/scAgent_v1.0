#!/usr/bin/env python3
"""
Database initialization script for scAgent.
Creates sample tables and inserts demo data.
"""

import sys
import os
from pathlib import Path

# Add the scAgent package to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scAgent.db import get_connection
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_geo_master_table(conn):
    """Create geo_master table with sample structure."""
    
    create_sql = """
    CREATE TABLE IF NOT EXISTS geo_master (
        id SERIAL PRIMARY KEY,
        geo_accession VARCHAR(50) UNIQUE NOT NULL,
        title TEXT,
        summary TEXT,
        organism VARCHAR(100),
        status VARCHAR(20),
        submission_date DATE,
        last_update_date DATE,
        platform VARCHAR(100),
        series_type VARCHAR(50),
        sample_count INTEGER,
        contributor TEXT,
        contact_email VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    with conn.cursor() as cur:
        cur.execute(create_sql)
        logger.info("Created geo_master table")

def create_sra_master_table(conn):
    """Create sra_master table with sample structure."""
    
    create_sql = """
    CREATE TABLE IF NOT EXISTS sra_master (
        id SERIAL PRIMARY KEY,
        run_accession VARCHAR(50) UNIQUE NOT NULL,
        sample_accession VARCHAR(50),
        experiment_accession VARCHAR(50),
        study_accession VARCHAR(50),
        study_title TEXT,
        study_abstract TEXT,
        platform VARCHAR(100),
        instrument VARCHAR(100),
        library_strategy VARCHAR(50),
        library_source VARCHAR(50),
        library_selection VARCHAR(50),
        library_layout VARCHAR(20),
        spots BIGINT,
        bases BIGINT,
        bytes BIGINT,
        organism VARCHAR(100),
        tissue VARCHAR(100),
        cell_type VARCHAR(100),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    with conn.cursor() as cur:
        cur.execute(create_sql)
        logger.info("Created sra_master table")

def insert_sample_geo_data(conn):
    """Insert sample data into geo_master table."""
    
    sample_data = [
        (
            'GSE123456',
            'Single-cell RNA-seq analysis of human brain cortex',
            'This study presents single-cell RNA sequencing data from human brain cortex samples to investigate cellular heterogeneity and gene expression patterns.',
            'Homo sapiens',
            'Public',
            '2023-01-15',
            '2023-02-01',
            'Illumina HiSeq 2500',
            'Expression profiling by high throughput sequencing',
            50,
            'John Doe, Jane Smith',
            'john.doe@university.edu'
        ),
        (
            'GSE789012',
            'Single-cell transcriptomics of mouse heart development',
            'Comprehensive single-cell RNA-seq analysis of mouse heart development across multiple time points.',
            'Mus musculus',
            'Public',
            '2023-03-10',
            '2023-03-15',
            'Illumina NovaSeq 6000',
            'Expression profiling by high throughput sequencing',
            75,
            'Alice Johnson',
            'alice.johnson@research.org'
        ),
        (
            'GSE345678',
            'scRNA-seq of human pancreatic islets',
            'Single-cell RNA sequencing of human pancreatic islets to study beta cell heterogeneity.',
            'Homo sapiens',
            'Public',
            '2023-05-20',
            '2023-06-01',
            'Illumina HiSeq 4000',
            'Expression profiling by high throughput sequencing',
            30,
            'Bob Wilson',
            'bob.wilson@medical.edu'
        )
    ]
    
    insert_sql = """
    INSERT INTO geo_master (
        geo_accession, title, summary, organism, status, submission_date, 
        last_update_date, platform, series_type, sample_count, contributor, contact_email
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (geo_accession) DO NOTHING;
    """
    
    with conn.cursor() as cur:
        cur.executemany(insert_sql, sample_data)
        logger.info(f"Inserted {len(sample_data)} sample records into geo_master")

def insert_sample_sra_data(conn):
    """Insert sample data into sra_master table."""
    
    sample_data = [
        (
            'SRR12345678',
            'SRS1234567',
            'SRX1234567',
            'SRP123456',
            'Single-cell RNA-seq of human brain cortex',
            'Comprehensive single-cell analysis of human brain cortex samples',
            'ILLUMINA',
            'Illumina HiSeq 2500',
            'RNA-Seq',
            'TRANSCRIPTOMIC',
            'RANDOM',
            'SINGLE',
            5000000,
            750000000,
            400000000,
            'Homo sapiens',
            'brain',
            'neuron'
        ),
        (
            'SRR87654321',
            'SRS7654321',
            'SRX7654321',
            'SRP789012',
            'Single-cell transcriptomics of mouse heart',
            'Single-cell RNA-seq analysis of mouse heart development',
            'ILLUMINA',
            'Illumina NovaSeq 6000',
            'RNA-Seq',
            'TRANSCRIPTOMIC',
            'RANDOM',
            'SINGLE',
            8000000,
            1200000000,
            600000000,
            'Mus musculus',
            'heart',
            'cardiomyocyte'
        ),
        (
            'SRR11223344',
            'SRS1122334',
            'SRX1122334',
            'SRP345678',
            'scRNA-seq of human pancreatic islets',
            'Single-cell RNA sequencing of human pancreatic islets',
            'ILLUMINA',
            'Illumina HiSeq 4000',
            'RNA-Seq',
            'TRANSCRIPTOMIC',
            'RANDOM',
            'SINGLE',
            3000000,
            450000000,
            250000000,
            'Homo sapiens',
            'pancreas',
            'beta cell'
        )
    ]
    
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
        cur.executemany(insert_sql, sample_data)
        logger.info(f"Inserted {len(sample_data)} sample records into sra_master")

def main():
    """Main function to initialize the database."""
    
    print("🚀 Initializing scAgent database...")
    
    try:
        # Connect to database
        conn = get_connection()
        print("✅ Connected to database")
        
        # Create tables
        print("📊 Creating tables...")
        create_geo_master_table(conn)
        create_sra_master_table(conn)
        
        # Insert sample data
        print("📥 Inserting sample data...")
        insert_sample_geo_data(conn)
        insert_sample_sra_data(conn)
        
        # Commit changes
        conn.commit()
        
        print("✅ Database initialization complete!")
        print("\nCreated tables:")
        print("  - geo_master (3 sample records)")
        print("  - sra_master (3 sample records)")
        
        # Show table counts
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM geo_master")
            geo_count = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM sra_master")
            sra_count = cur.fetchone()[0]
            
            print(f"\nFinal counts:")
            print(f"  - geo_master: {geo_count} records")
            print(f"  - sra_master: {sra_count} records")
        
        conn.close()
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 
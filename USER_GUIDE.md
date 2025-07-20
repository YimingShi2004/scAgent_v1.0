# scAgent User Guide

## Overview

scAgent is an AI-powered tool for identifying and analyzing single-cell RNA-seq datasets suitable for sc-eQTL (single-cell expression quantitative trait loci) analysis. It provides comprehensive data quality assessment, automated dataset filtering, and intelligent analysis capabilities.

## Key Features

🔍 **AI-Powered Analysis**: Uses Qwen3-235B-A22B model for intelligent dataset evaluation  
🧬 **sc-eQTL Specialization**: Specialized scoring system for eQTL suitability  
📈 **Batch Quality Assessment**: Evaluate multiple datasets simultaneously  
🔬 **Batch Effect Detection**: Identify potential technical confounders  
📥 **Automated Downloads**: Generate SRA download scripts  
📋 **Comprehensive Reporting**: Detailed analysis reports with export capabilities  
🎯 **Multi-Organism Support**: Supports human, mouse, and other model organisms  
🔗 **Database Integration**: Direct PostgreSQL database connectivity  

## Installation

```bash
# Clone the repository
git clone https://github.com/yanglab/scAgent.git
cd scAgent

# Install dependencies
pip install -e .
```

## Configuration

The system is pre-configured to work with:
- **Database**: PostgreSQL at 10.28.1.24:5432 (yanglab/labyang)
- **AI Model**: Qwen3-235B-A22B at http://10.28.1.21:30080/v1
- **Tables**: geo_master (203 records), sra_master (203 records)

Configuration file: `scAgent/settings.yml`

## Quick Start

1. **Test System Connectivity**
   ```bash
   scagent test-connection
   ```

2. **Find sc-eQTL Suitable Datasets**
   ```bash
   scagent find-eqtl-data --organisms "Homo sapiens" --max-datasets 10 --output candidates.csv
   ```

3. **Perform Quality Assessment**
   ```bash
   scagent batch-assess --source both --organisms "Homo sapiens" --max-records 50
   ```

## Command Reference

### Core Analysis Commands

#### `test-connection`
Test database and model API connections.
```bash
scagent test-connection
```

#### `find-eqtl-data`
Find datasets suitable for sc-eQTL analysis with AI evaluation.
```bash
scagent find-eqtl-data --organisms "Homo sapiens" "Mus musculus" \
                       --tissues "brain" "heart" \
                       --max-datasets 50 \
                       --output eqtl_candidates.csv
```

**Options:**
- `--organisms`: Filter by organism names
- `--tissues`: Filter by tissue types
- `--max-datasets`: Maximum datasets to analyze
- `--output`: Output file (CSV format)
- `--format`: Output format (csv, json, excel)

#### `batch-assess`
Perform comprehensive batch quality assessment.
```bash
scagent batch-assess --source both \
                     --organisms "Homo sapiens" \
                     --max-records 100 \
                     --output assessment.json
```

**Options:**
- `--source`: Data source (geo, sra, both)
- `--organisms`: Filter by organism names
- `--tissues`: Filter by tissue types
- `--max-records`: Maximum records to assess
- `--output`: Output file (JSON format)

#### `comprehensive-report`
Generate detailed data quality report.
```bash
scagent comprehensive-report --organisms "Homo sapiens" \
                            --include-ai \
                            --output full_report.json
```

**Options:**
- `--organisms`: Filter by organism names
- `--tissues`: Filter by tissue types
- `--max-records`: Maximum datasets to analyze
- `--include-ai`: Include AI analysis (may take longer)
- `--output`: Output file (JSON format)

### Data Management Commands

#### `analyze-geo`
Analyze GEO master data with AI insights.
```bash
scagent analyze-geo --max-records 100 --output geo_analysis.csv
```

#### `analyze-sra`
Analyze SRA master data with AI insights.
```bash
scagent analyze-sra --max-records 100 --output sra_analysis.csv
```

#### `clean-data`
Clean and standardize table data.
```bash
scagent clean-data --table geo_master --output cleaned_data.csv
```

#### `generate-downloads`
Generate SRA download scripts.
```bash
scagent generate-downloads --organisms "Homo sapiens" \
                          --quality-filter \
                          --script-name download.sh \
                          --output-dir ./downloads
```

**Options:**
- `--organisms`: Filter by organism names
- `--tissues`: Filter by tissue types
- `--max-records`: Maximum datasets to include
- `--quality-filter`: Only include high-quality datasets
- `--output-dir`: Directory for downloaded files
- `--script-name`: Name of the download script

### Utility Commands

#### `analyze-schema`
Analyze database table schemas.
```bash
scagent analyze-schema --table geo_master
```

#### `help`
Show detailed help and usage examples.
```bash
scagent help
```

## Common Workflows

### 1. Quick Dataset Discovery
```bash
# Step 1: Test connectivity
scagent test-connection

# Step 2: Find candidate datasets
scagent find-eqtl-data --organisms "Homo sapiens" --max-datasets 10 --output candidates.csv

# Step 3: Assess quality
scagent batch-assess --source both --organisms "Homo sapiens" --max-records 50
```

### 2. Data Download Pipeline
```bash
# Step 1: Identify datasets
scagent find-eqtl-data --organisms "Homo sapiens" --output candidates.csv

# Step 2: Generate download script
scagent generate-downloads --organisms "Homo sapiens" --quality-filter --script-name download.sh

# Step 3: Execute downloads
chmod +x download.sh && ./download.sh
```

### 3. Comprehensive Analysis
```bash
# Step 1: Analyze GEO data
scagent analyze-geo --max-records 200 --output geo_analysis.csv

# Step 2: Analyze SRA data
scagent analyze-sra --max-records 200 --output sra_analysis.csv

# Step 3: Generate comprehensive report
scagent comprehensive-report --organisms "Homo sapiens" --include-ai --output full_report.json
```

## Understanding sc-eQTL Suitability Scoring

scAgent uses a specialized scoring system to evaluate datasets for sc-eQTL analysis:

### Grading System
- **A Grade (Excellent)**: Score ≥10, ready for sc-eQTL analysis
- **B Grade (Good)**: Score 7-9, minor issues but usable
- **C Grade (Marginal)**: Score 4-6, significant limitations
- **D Grade (Poor)**: Score <4, major problems

### Scoring Criteria
1. **Sample Size** (0-3 points)
   - ≥100 samples: 3 points
   - 50-99 samples: 2 points
   - 20-49 samples: 1 point
   - <20 samples: 0 points

2. **Organism** (0-2 points)
   - Model organisms (Human, Mouse): 2 points
   - Other known organisms: 1 point
   - Unknown: 0 points

3. **Single-cell Technology** (0-3 points)
   - Confirmed single-cell: 3 points
   - Not confirmed: 0 points

4. **Genotype Data Likelihood** (0-4 points)
   - High likelihood: 4 points
   - Medium likelihood: 2 points
   - Low likelihood: 0 points

5. **Platform** (0-1 points)
   - Standard Illumina platforms: 1 point
   - Other/unknown: 0 points

### Critical Requirements for sc-eQTL
- **Genotype Data**: Paired SNP/genotype data for each individual
- **Multi-individual Design**: ≥20 individuals for statistical power
- **Cell-level Expression**: Single-cell resolution transcriptome data
- **Individual Mapping**: Clear mapping between cells and donors

## Output Formats

### CSV Files
Standard tabular format with dataset information and quality scores.

### JSON Files
Structured format with detailed metadata:
```json
{
  "timestamp": "2025-01-18T21:00:00",
  "parameters": {...},
  "sections": {
    "database_status": {...},
    "quality_assessment": {...},
    "top_candidates": [...]
  }
}
```

### Download Scripts
Executable bash scripts for SRA data download:
```bash
#!/bin/bash
# Generated download script
prefetch SRR123456 -O ./downloads
fastq-dump --split-files --gzip ./downloads/SRR123456/SRR123456.sra
```

## Best Practices

### 1. Data Quality
- Always run `batch-assess` before proceeding with analysis
- Focus on datasets with Grade A or B ratings
- Verify genotype data availability separately

### 2. Batch Effects
- Check platform diversity in your dataset collection
- Consider temporal span of data collection
- Plan for batch effect correction in downstream analysis

### 3. Resource Management
- Use `--max-records` to limit analysis scope for large datasets
- Enable `--quality-filter` for download scripts to save storage
- Regular database connection testing in automated workflows

### 4. AI Analysis
- Include AI analysis for detailed insights but be aware of longer processing times
- AI analysis may timeout for very large datasets
- Use AI recommendations as guidance, not absolute truth

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check network connectivity to 10.28.1.24:5432
   - Verify credentials (yanglab/labyang)
   - Ensure PostgreSQL service is running

2. **AI Model Timeout**
   - Reduce dataset size with `--max-records`
   - Skip AI analysis for large batches
   - Check model API availability at 10.28.1.21:30080

3. **No Datasets Found**
   - Broaden organism/tissue filters
   - Check database content with `analyze-schema`
   - Verify table has data with `analyze-geo` or `analyze-sra`

4. **Import Errors**
   - Ensure proper installation: `pip install -e .`
   - Check Python environment activation
   - Verify all dependencies are installed

### Getting Help

```bash
# Show detailed help
scagent help

# Get command-specific help
scagent find-eqtl-data --help

# Test system status
scagent test-connection
```

## Advanced Usage

### Custom Filtering
```bash
# Multi-organism analysis
scagent find-eqtl-data --organisms "Homo sapiens" "Mus musculus" --output multi_species.csv

# Tissue-specific analysis
scagent batch-assess --tissues "brain" "heart" "liver" --output tissue_analysis.json

# High-throughput analysis
scagent comprehensive-report --max-records 1000 --include-ai --output large_analysis.json
```

### Automation Scripts
```bash
#!/bin/bash
# Automated analysis pipeline
echo "Starting scAgent analysis pipeline..."

# Test connectivity
scagent test-connection || exit 1

# Find candidates
scagent find-eqtl-data --organisms "Homo sapiens" --max-datasets 100 --output candidates.csv

# Quality assessment
scagent batch-assess --source both --organisms "Homo sapiens" --max-records 200 --output assessment.json

# Generate downloads
scagent generate-downloads --organisms "Homo sapiens" --quality-filter --script-name auto_download.sh

echo "Analysis pipeline completed!"
```

## Support

For issues, questions, or contributions:
- Check the troubleshooting section above
- Use `scagent help` for command reference
- Review log files for detailed error messages
- Contact the development team for database/model access issues 
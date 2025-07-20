# scAgent

AI agent for identifying and cleaning sc-RNA data suitable for sc-eQTL analysis.

## Overview

scAgent is a specialized tool designed to:
1. Connect to static databases containing sc-RNA data
2. Identify datasets suitable for sc-eQTL analysis
3. Clean and process table data from geo_master and sra_master tables
4. Provide intelligent data filtering and quality assessment

## Features

- **Database Integration**: Connect to PostgreSQL databases with geo_master and sra_master tables
- **Smart Data Filtering**: AI-powered identification of sc-eQTL suitable datasets
- **Data Cleaning**: Automated cleaning and standardization of table data
- **Quality Assessment**: Evaluate data quality for sc-eQTL analysis requirements

## Installation

```bash
# Clone the repository
git clone https://github.com/yanglab/scAgent.git
cd scAgent

# Install dependencies
pip install -e .
```

## Configuration

The system uses a local Qwen3-235B-A22B model and connects to a PostgreSQL database.

Database configuration:
- Host: 10.28.1.24
- Port: 5432
- User: yanglab
- Password: labyang
- Timeout: 30s

## Usage

```bash
# Analyze geo_master table
scagent analyze-geo --max-records 100

# Analyze sra_master table  
scagent analyze-sra --max-records 100

# Clean and filter data
scagent clean-data --table geo_master --output cleaned_geo.csv

# Find sc-eQTL suitable datasets
scagent find-eqtl-data --tissue brain --cell-type neuron
```

## Database Schema

The system works with two main tables:
- `geo_master`: Contains GEO dataset metadata
- `sra_master`: Contains SRA dataset metadata

## Model Configuration

Uses local Qwen3-235B-A22B model with:
- Temperature: 0.7
- Top-p: 0.8
- Top-k: 20
- Max tokens: 32000
- Presence penalty: 1.5 
#!/usr/bin/env python3
"""
Test script for scAgent functionality.
"""

import sys
import os
import logging
from pathlib import Path

# Add the scAgent package to the path
sys.path.insert(0, str(Path(__file__).parent))

from scAgent.db import test_connection, get_table_info
from scAgent.models import get_qwen_client
from scAgent.db.query import query_geo_master, query_sra_master

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_database_connection():
    """Test database connection."""
    print("=" * 50)
    print("Testing Database Connection")
    print("=" * 50)
    
    try:
        result = test_connection()
        
        if result["status"] == "success":
            print("✅ Database connection successful!")
            print(f"   Database: {result['database']}")
            print(f"   Host: {result['connection_params']['host']}")
            print(f"   Port: {result['connection_params']['port']}")
            print(f"   User: {result['connection_params']['user']}")
            print(f"   Tables found: {len(result['tables'])}")
            
            if result['tables']:
                print("   Available tables:")
                for table in result['tables']:
                    print(f"     - {table}")
            
            return True
        else:
            print("❌ Database connection failed!")
            print(f"   Error: {result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        return False

def test_model_connection():
    """Test model API connection."""
    print("\n" + "=" * 50)
    print("Testing Model API Connection")
    print("=" * 50)
    
    try:
        client = get_qwen_client()
        result = client.test_connection()
        
        if result["status"] == "success":
            print("✅ Model API connection successful!")
            print(f"   Model: {result['model']}")
            print(f"   API URL: {result['api_url']}")
            print(f"   Test response: {result['response']}")
            
            return True
        else:
            print("❌ Model API connection failed!")
            print(f"   Error: {result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ Model API connection test failed: {e}")
        return False

def test_table_analysis():
    """Test table schema analysis."""
    print("\n" + "=" * 50)
    print("Testing Table Analysis")
    print("=" * 50)
    
    try:
        # Test with both tables
        table_info = get_table_info(["geo_master", "sra_master"])
        
        for table_name, info in table_info.items():
            print(f"\n📊 Table: {table_name}")
            
            if "error" in info:
                print(f"   ❌ Error: {info['error']}")
                continue
            
            print(f"   ✅ Analysis successful!")
            print(f"   Rows: {info['row_count']:,}")
            print(f"   Columns: {info['column_count']}")
            print(f"   Size: {info['table_size']}")
            
            # Show first few columns
            if info['columns']:
                print("   First 5 columns:")
                for col in info['columns'][:5]:
                    print(f"     - {col['column_name']}: {col['data_type']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Table analysis test failed: {e}")
        return False

def test_data_queries():
    """Test data queries."""
    print("\n" + "=" * 50)
    print("Testing Data Queries")
    print("=" * 50)
    
    try:
        # Test geo_master query
        print("Testing geo_master query...")
        geo_results = query_geo_master(limit=5)
        print(f"✅ geo_master query successful! Retrieved {len(geo_results)} records")
        
        if geo_results:
            print("   Sample record columns:")
            for key in list(geo_results[0].keys())[:5]:
                print(f"     - {key}")
        
        # Test sra_master query
        print("\nTesting sra_master query...")
        sra_results = query_sra_master(limit=5)
        print(f"✅ sra_master query successful! Retrieved {len(sra_results)} records")
        
        if sra_results:
            print("   Sample record columns:")
            for key in list(sra_results[0].keys())[:5]:
                print(f"     - {key}")
        
        return True
        
    except Exception as e:
        print(f"❌ Data query test failed: {e}")
        return False

def test_ai_analysis():
    """Test AI analysis functionality."""
    print("\n" + "=" * 50)
    print("Testing AI Analysis")
    print("=" * 50)
    
    try:
        client = get_qwen_client()
        
        # Test simple analysis
        prompt = """Analyze this sample bioinformatics data for sc-eQTL suitability:

Sample data: A dataset contains single-cell RNA-seq data from human brain tissue with 10,000 cells and 20,000 genes. The data includes cell type annotations and individual donor information.

Please provide a brief assessment of its suitability for sc-eQTL analysis."""
        
        print("Sending analysis request to AI model...")
        response = client.generate(prompt, temperature=0.3, max_tokens=500)
        
        print("✅ AI analysis successful!")
        print(f"Response length: {len(response.content)} characters")
        print("\nAI Response:")
        print("-" * 40)
        print(response.content[:300] + "..." if len(response.content) > 300 else response.content)
        
        return True
        
    except Exception as e:
        print(f"❌ AI analysis test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Starting scAgent System Tests")
    print("=" * 60)
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Model API Connection", test_model_connection),
        ("Table Analysis", test_table_analysis),
        ("Data Queries", test_data_queries),
        ("AI Analysis", test_ai_analysis),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! scAgent is ready to use.")
        return 0
    else:
        print(f"\n⚠️  {len(results) - passed} tests failed. Please check the configuration.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 
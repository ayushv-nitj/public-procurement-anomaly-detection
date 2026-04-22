"""
Quick test script to verify all data sources work correctly.
Run this to test the multi-source data loading capability.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.data_loader import load_data

def test_csv():
    """Test CSV loading"""
    print("\n" + "="*60)
    print("TEST 1: Loading from CSV")
    print("="*60)
    try:
        df, report = load_data(source='csv', filepath='data/contracts.csv', validate=True)
        print(f"✓ Success! Loaded {len(df)} contracts")
        print(f"  Columns: {list(df.columns)}")
        if report:
            print(f"  Quality Score: {report['data_quality_score']:.2f}/100")
        print(f"  Sample row:\n{df.iloc[0].to_dict()}")
        return True
    except Exception as e:
        print(f"✗ Failed: {str(e)}")
        return False

def test_json():
    """Test JSON loading"""
    print("\n" + "="*60)
    print("TEST 2: Loading from JSON")
    print("="*60)
    try:
        df, report = load_data(source='json', filepath='data/sample_contracts.json', validate=True)
        print(f"✓ Success! Loaded {len(df)} contracts")
        print(f"  Columns: {list(df.columns)}")
        if report:
            print(f"  Quality Score: {report['data_quality_score']:.2f}/100")
        print(f"  Sample row:\n{df.iloc[0].to_dict()}")
        return True
    except Exception as e:
        print(f"✗ Failed: {str(e)}")
        return False

def test_xml():
    """Test XML loading"""
    print("\n" + "="*60)
    print("TEST 3: Loading from XML")
    print("="*60)
    try:
        df, report = load_data(source='xml', filepath='data/sample_contracts.xml', validate=True)
        print(f"✓ Success! Loaded {len(df)} contracts")
        print(f"  Columns: {list(df.columns)}")
        if report:
            print(f"  Quality Score: {report['data_quality_score']:.2f}/100")
        print(f"  Sample row:\n{df.iloc[0].to_dict()}")
        return True
    except Exception as e:
        print(f"✗ Failed: {str(e)}")
        return False

def test_synthetic():
    """Test synthetic data generation"""
    print("\n" + "="*60)
    print("TEST 4: Generating Synthetic Data")
    print("="*60)
    try:
        df, report = load_data(source='synthetic', validate=True)
        print(f"✓ Success! Generated {len(df)} contracts")
        print(f"  Columns: {list(df.columns)}")
        if report:
            print(f"  Quality Score: {report['data_quality_score']:.2f}/100")
        print(f"  Sample row:\n{df.iloc[0].to_dict()}")
        return True
    except Exception as e:
        print(f"✗ Failed: {str(e)}")
        return False

def test_api_mock():
    """Test API loading (mock example - will fail without real API)"""
    print("\n" + "="*60)
    print("TEST 5: API Loading (Mock Test)")
    print("="*60)
    print("⚠ API test requires:")
    print("  - Valid API URL")
    print("  - API key (if required)")
    print("  - Internet connectivity")
    print("\nExample command:")
    print('  python run_pipeline.py --source api \\')
    print('    --api-url "https://api.data.gov.in/resource/YOUR_ID" \\')
    print('    --api-key "YOUR_KEY" \\')
    print('    --format json --limit 100')
    print("\n⚠ Skipping actual API test (requires credentials)")
    return None

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("MULTI-SOURCE DATA LOADER - TEST SUITE")
    print("="*60)
    
    results = {
        'CSV': test_csv(),
        'JSON': test_json(),
        'XML': test_xml(),
        'Synthetic': test_synthetic(),
        'API': test_api_mock()
    }
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for source, result in results.items():
        if result is True:
            status = "✓ PASS"
        elif result is False:
            status = "✗ FAIL"
        else:
            status = "⚠ SKIP"
        print(f"{source:12} : {status}")
    
    passed = sum(1 for r in results.values() if r is True)
    failed = sum(1 for r in results.values() if r is False)
    skipped = sum(1 for r in results.values() if r is None)
    
    print(f"\nTotal: {passed} passed, {failed} failed, {skipped} skipped")
    
    if failed == 0:
        print("\n✓ All tests passed! The application can load data from multiple sources.")
    else:
        print("\n✗ Some tests failed. Check error messages above.")
    
    print("\nNext steps:")
    print("1. Run full pipeline: python run_pipeline.py --source csv")
    print("2. View results: cd frontend && python -m http.server 8080")
    print("3. See USAGE_GUIDE.md for more examples")

if __name__ == "__main__":
    main()

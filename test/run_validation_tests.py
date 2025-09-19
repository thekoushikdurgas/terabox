#!/usr/bin/env python3
"""
Test Runner for RapidAPI Key Validation

This script runs all validation tests and provides a summary report.
"""

import sys
import os
import unittest
from io import StringIO

# Add the parent directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def run_validation_tests():
    """Run all RapidAPI key validation tests"""
    print("🧪 Running RapidAPI Key Validation Tests")
    print("=" * 50)
    
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(__file__)
    suite = loader.discover(start_dir, pattern='test_rapidapi_key_validation.py')
    
    # Run tests with detailed output
    stream = StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=2)
    result = runner.run(suite)
    
    # Print results
    print(stream.getvalue())
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"✅ Tests Run: {result.testsRun}")
    print(f"❌ Failures: {len(result.failures)}")
    print(f"⚠️  Errors: {len(result.errors)}")
    print(f"⏭️  Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    if result.failures:
        print("\n❌ Failed Tests:")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print("\n⚠️ Error Tests:")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    # Return success status
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\n🎯 Overall Result: {'PASS' if success else 'FAIL'}")
    
    return success

def validate_sample_keys():
    """Validate some sample API keys for demonstration"""
    print("\n🔍 Sample Key Validation Demo")
    print("-" * 30)
    
    try:
        from utils.terabox_rapidapi import TeraBoxRapidAPI
        
        client = TeraBoxRapidAPI()
        
        sample_keys = {
            "Valid Format": "298bbd7e09msh8c672d04ba26de4p154bc9jsn9de6459d8a13",
            "Too Short": "298bbd7e09msh8c672d04ba26de4p154bc9jsn9de6",
            "Missing 'msh'": "298bbd7e09xxx8c672d04ba26de4p154bc9jsn9de6459d8a13",
            "Invalid Chars": "298bbd7e09msh8c672d04ba26de4p154bc9jsn9de6459d8a1@"
        }
        
        for key_type, key_value in sample_keys.items():
            result = client.quick_validate_api_key_format(key_value)
            status_emoji = "✅" if result['status'] == 'success' else "❌"
            print(f"{status_emoji} {key_type}: {result['message']}")
            
    except ImportError as e:
        print(f"❌ Could not import TeraBoxRapidAPI: {e}")
        print("Make sure you're running from the correct directory")

if __name__ == "__main__":
    print("🚀 RapidAPI Key Validation Test Suite")
    print("====================================\n")
    
    # Run validation tests
    success = run_validation_tests()
    
    # Run sample validation demo
    validate_sample_keys()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

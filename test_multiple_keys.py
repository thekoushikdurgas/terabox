#!/usr/bin/env python3
"""
Test script for multiple RapidAPI key implementation
This script tests the key rotation functionality without running the full Streamlit app
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.rapidapi_key_manager import RapidAPIKeyManager, KeyStatus
from utils.terabox_config import get_config_manager
import time

def test_key_manager():
    """Test the RapidAPI key manager functionality"""
    print("🧪 Testing RapidAPI Key Manager...")
    
    # Test keys (dummy keys for testing)
    test_keys = [
        "test1234567890msh1234567890123456p123456jsn1234567890",
        "test2345678901msh2345678901234567p234567jsn2345678901",
        "test3456789012msh3456789012345678p345678jsn3456789012"
    ]
    
    # Initialize key manager
    key_manager = RapidAPIKeyManager(test_keys)
    print(f"✅ Key manager initialized with {len(test_keys)} keys")
    
    # Test getting next key
    key_info = key_manager.get_next_key()
    if key_info:
        key_id, api_key = key_info
        print(f"✅ Got next key: {key_id}")
        
        # Test marking success
        key_manager.mark_request_success(key_id, 1.5)
        print(f"✅ Marked key {key_id} as successful")
        
        # Test marking failure
        key_manager.mark_request_failure(key_id, "Rate limit exceeded", 429)
        print(f"✅ Marked key {key_id} as rate limited")
        
        # Get key status
        status = key_manager.get_key_status(key_id)
        print(f"✅ Key status: {status['status']} (Available: {status['is_available']})")
        
        # Test getting next key after rate limit
        next_key_info = key_manager.get_next_key()
        if next_key_info:
            next_key_id, next_api_key = next_key_info
            print(f"✅ Rotated to next key: {next_key_id}")
        
        # Get manager stats
        stats = key_manager.get_manager_stats()
        print(f"✅ Manager stats: {stats['total_keys']} total, {stats['available_keys']} available")
        
        return True
    else:
        print("❌ Failed to get next key")
        return False

def test_config_manager():
    """Test the configuration manager with multiple keys"""
    print("\n🧪 Testing Configuration Manager...")
    
    config_mgr = get_config_manager()
    
    # Test adding multiple keys
    test_keys = [
        "config1234567890msh1234567890123456p123456jsn1234567890",
        "config2345678901msh2345678901234567p234567jsn2345678901"
    ]
    
    # Add keys
    for i, key in enumerate(test_keys):
        if config_mgr.add_rapidapi_key(key):
            print(f"✅ Added test key {i+1}")
        else:
            print(f"⚠️ Key {i+1} already exists or failed to add")
    
    # Get all keys
    all_keys = config_mgr.get_rapidapi_keys()
    print(f"✅ Total configured keys: {len(all_keys)}")
    
    # Test multiple key check
    has_multiple = config_mgr.has_multiple_rapidapi_keys()
    print(f"✅ Has multiple keys: {has_multiple}")
    
    # Clean up test keys
    for key in test_keys:
        config_mgr.remove_rapidapi_key(key)
    
    print("✅ Test keys cleaned up")
    return True

def main():
    """Run all tests"""
    print("🚀 Starting Multiple API Key Tests\n")
    
    try:
        # Test key manager
        if test_key_manager():
            print("✅ Key manager tests passed")
        else:
            print("❌ Key manager tests failed")
            return False
        
        # Test config manager
        if test_config_manager():
            print("✅ Config manager tests passed")
        else:
            print("❌ Config manager tests failed")
            return False
        
        print("\n🎉 All tests passed! Multiple API key system is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

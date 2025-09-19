#!/usr/bin/env python3
"""
Test script to verify that the download path configuration is working correctly.
"""

import os
import sys

# Add the current directory to the Python path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_config_download_path():
    """Test that the config module provides the correct default download path"""
    try:
        from config import get_default_download_path, config
        
        print("✅ Testing config.py download path configuration...")
        print(f"   DEFAULT_DOWNLOAD_DIR: {config.DEFAULT_DOWNLOAD_DIR}")
        
        download_path = get_default_download_path()
        print(f"   get_default_download_path(): {download_path}")
        
        # Check that the directory exists
        if os.path.exists(download_path):
            print(f"   ✅ Directory exists: {download_path}")
        else:
            print(f"   ❌ Directory does not exist: {download_path}")
            return False
            
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_terabox_config_download_path():
    """Test that the terabox_config module provides the correct default download path"""
    try:
        from terabox_config import get_config_manager
        
        print("✅ Testing terabox_config.py download path configuration...")
        config_manager = get_config_manager()
        
        print(f"   default_download_dir: {config_manager.app_config.default_download_dir}")
        
        download_path = config_manager.get_default_download_path()
        print(f"   get_default_download_path(): {download_path}")
        
        # Check that the directory exists
        if os.path.exists(download_path):
            print(f"   ✅ Directory exists: {download_path}")
        else:
            print(f"   ❌ Directory does not exist: {download_path}")
            return False
            
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_core_modules():
    """Test that core modules can import the download path function"""
    try:
        print("✅ Testing core modules import...")
        
        # Test terabox_cookie_api
        try:
            from terabox_cookie_api import TeraBoxCookieAPI
            print("   ✅ terabox_cookie_api imports successfully")
        except Exception as e:
            print(f"   ❌ terabox_cookie_api import failed: {e}")
            return False
        
        # Test terabox_rapidapi
        try:
            from terabox_rapidapi import TeraBoxRapidAPI
            print("   ✅ terabox_rapidapi imports successfully")
        except Exception as e:
            print(f"   ❌ terabox_rapidapi import failed: {e}")
            return False
            
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing TeraDL Download Path Configuration")
    print("=" * 50)
    
    tests = [
        test_config_download_path,
        test_terabox_config_download_path,
        test_core_modules
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Download path configuration is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the configuration.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

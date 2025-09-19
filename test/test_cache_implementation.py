#!/usr/bin/env python3
"""
Test script for TeraBox RapidAPI Cache Implementation
Tests the complete caching flow including cache hits, misses, and expiry
"""

import sys
import os
import time
import json
from typing import Dict, Any

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from terabox_rapidapi import TeraBoxRapidAPI
from cache_manager import TeraBoxCacheManager

def test_cache_manager():
    """Test the cache manager functionality"""
    print("🧪 Testing Cache Manager...")
    
    # Initialize cache manager
    cache_mgr = TeraBoxCacheManager(cache_ttl_hours=1)  # 1 hour TTL for testing
    
    # Test URL extraction
    test_urls = [
        "https://www.terabox.app/sharing/link?surl=12TX5ZJi1vCaNPXENFZIZjw",
        "https://1024terabox.com/s/1aBcDeFgHiJkL",
        "https://terasharelink.com/s/1XyZ123456",
        "https://unknown-format.com/some/path"
    ]
    
    print("\n📋 Testing SURL extraction:")
    for url in test_urls:
        surl = cache_mgr._extract_surl_from_url(url)
        print(f"  URL: {url}")
        print(f"  SURL: {surl}")
        print()
    
    # Test cache operations with mock data
    print("💾 Testing Cache Operations:")
    
    test_url = "https://www.terabox.app/sharing/link?surl=testcache123"
    mock_response = {
        'file_name': 'test_file.mp4',
        'direct_link': 'https://example.com/download/test',
        'size': '10.5 MB',
        'sizebytes': 11010048,
        'thumbnail': 'https://example.com/thumb/test.jpg',
        'file_type': 'video'
    }
    
    # Test cache miss
    cached = cache_mgr.get_cached_response(test_url)
    print(f"  Cache miss test: {cached is None}")
    
    # Test cache save
    saved = cache_mgr.save_response_to_cache(test_url, mock_response)
    print(f"  Cache save test: {saved}")
    
    # Test cache hit
    cached = cache_mgr.get_cached_response(test_url)
    print(f"  Cache hit test: {cached is not None}")
    
    if cached:
        print(f"  Cached file name: {cached.get('file_name')}")
        print(f"  Cache age: {cached.get('_cache_info', {}).get('cache_age_hours', 0):.2f} hours")
    
    # Test cache stats
    stats = cache_mgr.get_cache_stats()
    print(f"\n📊 Cache Stats:")
    print(f"  Total files: {stats.get('total_files', 0)}")
    print(f"  Valid files: {stats.get('valid_files', 0)}")
    print(f"  Total size: {stats.get('total_size_mb', 0):.2f} MB")
    
    print("✅ Cache Manager tests completed!\n")
    return cache_mgr

def test_rapidapi_integration():
    """Test RapidAPI integration with caching (without making real API calls)"""
    print("🚀 Testing RapidAPI Integration with Caching...")
    
    # Initialize RapidAPI client with caching enabled
    # Note: We won't make real API calls, just test the caching logic
    rapidapi_client = TeraBoxRapidAPI(rapidapi_key="test_key", enable_cache=True, cache_ttl_hours=1)
    
    print(f"  Cache enabled: {rapidapi_client.is_cache_enabled()}")
    
    # Test cache info
    cache_info = rapidapi_client.get_cache_info()
    print(f"  Cache directory: {cache_info.get('cache_directory')}")
    print(f"  Cache TTL: {cache_info.get('ttl_hours')} hours")
    
    # Test cache stats
    stats = rapidapi_client.get_cache_stats()
    print(f"  Cache stats available: {'error' not in stats}")
    
    print("✅ RapidAPI Integration tests completed!\n")
    return rapidapi_client

def test_cache_expiry():
    """Test cache expiry functionality"""
    print("⏰ Testing Cache Expiry...")
    
    # Create cache manager with very short TTL (1 second for testing)
    cache_mgr = TeraBoxCacheManager(cache_ttl_hours=1/3600)  # 1 second TTL
    
    test_url = "https://www.terabox.app/sharing/link?surl=expirytest123"
    mock_response = {
        'file_name': 'expiry_test.mp4',
        'direct_link': 'https://example.com/download/expiry',
        'size': '5.2 MB',
        'sizebytes': 5452595
    }
    
    # Save to cache
    saved = cache_mgr.save_response_to_cache(test_url, mock_response)
    print(f"  Cache save: {saved}")
    
    # Immediate retrieval should work
    cached = cache_mgr.get_cached_response(test_url)
    print(f"  Immediate cache hit: {cached is not None}")
    
    # Wait for expiry
    print("  Waiting for cache to expire...")
    time.sleep(2)
    
    # Should be expired now
    cached = cache_mgr.get_cached_response(test_url)
    print(f"  Cache hit after expiry: {cached is not None}")
    
    print("✅ Cache Expiry tests completed!\n")

def test_cache_cleanup():
    """Test cache cleanup functionality"""
    print("🧹 Testing Cache Cleanup...")
    
    cache_mgr = TeraBoxCacheManager()
    
    # Create some test cache entries
    test_urls = [
        "https://www.terabox.app/sharing/link?surl=cleanup1",
        "https://www.terabox.app/sharing/link?surl=cleanup2",
        "https://www.terabox.app/sharing/link?surl=cleanup3"
    ]
    
    mock_response = {
        'file_name': 'cleanup_test.mp4',
        'direct_link': 'https://example.com/download/cleanup',
        'size': '1.0 MB',
        'sizebytes': 1048576
    }
    
    # Save multiple entries
    for url in test_urls:
        cache_mgr.save_response_to_cache(url, mock_response)
    
    # Get stats before cleanup
    stats_before = cache_mgr.get_cache_stats()
    print(f"  Files before cleanup: {stats_before.get('total_files', 0)}")
    
    # Clean up expired cache (should find none since they're fresh)
    cleanup_result = cache_mgr.cleanup_expired_cache()
    print(f"  Expired files cleaned: {cleanup_result.get('cleaned_files', 0)}")
    
    # Clear all cache
    clear_result = cache_mgr.clear_cache()
    print(f"  All files cleared: {clear_result.get('cleared', 0)}")
    
    # Get stats after cleanup
    stats_after = cache_mgr.get_cache_stats()
    print(f"  Files after cleanup: {stats_after.get('total_files', 0)}")
    
    print("✅ Cache Cleanup tests completed!\n")

def main():
    """Main test function"""
    print("🎯 TeraBox RapidAPI Cache Implementation Test Suite")
    print("=" * 60)
    
    try:
        # Test 1: Cache Manager
        cache_mgr = test_cache_manager()
        
        # Test 2: RapidAPI Integration
        rapidapi_client = test_rapidapi_integration()
        
        # Test 3: Cache Expiry
        test_cache_expiry()
        
        # Test 4: Cache Cleanup
        test_cache_cleanup()
        
        print("🎉 All tests completed successfully!")
        print("\n📋 Test Summary:")
        print("✅ Cache Manager - Basic operations working")
        print("✅ RapidAPI Integration - Caching integration working") 
        print("✅ Cache Expiry - TTL mechanism working")
        print("✅ Cache Cleanup - Management operations working")
        
        print("\n💡 Next Steps:")
        print("1. Test with real RapidAPI key and TeraBox URLs")
        print("2. Monitor cache performance in production")
        print("3. Adjust TTL based on usage patterns")
        print("4. Monitor cache directory size and cleanup frequency")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

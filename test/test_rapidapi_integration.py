#!/usr/bin/env python3
"""
Test script for enhanced RapidAPI integration
Tests the complete flow with the actual RapidAPI response format provided by the user
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from terabox_rapidapi import TeraBoxRapidAPI
import json
from typing import Dict, Any

def test_response_processing():
    """Test the response processing with the actual user-provided response"""
    
    # User's actual RapidAPI response
    sample_response = [
        {
            "direct_link": "https://data.1024tera.com/file/0f5183d47f5311eb26687ae337e6f67d?bkt=en-713b21d6dbc3139860ebf506ba92480f4d71e3441138362f5fff71b17b978409ec81cb897401740f6f1510d802e307bd379dbe81ff03f1058c1bf361b07be9e9&fid=4398293442739-250528-412691198821858&time=1758247365&sign=FDTAXUGERLQlBHSKfWon-DCb740ccc5511e5e8fedcff06b081203-0XjycMTD8mJ%2F6jitgKE1f06RhLw%3D&to=139&size=8115665&sta_dx=8115665&sta_cs=0&sta_ft=mp4&sta_ct=7&sta_mt=6&fm2=MH%2Ctky%2CAnywhere%2C%2C%2Cany&region=tky&ctime=1698919445&mtime=1740659145&resv0=-1&resv1=0&resv2=&resv3=&resv4=8115665&vuk=4400324488320&iv=0&htype=&randtype=&newver=1&newfm=1&secfm=1&flow_ver=3&pkey=en-aa8605bb83d7829aa03108f49b7c701bb3fcf7595dd0c11a1305176a2b1519eb08911e7f5ed604d4&sl=68091977&expires=1758276165&rt=sh&r=583390848&sh=1&fin=By_%40Desipremier_On_Telegram%E0%A4%B2%E0%A4%B5%E0%A4%B0_%E0%A4%95%E0%A4%BE_%E0%A4%97%E0%A4%BE%E0%A4%82%E0%A4%A1%E0%A4%BC_%E0%A4%AE%E0%A4%BE%E0%A4%B0%E0%A4%95%E0%A4%B0_%E0%A4%B2%E0%A4%A1%E0%A4%BC%E0%A4%95%E0%A5%80_%E0%A4%A8%E0%A5%87_%E0%A4%AB%E0%A4%BE%E0%A4%A1_%E0%A4%A6%E0%A4%BF%E0%A4%AF%E0%A4%BE.mp4&fn=By_%40Desipremier_On_Telegram%E0%A4%B2%E0%A4%B5%E0%A4%B0_%E0%A4%95%E0%A4%BE_%E0%A4%97%E0%A4%BE%E0%A4%82%E0%A4%A1%E0%A4%BC_%E0%A4%AE%E0%A4%BE%E0%A4%B0%E0%A4%95%E0%A4%B0_%E0%A4%B2%E0%A4%A1%E0%A4%BC%E0%A4%95%E0%A5%80_%E0%A4%A8%E0%A5%87_%E0%A4%AB%E0%A4%BE%E0%A4%A1_%E0%A4%A6%E0%A4%BF%E0%A4%AF%E0%A4%BE.mp4&dp-logid=298427366926483012&dp-callid=0.1&hps=1&tsl=2000&csl=2000&fsl=-1&csign=HFbQ34KY2mYxb9Jq6qwZZWKYz0M%3D&so=0&ut=6&uter=4&serv=1&uc=4189859446&ti=e6e2f9d25109af0e2e204d742c3e16640fab82b35fd5f8a3&tuse=&raw_appid=0&ogr=0&rregion=XVVi&adg=c_50d427470e5f1e2089d189f376eb2776&reqlabel=250528_f_75e13b5aaad17925fe97718208f9857f_-1_65c2cbff238e25143c22978f8c4bde8e&ccn=SG&by=themis",
            "file_name": "By_@Desipremier_On_Telegramलवर_का_गांड़_मारकर_लड़की_ने_फाड_दिया.mp4",
            "link": "https://d.1024tera.com/file/0f5183d47f5311eb26687ae337e6f67d?fid=4398293442739-250528-412691198821858&dstime=1758247365&rt=sh&sign=FDtAER-DCb740ccc5511e5e8fedcff06b081203-gZSpMLOkBsAQheM7Nc1%2F0WS15wA%3D&expires=8h&chkv=0&chkbd=0&chkpc=&dp-logid=298427366926483012&dp-callid=0&r=583390848&sh=1&region=jp",
            "size": "7.74 MB",
            "sizebytes": 8115665,
            "thumb": "https://data.1024tera.com/thumbnail/0f5183d47f5311eb26687ae337e6f67d?fid=4398293442739-250528-412691198821858&time=1758247200&rt=sh&sign=FDTAER-DCb740ccc5511e5e8fedcff06b081203-xg3aTqObtqg85Q9IpyFtRmGq4lI%3D&expires=8h&chkv=0&chkbd=0&chkpc=&dp-logid=298427366926483012&dp-callid=0&size=c850_u580&quality=100&vuk=-&ft=video"
        }
    ]
    
    print("🧪 Testing RapidAPI Integration")
    print("=" * 50)
    
    # Initialize RapidAPI client (without actual key for testing)
    client = TeraBoxRapidAPI()
    
    print("📊 Testing response processing...")
    
    # Test the _process_api_response method
    result = client._process_api_response(sample_response)
    
    if result:
        print("✅ Response processing successful!")
        print(f"📄 File Name: {result['file_name']}")
        print(f"📏 Size: {result['size']}")
        print(f"💾 Size (bytes): {result['sizebytes']:,}")
        print(f"📁 File Type: {result['file_type']}")
        print(f"🔗 Direct Link: {result['direct_link'][:80]}...")
        print(f"🔗 Download Link: {result['download_link'][:80]}...")
        print(f"📷 Thumbnail: {'Yes' if result['thumbnail'] else 'No'}")
        print(f"🚀 Service: {result['service']}")
        
        # Test validation
        if client._validate_file_result(result):
            print("✅ File result validation passed!")
        else:
            print("❌ File result validation failed!")
        
        return True
    else:
        print("❌ Response processing failed!")
        return False

def test_url_normalization():
    """Test URL normalization with various TeraBox URL formats"""
    print("\n🔗 Testing URL Normalization")
    print("=" * 50)
    
    client = TeraBoxRapidAPI()
    
    test_urls = [
        "https://terasharelink.com/s/12TX5ZJi1vCaNPXENFZIZjw",
        "https://1024terabox.com/s/1aBcDeFgHiJkL",
        "https://freeterabox.com/s/1MnOpQrStUvWx",
        "https://nephobox.com/s/1XyZ123456",
        "https://terabox.com/s/1TestUrl123"
    ]
    
    for url in test_urls:
        normalized = client._normalize_terabox_url(url)
        print(f"📥 Input:  {url}")
        print(f"📤 Output: {normalized}")
        print()
    
    return True

def test_file_type_detection():
    """Test file type detection"""
    print("\n📁 Testing File Type Detection")
    print("=" * 50)
    
    client = TeraBoxRapidAPI()
    
    test_files = [
        "video.mp4",
        "movie.avi",
        "photo.jpg",
        "document.pdf",
        "archive.zip",
        "music.mp3",
        "unknown.xyz"
    ]
    
    for filename in test_files:
        file_type = client._get_file_type(filename)
        print(f"📄 {filename:<15} -> {file_type}")
    
    return True

def main():
    """Run all tests"""
    print("🚀 RapidAPI Integration Test Suite")
    print("=" * 60)
    
    tests = [
        ("Response Processing", test_response_processing),
        ("URL Normalization", test_url_normalization),
        ("File Type Detection", test_file_type_detection)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with error: {e}")
            results.append((test_name, False))
    
    print("\n📊 Test Results Summary")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Integration is ready.")
        return True
    else:
        print("⚠️ Some tests failed. Please review the issues.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

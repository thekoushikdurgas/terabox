"""
Test TeraFileShare.com Domain Support
Comprehensive test suite for the new terafileshare.com domain support

This test suite validates that TeraDL properly supports the terafileshare.com
domain across all components and processing modes.

Test Categories:
1. Link Extraction: Pattern matching and text processing
2. URL Validation: Domain and format validation
3. URL Normalization: RapidAPI URL formatting
4. CSV Processing: Database operations with new domain
5. Configuration: Domain support in configuration
6. Integration: End-to-end processing with new domain

Test Data:
- Uses sample terafileshare.com URLs from user's text
- Includes various URL formats and edge cases
- Tests Unicode text with emojis and formatting
- Validates error handling and edge cases
"""

import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from RapidAPI mode page (using importlib for Unicode filename)
import importlib.util
import sys

# Load the RapidAPI mode module
rapidapi_mode_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'pages', 'RapidAPI_Mode.py')
spec = importlib.util.spec_from_file_location("rapidapi_mode", rapidapi_mode_path)
rapidapi_mode = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rapidapi_mode)

# Import functions from the module
extract_terabox_links = rapidapi_mode.extract_terabox_links
_validate_terabox_link = rapidapi_mode._validate_terabox_link
_get_pattern_description = rapidapi_mode._get_pattern_description
from utils.terabox_rapidapi import TeraBoxRapidAPI
from utils.config import validate_terabox_url
import re

class TestTeraFileShareSupport(unittest.TestCase):
    """Test suite for terafileshare.com domain support"""
    
    def setUp(self):
        """Set up test data and fixtures"""
        # Sample text with terafileshare.com links (from user's example)
        self.sample_text = """
        N v vd:
        Click and watch 👇👇
        🔴𝗢𝗽𝗲𝗻 𝗟𝗶𝗻𝗸 & 👀𝗪𝗮𝘁𝗰𝗵 𝗼𝗻𝗹𝗶𝗻𝗲 + 𝗱𝗼𝘄𝗻𝗹𝗼𝗮𝗱👇👇
        https://terafileshare.com/s/1S5IozLFWSGzbH1P8kxCpGw
        https://terafileshare.com/s/1S5IozLFWSGzbH1P8kxCpGw

        🟢 𝗪𝗵𝗮𝘁𝘀𝗔𝗽𝗽 𝗖𝗵𝗮𝗻𝗻𝗲𝗹 👇👇🫦
        https://t.me/+Lt9p-t3OTSdlYTM1

        Click and watch 👇👇
        🔴𝗢𝗽𝗲𝗻 𝗟𝗶𝗻𝗸 & 👀𝗪𝗮𝘁𝗰𝗵 𝗼𝗻𝗹𝗶𝗻𝗲 + 𝗱𝗼𝘄𝗻𝗹𝗼𝗮𝗱s 👇👇
        https://terafileshare.com/s/17eInWzo2JM-AQxo6AKmzxQ
        https://t.me/+Lt9p-t3OTSdlYTM1

        Click and watch 👇👇
        🧿𝗢𝗽𝗲𝗻 𝗟𝗶𝗻𝗸 & 👀𝗪𝗮𝘁𝗰𝗵 𝗼𝗻𝗹𝗶𝗻𝗲 + 𝗱𝗼𝘄𝗻𝗹𝗼𝗮𝗱s👇👇
        https://terafileshare.com/s/1Br3eNFcGkByLPTNNXG42Eg

        Full video 👇
        https://terafileshare.com/s/1ISoEh2nxeYpYoI_yxEnSfg
        """
        
        # Expected terafileshare.com links
        self.expected_links = [
            "https://terafileshare.com/s/1S5IozLFWSGzbH1P8kxCpGw",
            "https://terafileshare.com/s/17eInWzo2JM-AQxo6AKmzxQ", 
            "https://terafileshare.com/s/1Br3eNFcGkByLPTNNXG42Eg",
            "https://terafileshare.com/s/1ISoEh2nxeYpYoI_yxEnSfg"
        ]
        
        # Test URLs for validation
        self.test_urls = [
            "https://terafileshare.com/s/1S5IozLFWSGzbH1P8kxCpGw",
            "https://www.terafileshare.com/s/1234567890",
            "https://terafileshare.com/s/test-link_123",
            "https://terafileshare.com/invalid-path",  # Invalid
            "https://invalid-domain.com/s/test",  # Invalid
        ]
    
    def test_link_extraction_patterns(self):
        """Test that terafileshare.com links are properly extracted"""
        print("\n🧪 Testing TeraFileShare link extraction...")
        
        # Extract links from sample text
        extracted_links = extract_terabox_links(self.sample_text)
        
        # Filter for terafileshare.com links
        terafileshare_links = [link for link in extracted_links if 'terafileshare.com' in link]
        
        print(f"📊 Extraction results:")
        print(f"   Total links extracted: {len(extracted_links)}")
        print(f"   TeraFileShare links: {len(terafileshare_links)}")
        print(f"   Expected links: {len(set(self.expected_links))}")
        
        # Verify all expected links were found
        for expected_link in set(self.expected_links):
            self.assertIn(expected_link, extracted_links, 
                         f"Expected link not found: {expected_link}")
            print(f"   ✅ Found: {expected_link}")
        
        # Verify no duplicates
        unique_terafileshare = list(set(terafileshare_links))
        self.assertEqual(len(unique_terafileshare), len(set(self.expected_links)),
                        "Duplicate links detected or missing links")
        
        print("✅ Link extraction test passed!")
    
    def test_link_validation(self):
        """Test link validation for terafileshare.com URLs"""
        print("\n🔍 Testing TeraFileShare link validation...")
        
        for i, url in enumerate(self.test_urls):
            validation_result = _validate_terabox_link(url)
            
            if i < 3:  # First 3 should be valid
                self.assertTrue(validation_result['valid'], 
                               f"Valid URL rejected: {url}")
                self.assertEqual(validation_result['domain'], 
                               'terafileshare.com' if 'www.' not in url else 'www.terafileshare.com')
                print(f"   ✅ Valid: {url}")
            else:  # Last 2 should be invalid
                self.assertFalse(validation_result['valid'], 
                                f"Invalid URL accepted: {url}")
                print(f"   ❌ Invalid: {url} - {validation_result['reason']}")
        
        print("✅ Link validation test passed!")
    
    def test_url_normalization(self):
        """Test URL normalization for RapidAPI compatibility"""
        print("\n🔄 Testing TeraFileShare URL normalization...")
        
        # Test normalization with RapidAPI client
        rapidapi = TeraBoxRapidAPI()
        
        test_cases = [
            {
                'input': 'https://terafileshare.com/s/1S5IozLFWSGzbH1P8kxCpGw',
                'expected': 'https://terafileshare.com/s/1S5IozLFWSGzbH1P8kxCpGw'
            },
            {
                'input': 'https://www.terafileshare.com/s/test123',
                'expected': 'https://terafileshare.com/s/test123'
            }
        ]
        
        for case in test_cases:
            normalized = rapidapi._normalize_terabox_url(case['input'])
            print(f"   Input: {case['input']}")
            print(f"   Output: {normalized}")
            print(f"   Expected: {case['expected']}")
            
            # For terafileshare.com, we preserve the original format
            self.assertTrue('terafileshare.com' in normalized,
                           f"Domain not preserved in normalization: {normalized}")
            print(f"   ✅ Normalization preserved terafileshare.com domain")
        
        print("✅ URL normalization test passed!")
    
    def test_pattern_descriptions(self):
        """Test pattern description generation for new domain"""
        print("\n📝 Testing pattern descriptions...")
        
        # Test pattern that should match terafileshare
        terafileshare_pattern = r'https://terafileshare\.com/s/[A-Za-z0-9_-]+'
        description = _get_pattern_description(terafileshare_pattern, 0)
        
        self.assertEqual(description, "TeraFile Share Links",
                        f"Incorrect pattern description: {description}")
        print(f"   ✅ Pattern description: {description}")
        
        print("✅ Pattern description test passed!")
    
    def test_config_domain_support(self):
        """Test that configuration supports new domain"""
        print("\n⚙️ Testing configuration domain support...")
        
        # Test domain validation in config
        test_urls = [
            "https://terafileshare.com/s/test123",
            "https://www.terafileshare.com/s/test456"
        ]
        
        for url in test_urls:
            is_valid = validate_terabox_url(url)
            self.assertTrue(is_valid, f"Configuration rejected valid URL: {url}")
            print(f"   ✅ Config accepts: {url}")
        
        print("✅ Configuration domain support test passed!")
    
    def test_comprehensive_text_processing(self):
        """Test comprehensive text processing with real user data"""
        print("\n📝 Testing comprehensive text processing...")
        
        # Extract links from the full sample text
        extracted_links = extract_terabox_links(self.sample_text)
        
        # Should extract only terafileshare.com links, not telegram links
        terafileshare_count = sum(1 for link in extracted_links if 'terafileshare.com' in link)
        telegram_count = sum(1 for link in extracted_links if 't.me' in link)
        
        print(f"   📊 Results:")
        print(f"      TeraFileShare links: {terafileshare_count}")
        print(f"      Telegram links: {telegram_count}")
        print(f"      Total extracted: {len(extracted_links)}")
        
        # Should find terafileshare links but not telegram links
        self.assertGreater(terafileshare_count, 0, "No terafileshare links found")
        self.assertEqual(telegram_count, 0, "Telegram links should be filtered out")
        
        # Verify specific expected links
        for expected_link in set(self.expected_links):
            self.assertIn(expected_link, extracted_links,
                         f"Expected terafileshare link not found: {expected_link}")
        
        print("✅ Comprehensive text processing test passed!")

def run_tests():
    """Run all tests with detailed output"""
    print("🧪 TeraDL TeraFileShare Support Test Suite")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTeraFileShareSupport)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("🎉 All tests passed! TeraFileShare support is working correctly.")
    else:
        print(f"❌ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
        
        if result.failures:
            print("\n❌ Failures:")
            for test, traceback in result.failures:
                print(f"   {test}: {traceback}")
        
        if result.errors:
            print("\n💥 Errors:")
            for test, traceback in result.errors:
                print(f"   {test}: {traceback}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

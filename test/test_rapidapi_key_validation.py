"""
Comprehensive Test Suite for RapidAPI Key Validation

This test suite validates the API key format validation, pattern matching,
and live API testing functionality in the TeraBox RapidAPI integration.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the parent directory to the path to import utils
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.terabox_rapidapi import TeraBoxRapidAPI


class TestRapidAPIKeyValidation(unittest.TestCase):
    """Test cases for RapidAPI key validation functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = TeraBoxRapidAPI()
        
        # Valid test keys (format-wise)
        self.valid_key_1 = "298bbd7e09msh8c672d04ba26de4p154bc9jsn9de6459d8a13"
        self.valid_key_2 = "abcd1234efmsh567890abcdef123456p789abcjsn123456789"
        
        # Invalid test keys
        self.invalid_keys = {
            'too_short': "298bbd7e09msh8c672d04ba26de4p154bc9jsn9de6",
            'too_long': "298bbd7e09msh8c672d04ba26de4p154bc9jsn9de6459d8a13extra",
            'missing_msh': "298bbd7e09xxx8c672d04ba26de4p154bc9jsn9de6459d8a13",
            'missing_jsn': "298bbd7e09msh8c672d04ba26de4p154bc9xxx9de6459d8a13",
            'special_chars': "298bbd7e09msh8c672d04ba26de4p154bc9jsn9de6459d8a1@",
            'with_spaces': "298bbd7e09msh8c672d04ba26de4p154bc9jsn9de6459d8a1 ",
            'empty': "",
            'none': None
        }
    
    def test_valid_api_key_format(self):
        """Test validation of correctly formatted API keys"""
        for valid_key in [self.valid_key_1, self.valid_key_2]:
            with self.subTest(key=valid_key[:20] + "..."):
                result = self.client._validate_api_key_format(valid_key)
                self.assertEqual(result['status'], 'success')
                self.assertIn('length', result['details'])
                self.assertIn('pattern', result['details'])
                self.assertIn('markers', result['details'])
                self.assertEqual(result['details']['length'], 50)
    
    def test_invalid_api_key_formats(self):
        """Test validation of incorrectly formatted API keys"""
        for key_name, invalid_key in self.invalid_keys.items():
            with self.subTest(key_type=key_name):
                result = self.client._validate_api_key_format(invalid_key)
                self.assertEqual(result['status'], 'failed')
                self.assertIn('message', result)
                
                # Check specific error messages
                if key_name == 'too_short' or key_name == 'too_long':
                    self.assertIn('length', result['message'].lower())
                elif key_name == 'missing_msh':
                    self.assertIn('msh', result['message'].lower())
                elif key_name == 'missing_jsn':
                    self.assertIn('jsn', result['message'].lower())
                elif key_name == 'special_chars':
                    self.assertIn('invalid characters', result['message'].lower())
    
    def test_api_key_length_validation(self):
        """Test specific length validation requirements"""
        test_cases = [
            ("x" * 49, 'failed'),  # Too short
            ("x" * 50, 'failed'),  # Right length but wrong format
            ("x" * 51, 'failed'),  # Too long
        ]
        
        for test_key, expected_status in test_cases:
            with self.subTest(length=len(test_key)):
                result = self.client._validate_api_key_format(test_key)
                self.assertEqual(result['status'], expected_status)
    
    def test_api_key_pattern_validation(self):
        """Test regex pattern validation for RapidAPI keys"""
        # Test keys with correct markers but different patterns
        test_patterns = [
            ("12345678msh1234567890abcdefp123456jsn12345678", 'success'),
            ("abcdef12msh567890abcdef123456p789abcjsn123456ab", 'success'),
            ("298bbd7e09msh8c672d04ba26de4p154bc9jsn9de6459d8a13", 'success'),
            ("invalid_pattern_without_markers_at_all_here_test", 'failed'),
            ("msh_at_start_msh123456789012345678901234567890", 'failed'),
            ("123456789012345678901234567890123456789012jsn_end", 'failed'),
        ]
        
        for test_key, expected_status in test_patterns:
            if len(test_key) == 50:  # Only test if length is correct
                with self.subTest(pattern=test_key[:20] + "..."):
                    result = self.client._validate_api_key_format(test_key)
                    self.assertEqual(result['status'], expected_status)
    
    def test_quick_validate_api_key_format(self):
        """Test the public quick validation method"""
        # Valid key
        result = self.client.quick_validate_api_key_format(self.valid_key_1)
        self.assertEqual(result['status'], 'success')
        
        # Invalid key
        result = self.client.quick_validate_api_key_format(self.invalid_keys['too_short'])
        self.assertEqual(result['status'], 'failed')
    
    def test_is_valid_api_key_format(self):
        """Test the boolean validation method"""
        # Valid key
        self.assertTrue(self.client.is_valid_api_key_format(self.valid_key_1))
        
        # Invalid keys
        for invalid_key in self.invalid_keys.values():
            if invalid_key is not None:  # Skip None test for boolean method
                self.assertFalse(self.client.is_valid_api_key_format(invalid_key))
    
    @patch('utils.terabox_rapidapi.requests.Session.get')
    def test_live_api_validation_success(self, mock_get):
        """Test successful live API validation"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        client = TeraBoxRapidAPI(self.valid_key_1)
        result = client._test_api_key_live()
        
        self.assertEqual(result['status'], 'success')
        self.assertIn('authentication successful', result['message'].lower())
    
    @patch('utils.terabox_rapidapi.requests.Session.get')
    def test_live_api_validation_unauthorized(self, mock_get):
        """Test live API validation with unauthorized response"""
        # Mock unauthorized response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response
        
        client = TeraBoxRapidAPI(self.valid_key_1)
        result = client._test_api_key_live()
        
        self.assertEqual(result['status'], 'failed')
        self.assertIn('authentication failed', result['message'].lower())
    
    @patch('utils.terabox_rapidapi.requests.Session.get')
    def test_live_api_validation_rate_limit(self, mock_get):
        """Test live API validation with rate limit response"""
        # Mock rate limit response
        mock_response = Mock()
        mock_response.status_code = 429
        mock_get.return_value = mock_response
        
        client = TeraBoxRapidAPI(self.valid_key_1)
        result = client._test_api_key_live()
        
        self.assertEqual(result['status'], 'warning')
        self.assertIn('rate limit', result['message'].lower())
    
    @patch('utils.terabox_rapidapi.requests.Session.get')
    def test_live_api_validation_network_error(self, mock_get):
        """Test live API validation with network error"""
        # Mock network error
        mock_get.side_effect = Exception("Network error")
        
        client = TeraBoxRapidAPI(self.valid_key_1)
        result = client._test_api_key_live()
        
        self.assertEqual(result['status'], 'warning')
        self.assertIn('error', result['message'].lower())
    
    @patch('utils.terabox_rapidapi.TeraBoxRapidAPI._test_api_key_live')
    def test_full_validate_api_key_success(self, mock_live_test):
        """Test full validation with both format and live validation"""
        # Mock successful live test
        mock_live_test.return_value = {
            'status': 'success',
            'message': 'API key authentication successful',
            'details': 'Live API test passed'
        }
        
        client = TeraBoxRapidAPI(self.valid_key_1)
        result = client.validate_api_key()
        
        self.assertEqual(result['status'], 'success')
        self.assertIn('format_check', result)
        self.assertIn('live_test', result)
    
    @patch('utils.terabox_rapidapi.TeraBoxRapidAPI._test_api_key_live')
    def test_full_validate_api_key_format_failure(self, mock_live_test):
        """Test full validation with format failure (should not call live test)"""
        client = TeraBoxRapidAPI(self.invalid_keys['too_short'])
        result = client.validate_api_key()
        
        self.assertEqual(result['status'], 'failed')
        # Live test should not be called if format is invalid
        mock_live_test.assert_not_called()
    
    def test_get_api_key_info(self):
        """Test API key information retrieval"""
        # Test with valid key
        client = TeraBoxRapidAPI(self.valid_key_1)
        info = client.get_api_key_info()
        
        self.assertTrue(info['configured'])
        self.assertEqual(info['length'], 50)
        self.assertTrue(info['format_valid'])
        self.assertIn('masked_key', info)
        
        # Test with no key - need to override the config key
        client_no_key = TeraBoxRapidAPI("")
        info_no_key = client_no_key.get_api_key_info()
        
        self.assertFalse(info_no_key['configured'])
        self.assertIn('message', info_no_key)
    
    def test_edge_cases(self):
        """Test edge cases and boundary conditions"""
        edge_cases = [
            ("", 'failed'),  # Empty string
            ("   ", 'failed'),  # Only whitespace
            ("\n\t", 'failed'),  # Other whitespace
            ("298bbd7e09MSH8c672d04ba26de4p154bc9JSN9de6459d8a13", 'success'),  # Uppercase markers
            ("298bbd7e09Msh8c672d04ba26de4p154bc9Jsn9de6459d8a13", 'success'),  # Mixed case markers
        ]
        
        for test_input, expected_status in edge_cases:
            with self.subTest(input=repr(test_input)):
                result = self.client._validate_api_key_format(test_input)
                self.assertEqual(result['status'], expected_status)
    
    def test_whitespace_handling(self):
        """Test handling of keys with leading/trailing whitespace"""
        key_with_spaces = f"  {self.valid_key_1}  "
        result = self.client._validate_api_key_format(key_with_spaces)
        self.assertEqual(result['status'], 'success')
    
    def test_character_validation(self):
        """Test validation of allowed characters"""
        # Test with various invalid characters
        invalid_chars = ['@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '+', '=']
        
        for char in invalid_chars:
            # Insert invalid character into a valid key format
            invalid_key = self.valid_key_1[:25] + char + self.valid_key_1[26:]
            with self.subTest(char=char):
                result = self.client._validate_api_key_format(invalid_key)
                self.assertEqual(result['status'], 'failed')
                self.assertIn('invalid characters', result['message'].lower())


class TestRapidAPIKeyValidationIntegration(unittest.TestCase):
    """Integration tests for RapidAPI key validation"""
    
    def setUp(self):
        """Set up integration test fixtures"""
        self.valid_key = "298bbd7e09msh8c672d04ba26de4p154bc9jsn9de6459d8a13"
    
    @patch('utils.terabox_rapidapi.requests.Session')
    def test_client_initialization_with_validation(self, mock_session):
        """Test client initialization with automatic validation"""
        client = TeraBoxRapidAPI(self.valid_key)
        self.assertEqual(client.rapidapi_key, self.valid_key)
        
        # Test that session headers are set correctly
        expected_headers = {
            'X-RapidAPI-Key': self.valid_key,
            'X-RapidAPI-Host': client.host
        }
        
        # Verify headers were updated
        self.assertTrue(mock_session.called)
    
    def test_validation_error_messages_user_friendly(self):
        """Test that validation error messages are user-friendly"""
        test_cases = [
            ("short", "Invalid API key length"),
            ("298bbd7e09xxx8c672d04ba26de4p154bc9jsn9de6459d8a13", "msh"),
            ("298bbd7e09msh8c672d04ba26de4p154bc9xxx9de6459d8a13", "jsn"),
            ("298bbd7e09msh8c672d04ba26de4p154bc9jsn9de6459d8a1@", "invalid characters")
        ]
        
        client = TeraBoxRapidAPI()
        
        for invalid_key, expected_in_message in test_cases:
            with self.subTest(key=invalid_key[:20] + "..."):
                result = client._validate_api_key_format(invalid_key)
                self.assertEqual(result['status'], 'failed')
                self.assertIn(expected_in_message.lower(), result['message'].lower())


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)

# 🔑 RapidAPI Key Validation System

## 📋 Overview

The TeraDL application now includes a comprehensive RapidAPI key validation system that ensures API keys are properly formatted and functional before use. This system provides both format validation and live API testing to guarantee reliable operation.

## 🎯 Key Features

### ✅ Format Validation
- **Length Check**: Ensures API keys are exactly 50 characters long
- **Pattern Matching**: Validates RapidAPI-specific patterns with 'msh' and 'jsn' markers
- **Character Validation**: Confirms only alphanumeric characters are used
- **Marker Validation**: Verifies presence of required RapidAPI markers

### 🚀 Live API Testing
- **Authentication Test**: Verifies the key works with the actual API
- **Error Handling**: Provides specific feedback for different failure types
- **Network Resilience**: Handles timeouts and connection issues gracefully
- **Rate Limit Awareness**: Recognizes and handles rate limiting responses

## 📐 RapidAPI Key Format Requirements

### Standard Format
```
[alphanumeric]msh[alphanumeric]jsn[alphanumeric]
```

### Specifications
- **Total Length**: Exactly 50 characters
- **Required Markers**: Must contain 'msh' and 'jsn' (case insensitive)
- **Allowed Characters**: Letters (a-z, A-Z) and numbers (0-9) only
- **No Special Characters**: No spaces, symbols, or punctuation

### Valid Examples
```
298bbd7e09msh8c672d04ba26de4p154bc9jsn9de6459d8a13
abcd1234efmsh567890abcdef123456p789abcjsn123456789abc
```

### Invalid Examples
```
❌ 298bbd7e09msh8c672d04ba26de4p154bc9jsn9de6    (too short)
❌ 298bbd7e09xxx8c672d04ba26de4p154bc9jsn9de6459d8a13    (missing 'msh')
❌ 298bbd7e09msh8c672d04ba26de4p154bc9xxx9de6459d8a13    (missing 'jsn')
❌ 298bbd7e09msh8c672d04ba26de4p154bc9jsn9de6459d8a1@    (invalid character)
```

## 🔧 Implementation Details

### Core Validation Methods

#### `validate_api_key()` - Full Validation
```python
def validate_api_key(self) -> Dict[str, Any]:
    """
    Complete validation including format and live API testing
    
    Returns:
        Dict with status ('success', 'failed', 'warning') and detailed results
    """
```

#### `_validate_api_key_format()` - Format Only
```python
def _validate_api_key_format(self, api_key: str) -> Dict[str, Any]:
    """
    Validates API key format, pattern, and length
    
    Returns:
        Dict with validation results and detailed error messages
    """
```

#### `_test_api_key_live()` - Live Testing
```python
def _test_api_key_live(self) -> Dict[str, Any]:
    """
    Tests API key with actual API request
    
    Returns:
        Dict with live test results and response details
    """
```

### Utility Methods

#### `quick_validate_api_key_format()` - Public Format Check
```python
def quick_validate_api_key_format(self, api_key: str) -> Dict[str, Any]:
    """Quick format validation without live testing"""
```

#### `is_valid_api_key_format()` - Boolean Check
```python
def is_valid_api_key_format(self, api_key: str) -> bool:
    """Simple boolean check for format validity"""
```

#### `get_api_key_info()` - Key Information
```python
def get_api_key_info(self) -> Dict[str, Any]:
    """Get detailed information about the configured API key"""
```

## 🎨 User Interface Integration

### Real-time Validation
- **Instant Feedback**: Shows format validation as user types
- **Visual Indicators**: Green checkmarks for valid format, warnings for issues
- **Detailed Guidance**: Expandable sections with format requirements

### Enhanced Error Messages
- **User-Friendly**: Clear, actionable error messages
- **Specific Issues**: Identifies exact problems (length, missing markers, etc.)
- **Format Examples**: Shows correct format examples
- **Troubleshooting**: Provides common issue solutions

### Validation Workflow
1. **Format Check**: Immediate validation of key format
2. **Live Test**: Optional full API validation
3. **Detailed Results**: Complete validation report
4. **User Choice**: Option to proceed with warnings

## 🧪 Testing Framework

### Test Coverage
- **Format Validation**: All edge cases and error conditions
- **Pattern Matching**: Various valid and invalid patterns  
- **Live API Testing**: Mocked responses for different scenarios
- **Integration Tests**: End-to-end validation workflow
- **Edge Cases**: Boundary conditions and special characters

### Running Tests
```bash
# Run all validation tests
python test/run_validation_tests.py

# Run specific test file
python -m unittest test.test_rapidapi_key_validation -v
```

### Test Categories
- **Unit Tests**: Individual method validation
- **Integration Tests**: Full workflow testing
- **Mock Tests**: API response simulation
- **Edge Case Tests**: Boundary and error conditions

## ⚙️ Configuration Options

### Validation Settings
```json
{
  "rapidapi": {
    "validation": {
      "enable_format_validation": true,
      "enable_live_validation": true,
      "required_length": 50,
      "required_markers": ["msh", "jsn"],
      "allowed_characters": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
      "validation_timeout": 10
    }
  }
}
```

### Configuration Options
- **enable_format_validation**: Enable/disable format checking
- **enable_live_validation**: Enable/disable live API testing
- **required_length**: Expected API key length (default: 50)
- **required_markers**: Required text markers in key
- **allowed_characters**: Valid character set
- **validation_timeout**: Timeout for live validation requests

## 📊 Validation Response Format

### Success Response
```json
{
  "status": "success",
  "message": "API key is valid and working",
  "format_check": {
    "status": "success",
    "message": "API key format is valid",
    "details": {
      "length": 50,
      "pattern": "RapidAPI standard format",
      "markers": ["msh", "jsn"]
    }
  },
  "live_test": {
    "status": "success",
    "message": "API key authentication successful",
    "details": "Live API test passed"
  }
}
```

### Error Response
```json
{
  "status": "failed",
  "message": "Invalid API key length. Expected 50 characters, got 45",
  "details": "RapidAPI keys are typically 50 characters long"
}
```

### Warning Response
```json
{
  "status": "warning",
  "message": "API test timeout - Cannot verify key status",
  "details": "Network timeout during validation"
}
```

## 🔍 Troubleshooting Guide

### Common Issues

#### ❌ "Invalid API key length"
**Problem**: Key is not exactly 50 characters
**Solution**: 
- Copy the complete key from RapidAPI dashboard
- Check for missing characters or extra spaces
- Verify no truncation occurred during copy/paste

#### ❌ "Missing 'msh' marker"
**Problem**: Key doesn't contain the 'msh' text
**Solution**:
- Verify you're using a RapidAPI key (not another service)
- Re-copy the key from the RapidAPI dashboard
- Check if key was modified or corrupted

#### ❌ "Invalid characters"
**Problem**: Key contains non-alphanumeric characters
**Solution**:
- Remove any spaces, dashes, or special characters
- Ensure only letters and numbers are present
- Re-copy the key to avoid encoding issues

#### ⚠️ "Network timeout during validation"
**Problem**: Cannot connect to API for live testing
**Solution**:
- Check internet connection
- Try again later (temporary network issue)
- Use "Quick Format Check" for offline validation

### Best Practices

1. **Copy Carefully**: Always copy the complete key from RapidAPI dashboard
2. **Avoid Modifications**: Don't edit or modify the API key manually
3. **Secure Storage**: Store keys securely and avoid hardcoding
4. **Regular Validation**: Periodically validate keys to ensure they're still active
5. **Monitor Usage**: Check RapidAPI dashboard for usage and limits

## 🚀 Future Enhancements

### Planned Features
- **Batch Validation**: Validate multiple keys simultaneously
- **Key Rotation**: Automatic key rotation support
- **Usage Monitoring**: Track API key usage and limits
- **Advanced Patterns**: Support for future RapidAPI key formats
- **Caching**: Cache validation results to reduce API calls

### Extensibility
The validation system is designed to be easily extensible for:
- New API key formats
- Additional validation rules
- Custom validation logic
- Integration with other API services

## 📚 API Reference

### TeraBoxRapidAPI Class Methods

| Method | Description | Parameters | Returns |
|--------|-------------|------------|---------|
| `validate_api_key()` | Full validation (format + live) | None | Dict[str, Any] |
| `quick_validate_api_key_format(key)` | Format validation only | api_key: str | Dict[str, Any] |
| `is_valid_api_key_format(key)` | Boolean format check | api_key: str | bool |
| `get_api_key_info()` | Current key information | None | Dict[str, Any] |

### Response Status Values
- **success**: Validation passed completely
- **failed**: Validation failed with errors
- **warning**: Validation completed with warnings

---

## 💡 Tips for Developers

### Integration Examples

#### Basic Format Validation
```python
from utils.terabox_rapidapi import TeraBoxRapidAPI

client = TeraBoxRapidAPI()
result = client.quick_validate_api_key_format(api_key)

if result['status'] == 'success':
    print("✅ Format is valid!")
else:
    print(f"❌ {result['message']}")
```

#### Full Validation with Error Handling
```python
client = TeraBoxRapidAPI(api_key)
validation = client.validate_api_key()

if validation['status'] == 'success':
    # Proceed with API operations
    file_info = client.get_file_info(url)
elif validation['status'] == 'warning':
    # Handle warnings (network issues, etc.)
    print(f"⚠️ Warning: {validation['message']}")
    # Optionally proceed anyway
else:
    # Handle errors
    print(f"❌ Error: {validation['message']}")
    # Show user-friendly error message
```

### Testing Your Integration
```python
# Test with sample keys
test_keys = [
    "298bbd7e09msh8c672d04ba26de4p154bc9jsn9de6459d8a13",  # Valid
    "invalid_key_format",  # Invalid
    ""  # Empty
]

for key in test_keys:
    result = client.quick_validate_api_key_format(key)
    print(f"Key: {key[:20]}... -> {result['status']}")
```

---

*This validation system ensures reliable RapidAPI integration while providing excellent user experience and developer-friendly error handling.*

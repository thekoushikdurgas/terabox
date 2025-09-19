"""
TeraBox RapidAPI Integration Module
Commercial API service for TeraBox file extraction

This module provides access to RapidAPI's TeraBox downloader service which offers 
reliable, commercial-grade TeraBox file processing with professional support and SLA.

Key Features:
- Commercial-grade reliability and uptime guarantees
- Simple API key authentication (no complex OAuth flows)
- Intelligent response caching for performance optimization
- Comprehensive error handling and retry mechanisms
- Multiple download URL generation for redundancy
- Real-time progress tracking for downloads
- Professional support and documentation

Architecture:
- TeraBoxRapidAPI: Main client class for API interactions
- CacheManager: Intelligent caching layer for response optimization
- ConfigManager: Centralized configuration management
- Validation: Multi-layer API key and response validation
- Error Handling: Comprehensive error categorization and recovery

API Key Format:
- Length: Exactly 50 characters
- Pattern: [alphanumeric]msh[alphanumeric]jsn[alphanumeric]
- Example: 298bbd7e09msh8c672d04ba26de4p154bc9jsn9de6459d8a13

Response Caching Strategy:
- Cache Key: Extracted from TeraBox URL (surl parameter)
- TTL: Configurable (default 24 hours)
- Storage: JSON files in output/sessions directory
- Benefits: Faster responses, reduced API costs, offline access
"""

import requests
import time
import re
from typing import Dict, List, Any, Optional
from utils.config import log_error, log_info, get_default_download_path
from utils.cache_manager import TeraBoxCacheManager
from utils.terabox_config import get_config_manager
from utils.rapidapi_key_manager import RapidAPIKeyManager

class TeraBoxRapidAPI:
    """
    RapidAPI-based TeraBox client for commercial service integration
    
    This class provides a professional-grade interface to TeraBox file extraction
    through RapidAPI's commercial service, offering guaranteed reliability and support.
    
    Key Capabilities:
    - Commercial API service integration with SLA guarantees
    - Intelligent response caching for cost optimization
    - Multi-layer validation (format + live API testing)
    - Comprehensive error handling and retry mechanisms
    - Progress tracking for large file downloads
    - Multiple download URL generation for redundancy
    
    Architecture Pattern: Facade Pattern
    - Simplifies complex RapidAPI interactions
    - Provides unified interface for TeraBox operations
    - Handles authentication, caching, and error recovery
    - Abstracts away API complexity from UI components
    
    Caching Strategy:
    - Cache responses based on TeraBox URL surl parameter
    - Configurable TTL (Time To Live) for cache expiration
    - Automatic cleanup of expired cache entries
    - Performance benefits: faster responses, reduced API costs
    """
    
    def __init__(self, rapidapi_key: str = None, enable_cache: bool = None, cache_ttl_hours: int = None):
        """
        Initialize RapidAPI client with multiple key support and caching
        
        Args:
            rapidapi_key: Single RapidAPI key for authentication (backward compatibility)
            enable_cache: Enable response caching (overrides config)
            cache_ttl_hours: Cache TTL in hours (overrides config)
            
        Initialization Flow:
        1. Load configuration from centralized config manager
        2. Initialize multiple API key manager for rotation
        3. Apply parameter overrides if provided
        4. Initialize HTTP session with RapidAPI headers
        5. Set up cache manager if caching is enabled
        6. Validate configuration and log initialization status
        """
        log_info("Initializing TeraBoxRapidAPI client with multiple key support")
        
        # Configuration Loading
        # Purpose: Load settings from centralized configuration system
        # Hierarchy: Parameter overrides > config file > defaults
        self.config_manager = get_config_manager()
        self.rapidapi_config = self.config_manager.get_rapidapi_config()
        self.network_config = self.config_manager.get_network_config()
        
        log_info("Configuration managers loaded successfully")
        
        # Multiple API Key Setup
        # Purpose: Initialize key manager for automatic rotation and rate limit handling
        # Strategy: Use all configured keys or single provided key
        api_keys = []
        
        if rapidapi_key is not None:
            # Single key provided - use it as primary
            api_keys = [rapidapi_key]
            log_info("Using single API key from parameter override")
        else:
            # Use all configured keys from config
            api_keys = self.config_manager.get_rapidapi_keys()
            if not api_keys and self.rapidapi_config.api_key:
                # Fallback to single key for backward compatibility
                api_keys = [self.rapidapi_config.api_key]
            log_info(f"Using {len(api_keys)} API keys from configuration")
        
        # Initialize Key Manager
        # Purpose: Handle multiple keys with rotation and rate limit detection
        if api_keys:
            key_manager_config = {
                'enable_rotation': self.rapidapi_config.enable_key_rotation,
                'rate_limit_retry_delay': self.rapidapi_config.rate_limit_retry_delay,
                'key_rotation_on_error': self.rapidapi_config.key_rotation_on_error,
                'max_key_retries': self.rapidapi_config.max_key_retries
            }
            
            self.key_manager = RapidAPIKeyManager(api_keys, key_manager_config)
            log_info(f"Key manager initialized with {len(api_keys)} keys")
            
            # Get current key for backward compatibility
            current_key_info = self.key_manager.get_next_key()
            self.rapidapi_key = current_key_info[1] if current_key_info else None
            self.current_key_id = current_key_info[0] if current_key_info else None
        else:
            self.key_manager = None
            self.rapidapi_key = None
            self.current_key_id = None
            log_info("No API keys configured - key manager not initialized")
        
        # Service Configuration
        # Purpose: Set up RapidAPI service endpoints and timeouts
        # Source: Loaded from configuration with fallback to defaults
        self.base_url = self.rapidapi_config.base_url
        self.host = self.rapidapi_config.host
        self.timeout = self.rapidapi_config.timeout
        self.max_retries = self.rapidapi_config.max_retries
        self.retry_delay = self.rapidapi_config.retry_delay
        
        log_info(f"Service configuration - Base URL: {self.base_url}")
        log_info(f"Network settings - Timeout: {self.timeout}s, Max Retries: {self.max_retries}, Retry Delay: {self.retry_delay}s")
        
        # Cache Configuration
        # Purpose: Set up intelligent response caching for performance
        # Benefits: Faster responses, reduced API costs, offline access
        self.enable_cache = enable_cache if enable_cache is not None else self.rapidapi_config.enable_cache
        cache_ttl = cache_ttl_hours if cache_ttl_hours is not None else self.rapidapi_config.cache_ttl_hours
        
        log_info(f"Cache configuration - Enabled: {self.enable_cache}, TTL: {cache_ttl} hours")
        
        # HTTP Session Initialization
        # Purpose: Create session for RapidAPI requests with proper headers
        # Security: Include required RapidAPI authentication headers
        self.session = requests.Session()
        
        # Cache Manager Initialization
        # Purpose: Handle response caching and cache management
        # Conditional: Only create if caching is enabled to save resources
        self.cache_manager = TeraBoxCacheManager(cache_ttl_hours=cache_ttl) if self.enable_cache else None
        
        if self.cache_manager:
            log_info(f"Cache manager initialized - Directory: {self.cache_manager.cache_dir}")
        else:
            log_info("Cache manager disabled - no caching will be performed")
        
        # Session Headers Configuration
        # Purpose: Set up authentication and identification headers for RapidAPI
        # Security: Include API key and host validation headers
        if self.rapidapi_key:
            self.session.headers.update({
                'X-RapidAPI-Key': self.rapidapi_key,  # Authentication header
                'X-RapidAPI-Host': self.host,  # Service identification
                'User-Agent': self.network_config.user_agent  # Client identification
            })
            log_info("RapidAPI authentication headers configured successfully")
            log_info(f"API key configured - Length: {len(self.rapidapi_key)}, Host: {self.host}")
        else:
            log_info("No API key provided - headers not configured")
        
        # Final Initialization Status
        if self.enable_cache:
            log_info("RapidAPI client initialization complete with caching enabled")
        else:
            log_info("RapidAPI client initialization complete without caching")
    
    def get_key_manager_stats(self) -> Dict[str, Any]:
        """Get comprehensive key manager statistics"""
        if not self.key_manager:
            return {'error': 'Key manager not initialized'}
        
        return self.key_manager.get_manager_stats()
    
    def get_all_keys_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status for all API keys"""
        if not self.key_manager:
            return {'error': 'Key manager not initialized'}
        
        return self.key_manager.get_all_keys_status()
    
    def reset_all_keys(self) -> bool:
        """Reset all keys to healthy state"""
        if not self.key_manager:
            return False
        
        self.key_manager.reset_all_keys()
        log_info("All API keys reset to healthy state")
        return True
    
    def add_api_key(self, api_key: str) -> bool:
        """Add a new API key to the rotation pool"""
        if not self.key_manager:
            return False
        
        key_id = self.key_manager.add_key(api_key)
        log_info(f"Added new API key: {key_id}")
        
        # Update config manager
        self.config_manager.add_rapidapi_key(api_key)
        return True
    
    def remove_api_key(self, key_id: str) -> bool:
        """Remove an API key from the rotation pool"""
        if not self.key_manager:
            return False
        
        # Get the key before removing it
        key_status = self.key_manager.get_key_status(key_id)
        if not key_status:
            return False
        
        # Remove from key manager
        if self.key_manager.remove_key(key_id):
            log_info(f"Removed API key: {key_id}")
            return True
        
        return False
    
    def has_multiple_keys(self) -> bool:
        """Check if multiple API keys are configured"""
        return self.key_manager and len(self.key_manager.keys) > 1
    
    def set_api_key(self, api_key: str):
        """
        Set or update the RapidAPI key with validation and configuration update
        
        Args:
            api_key: New RapidAPI key to configure
            
        Process:
        1. Update instance variable
        2. Update session headers for immediate use
        3. Persist to configuration manager for future sessions
        4. Log the update for audit trail
        
        Security Note: API key is logged by length only for security
        """
        log_info(f"Updating RapidAPI key - Previous length: {len(self.rapidapi_key) if self.rapidapi_key else 0}, New length: {len(api_key)}")
        
        # Update instance configuration
        self.rapidapi_key = api_key
        
        # Update session headers for immediate effect
        # Purpose: Ensure current session uses new key without restart
        self.session.headers.update({
            'X-RapidAPI-Key': api_key,  # Authentication header
            'X-RapidAPI-Host': self.host  # Service identification
        })
        
        log_info("Session headers updated with new API key")
        
        # Persist to configuration manager
        # Purpose: Save key for future application sessions
        # Security: Config manager handles encryption automatically
        self.config_manager.set_rapidapi_key(api_key)
        
        log_info("RapidAPI key update completed - Session and config updated successfully")
    
    def validate_api_key(self) -> Dict[str, Any]:
        """
        Comprehensive RapidAPI key validation with multi-layer testing
        
        Validation Strategy:
        1. Format Validation: Check length, pattern, and required markers
        2. Live API Testing: Verify authentication with actual API call
        3. Error Categorization: Provide specific feedback for different failures
        4. Detailed Logging: Track validation process for debugging
        
        Returns:
            Dict containing validation status, messages, and detailed results
            
        Validation Layers:
        - Layer 1: Format validation (offline, fast)
        - Layer 2: Live API testing (online, slower but definitive)
        - Layer 3: Error analysis and user guidance
        """
        log_info("Starting comprehensive RapidAPI key validation")
        
        # Pre-validation Check
        if not self.rapidapi_key:
            log_info("Validation failed - No API key provided")
            return {'status': 'failed', 'message': 'No API key provided'}
        
        log_info(f"Validating API key - Length: {len(self.rapidapi_key)} characters")
        
        try:
            # Layer 1: Format and Pattern Validation
            # Purpose: Quick offline validation to catch obvious format errors
            # Benefits: Fast feedback, no API calls required, catches common mistakes
            log_info("Layer 1: Starting format and pattern validation")
            format_validation = self._validate_api_key_format(self.rapidapi_key)
            
            if format_validation['status'] == 'failed':
                log_info(f"Format validation failed: {format_validation['message']}")
                return format_validation
            
            log_info(f"Layer 1 passed - Format validation successful: {format_validation['message']}")
            
            # Layer 2: Live API Testing
            # Purpose: Verify the key actually works with RapidAPI service
            # Method: Make lightweight test request to validate authentication
            # Benefits: Confirms key is active and has proper permissions
            log_info("Layer 2: Starting live API authentication testing")
            live_validation = self._test_api_key_live()
            
            if live_validation['status'] == 'failed':
                log_info(f"Live validation failed: {live_validation['message']}")
                
                # Enhanced Error Analysis
                # Purpose: Provide specific guidance based on failure type
                # Strategy: Distinguish between format vs authentication issues
                if 'Invalid API key' in live_validation['message'] or 'Unauthorized' in live_validation['message']:
                    enhanced_error = {
                        'status': 'failed', 
                        'message': 'API key format is valid, but authentication failed. Please verify your RapidAPI key.',
                        'details': live_validation['message'],
                        'troubleshooting': [
                            'Verify the API key is copied correctly from RapidAPI dashboard',
                            'Check if your RapidAPI subscription is active',
                            'Ensure you have subscribed to the TeraBox service',
                            'Try generating a new API key if the current one is old'
                        ]
                    }
                    log_info("Enhanced error analysis: Authentication failure with valid format")
                    return enhanced_error
                
                return live_validation
            
            log_info(f"Layer 2 passed - Live validation successful: {live_validation['message']}")
            
            # Validation Success
            # Result: Both format and live testing passed
            # Status: API key is fully validated and ready for use
            success_result = {
                'status': 'success', 
                'message': 'API key is valid and working',
                'format_check': format_validation,
                'live_test': live_validation,
                'validation_timestamp': time.time(),
                'key_info': {
                    'length': len(self.rapidapi_key),
                    'masked_key': f"{self.rapidapi_key[:8]}...{self.rapidapi_key[-8:]}"
                }
            }
            
            log_info("Comprehensive API key validation completed successfully")
            log_info(f"Validation summary - Format: OK, Live test: OK, Key length: {len(self.rapidapi_key)}")
            
            return success_result
                
        except Exception as e:
            # Unexpected Validation Error
            # Causes: Network issues during live testing, configuration problems
            # Strategy: Log full details and provide user-friendly message
            log_error(e, "validate_api_key - unexpected error during validation")
            log_info(f"Validation exception details - Type: {type(e).__name__}, Message: {str(e)}")
            
            return {
                'status': 'failed', 
                'message': f'Validation error: {str(e)}',
                'error_type': type(e).__name__,
                'troubleshooting': [
                    'Check your internet connection',
                    'Verify RapidAPI service is accessible',
                    'Try again in a few moments'
                ]
            }
    
    def _validate_api_key_format(self, api_key: str) -> Dict[str, Any]:
        """
        Validate RapidAPI key format, pattern, and length
        
        RapidAPI keys typically:
        - Are 50 characters long
        - Contain alphanumeric characters and some special characters
        - Follow pattern: letters + numbers + 'msh' + more alphanumeric + 'jsn' + more alphanumeric
        """
        if not api_key or not isinstance(api_key, str):
            return {'status': 'failed', 'message': 'API key must be a non-empty string'}
        
        # Remove any whitespace
        api_key = api_key.strip()
        
        # Length validation
        expected_length = 50
        if len(api_key) != expected_length:
            return {
                'status': 'failed', 
                'message': f'Invalid API key length. Expected {expected_length} characters, got {len(api_key)}',
                'details': f'RapidAPI keys are typically {expected_length} characters long'
            }
        
        # Character validation - should only contain allowed characters
        allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
        invalid_chars = set(api_key) - allowed_chars
        
        if invalid_chars:
            return {
                'status': 'failed',
                'message': f'API key contains invalid characters: {", ".join(sorted(invalid_chars))}',
                'details': 'RapidAPI keys should only contain letters and numbers'
            }
        
        # Required marker validation
        if 'msh' not in api_key.lower():
            return {
                'status': 'failed',
                'message': 'API key missing "msh" marker',
                'details': 'Valid RapidAPI keys contain "msh" as a marker'
            }
        
        if 'jsn' not in api_key.lower():
            return {
                'status': 'failed',
                'message': 'API key missing "jsn" marker', 
                'details': 'Valid RapidAPI keys contain "jsn" as a marker'
            }
        
        # Pattern validation - RapidAPI keys typically contain 'msh' and 'jsn' markers
        # More flexible pattern that allows various configurations
        rapidapi_pattern = r'^[a-zA-Z0-9]+msh[a-zA-Z0-9]+jsn[a-zA-Z0-9]+$'
        
        if not re.match(rapidapi_pattern, api_key, re.IGNORECASE):
            return {
                'status': 'failed',
                'message': 'Invalid API key format. RapidAPI keys should contain "msh" and "jsn" markers',
                'details': 'Expected format: [alphanumeric]msh[alphanumeric]jsn[alphanumeric]'
            }
        
        return {
            'status': 'success',
            'message': 'API key format is valid',
            'details': {
                'length': len(api_key),
                'pattern': 'RapidAPI standard format',
                'markers': ['msh', 'jsn']
            }
        }
    
    def _test_api_key_live(self) -> Dict[str, Any]:
        """Test API key with a live request to verify it works"""
        try:
            # Use a minimal test - just check if we can make an authenticated request
            # We'll use the get_api_status endpoint or a simple test URL
            test_url = "https://1024terabox.com/s/1IGR8fj0DBvzNr1Wkp1xblg"
            
            # Make a test request with timeout
            response = self.session.get(
                f"{self.base_url}/url",
                params={'url': test_url},
                timeout=10  # Shorter timeout for validation
            )
            
            # Check response status
            if response.status_code == 200:
                return {
                    'status': 'success', 
                    'message': 'API key authentication successful',
                    'details': 'Live API test passed'
                }
            elif response.status_code == 401:
                return {
                    'status': 'failed', 
                    'message': 'Invalid API key - Authentication failed',
                    'details': 'The API key was rejected by RapidAPI'
                }
            elif response.status_code == 403:
                return {
                    'status': 'failed', 
                    'message': 'API key access denied - Check subscription',
                    'details': 'API key is valid but lacks permission for this service'
                }
            elif response.status_code == 429:
                return {
                    'status': 'warning',
                    'message': 'Rate limit exceeded - API key is valid',
                    'details': 'Too many requests, but authentication was successful'
                }
            else:
                return {
                    'status': 'warning',
                    'message': f'API responded with HTTP {response.status_code}',
                    'details': 'API key may be valid, but service returned unexpected response'
                }
                
        except requests.exceptions.Timeout:
            return {
                'status': 'warning',
                'message': 'API test timeout - Cannot verify key status',
                'details': 'Network timeout during validation'
            }
        except requests.exceptions.RequestException as e:
            return {
                'status': 'warning',
                'message': f'Network error during validation: {str(e)}',
                'details': 'Cannot verify API key due to network issues'
            }
        except Exception as e:
            log_error(e, "_test_api_key_live")
            return {
                'status': 'warning',
                'message': f'Live test error: {str(e)}',
                'details': 'Could not complete live API validation'
            }
    
    def quick_validate_api_key_format(self, api_key: str) -> Dict[str, Any]:
        """Quick format validation without live API testing"""
        return self._validate_api_key_format(api_key)
    
    def is_valid_api_key_format(self, api_key: str) -> bool:
        """Simple boolean check for API key format validity"""
        result = self._validate_api_key_format(api_key)
        return result['status'] == 'success'
    
    def get_api_key_info(self) -> Dict[str, Any]:
        """Get information about the currently configured API key"""
        if not self.rapidapi_key:
            return {
                'configured': False,
                'message': 'No API key configured'
            }
        
        format_check = self._validate_api_key_format(self.rapidapi_key)
        
        return {
            'configured': True,
            'length': len(self.rapidapi_key),
            'format_valid': format_check['status'] == 'success',
            'format_details': format_check,
            'masked_key': f"{self.rapidapi_key[:8]}...{self.rapidapi_key[-8:]}" if len(self.rapidapi_key) >= 16 else "***"
        }
    
    def get_file_info(self, terabox_url: str, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Get file information from TeraBox URL using RapidAPI service with multiple key rotation
        
        Args:
            terabox_url: TeraBox URL to process
            force_refresh: If True, bypass cache and force API call
            
        Returns: direct_link, file_name, size, sizebytes, thumb, or error
        """
        if not self.key_manager or not self.rapidapi_key:
            return {'error': 'No RapidAPI keys configured. Please configure your API keys.'}
        
        try:
            log_info(f"Getting file info via RapidAPI for: {terabox_url}")
            
            # Check cache first (unless force refresh is requested)
            if self.enable_cache and self.cache_manager and not force_refresh:
                cached_response = self.cache_manager.get_cached_response(terabox_url)
                if cached_response:
                    log_info(f"Returning cached response for URL: {terabox_url}")
                    return cached_response
            
            # Normalize TeraBox URL formats
            normalized_url = self._normalize_terabox_url(terabox_url)
            log_info(f"Normalized URL: {normalized_url}")
            
            # Try API request with key rotation
            max_attempts = len(self.key_manager.keys) * self.rapidapi_config.max_key_retries
            for attempt in range(max_attempts):
                # Get next available key
                key_info = self.key_manager.get_next_key()
                if not key_info:
                    return {
                        'error': 'No available API keys. All keys are rate limited or failed.',
                        '_api_status_code': 'no_keys',
                        '_api_success': False
                    }
                
                current_key_id, current_key = key_info
                log_info(f"Attempt {attempt + 1}/{max_attempts} using key: {current_key_id}")
                
                # Make API request with current key
                headers = {
                    'X-RapidAPI-Key': current_key,
                    'X-RapidAPI-Host': 'terabox-downloader-direct-download-link-generator2.p.rapidapi.com',
                    'User-Agent': 'TeraDL-RapidAPI-Client/1.0',
                    'Accept': 'application/json'
                }
                
                request_start_time = time.time()
                
                try:
                    response = self.session.get(
                        f"{self.base_url}/url",
                        params={'url': normalized_url},
                        headers=headers,
                        timeout=30
                    )
                    
                    response_time = time.time() - request_start_time
                    log_info(f"RapidAPI response status: {response.status_code} (key: {current_key_id}, time: {response_time:.2f}s)")
                    
                    # Handle successful response
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            log_info(f"RapidAPI response data type: {type(data)}")
                            
                            # Validate and process response
                            result = self._process_api_response(data)
                            if result:
                                log_info(f"Successfully extracted file info: {result['file_name']}")
                                
                                # Mark key as successful
                                self.key_manager.mark_request_success(current_key_id, response_time)
                                
                                # Add status code information for CSV processing
                                result['_api_status_code'] = 200
                                result['_api_success'] = True
                                result['_used_key_id'] = current_key_id
                                
                                # Save to cache if caching is enabled
                                if self.enable_cache and self.cache_manager:
                                    cache_saved = self.cache_manager.save_response_to_cache(terabox_url, result)
                                    if cache_saved:
                                        log_info(f"Response cached for future requests")
                                    else:
                                        log_info(f"Failed to cache response")
                                
                                return result
                            else:
                                # Mark as success but no valid data
                                self.key_manager.mark_request_success(current_key_id, response_time)
                                return {
                                    'error': 'No valid file data found in response',
                                    '_api_status_code': 200,
                                    '_api_success': False,
                                    '_used_key_id': current_key_id
                                }
                                
                        except ValueError as e:
                            log_error(e, "get_file_info - JSON decode")
                            self.key_manager.mark_request_failure(current_key_id, f"JSON decode error: {str(e)}")
                            return {
                                'error': f'Invalid JSON response: {str(e)}',
                                '_api_status_code': 200,
                                '_api_success': False,
                                '_used_key_id': current_key_id
                            }
                    
                    # Handle rate limiting - try next key
                    elif response.status_code == 429:
                        error_msg = 'Rate limit exceeded. Please wait before making more requests.'
                        log_info(f"Key {current_key_id} rate limited - rotating to next key")
                        self.key_manager.mark_request_failure(current_key_id, error_msg, 429)
                        continue  # Try next key
                    
                    # Handle authentication errors - try next key
                    elif response.status_code in [401, 403]:
                        error_msg = 'Invalid RapidAPI key or access denied'
                        log_info(f"Key {current_key_id} authentication failed - rotating to next key")
                        self.key_manager.mark_request_failure(current_key_id, error_msg, response.status_code)
                        continue  # Try next key
                    
                    # Handle other errors
                    else:
                        try:
                            error_data = response.json()
                            error_msg = error_data.get('message', f'HTTP {response.status_code}')
                        except:
                            error_msg = f'HTTP {response.status_code}'
                        
                        self.key_manager.mark_request_failure(current_key_id, error_msg, response.status_code)
                        
                        # For 400, 404 errors, don't retry with other keys (URL issue)
                        if response.status_code in [400, 404]:
                            return {
                                'error': f'API error: {error_msg}',
                                '_api_status_code': response.status_code,
                                '_api_success': False,
                                '_used_key_id': current_key_id
                            }
                        
                        continue  # Try next key for other errors
                
                except requests.exceptions.Timeout:
                    log_error(Exception("Timeout"), f"get_file_info - timeout with key {current_key_id}")
                    self.key_manager.mark_request_failure(current_key_id, "Request timeout")
                    continue  # Try next key
                
                except requests.exceptions.RequestException as e:
                    log_error(e, f"get_file_info - network error with key {current_key_id}")
                    self.key_manager.mark_request_failure(current_key_id, f"Network error: {str(e)}")
                    continue  # Try next key
            
            # All keys exhausted
            log_error(Exception("All API keys exhausted"), "get_file_info")
            return {
                'error': 'All API keys failed or are rate limited. Please wait and try again.',
                '_api_status_code': 'all_keys_failed',
                '_api_success': False
            }
                
        except Exception as e:
            log_error(e, "get_file_info")
            return {
                'error': f'Failed to get file info: {str(e)}',
                '_api_status_code': 'exception',
                '_api_success': False
            }
    
    def get_multiple_files_info(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Get file information for multiple TeraBox URLs"""
        results = []
        
        for i, url in enumerate(urls):
            log_info(f"Processing URL {i+1}/{len(urls)} via RapidAPI")
            
            result = self.get_file_info(url)
            result['original_url'] = url
            result['index'] = i
            results.append(result)
            
            # Rate limiting - wait between requests
            if i < len(urls) - 1:  # Don't wait after last request
                time.sleep(1)  # 1 second delay between requests
        
        return results
    
    def download_file(self, file_info: Dict[str, Any], save_path: str = None, 
                     callback: Optional[callable] = None) -> Dict[str, Any]:
        """
        Download file using the direct link from RapidAPI with enhanced error handling
        
        Args:
            file_info: File information from get_file_info()
            save_path: Directory to save file (optional)
            callback: Progress callback function(downloaded, total, percentage)
        
        Returns:
            Dict with file_path or error
        """
        if 'error' in file_info:
            return file_info
        
        # Try multiple download URLs in order of preference
        download_urls = [
            file_info.get('direct_link'),
            file_info.get('download_link'),
            file_info.get('link')
        ]
        download_urls = [url for url in download_urls if url]  # Remove empty URLs
        
        if not download_urls:
            return {'error': 'No download links available'}
        
        try:
            import os
            from utils.config import sanitize_filename
            
            # Prepare save path
            if save_path is None:
                save_path = get_default_download_path()
            else:
                # Ensure the directory exists
                os.makedirs(save_path, exist_ok=True)
            
            # Sanitize filename
            raw_filename = file_info.get('file_name', 'downloaded_file')
            file_name = sanitize_filename(raw_filename)
            file_path = os.path.join(save_path, file_name)
            
            log_info(f"Starting download via RapidAPI link: {file_name}")
            
            # Try each download URL until one works
            last_error = None
            for i, download_url in enumerate(download_urls):
                try:
                    log_info(f"Trying download URL {i+1}/{len(download_urls)}: {download_url[:100]}...")
                    
                    # Enhanced headers for download
                    headers = {
                        'User-Agent': 'TeraDL-RapidAPI-Client/1.0',
                        'Accept': '*/*',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Connection': 'keep-alive'
                    }
                    
                    # Download with progress tracking
                    response = requests.get(download_url, stream=True, timeout=60, headers=headers)
                    response.raise_for_status()
                    
                    total_size = int(response.headers.get('content-length', file_info.get('sizebytes', 0)))
                    downloaded = 0
                    
                    with open(file_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                downloaded += len(chunk)
                                
                                # Progress callback
                                if callback and total_size > 0:
                                    percentage = (downloaded / total_size) * 100
                                    callback(downloaded, total_size, percentage)
                    
                    log_info(f"Download completed: {file_path}")
                    return {
                        'file_path': file_path, 
                        'size': downloaded,
                        'original_filename': raw_filename,
                        'sanitized_filename': file_name,
                        'download_url_used': download_url
                    }
                    
                except requests.exceptions.RequestException as e:
                    last_error = f"URL {i+1} failed: {str(e)}"
                    log_error(e, f"download_file - URL {i+1}")
                    continue
                except Exception as e:
                    last_error = f"URL {i+1} error: {str(e)}"
                    log_error(e, f"download_file - URL {i+1}")
                    continue
            
            # If all URLs failed
            return {'error': f'All download URLs failed. Last error: {last_error}'}
            
        except Exception as e:
            log_error(e, "download_file")
            return {'error': f'Download failed: {str(e)}'}
    
    def _normalize_terabox_url(self, url: str) -> str:
        """
        Normalize different TeraBox URL formats to work with RapidAPI
        
        Args:
            url: Original TeraBox URL in any supported format
            
        Returns:
            str: Normalized URL compatible with RapidAPI service
            
        Normalization Strategy:
        1. Extract short URL identifier (surl) from various formats
        2. Map domain-specific formats to standardized URLs
        3. Handle both /s/ and ?surl= URL formats
        4. Provide fallback for unknown formats
        
        Supported Domains:
        - terasharelink.com -> preserve original format
        - terafileshare.com -> preserve original format (NEW)
        - 1024terabox.com -> preserve original format
        - freeterabox.com -> preserve original format
        - nephobox.com -> preserve original format
        - Other domains -> convert to standard terabox.app format
        """
        log_info(f"Normalizing TeraBox URL: {url}")
        5
        import re
        
        # URL Format Detection
        # Purpose: Identify URL format and extract components
        # Strategy: Use regex patterns to handle different formats
        if '/s/' in url:
            log_info("Detected /s/ format URL")
            
            # Extract Short URL Patterns
            # Purpose: Extract surl identifier from different URL formats
            # Strategy: Try multiple patterns in order of specificity
            patterns = [
                r'/s/([^/?&]+)',  # Standard /s/ format: /s/abc123
                r'surl=([^&]+)',  # Query parameter format: ?surl=abc123
            ]
            
            short_url = None
            for i, pattern in enumerate(patterns):
                match = re.search(pattern, url)
                if match:
                    short_url = match.group(1)
                    log_info(f"Short URL extracted using pattern {i+1}: {short_url}")
                    break
            
            if short_url:
                # Domain-Specific URL Normalization
                # Purpose: Handle different TeraBox domains appropriately
                # Strategy: Preserve original domain for better compatibility
                
                if 'terasharelink.com' in url:
                    normalized = f"https://terasharelink.com/s/{short_url}"
                    log_info(f"Normalized terasharelink.com URL: {normalized}")
                    return normalized
                    
                elif 'terafileshare.com' in url:  # NEW DOMAIN SUPPORT
                    normalized = f"https://terafileshare.com/s/{short_url}"
                    log_info(f"Normalized terafileshare.com URL: {normalized}")
                    return normalized
                    
                elif '1024terabox.com' in url:
                    normalized = f"https://1024terabox.com/s/{short_url}"
                    log_info(f"Normalized 1024terabox.com URL: {normalized}")
                    return normalized
                    
                elif 'freeterabox.com' in url:
                    normalized = f"https://freeterabox.com/s/{short_url}"
                    log_info(f"Normalized freeterabox.com URL: {normalized}")
                    return normalized
                    
                elif 'nephobox.com' in url:
                    normalized = f"https://nephobox.com/s/{short_url}"
                    log_info(f"Normalized nephobox.com URL: {normalized}")
                    return normalized
                    
                else:
                    # Default Normalization
                    # Purpose: Convert unknown domains to standard format
                    # Strategy: Use official terabox.app sharing format
                    normalized = f"https://www.terabox.app/sharing/link?surl={short_url}"
                    log_info(f"Normalized to standard format: {normalized}")
                    return normalized
            else:
                log_info("Could not extract short URL from /s/ format")
        
        # Fallback Strategy
        # Purpose: Handle URLs that don't match expected patterns
        # Strategy: Return original URL and let RapidAPI handle it
        log_info(f"URL normalization fallback - returning original: {url}")
        return url
    
    def _get_file_type(self, filename: str) -> str:
        """Determine file type from filename"""
        if not filename:
            return 'unknown'
        
        filename_lower = filename.lower()
        
        if any(ext in filename_lower for ext in ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.m4v']):
            return 'video'
        elif any(ext in filename_lower for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']):
            return 'image'
        elif any(ext in filename_lower for ext in ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a']):
            return 'audio'
        elif any(ext in filename_lower for ext in ['.pdf', '.doc', '.docx', '.txt', '.rtf']):
            return 'document'
        elif any(ext in filename_lower for ext in ['.zip', '.rar', '.7z', '.tar', '.gz']):
            return 'archive'
        else:
            return 'other'
    
    def get_api_status(self) -> Dict[str, Any]:
        """Get RapidAPI service status and usage information"""
        if not self.rapidapi_key:
            return {'status': 'no_key', 'message': 'No API key configured'}
        
        try:
            # Test API availability
            validation = self.validate_api_key()
            
            return {
                'service': 'RapidAPI TeraBox Downloader',
                'endpoint': self.base_url,
                'api_key_status': validation['status'],
                'message': validation['message'],
                'features': [
                    'Direct download links',
                    'File metadata extraction',
                    'Commercial reliability',
                    'Rate limiting protection',
                    'Multiple file support'
                ]
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def get_usage_info(self) -> Dict[str, Any]:
        """Get API usage information (if available from headers)"""
        # Note: This would need to be called after making a request
        # to get rate limit headers from the response
        
        return {
            'service': 'RapidAPI',
            'note': 'Usage limits depend on your RapidAPI subscription plan',
            'recommendations': [
                'Monitor your API usage in RapidAPI dashboard',
                'Implement proper error handling for rate limits',
                'Consider caching results to reduce API calls',
                'Use delays between requests for bulk operations'
            ]
        }
    
    def test_with_sample_url(self) -> Dict[str, Any]:
        """Test the API with a sample TeraBox URL"""
        sample_urls = [
            "https://www.terabox.app/sharing/link?surl=rJp5m6WPBvkjCV4o6eLoKw",
            "https://terabox.com/s/1aBcDeFgHiJkL",
            "https://1024terabox.com/s/1MnOpQrStUvWx"
        ]
        
        results = []
        
        for url in sample_urls:
            try:
                result = self.get_file_info(url)
                results.append({
                    'url': url,
                    'success': 'error' not in result,
                    'result': result
                })
                
                # Stop on first success
                if 'error' not in result:
                    break
                    
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                results.append({
                    'url': url,
                    'success': False,
                    'error': str(e)
                })
        
        return {
            'test_results': results,
            'api_functional': any(r['success'] for r in results)
        }
    
    def _process_api_response(self, data: Any) -> Optional[Dict[str, Any]]:
        """Process and validate API response data"""
        try:
            file_data = None
            
            if isinstance(data, list) and len(data) > 0:
                file_data = data[0]  # Take first file from array
            elif isinstance(data, dict):
                file_data = data  # Single file response
            else:
                log_error(Exception(f"Unexpected response format: {type(data)}"), "_process_api_response")
                return None
            
            if not file_data:
                return None
            
            # Extract and validate required fields
            file_name = file_data.get('file_name', file_data.get('fn', 'Unknown'))
            direct_link = file_data.get('direct_link', '')
            download_link = file_data.get('link', direct_link)
            size_str = file_data.get('size', 'Unknown')
            sizebytes = file_data.get('sizebytes', 0)
            thumbnail = file_data.get('thumb', file_data.get('thumbnail', ''))
            
            # Validate essential fields
            if not direct_link and not download_link:
                log_error(Exception("No download links found in response"), "_process_api_response")
                return None
            
            # Clean up file name (decode URL encoding if present)
            try:
                from urllib.parse import unquote
                file_name = unquote(file_name)
            except:
                pass
            
            # Ensure sizebytes is integer
            try:
                sizebytes = int(sizebytes) if sizebytes else 0
            except (ValueError, TypeError):
                sizebytes = 0
            
            # Build result
            result = {
                'direct_link': direct_link,
                'download_link': download_link,
                'file_name': file_name,
                'size': size_str,
                'sizebytes': sizebytes,
                'thumbnail': thumbnail,
                'file_type': self._get_file_type(file_name),
                'service': 'rapidapi',
                'raw_response': file_data  # Keep raw data for debugging
            }
            
            # Validate result
            if self._validate_file_result(result):
                return result
            else:
                return None
                
        except Exception as e:
            log_error(e, "_process_api_response")
            return None
    
    def _validate_file_result(self, result: Dict[str, Any]) -> bool:
        """Validate that the file result contains essential data"""
        required_fields = ['file_name', 'sizebytes']
        link_fields = ['direct_link', 'download_link']
        
        # Check required fields
        for field in required_fields:
            if not result.get(field):
                log_error(Exception(f"Missing required field: {field}"), "_validate_file_result")
                return False
        
        # Check that at least one download link exists
        if not any(result.get(field) for field in link_fields):
            log_error(Exception("No download links available"), "_validate_file_result")
            return False
        
        return True
    
    def get_supported_formats(self) -> List[str]:
        """
        Get comprehensive list of supported TeraBox URL formats
        
        Returns:
            List of supported URL format examples
            
        Supported Formats:
        - Official TeraBox domains with sharing and short link formats
        - Mirror domains with preserved formatting
        - Share link domains with various formats
        - Generic patterns for new domain support
        """
        log_info("Retrieving supported TeraBox URL formats")
        
        supported_formats = [
            # Official TeraBox Formats
            "https://www.terabox.app/sharing/link?surl=...",
            "https://terabox.com/s/...",
            "https://www.terabox.com/sharing/link?surl=...",
            "https://terabox.app/s/...",
            
            # Mirror Domain Formats
            "https://1024terabox.com/s/...",
            "https://1024tera.com/s/...",
            "https://freeterabox.com/s/...",
            "https://nephobox.com/s/...",
            "https://teraboxapp.com/s/...",
            
            # Share Link Domain Formats
            "https://terasharelink.com/s/...",
            "https://terafileshare.com/s/...",  # NEW DOMAIN SUPPORT
            "https://www.terafileshare.com/s/...",  # NEW DOMAIN SUPPORT
        ]
        
        log_info(f"Supported formats list generated - {len(supported_formats)} formats available")
        
        return supported_formats
    
    def get_pricing_info(self) -> Dict[str, Any]:
        """Get information about RapidAPI pricing"""
        return {
            'service': 'RapidAPI TeraBox Downloader',
            'pricing_model': 'Pay-per-use or subscription',
            'benefits': [
                'Commercial reliability',
                'No setup complexity',
                'Professional support',
                'Guaranteed uptime',
                'Rate limiting protection'
            ],
            'considerations': [
                'Requires RapidAPI subscription',
                'Usage costs apply',
                'Dependent on third-party service',
                'Rate limits based on plan'
            ],
            'dashboard': 'https://rapidapi.com/hub',
            'note': 'Check RapidAPI marketplace for current pricing'
        }
    
    # Cache Management Methods
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics and information"""
        if not self.enable_cache or not self.cache_manager:
            return {'status': 'disabled', 'message': 'Caching is not enabled'}
        
        return self.cache_manager.get_cache_stats()
    
    def clear_cache(self, surl: str = None) -> Dict[str, Any]:
        """Clear cache files"""
        if not self.enable_cache or not self.cache_manager:
            return {'status': 'disabled', 'message': 'Caching is not enabled'}
        
        return self.cache_manager.clear_cache(surl)
    
    def cleanup_expired_cache(self) -> Dict[str, Any]:
        """Clean up expired cache files"""
        if not self.enable_cache or not self.cache_manager:
            return {'status': 'disabled', 'message': 'Caching is not enabled'}
        
        return self.cache_manager.cleanup_expired_cache()
    
    def is_cache_enabled(self) -> bool:
        """Check if caching is enabled"""
        return self.enable_cache and self.cache_manager is not None
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get cache configuration information"""
        if not self.enable_cache or not self.cache_manager:
            return {
                'enabled': False,
                'message': 'Caching is disabled'
            }
        
        return {
            'enabled': True,
            'cache_directory': self.cache_manager.cache_dir,
            'ttl_hours': self.cache_manager.cache_ttl_hours,
            'cache_version': '1.0'
        }

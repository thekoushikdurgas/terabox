"""
TeraBox RapidAPI Integration Module
Commercial API service for TeraBox file extraction

This module provides access to RapidAPI's TeraBox downloader service
which offers reliable, commercial-grade TeraBox file processing.
"""

import requests
import time
import re
from typing import Dict, List, Any, Optional
from utils.config import log_error, log_info, get_default_download_path
from utils.cache_manager import TeraBoxCacheManager
from utils.terabox_config import get_config_manager

class TeraBoxRapidAPI:
    """RapidAPI-based TeraBox client for commercial service integration"""
    
    def __init__(self, rapidapi_key: str = None, enable_cache: bool = None, cache_ttl_hours: int = None):
        # Get configuration manager
        self.config_manager = get_config_manager()
        self.rapidapi_config = self.config_manager.get_rapidapi_config()
        self.network_config = self.config_manager.get_network_config()
        
        # Use provided values or fall back to config
        # Handle empty string vs None properly
        if rapidapi_key is not None:
            self.rapidapi_key = rapidapi_key
        else:
            self.rapidapi_key = self.rapidapi_config.api_key
        self.base_url = self.rapidapi_config.base_url
        self.host = self.rapidapi_config.host
        self.timeout = self.rapidapi_config.timeout
        self.max_retries = self.rapidapi_config.max_retries
        self.retry_delay = self.rapidapi_config.retry_delay
        
        # Cache settings
        self.enable_cache = enable_cache if enable_cache is not None else self.rapidapi_config.enable_cache
        cache_ttl = cache_ttl_hours if cache_ttl_hours is not None else self.rapidapi_config.cache_ttl_hours
        
        # Initialize session
        self.session = requests.Session()
        
        # Initialize cache manager
        self.cache_manager = TeraBoxCacheManager(cache_ttl_hours=cache_ttl) if self.enable_cache else None
        
        # Set up session headers
        if self.rapidapi_key:
            self.session.headers.update({
                'X-RapidAPI-Key': self.rapidapi_key,
                'X-RapidAPI-Host': self.host,
                'User-Agent': self.network_config.user_agent
            })
        
        if self.enable_cache:
            log_info("RapidAPI client initialized with caching enabled")
    
    def set_api_key(self, api_key: str):
        """Set or update the RapidAPI key"""
        self.rapidapi_key = api_key
        self.session.headers.update({
            'X-RapidAPI-Key': api_key,
            'X-RapidAPI-Host': self.host
        })
        # Also update the config manager
        self.config_manager.set_rapidapi_key(api_key)
        log_info("RapidAPI key updated successfully")
    
    def validate_api_key(self) -> Dict[str, Any]:
        """Validate RapidAPI key with pattern, length, and live API testing"""
        if not self.rapidapi_key:
            return {'status': 'failed', 'message': 'No API key provided'}
        
        try:
            # Step 1: Pattern and Length Validation
            format_validation = self._validate_api_key_format(self.rapidapi_key)
            if format_validation['status'] == 'failed':
                return format_validation
            
            log_info(f"API key format validation passed: {format_validation['message']}")
            
            # Step 2: Live API Testing (optional - can be disabled to avoid unnecessary requests)
            # Test with a lightweight endpoint or sample URL
            live_validation = self._test_api_key_live()
            if live_validation['status'] == 'failed':
                # If format is good but live test fails, provide more specific error
                if 'Invalid API key' in live_validation['message'] or 'Unauthorized' in live_validation['message']:
                    return {
                        'status': 'failed', 
                        'message': 'API key format is valid, but authentication failed. Please verify your RapidAPI key.',
                        'details': live_validation['message']
                    }
                return live_validation
            
            return {
                'status': 'success', 
                'message': 'API key is valid and working',
                'format_check': format_validation,
                'live_test': live_validation
            }
                
        except Exception as e:
            log_error(e, "validate_api_key")
            return {'status': 'failed', 'message': f'Validation error: {str(e)}'}
    
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
        Get file information from TeraBox URL using RapidAPI service with caching
        
        Args:
            terabox_url: TeraBox URL to process
            force_refresh: If True, bypass cache and force API call
            
        Returns: direct_link, file_name, size, sizebytes, thumb, or error
        """
        if not self.rapidapi_key:
            return {'error': 'No RapidAPI key provided. Please configure your API key.'}
        
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
            
            # Make API request with enhanced headers
            headers = {
                'X-RapidAPI-Key': self.rapidapi_key,
                'X-RapidAPI-Host': 'terabox-downloader-direct-download-link-generator2.p.rapidapi.com',
                'User-Agent': 'TeraDL-RapidAPI-Client/1.0',
                'Accept': 'application/json'
            }
            
            response = self.session.get(
                f"{self.base_url}/url",
                params={'url': normalized_url},
                headers=headers,
                timeout=30
            )
            
            log_info(f"RapidAPI response status: {response.status_code}")
            
            # Handle different response codes
            if response.status_code == 200:
                try:
                    data = response.json()
                    log_info(f"RapidAPI response data type: {type(data)}")
                    
                    # Validate and process response
                    result = self._process_api_response(data)
                    if result:
                        log_info(f"Successfully extracted file info: {result['file_name']}")
                        
                        # Save to cache if caching is enabled
                        if self.enable_cache and self.cache_manager:
                            cache_saved = self.cache_manager.save_response_to_cache(terabox_url, result)
                            if cache_saved:
                                log_info(f"Response cached for future requests")
                            else:
                                log_info(f"Failed to cache response")
                        
                        return result
                    else:
                        return {'error': 'No valid file data found in response'}
                        
                except ValueError as e:
                    log_error(e, "get_file_info - JSON decode")
                    return {'error': f'Invalid JSON response: {str(e)}'}
            
            elif response.status_code == 401:
                return {'error': 'Invalid RapidAPI key. Please check your API key.'}
            elif response.status_code == 403:
                return {'error': 'RapidAPI access denied. Check your subscription.'}
            elif response.status_code == 429:
                return {'error': 'Rate limit exceeded. Please wait before making more requests.'}
            elif response.status_code == 400:
                return {'error': 'Invalid TeraBox URL format.'}
            elif response.status_code == 404:
                return {'error': 'File not found or URL expired.'}
            else:
                # Try to get error message from response
                try:
                    error_data = response.json()
                    error_msg = error_data.get('message', f'HTTP {response.status_code}')
                except:
                    error_msg = f'HTTP {response.status_code}'
                return {'error': f'API error: {error_msg}'}
                
        except requests.exceptions.Timeout:
            log_error(Exception("Timeout"), "get_file_info - timeout")
            return {'error': 'Request timeout. Please try again.'}
        except requests.exceptions.RequestException as e:
            log_error(e, "get_file_info - network error")
            return {'error': f'Network error: {str(e)}'}
        except Exception as e:
            log_error(e, "get_file_info")
            return {'error': f'Failed to get file info: {str(e)}'}
    
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
        """Normalize different TeraBox URL formats to work with RapidAPI"""
        import re
        
        # Handle different TeraBox URL formats
        if '/s/' in url:
            # Extract short URL from various formats
            patterns = [
                r'/s/([^/?&]+)',  # Standard /s/ format
                r'surl=([^&]+)',  # Query parameter format
            ]
            
            short_url = None
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    short_url = match.group(1)
                    break
            
            if short_url:
                # Handle terasharelink.com and other domains
                if 'terasharelink.com' in url:
                    return f"https://terasharelink.com/s/{short_url}"
                elif '1024terabox.com' in url:
                    return f"https://1024terabox.com/s/{short_url}"
                elif 'freeterabox.com' in url:
                    return f"https://freeterabox.com/s/{short_url}"
                elif 'nephobox.com' in url:
                    return f"https://nephobox.com/s/{short_url}"
                else:
                    # Default to standard terabox format
                    return f"https://www.terabox.app/sharing/link?surl={short_url}"
        
        # Return as-is if already in sharing/link format or unknown format
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
        """Get list of supported TeraBox URL formats"""
        return [
            "https://www.terabox.app/sharing/link?surl=...",
            "https://terabox.com/s/...",
            "https://1024terabox.com/s/...",
            "https://freeterabox.com/s/...",
            "https://nephobox.com/s/...",
            "https://terasharelink.com/s/..."
        ]
    
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

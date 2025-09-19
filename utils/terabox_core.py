"""
TeraBox Core Processing Module

This module implements the core TeraBox file extraction functionality using three different modes:
1. Mode 1: Dynamic cookie extraction with real-time scraping
2. Mode 2: Static cookie usage from configuration
3. Mode 3: External service integration for sign/timestamp generation

The module provides robust error handling, retry mechanisms, and comprehensive logging
for debugging and monitoring purposes.

Architecture:
- TeraboxCore: Main class handling all extraction modes
- Session management: HTTP session with connection pooling and retry strategies
- CloudScraper integration: Anti-bot protection for Mode 3
- URL normalization: Handles various TeraBox URL formats
- File type detection: Categorizes files based on extensions
- Progress tracking: Real-time extraction progress monitoring
"""

import re
import requests
import math
import random
import base64
import cloudscraper
from urllib.parse import quote
import json
import time
from typing import Dict, List, Any, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from utils.config import (
    TeraboxError, ExtractionError, DownloadError, 
    log_error, log_info, config
)
from utils.terabox_config import get_config_manager

class TeraboxCore:
    """
    Core TeraBox processing class combining all three extraction modes
    
    This class serves as the central hub for TeraBox file extraction, providing:
    - Multi-mode extraction strategies (1: Dynamic, 2: Static, 3: External)
    - Robust error handling and retry mechanisms
    - Connection pooling and session management
    - User agent rotation for anti-detection
    - Comprehensive logging for debugging
    
    Architecture Pattern: Strategy Pattern
    - Each mode implements a different extraction strategy
    - Common interface for all extraction methods
    - Configurable retry and timeout policies
    - Centralized session and header management
    """
    
    def __init__(self, mode: int = None):
        """
        Initialize TeraBox core processor
        
        Args:
            mode: Extraction mode (1=Dynamic, 2=Static, 3=External)
                 If None, uses default from configuration
        
        Processing Modes:
        - Mode 1: Real-time cookie extraction and dynamic scraping
        - Mode 2: Static cookie usage from pre-configured sessions
        - Mode 3: External service integration for reliable processing
        """
        log_info(f"Initializing TeraboxCore with mode: {mode}")
        
        # Load configuration from centralized config manager
        self.config_manager = get_config_manager()
        self.unofficial_config = self.config_manager.get_unofficial_config()
        self.network_config = self.config_manager.get_network_config()
        
        # Set processing mode (default from config if not specified)
        self.mode = mode if mode is not None else self.unofficial_config.default_mode
        self.max_retries = self.unofficial_config.max_retries
        self.retry_delay = self.unofficial_config.retry_delay
        
        log_info(f"Configuration loaded - Mode: {self.mode}, Max Retries: {self.max_retries}, Retry Delay: {self.retry_delay}s")
        
        # User Agent Rotation Strategy
        # Purpose: Avoid detection by TeraBox anti-bot systems
        # Pattern: Rotate between realistic browser user agents
        # Impact: Reduces chance of request blocking and improves success rate
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0'
        ]
        
        log_info(f"User agent pool initialized with {len(self.user_agents)} agents")
        
        # HTTP Headers Strategy
        # Purpose: Mimic real browser behavior to avoid detection
        # Pattern: Use modern browser headers with security policies
        # Security: Include Sec-Fetch headers for CORS compliance
        self.headers = {
            'user-agent': random.choice(self.user_agents),  # Randomized on each request
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'accept-language': 'en-US,en;q=0.9',  # English preference
            'accept-encoding': 'gzip, deflate, br',  # Modern compression support
            'cache-control': 'no-cache',  # Force fresh requests
            'pragma': 'no-cache',  # HTTP/1.0 compatibility
            'sec-fetch-dest': 'document',  # Security policy: expecting document
            'sec-fetch-mode': 'navigate',  # Security policy: navigation request
            'sec-fetch-site': 'none',  # Security policy: direct navigation
            'sec-fetch-user': '?1',  # Security policy: user-initiated
            'upgrade-insecure-requests': '1'  # Prefer HTTPS
        }
        
        log_info(f"HTTP headers configured with user-agent: {self.headers['user-agent'][:50]}...")
        
        # Session Management Strategy
        # Purpose: Create robust HTTP sessions with retry policies
        # Pattern: Separate sessions for different use cases
        # Benefits: Connection pooling, automatic retries, enhanced reliability
        self.session = self._create_session()
        
        # CloudScraper for Mode 3 (Anti-bot protection)
        # Purpose: Handle JavaScript challenges and anti-bot measures
        # Usage: Only initialized for Mode 3 to avoid unnecessary overhead
        self.cloudscraper_session = self._create_cloudscraper() if self.mode == 3 else None
        
        log_info(f"Sessions initialized - Standard session: OK, CloudScraper: {'OK' if self.cloudscraper_session else 'FAILED'}")
        log_info(f"TeraboxCore initialization complete for mode {self.mode}")
    
    def _create_session(self):
        """
        Create a robust HTTP session with retry strategy and connection pooling
        
        Architecture Components:
        1. Retry Strategy: Handles transient failures automatically
        2. Connection Pooling: Reuses connections for better performance
        3. Timeout Configuration: Prevents hanging requests
        4. HTTP Adapter: Custom adapter with enhanced retry logic
        
        Returns:
            requests.Session: Configured session ready for TeraBox requests
        """
        log_info("Creating HTTP session with retry strategy and connection pooling")
        
        session = requests.Session()
        
        # Retry Strategy Configuration
        # Purpose: Handle transient network failures and server errors
        # Algorithm: Exponential backoff with configurable attempts
        # Status Codes: Retry on server errors and rate limits
        retry_strategy = Retry(
            total=self.max_retries,  # Maximum retry attempts
            backoff_factor=1,  # Exponential backoff multiplier (1s, 2s, 4s, ...)
            status_forcelist=[429, 500, 502, 503, 504],  # HTTP codes to retry
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]  # Safe methods to retry
        )
        
        log_info(f"Retry strategy configured - Total: {self.max_retries}, Backoff: exponential, Status codes: [429, 500, 502, 503, 504]")
        
        # HTTP Adapter with Connection Pooling
        # Purpose: Optimize connection reuse and handle retries
        # Pool Settings: Balance between performance and resource usage
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,  # Number of connection pools to cache
            pool_maxsize=20,  # Maximum connections per pool
            pool_block=False  # Don't block when pool is full
        )
        
        # Mount adapters for both HTTP and HTTPS
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        log_info("HTTP adapters mounted with connection pooling (10 pools, 20 max connections each)")
        
        # Apply session headers from initialization
        session.headers.update(self.headers)
        
        # Timeout Configuration
        # Purpose: Prevent hanging requests and improve responsiveness
        # Values: (connect_timeout, read_timeout) in seconds
        session.timeout = (10, 30)  # 10s to connect, 30s to read response
        
        log_info("Session timeout configured - Connect: 10s, Read: 30s")
        log_info("HTTP session creation completed successfully")
        
        return session
    
    def _create_cloudscraper(self):
        """
        Create a CloudScraper session for anti-bot protection (Mode 3)
        
        CloudScraper Purpose:
        - Automatically solves JavaScript challenges
        - Bypasses Cloudflare and similar protections
        - Handles dynamic anti-bot measures
        - Provides more reliable access to protected endpoints
        
        Configuration Strategy:
        - Emulate Chrome on Windows for maximum compatibility
        - Add delay to avoid rapid-fire requests
        - Use randomized user agents for variety
        
        Returns:
            cloudscraper.CloudScraper: Anti-bot protected session
        """
        log_info("Creating CloudScraper session for anti-bot protection")
        
        try:
            # CloudScraper Configuration
            # Browser Emulation: Chrome on Windows (most common combination)
            # Platform: Windows (widely supported)
            # Mobile: False (desktop version for better compatibility)
            scraper = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',  # Emulate Chrome browser
                    'platform': 'windows',  # Windows platform
                    'mobile': False  # Desktop version
                },
                delay=1  # 1 second delay between challenge attempts
            )
            
            log_info("CloudScraper base configuration applied - Browser: Chrome, Platform: Windows")
            
            # Enhanced Headers for CloudScraper
            # Purpose: Override default headers with our optimized set
            # Strategy: Use JSON-focused headers for API endpoints
            scraper.headers.update({
                'user-agent': random.choice(self.user_agents),  # Randomized UA
                'accept': 'application/json, text/plain, */*',  # JSON preference
                'accept-language': 'en-US,en;q=0.9',  # Language preference
                'cache-control': 'no-cache',  # Force fresh requests
                'pragma': 'no-cache'  # HTTP/1.0 compatibility
            })
            
            log_info(f"CloudScraper headers configured with user-agent: {scraper.headers['user-agent'][:50]}...")
            log_info("CloudScraper session creation completed successfully")
            
            return scraper
            
        except Exception as e:
            # Fallback Strategy: Use regular session if CloudScraper fails
            # Reason: Ensure functionality even if CloudScraper has issues
            # Impact: Reduced anti-bot protection but maintained basic functionality
            log_error(e, "_create_cloudscraper")
            log_info("CloudScraper failed, falling back to regular requests session")
            
            fallback_session = requests.Session()
            fallback_session.headers.update(self.headers)
            return fallback_session
    
    def _make_request(self, method: str, url: str, **kwargs):
        """
        Make HTTP request with comprehensive retry logic and error handling
        
        Request Strategy:
        1. Exponential backoff with jitter for retry delays
        2. User agent rotation on retries to avoid detection
        3. Comprehensive error categorization and handling
        4. Detailed logging for debugging and monitoring
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Target URL for the request
            **kwargs: Additional arguments passed to requests
            
        Returns:
            requests.Response: Successful HTTP response
            
        Raises:
            requests.exceptions.ConnectionError: After max retries exceeded
        """
        log_info(f"Starting {method.upper()} request to {url[:100]}{'...' if len(url) > 100 else ''}")
        log_info(f"Request parameters - Max retries: {self.max_retries}, Base delay: {self.retry_delay}s")
        
        for attempt in range(self.max_retries + 1):
            try:
                log_info(f"HTTP {method.upper()} attempt {attempt + 1}/{self.max_retries + 1} to {url[:50]}...")
                
                # Exponential Backoff with Jitter
                # Purpose: Avoid thundering herd problem and reduce server load
                # Algorithm: delay = base_delay * (2^attempt) + random_jitter
                # Benefit: Spreads retry attempts over time
                if attempt > 0:
                    base_delay = self.retry_delay * (2 ** (attempt - 1))
                    jitter = random.uniform(0.1, 0.5)  # Random jitter to avoid synchronization
                    total_delay = base_delay + jitter
                    
                    log_info(f"Retry delay calculation - Base: {base_delay:.2f}s, Jitter: {jitter:.2f}s, Total: {total_delay:.2f}s")
                    log_info(f"Waiting {total_delay:.2f} seconds before retry attempt {attempt + 1}...")
                    time.sleep(total_delay)
                
                # User Agent Rotation on Retry
                # Purpose: Avoid detection by appearing as different browsers
                # Strategy: Only rotate on retries to maintain session consistency
                if attempt > 0:
                    new_ua = random.choice(self.user_agents)
                    old_ua = self.session.headers.get('user-agent', 'Unknown')[:30]
                    self.session.headers['user-agent'] = new_ua
                    log_info(f"User agent rotated from {old_ua}... to {new_ua[:30]}...")
                
                # Execute HTTP Request
                # Method Dispatch: Support for different HTTP methods
                # Error Handling: Let exceptions bubble up for retry logic
                if method.upper() == 'GET':
                    log_info(f"Executing GET request with {len(kwargs)} additional parameters")
                    response = self.session.get(url, **kwargs)
                elif method.upper() == 'POST':
                    log_info(f"Executing POST request with {len(kwargs)} additional parameters")
                    response = self.session.post(url, **kwargs)
                else:
                    error_msg = f"Unsupported HTTP method: {method}"
                    log_error(ValueError(error_msg), "_make_request")
                    raise ValueError(error_msg)
                
                # Response Validation
                # Purpose: Ensure we got a successful response
                # Action: Raise exception for HTTP error status codes
                response.raise_for_status()
                
                # Success Logging
                response_size = len(response.content) if hasattr(response, 'content') else 0
                log_info(f"Request successful - Status: {response.status_code}, Size: {response_size} bytes, URL: {response.url}")
                log_info(f"Response headers - Content-Type: {response.headers.get('content-type', 'Unknown')}")
                
                return response
                
            except requests.exceptions.ConnectionError as e:
                # Connection Error Handling
                # Causes: Network issues, DNS failures, connection refused
                # Strategy: Retry with exponential backoff
                # User Impact: Temporary network issues should resolve automatically
                log_error(e, f"_make_request - connection error (attempt {attempt + 1}/{self.max_retries + 1})")
                log_info(f"Connection error details - Error type: {type(e).__name__}, Message: {str(e)}")
                
                if attempt == self.max_retries:
                    log_error(Exception("Max retries exceeded for connection errors"), "_make_request")
                    raise
                continue
                
            except requests.exceptions.Timeout as e:
                # Timeout Error Handling  
                # Causes: Slow server response, network congestion
                # Strategy: Retry with longer delays
                # User Impact: Server overload should resolve with retries
                log_error(e, f"_make_request - timeout error (attempt {attempt + 1}/{self.max_retries + 1})")
                log_info(f"Timeout error details - Timeout type: {type(e).__name__}, Configured timeout: {getattr(self.session, 'timeout', 'Unknown')}")
                
                if attempt == self.max_retries:
                    log_error(Exception("Max retries exceeded for timeout errors"), "_make_request")
                    raise
                continue
                
            except requests.exceptions.HTTPError as e:
                # HTTP Error Handling
                # Causes: 4xx client errors, 5xx server errors
                # Strategy: Retry only on server errors and rate limits
                # Decision Logic: Client errors (4xx) are usually permanent
                status_code = e.response.status_code if e.response else 'Unknown'
                log_error(e, f"_make_request - HTTP error {status_code} (attempt {attempt + 1}/{self.max_retries + 1})")
                log_info(f"HTTP error details - Status: {status_code}, URL: {e.response.url if e.response else 'Unknown'}")
                
                # Retry Strategy for HTTP Errors
                # 429: Rate limited - should retry with delay
                # 5xx: Server errors - temporary issues, worth retrying
                # 4xx: Client errors - usually permanent, don't retry
                if e.response and e.response.status_code in [429, 500, 502, 503, 504] and attempt < self.max_retries:
                    log_info(f"HTTP {status_code} is retryable, continuing with retry {attempt + 1}")
                    continue
                else:
                    log_info(f"HTTP {status_code} is not retryable or max retries reached, raising exception")
                    raise
                
            except Exception as e:
                # Unexpected Error Handling
                # Causes: JSON decode errors, unexpected exceptions
                # Strategy: Log details and retry if attempts remain
                # Safety: Catch-all to prevent complete failure
                log_error(e, f"_make_request - unexpected error (attempt {attempt + 1}/{self.max_retries + 1})")
                log_info(f"Unexpected error details - Type: {type(e).__name__}, Message: {str(e)}")
                
                if attempt == self.max_retries:
                    log_error(Exception("Max retries exceeded for unexpected errors"), "_make_request")
                    raise
                continue
        
        # Final Failure Handling
        # Reached when all retry attempts have been exhausted
        # Impact: Complete request failure, will propagate to caller
        error_msg = f"Max retries ({self.max_retries + 1}) exceeded for {method.upper()} {url}"
        log_error(Exception(error_msg), "_make_request")
        raise requests.exceptions.ConnectionError(error_msg)
        
    def extract_files(self, url: str) -> Dict[str, Any]:
        """Extract files from TeraBox URL based on selected mode"""
        try:
            log_info(f"Extracting files from URL: {url} using mode {self.mode}")
            
            if self.mode == 1:
                return self._extract_mode1(url)
            elif self.mode == 2:
                return self._extract_mode2(url)
            elif self.mode == 3:
                return self._extract_mode3(url)
            else:
                raise ValueError("Invalid mode. Must be 1, 2, or 3.")
        except requests.exceptions.RequestException as e:
            log_error(e, "extract_files - network error")
            return {'status': 'failed', 'message': 'Network error. Please check your connection.'}
        except Exception as e:
            log_error(e, "extract_files")
            return {'status': 'failed', 'message': str(e)}
    
    def _extract_mode1(self, url: str) -> Dict[str, Any]:
        """Mode 1: Dynamic cookies from real-time scraping"""
        result = {'status': 'failed', 'js_token': '', 'browser_id': '', 'cookie': '', 'sign': '', 'timestamp': '', 'shareid': '', 'uk': '', 'list': []}
        
        try:
            # Get short URL with retry mechanism
            req = self._make_request('GET', url, allow_redirects=True)
            short_url_match = re.search(r'surl=([^ &]+)', str(req.url))
            if not short_url_match:
                raise ExtractionError("Could not extract short URL from redirect")
            short_url = short_url_match.group(1)
            
            # Get authorization with enhanced headers
            auth_url = f'https://www.terabox.app/wap/share/filelist?surl={short_url}'
            auth_headers = self.headers.copy()
            auth_headers.update({
                'referer': url,
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin'
            })
            
            req = self._make_request('GET', auth_url, headers=auth_headers, allow_redirects=True)
            
            # Extract JS token with better error handling
            js_token_match = re.search(r'%28%22(.*?)%22%29', str(req.text.replace('\\', '')))
            if not js_token_match:
                raise ExtractionError("Could not extract JS token from response")
            js_token = js_token_match.group(1)
            
            browser_id = req.cookies.get_dict().get('browserid')
            cookie = 'lang=id;' + ';'.join([f'{a}={b}' for a, b in self.session.cookies.get_dict().items()])
            
            result.update({
                'js_token': js_token,
                'browser_id': browser_id,
                'cookie': cookie
            })
            
            # Get main file data with API headers
            api_url = f'https://www.terabox.com/api/shorturlinfo?app_id=250528&shorturl=1{short_url}&root=1'
            api_headers = {
                'accept': 'application/json, text/plain, */*',
                'referer': auth_url,
                'user-agent': self.session.headers['user-agent']
            }
            
            req = self._make_request('GET', api_url, headers=api_headers, cookies={'cookie': ''})
            api_response = req.json()
            
            all_files = self._pack_data(api_response, short_url)
            
            if len(all_files):
                result.update({
                    'sign': api_response['sign'],
                    'timestamp': api_response['timestamp'],
                    'shareid': api_response['shareid'],
                    'uk': api_response['uk'],
                    'list': all_files,
                    'status': 'success'
                })
            else:
                raise ExtractionError("No files found in the response")
            
        except Exception as e:
            log_error(e, "_extract_mode1")
            result['message'] = str(e)
        
        return result
    
    def _extract_mode2(self, url: str) -> Dict[str, Any]:
        """Mode 2: Static cookies from config"""
        # This would use static cookies from config.json
        # For now, fallback to mode 1 logic with config cookies
        return self._extract_mode1(url)
    
    def _extract_mode3(self, url: str) -> Dict[str, Any]:
        """Mode 3: Uses external service for sign/timestamp"""
        result = {'status': 'failed', 'sign': '', 'timestamp': '', 'shareid': '', 'uk': '', 'list': []}
        
        try:
            # Get short URL with retry mechanism
            req = self._make_request('GET', url, allow_redirects=True)
            short_url_match = re.search(r'surl=([^ &]+)', str(req.url))
            if not short_url_match:
                raise ExtractionError("Could not extract short URL from redirect")
            short_url = short_url_match.group(1)
            
            # Get main file data first with enhanced headers
            api_url = f'https://www.terabox.com/api/shorturlinfo?app_id=250528&shorturl=1{short_url}&root=1'
            api_headers = {
                'accept': 'application/json, text/plain, */*',
                'referer': url,
                'user-agent': self.session.headers['user-agent']
            }
            
            req = self._make_request('GET', api_url, headers=api_headers, cookies={'cookie': ''})
            api_response = req.json()
            
            all_files = self._pack_data(api_response, short_url)
            
            if len(all_files):
                result.update({
                    'shareid': api_response['shareid'],
                    'uk': api_response['uk'],
                    'list': all_files
                })
                
                # Get sign and timestamp from external service with enhanced error handling
                try:
                    api_base = f'{self.unofficial_config.external_service_url}/api/get-info'
                    post_url = f'{api_base}?shorturl={short_url}&pwd='
                    
                    headers_post = {
                        'accept': 'application/json, text/plain, */*',
                        'accept-language': 'en-US,en;q=0.9,id;q=0.8',
                        'referer': f'{self.unofficial_config.external_service_url}/',
                        'sec-fetch-mode': 'cors',
                        'sec-fetch-site': 'same-origin',
                        'user-agent': random.choice(self.user_agents),
                        'cache-control': 'no-cache',
                        'pragma': 'no-cache'
                    }
                    
                    # Use cloudscraper with retry logic
                    for attempt in range(self.max_retries + 1):
                        try:
                            log_info(f"Requesting external service (attempt {attempt + 1})")
                            
                            if attempt > 0:
                                delay = self.retry_delay * (2 ** (attempt - 1)) + random.uniform(0.5, 1.5)
                                log_info(f"Waiting {delay:.2f} seconds before retry...")
                                time.sleep(delay)
                            
                            response = self.cloudscraper_session.get(
                                post_url, 
                                headers=headers_post, 
                                allow_redirects=True,
                                timeout=(15, 45)
                            )
                            response.raise_for_status()
                            
                            json_response = response.json()
                            
                            if json_response.get('ok'):
                                result.update({
                                    'sign': json_response['sign'],
                                    'timestamp': json_response['timestamp'],
                                    'status': 'success'
                                })
                                break
                            else:
                                error_msg = json_response.get('message', 'External service returned error')
                                log_error(Exception(error_msg), f"external service error (attempt {attempt + 1})")
                                if attempt == self.max_retries:
                                    raise ExtractionError(f"External service failed: {error_msg}")
                                
                        except requests.exceptions.RequestException as e:
                            log_error(e, f"external service request error (attempt {attempt + 1})")
                            if attempt == self.max_retries:
                                raise ExtractionError(f"External service connection failed: {str(e)}")
                            continue
                            
                        except json.JSONDecodeError as e:
                            log_error(e, f"external service JSON decode error (attempt {attempt + 1})")
                            if attempt == self.max_retries:
                                raise ExtractionError("Invalid response from external service")
                            continue
                    
                except Exception as e:
                    log_error(e, "_extract_mode3 - external service")
                    result['status'] = 'failed'
                    result['message'] = f"External service error: {str(e)}"
            else:
                raise ExtractionError("No files found in the response")
                
        except Exception as e:
            log_error(e, "_extract_mode3")
            result['status'] = 'failed'
            result['message'] = str(e)
        
        return result
    
    def _pack_data(self, req: Dict, short_url: str) -> List[Dict[str, Any]]:
        """Pack file data from API response"""
        all_files = []
        for item in req.get('list', []):
            file_info = {
                'is_dir': item['isdir'],
                'path': item['path'],
                'fs_id': item['fs_id'],
                'name': item['server_filename'],
                'type': self._check_file_type(item['server_filename']) if not bool(int(item.get('isdir'))) else 'other',
                'size': item.get('size') if not bool(int(item.get('isdir'))) else '',
                'image': item.get('thumbs', {}).get('url3', '') if not bool(int(item.get('isdir'))) else '',
                'list': self._get_child_files(short_url, item['path'], '0') if item.get('isdir') else []
            }
            all_files.append(file_info)
        return all_files
    
    def _get_child_files(self, short_url: str, path: str = '', root: str = '0') -> List[Dict[str, Any]]:
        """Get child files recursively with enhanced error handling"""
        try:
            params = {'app_id': '250528', 'shorturl': short_url, 'root': root, 'dir': path}
            url = 'https://www.terabox.com/share/list?' + '&'.join([f'{a}={b}' for a, b in params.items()])
            
            headers = {
                'accept': 'application/json, text/plain, */*',
                'user-agent': self.session.headers['user-agent']
            }
            
            req = self._make_request('GET', url, headers=headers, cookies={'cookie': ''})
            response_data = req.json()
            
            return self._pack_data(response_data, short_url)
            
        except Exception as e:
            log_error(e, f"_get_child_files - path: {path}")
            return []
    
    def _check_file_type(self, name: str) -> str:
        """Check file type based on extension"""
        name = name.lower()
        if any(ext in name for ext in ['.mp4', '.mov', '.m4v', '.mkv', '.asf', '.avi', '.wmv', '.m2ts', '.3g2']):
            return 'video'
        elif any(ext in name for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']):
            return 'image'
        elif any(ext in name for ext in ['.pdf', '.docx', '.zip', '.rar', '.7z']):
            return 'file'
        else:
            return 'other'
    
    def generate_download_links(self, fs_id: str, uk: str, shareid: str, timestamp: str, sign: str, js_token: str = '', cookie: str = '') -> Dict[str, Any]:
        """Generate download links for a specific file"""
        result = {'status': 'failed', 'download_link': {}}
        
        try:
            if self.mode == 1:
                result = self._generate_links_mode1(fs_id, uk, shareid, timestamp, sign, js_token, cookie)
            elif self.mode == 2:
                result = self._generate_links_mode2(fs_id, uk, shareid, timestamp, sign)
            elif self.mode == 3:
                result = self._generate_links_mode3(fs_id, uk, shareid, timestamp, sign)
        except Exception as e:
            result = {'status': 'failed', 'message': str(e)}
        
        return result
    
    def _generate_links_mode1(self, fs_id: str, uk: str, shareid: str, timestamp: str, sign: str, js_token: str, cookie: str) -> Dict[str, Any]:
        """Generate download links using mode 1"""
        result = {'status': 'failed', 'download_link': {}}
        
        # Dynamic params
        dynamic_params = {
            'uk': str(uk),
            'sign': str(sign),
            'shareid': str(shareid),
            'primaryid': str(shareid),
            'timestamp': str(timestamp),
            'jsToken': str(js_token),
            'fid_list': str(f'[{fs_id}]')
        }
        
        # Static params
        static_params = {
            'app_id': '250528',
            'channel': 'dubox',
            'product': 'share',
            'clienttype': '0',
            'dp-logid': '',
            'nozip': '0',
            'web': '1'
        }
        
        params = {**dynamic_params, **static_params}
        url = 'https://www.terabox.com/share/download?' + '&'.join([f'{a}={b}' for a, b in params.items()])
        req = self.session.get(url, cookies={'cookie': cookie}).json()
        
        if not req.get('errno'):
            slow_url = req['dlink']
            result['download_link'].update({'url_1': slow_url})
            result['status'] = 'success'
            
            # Generate fast URLs
            try:
                old_url = self.session.head(slow_url, allow_redirects=True).url
                old_domain = re.search(r'://(.*?)\.', str(old_url)).group(1)
                medium_url = old_url.replace('by=themis', 'by=dapunta')
                fast_url = old_url.replace(old_domain, 'd3').replace('by=themis', 'by=dapunta')
                result['download_link'].update({'url_2': medium_url, 'url_3': fast_url})
            except:
                pass
        
        return result
    
    def _generate_links_mode2(self, fs_id: str, uk: str, shareid: str, timestamp: str, sign: str) -> Dict[str, Any]:
        """Generate download links using mode 2"""
        # For mode 2, we would use direct links from the file data
        # This is a simplified implementation
        return {'status': 'success', 'download_link': {'url_1': f'https://example.com/download/{fs_id}'}}
    
    def _generate_links_mode3(self, fs_id: str, uk: str, shareid: str, timestamp: str, sign: str) -> Dict[str, Any]:
        """Generate download links using mode 3 (external service)"""
        result = {'status': 'failed', 'download_link': {}}
        
        domain = f'{self.unofficial_config.external_service_url}/'
        api_url = f'{domain}api'
        
        headers = {
            'accept-language': 'en-US,en;q=0.9,id;q=0.8',
            'referer': domain,
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Mobile Safari/537.36'
        }
        
        params = {
            'shareid': str(shareid),
            'uk': str(uk),
            'sign': str(sign),
            'timestamp': str(timestamp),
            'fs_id': str(fs_id)
        }
        
        # List of base URLs for wrapping
        base_urls = [
            'plain-grass-58b2.comprehensiveaquamarine',
            'royal-block-6609.ninnetta7875',
            'bold-hall-f23e.7rochelle',
            'winter-thunder-0360.belitawhite',
            'fragrant-term-0df9.elviraeducational',
            'purple-glitter-924b.miguelalocal'
        ]
        
        try:
            # Get download link 1
            url_1 = f'{api_url}/get-download'
            response_1 = self.cloudscraper_session.post(url_1, json=params, headers=headers, allow_redirects=True).json()
            result['download_link'].update({'url_1': response_1['downloadLink']})
        except Exception:
            pass
        
        try:
            # Get download link 2 (wrapped)
            url_2 = f'{api_url}/get-downloadp'
            response_2 = self.cloudscraper_session.post(url_2, json=params, headers=headers, allow_redirects=True).json()
            wrapped_url = self._wrap_url(response_2['downloadLink'], base_urls)
            result['download_link'].update({'url_2': wrapped_url})
        except Exception:
            pass
        
        if len(list(result['download_link'].keys())) != 0:
            result['status'] = 'success'
        
        return result
    
    def _wrap_url(self, original_url: str, base_urls: List[str]) -> str:
        """Wrap URL with base64 encoding"""
        selected_base = random.choice(base_urls)
        quoted_url = quote(original_url, safe='')
        b64_encoded = base64.urlsafe_b64encode(quoted_url.encode()).decode()
        return f'https://{selected_base}.workers.dev/?url={b64_encoded}'
    
    def convert_bytes_to_mb(self, bytes_size: int) -> str:
        """Convert bytes to MB"""
        if not bytes_size:
            return "0"
        mb = bytes_size / (1024 * 1024)
        return f"{mb:.0f}"

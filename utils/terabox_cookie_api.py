"""
TeraBox Cookie-Based API Integration
Based on the terabox-downloader PyPI package approach but integrated with TeraDL

This module provides cookie-based authentication similar to the terabox-downloader package
but with enhanced features and integration with our existing TeraDL system.

Cookie Authentication Strategy:
- Uses browser session cookies to authenticate with TeraBox
- Provides middle ground between scraping and full API integration
- Leverages existing user sessions for reliable access
- Maintains session state for consistent file access

Key Features:
- Session cookie validation and management
- Direct download link generation
- Progress tracking for large downloads
- Multiple retry strategies for reliability
- Comprehensive error handling and recovery
- File metadata extraction and processing

Architecture Components:
- TeraBoxCookieAPI: Main cookie-based client class
- Cookie Parser: Handles various cookie formats and validation
- Session Manager: Maintains HTTP session with cookie authentication
- Error Handler: Comprehensive error categorization and recovery
- Progress Tracker: Real-time download progress monitoring

Cookie Format Support:
- Standard cookie strings (name=value; name2=value2)
- Browser export formats (tabular, tab-separated)
- Line-by-line format (one cookie per line)
- Auto-detection of cookie format types

Security Considerations:
- Cookies contain sensitive session information
- Proper validation prevents invalid/expired cookies
- Session timeout handling for expired cookies
- Secure cookie storage and transmission
"""

import requests
import re
import os
import json
import time
from typing import Dict, List, Any, Optional, Callable
from urllib.parse import urlparse, parse_qs
from utils.config import log_error, log_info, get_default_download_path

class TeraBoxCookieAPI:
    """
    Cookie-based TeraBox API client similar to terabox-downloader package
    
    This class provides authenticated access to TeraBox using browser session cookies,
    offering a balance between reliability and ease of use without requiring API registration.
    
    Authentication Strategy:
    - Uses browser session cookies for authentication
    - Maintains session state for consistent access
    - Handles cookie validation and expiration
    - Provides direct access to TeraBox APIs
    
    Key Capabilities:
    - Direct download link generation
    - File metadata extraction and processing
    - Progress tracking for downloads
    - Multiple file processing support
    - Comprehensive error handling and recovery
    
    Session Management:
    - HTTP session with cookie-based authentication
    - Modern browser header emulation
    - Security headers for CORS compliance
    - Connection reuse for performance
    """
    
    def __init__(self, cookie: str = None):
        """
        Initialize Cookie API client with session management
        
        Args:
            cookie: TeraBox session cookie string
            
        Initialization Process:
        1. Set up HTTP session with modern browser headers
        2. Configure cookie authentication if provided
        3. Prepare security headers for TeraBox compatibility
        4. Log initialization status for debugging
        """
        log_info("Initializing TeraBoxCookieAPI client")
        
        # Cookie Configuration
        self.cookie = cookie
        if cookie:
            log_info(f"Cookie provided - Length: {len(cookie)} characters")
        else:
            log_info("No cookie provided - will need to be set before use")
        
        # HTTP Session Initialization
        # Purpose: Create persistent session for cookie-based requests
        # Benefits: Connection reuse, cookie persistence, header consistency
        self.session = requests.Session()
        log_info("HTTP session created for cookie-based authentication")
        
        # Modern Browser Headers
        # Purpose: Emulate real browser behavior to avoid detection
        # Strategy: Use Chrome headers with modern security policies
        # Security: Include Sec-Fetch headers for CORS compliance
        self.base_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',  # English preference
            'Accept-Encoding': 'gzip, deflate, br',  # Modern compression
            'DNT': '1',  # Do Not Track header
            'Connection': 'keep-alive',  # Connection reuse
            'Upgrade-Insecure-Requests': '1',  # HTTPS preference
            'Sec-Fetch-Dest': 'document',  # Security policy
            'Sec-Fetch-Mode': 'navigate',  # Navigation mode
            'Sec-Fetch-Site': 'none',  # Direct navigation
            'Sec-Fetch-User': '?1',  # User-initiated
            'Cache-Control': 'max-age=0',  # Force fresh requests
        }
        
        log_info("Browser headers configured for TeraBox compatibility")
        
        # Session Configuration
        # Purpose: Apply headers and cookie to session
        # Strategy: Configure session once, reuse for all requests
        if self.cookie:
            self.session.headers.update(self.base_headers)
            self.session.headers['Cookie'] = self.cookie
            log_info("Session configured with cookie authentication")
        else:
            log_info("Session configured without cookie - authentication required before use")
    
    def set_cookie(self, cookie: str):
        """
        Set or update the TeraBox session cookie
        
        Args:
            cookie: New TeraBox session cookie string
            
        Process:
        1. Update instance cookie variable
        2. Update session headers for immediate effect
        3. Log update for audit trail
        
        Security Note: Cookie length logged for debugging, content not logged for security
        """
        log_info(f"Updating TeraBox cookie - Previous length: {len(self.cookie) if self.cookie else 0}, New length: {len(cookie)}")
        
        # Update instance variable
        self.cookie = cookie
        
        # Update session headers for immediate effect
        # Purpose: Ensure all subsequent requests use new cookie
        self.session.headers['Cookie'] = cookie
        
        log_info("Cookie update completed - Session headers updated successfully")
    
    def validate_cookie(self) -> Dict[str, Any]:
        """Validate if the current cookie is working with improved error handling and retry logic"""
        if not self.cookie:
            return {'status': 'failed', 'message': 'No cookie provided'}
        
        # First, do a basic cookie format validation
        basic_validation = self._validate_cookie_format()
        if basic_validation['status'] == 'failed':
            return basic_validation
        
        # Try multiple validation methods with retry logic
        validation_methods = [
            self._validate_with_main_page,
            self._validate_with_api_endpoint,
            self._validate_with_user_info
        ]
        
        last_error = None
        for method in validation_methods:
            try:
                result = self._retry_request(method)
                if result['status'] in ['success', 'warning']:
                    return result
                last_error = result.get('message', 'Unknown error')
            except Exception as e:
                last_error = str(e)
                continue
        
        # If all methods failed, return the last error
        log_error(Exception(last_error), "validate_cookie")
        return {
            'status': 'failed', 
            'message': f'Cookie validation failed: {last_error}',
            'suggestion': 'Try getting a fresh cookie from your browser'
        }
    
    def _validate_cookie_format(self) -> Dict[str, Any]:
        """Basic cookie format validation"""
        if not self.cookie or len(self.cookie.strip()) < 10:
            return {'status': 'failed', 'message': 'Cookie is too short or empty'}
        
        # Check for important TeraBox cookie components
        important_cookies = ['ndus', 'BDUSS', 'STOKEN']
        found_cookies = [cookie for cookie in important_cookies if f'{cookie}=' in self.cookie]
        
        if not found_cookies:
            # Check for other TeraBox-related cookies
            other_cookies = ['__bid_n', '__stripe_mid', 'sessionid']
            found_other = [cookie for cookie in other_cookies if f'{cookie}=' in self.cookie]
            
            if found_other:
                return {'status': 'warning', 'message': f'Cookie contains {", ".join(found_other)} but missing core TeraBox cookies'}
            else:
                return {'status': 'failed', 'message': 'Cookie does not contain any recognized TeraBox cookies'}
        
        return {'status': 'success', 'message': f'Cookie format looks valid (found: {", ".join(found_cookies)})'}
    
    def _retry_request(self, method_func, max_retries: int = 3):
        """Retry a request method with exponential backoff"""
        import time
        
        for attempt in range(max_retries):
            try:
                return method_func()
            except (requests.exceptions.ConnectionError, 
                   requests.exceptions.Timeout,
                   requests.exceptions.RequestException) as e:
                
                if attempt == max_retries - 1:  # Last attempt
                    raise e
                
                # Exponential backoff: 1s, 2s, 4s
                wait_time = 2 ** attempt
                log_info(f"Request failed (attempt {attempt + 1}/{max_retries}), retrying in {wait_time}s...")
                time.sleep(wait_time)
        
        raise Exception("Max retries exceeded")
    
    def _validate_with_main_page(self) -> Dict[str, Any]:
        """Validate cookie by accessing TeraBox main page"""
        response = self.session.get('https://www.terabox.com/', timeout=15)
        
        if response.status_code == 200:
            # Look for login indicators in the response
            content = response.text.lower()
            
            # Check for logged-in indicators
            logged_in_indicators = ['logout', 'profile', 'dashboard', 'my files']
            login_indicators = ['login', 'sign in', 'register']
            
            logged_in_score = sum(1 for indicator in logged_in_indicators if indicator in content)
            login_score = sum(1 for indicator in login_indicators if indicator in content)
            
            if logged_in_score > login_score:
                return {'status': 'success', 'message': 'Cookie appears to be valid (logged in)'}
            else:
                return {'status': 'warning', 'message': 'Cookie may not be fully authenticated'}
        else:
            return {'status': 'failed', 'message': f'HTTP {response.status_code} - Server rejected request'}
    
    def _validate_with_api_endpoint(self) -> Dict[str, Any]:
        """Validate cookie using a TeraBox API endpoint"""
        try:
            # Try a lightweight API endpoint
            response = self.session.get('https://www.terabox.com/api/user/info', timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('errno') == 0:  # TeraBox success code
                    return {'status': 'success', 'message': 'Cookie validated via API'}
                else:
                    return {'status': 'warning', 'message': 'API returned error, cookie may be invalid'}
            elif response.status_code == 401:
                return {'status': 'failed', 'message': 'Cookie is invalid or expired'}
            else:
                return {'status': 'warning', 'message': f'API returned HTTP {response.status_code}'}
        
        except requests.exceptions.JSONDecodeError:
            return {'status': 'warning', 'message': 'API response was not JSON, but request succeeded'}
        except Exception as e:
            raise e  # Re-raise for retry logic
    
    def _validate_with_user_info(self) -> Dict[str, Any]:
        """Validate cookie by trying to get user information"""
        try:
            # Try to access user profile or settings page
            response = self.session.get('https://www.terabox.com/main', timeout=10)
            
            if response.status_code == 200:
                # Check if we get redirected to login page
                if 'login' in response.url.lower() or 'signin' in response.url.lower():
                    return {'status': 'failed', 'message': 'Cookie is invalid - redirected to login'}
                else:
                    return {'status': 'success', 'message': 'Cookie allows access to main page'}
            else:
                return {'status': 'failed', 'message': f'HTTP {response.status_code} - Access denied'}
                
        except Exception as e:
            raise e  # Re-raise for retry logic
    
    def get_cookie_info(self) -> Dict[str, Any]:
        """Get detailed information about the current cookie"""
        if not self.cookie:
            return {
                'status': 'no_cookie',
                'message': 'No cookie set',
                'components': [],
                'cookie_length': 0
            }
        
        # Parse cookie components
        components = []
        important_cookies = ['ndus', 'BDUSS', 'STOKEN', 'csrfToken', 'lang']
        other_relevant = ['__bid_n', '__stripe_mid', '__stripe_sid', 'sessionid']
        
        cookie_parts = self.cookie.split(';')
        found_important = []
        found_other = []
        
        for part in cookie_parts:
            if '=' in part:
                name = part.split('=')[0].strip()
                value = part.split('=', 1)[1].strip()
                
                components.append({
                    'name': name,
                    'value': value[:20] + '...' if len(value) > 20 else value,
                    'length': len(value)
                })
                
                if name in important_cookies:
                    found_important.append(name)
                elif name in other_relevant:
                    found_other.append(name)
        
        # Determine status
        if found_important:
            status = 'valid'
            message = f'Cookie contains important components: {", ".join(found_important)}'
        elif found_other:
            status = 'incomplete'
            message = f'Cookie contains some relevant components: {", ".join(found_other)}'
        else:
            status = 'invalid'
            message = 'Cookie does not contain recognized TeraBox components'
        
        return {
            'status': status,
            'message': message,
            'components': components,
            'cookie_length': len(self.cookie),
            'has_ndus': 'ndus=' in self.cookie,
            'has_bduss': 'BDUSS=' in self.cookie,
            'has_stoken': 'STOKEN=' in self.cookie,
            'important_cookies': found_important,
            'other_cookies': found_other,
            'total_components': len(components)
        }
    
    def get_file_info(self, link: str) -> Dict[str, Any]:
        """
        Get file information from TeraBox link
        Returns: file_name, download_link, thumbnail, file_size, sizebytes, or error
        """
        if not self.cookie:
            return {'error': 'No cookie provided. Please set a valid TeraBox cookie.'}
        
        try:
            log_info(f"Getting file info for: {link}")
            
            # Extract short URL from the link
            short_url = self._extract_short_url(link)
            if not short_url:
                return {'error': 'Invalid TeraBox link format'}
            
            # Get the file page
            response = self.session.get(link, timeout=15)
            response.raise_for_status()
            
            # Extract file information from the page
            file_info = self._parse_file_info(response.text, link)
            
            if file_info.get('error'):
                return file_info
            
            # Get direct download link
            download_info = self._get_download_link(file_info, short_url)
            
            if download_info.get('error'):
                return download_info
            
            # Combine all information
            result = {
                'file_name': file_info.get('file_name', 'Unknown'),
                'download_link': download_info.get('download_link', ''),
                'thumbnail': file_info.get('thumbnail', ''),
                'file_size': file_info.get('file_size', 'Unknown'),
                'sizebytes': file_info.get('sizebytes', 0),
                'file_type': file_info.get('file_type', 'unknown'),
                'fs_id': file_info.get('fs_id', ''),
                'uk': file_info.get('uk', ''),
                'shareid': file_info.get('shareid', '')
            }
            
            log_info(f"Successfully extracted file info: {result['file_name']}")
            return result
            
        except requests.exceptions.RequestException as e:
            log_error(e, "get_file_info - network error")
            return {'error': f'Network error: {str(e)}'}
        except Exception as e:
            log_error(e, "get_file_info")
            return {'error': f'Failed to get file info: {str(e)}'}
    
    def _extract_short_url(self, link: str) -> Optional[str]:
        """Extract short URL identifier from TeraBox link"""
        patterns = [
            r'/s/([a-zA-Z0-9_-]+)',
            r'surl=([a-zA-Z0-9_-]+)',
            r'shorturl=([a-zA-Z0-9_-]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, link)
            if match:
                return match.group(1)
        
        return None
    
    def _parse_file_info(self, html_content: str, original_link: str) -> Dict[str, Any]:
        """Parse file information from HTML content"""
        try:
            # Look for JSON data in script tags
            json_pattern = r'window\.yunData\s*=\s*({.+?});'
            json_match = re.search(json_pattern, html_content, re.DOTALL)
            
            if json_match:
                try:
                    data = json.loads(json_match.group(1))
                    return self._extract_from_yundata(data)
                except json.JSONDecodeError:
                    pass
            
            # Fallback: Extract from various script patterns
            patterns = {
                'file_name': [
                    r'"server_filename"\s*:\s*"([^"]+)"',
                    r'"filename"\s*:\s*"([^"]+)"',
                    r'<title>([^<]+)</title>'
                ],
                'file_size': [
                    r'"size"\s*:\s*(\d+)',
                    r'"filesize"\s*:\s*(\d+)'
                ],
                'thumbnail': [
                    r'"thumbs"\s*:\s*{[^}]*"url3"\s*:\s*"([^"]+)"',
                    r'"thumb_url"\s*:\s*"([^"]+)"'
                ],
                'fs_id': [
                    r'"fs_id"\s*:\s*"?(\d+)"?',
                    r'"fsid"\s*:\s*"?(\d+)"?'
                ],
                'uk': [
                    r'"uk"\s*:\s*"?(\d+)"?'
                ],
                'shareid': [
                    r'"shareid"\s*:\s*"?(\d+)"?'
                ]
            }
            
            result = {}
            
            for key, pattern_list in patterns.items():
                for pattern in pattern_list:
                    match = re.search(pattern, html_content)
                    if match:
                        value = match.group(1)
                        if key in ['file_size', 'fs_id', 'uk', 'shareid']:
                            try:
                                value = int(value)
                            except ValueError:
                                continue
                        result[key] = value
                        break
            
            # Calculate human-readable file size
            if 'file_size' in result:
                result['sizebytes'] = result['file_size']
                result['file_size'] = self._format_file_size(result['file_size'])
            
            # Determine file type
            if 'file_name' in result:
                result['file_type'] = self._get_file_type(result['file_name'])
            
            if not result.get('file_name'):
                result['error'] = 'Could not extract file information from the page'
            
            return result
            
        except Exception as e:
            log_error(e, "_parse_file_info")
            return {'error': f'Failed to parse file info: {str(e)}'}
    
    def _extract_from_yundata(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract file info from yunData object"""
        try:
            result = {}
            
            # Try different data structures
            file_list = data.get('file_list', [])
            if not file_list:
                file_list = data.get('list', [])
            
            if file_list and len(file_list) > 0:
                file_data = file_list[0]
                
                result['file_name'] = file_data.get('server_filename', file_data.get('filename', 'Unknown'))
                result['file_size'] = file_data.get('size', 0)
                result['sizebytes'] = result['file_size']
                result['file_size'] = self._format_file_size(result['file_size'])
                result['fs_id'] = str(file_data.get('fs_id', ''))
                
                # Get thumbnail
                thumbs = file_data.get('thumbs', {})
                if thumbs:
                    result['thumbnail'] = thumbs.get('url3', thumbs.get('url2', thumbs.get('url1', '')))
                
                # Get file type
                result['file_type'] = self._get_file_type(result['file_name'])
            
            # Extract share info
            result['uk'] = str(data.get('uk', ''))
            result['shareid'] = str(data.get('shareid', ''))
            
            return result
            
        except Exception as e:
            log_error(e, "_extract_from_yundata")
            return {'error': f'Failed to extract from yunData: {str(e)}'}
    
    def _get_download_link(self, file_info: Dict[str, Any], short_url: str) -> Dict[str, Any]:
        """Get direct download link for the file"""
        try:
            # Method 1: Try to get download link from API
            if file_info.get('fs_id') and file_info.get('uk') and file_info.get('shareid'):
                api_result = self._get_download_from_api(file_info)
                if api_result.get('download_link'):
                    return api_result
            
            # Method 2: Try to extract from share page
            share_result = self._get_download_from_share(short_url)
            if share_result.get('download_link'):
                return share_result
            
            return {'error': 'Could not generate download link'}
            
        except Exception as e:
            log_error(e, "_get_download_link")
            return {'error': f'Failed to get download link: {str(e)}'}
    
    def _get_download_from_api(self, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """Get download link using TeraBox API"""
        try:
            api_url = 'https://www.terabox.com/share/download'
            
            params = {
                'app_id': '250528',
                'channel': 'dubox',
                'clienttype': '0',
                'sign': '',  # We'll try without sign first
                'timestamp': str(int(time.time())),
                'uk': file_info['uk'],
                'shareid': file_info['shareid'],
                'fid_list': f"[{file_info['fs_id']}]",
                'nozip': '0',
                'web': '1'
            }
            
            response = self.session.get(api_url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('errno') == 0 and data.get('dlink'):
                return {'download_link': data['dlink']}
            
            return {'error': f"API error: {data.get('errno', 'unknown')}"}
            
        except Exception as e:
            log_error(e, "_get_download_from_api")
            return {'error': str(e)}
    
    def _get_download_from_share(self, short_url: str) -> Dict[str, Any]:
        """Get download link from share page"""
        try:
            share_api = f'https://www.terabox.com/api/shorturlinfo'
            
            params = {
                'app_id': '250528',
                'shorturl': short_url,
                'root': '1'
            }
            
            response = self.session.get(share_api, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('errno') == 0 and data.get('list'):
                file_data = data['list'][0]
                if file_data.get('dlink'):
                    return {'download_link': file_data['dlink']}
            
            return {'error': 'No download link found in share data'}
            
        except Exception as e:
            log_error(e, "_get_download_from_share")
            return {'error': str(e)}
    
    def download(self, file_info: Dict[str, Any], save_path: str = None, 
                 callback: Callable[[int, int, float], None] = None) -> Dict[str, Any]:
        """
        Download file with progress tracking
        
        Args:
            file_info: File info from get_file_info()
            save_path: Directory to save file (optional)
            callback: Progress callback function(downloaded, total, percentage)
        
        Returns:
            Dict with file_path or error
        """
        if 'error' in file_info:
            return file_info
        
        if not file_info.get('download_link'):
            return {'error': 'No download link available'}
        
        try:
            # Prepare save path
            if save_path is None:
                save_path = get_default_download_path()
            else:
                # Ensure the directory exists
                os.makedirs(save_path, exist_ok=True)
            
            file_name = file_info.get('file_name', 'downloaded_file')
            file_path = os.path.join(save_path, file_name)
            
            # Start download
            log_info(f"Starting download: {file_name}")
            
            response = self.session.get(
                file_info['download_link'], 
                stream=True, 
                timeout=30,
                headers={'Referer': 'https://www.terabox.com/'}
            )
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if callback:
                            percentage = (downloaded / total_size * 100) if total_size > 0 else 0
                            callback(downloaded, total_size, percentage)
                        elif total_size > 0:
                            # Default progress display
                            percentage = downloaded / total_size * 100
                            bar_length = 50
                            filled_length = int(bar_length * downloaded // total_size)
                            bar = '=' * filled_length + '-' * (bar_length - filled_length)
                            print(f'\r[{bar}] {percentage:.1f}%', end='', flush=True)
            
            if not callback and total_size > 0:
                print()  # New line after progress bar
            
            log_info(f"Download completed: {file_path}")
            return {'file_path': file_path, 'size': downloaded}
            
        except Exception as e:
            log_error(e, "download")
            return {'error': f'Download failed: {str(e)}'}
    
    def get_multiple_files_info(self, links: List[str]) -> List[Dict[str, Any]]:
        """Get file information for multiple links"""
        results = []
        
        for i, link in enumerate(links):
            log_info(f"Processing link {i+1}/{len(links)}")
            result = self.get_file_info(link)
            result['original_link'] = link
            results.append(result)
            
            # Small delay to avoid rate limiting
            time.sleep(0.5)
        
        return results
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        size = float(size_bytes)
        
        while size >= 1024.0 and i < len(size_names) - 1:
            size /= 1024.0
            i += 1
        
        return f"{size:.1f} {size_names[i]}"
    
    def _get_file_type(self, filename: str) -> str:
        """Determine file type from filename"""
        if not filename:
            return 'unknown'
        
        filename_lower = filename.lower()
        
        if any(ext in filename_lower for ext in ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv']):
            return 'video'
        elif any(ext in filename_lower for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']):
            return 'image'
        elif any(ext in filename_lower for ext in ['.mp3', '.wav', '.flac', '.aac', '.ogg']):
            return 'audio'
        elif any(ext in filename_lower for ext in ['.pdf', '.doc', '.docx', '.txt', '.rtf']):
            return 'document'
        elif any(ext in filename_lower for ext in ['.zip', '.rar', '.7z', '.tar', '.gz']):
            return 'archive'
        else:
            return 'other'
    
    def get_cookie_info(self) -> Dict[str, Any]:
        """Get information about the current cookie"""
        if not self.cookie:
            return {'status': 'no_cookie', 'message': 'No cookie set'}
        
        try:
            # Parse cookie components
            cookie_parts = {}
            for part in self.cookie.split(';'):
                if '=' in part:
                    key, value = part.split('=', 1)
                    cookie_parts[key.strip()] = value.strip()
            
            # Check for important components
            has_ndus = 'ndus' in cookie_parts
            has_bduss = 'BDUSS' in cookie_parts
            has_stoken = 'STOKEN' in cookie_parts
            
            return {
                'status': 'valid' if (has_ndus or has_bduss) else 'incomplete',
                'components': list(cookie_parts.keys()),
                'has_ndus': has_ndus,
                'has_bduss': has_bduss,
                'has_stoken': has_stoken,
                'cookie_length': len(self.cookie)
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def test_download_capability(self, test_link: str) -> Dict[str, Any]:
        """Test if the cookie can download files"""
        try:
            file_info = self.get_file_info(test_link)
            
            if 'error' in file_info:
                return {'status': 'failed', 'message': file_info['error']}
            
            if file_info.get('download_link'):
                return {'status': 'success', 'message': 'Download capability confirmed'}
            else:
                return {'status': 'limited', 'message': 'Can get file info but no download link'}
                
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

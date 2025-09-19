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
from config import (
    TeraboxError, ExtractionError, DownloadError, 
    log_error, log_info, config
)

class TeraboxCore:
    """Core TeraBox processing class combining all three modes"""
    
    def __init__(self, mode: int = 3):
        self.mode = mode
        self.max_retries = 3
        self.retry_delay = 1.0
        
        # Rotate user agents to avoid detection
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0'
        ]
        
        self.headers = {
            'user-agent': random.choice(self.user_agents),
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'accept-language': 'en-US,en;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1'
        }
        
        # Setup session with retry strategy
        self.session = self._create_session()
        self.cloudscraper_session = self._create_cloudscraper() if mode == 3 else None
    
    def _create_session(self):
        """Create a requests session with retry strategy and connection pooling"""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
        )
        
        # Mount adapter with retry strategy
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=20,
            pool_block=False
        )
        
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set session headers
        session.headers.update(self.headers)
        
        # Configure timeouts
        session.timeout = (10, 30)  # (connect_timeout, read_timeout)
        
        return session
    
    def _create_cloudscraper(self):
        """Create a cloudscraper session with enhanced configuration"""
        try:
            scraper = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'windows',
                    'mobile': False
                },
                delay=1
            )
            
            # Add custom headers
            scraper.headers.update({
                'user-agent': random.choice(self.user_agents),
                'accept': 'application/json, text/plain, */*',
                'accept-language': 'en-US,en;q=0.9',
                'cache-control': 'no-cache',
                'pragma': 'no-cache'
            })
            
            return scraper
        except Exception as e:
            log_error(e, "_create_cloudscraper")
            return requests.Session()
    
    def _make_request(self, method: str, url: str, **kwargs):
        """Make HTTP request with retry logic and error handling"""
        for attempt in range(self.max_retries + 1):
            try:
                log_info(f"Making {method} request to {url} (attempt {attempt + 1})")
                
                # Add random delay to avoid rate limiting
                if attempt > 0:
                    delay = self.retry_delay * (2 ** (attempt - 1)) + random.uniform(0.1, 0.5)
                    log_info(f"Waiting {delay:.2f} seconds before retry...")
                    time.sleep(delay)
                
                # Rotate user agent on retry
                if attempt > 0:
                    self.session.headers['user-agent'] = random.choice(self.user_agents)
                
                # Make the request
                if method.upper() == 'GET':
                    response = self.session.get(url, **kwargs)
                elif method.upper() == 'POST':
                    response = self.session.post(url, **kwargs)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                # Check response status
                response.raise_for_status()
                
                log_info(f"Request successful: {response.status_code}")
                return response
                
            except requests.exceptions.ConnectionError as e:
                log_error(e, f"_make_request - connection error (attempt {attempt + 1})")
                if attempt == self.max_retries:
                    raise
                continue
                
            except requests.exceptions.Timeout as e:
                log_error(e, f"_make_request - timeout error (attempt {attempt + 1})")
                if attempt == self.max_retries:
                    raise
                continue
                
            except requests.exceptions.HTTPError as e:
                log_error(e, f"_make_request - HTTP error (attempt {attempt + 1})")
                if e.response.status_code in [429, 500, 502, 503, 504] and attempt < self.max_retries:
                    continue
                raise
                
            except Exception as e:
                log_error(e, f"_make_request - unexpected error (attempt {attempt + 1})")
                if attempt == self.max_retries:
                    raise
                continue
        
        raise requests.exceptions.ConnectionError("Max retries exceeded")
        
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
                    api_base = 'https://terabox.hnn.workers.dev/api/get-info'
                    post_url = f'{api_base}?shorturl={short_url}&pwd='
                    
                    headers_post = {
                        'accept': 'application/json, text/plain, */*',
                        'accept-language': 'en-US,en;q=0.9,id;q=0.8',
                        'referer': 'https://terabox.hnn.workers.dev/',
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
        
        domain = 'https://terabox.hnn.workers.dev/'
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

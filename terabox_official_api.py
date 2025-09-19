"""
TeraBox Official API Integration Module
Based on TeraBox Open Platform Integration Document v1.0

This module provides access to official TeraBox APIs including:
- OAuth 2.0 authentication
- File management (upload, download, list, search)
- Share management
- Streaming APIs
- User management
"""

import requests
import hashlib
import time
import json
import base64
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import urlencode, quote
import secrets
import qrcode
from io import BytesIO
from config import log_error, log_info

class TeraBoxOfficialAPI:
    """Official TeraBox API client implementing the complete Open Platform API"""
    
    def __init__(self, client_id: str = None, client_secret: str = None, private_secret: str = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.private_secret = private_secret
        self.access_token = None
        self.refresh_token = None
        self.api_domain = "www.terabox.com"
        self.upload_domain = None
        self.session = requests.Session()
        
        # Set up session headers
        self.session.headers.update({
            'User-Agent': 'TeraDL-Official-Client/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        })
    
    def _generate_signature(self, timestamp: int) -> str:
        """Generate dynamic signature for API requests"""
        if not all([self.client_id, self.client_secret, self.private_secret]):
            raise ValueError("Missing required credentials for signature generation")
        
        # Signature rule: md5("client_id"_"timestamp"_"client_secret"_"private_secret")
        signature_string = f"{self.client_id}_{timestamp}_{self.client_secret}_{self.private_secret}"
        return hashlib.md5(signature_string.encode()).hexdigest()
    
    # ============================================================================
    # OAuth 2.0 Authorization Flow
    # ============================================================================
    
    def get_authorization_url(self, is_mobile: bool = False) -> str:
        """Get authorization URL for web/mobile login"""
        base_url = "https://www.terabox.com/wap/outside/login"
        params = {
            'clientId': self.client_id
        }
        
        if is_mobile:
            params['isFromApp'] = '1'
        
        return f"{base_url}?{urlencode(params)}"
    
    def exchange_code_for_token(self, authorization_code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        timestamp = int(time.time())
        sign = self._generate_signature(timestamp)
        
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'authorization_code',
            'code': authorization_code,
            'timestamp': timestamp,
            'sign': sign
        }
        
        try:
            response = self.session.post(
                'https://www.terabox.com/oauth/gettoken',
                data=data
            )
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('errno') == 0:
                token_data = result['data']
                self.access_token = token_data['access_token']
                self.refresh_token = token_data['refresh_token']
                
                log_info("Successfully obtained access token")
                return {
                    'status': 'success',
                    'access_token': self.access_token,
                    'refresh_token': self.refresh_token,
                    'expires_in': token_data['expires_in']
                }
            else:
                error_msg = f"Token exchange failed: {result.get('errno')}"
                log_error(Exception(error_msg), "exchange_code_for_token")
                return {'status': 'failed', 'message': error_msg}
                
        except Exception as e:
            log_error(e, "exchange_code_for_token")
            return {'status': 'failed', 'message': str(e)}
    
    def get_token_info(self) -> Dict[str, Any]:
        """Get access token information and API domains"""
        if not self.access_token:
            return {'status': 'failed', 'message': 'No access token available'}
        
        try:
            data = {'access_token': self.access_token}
            response = self.session.post(
                'https://www.terabox.com/oauth/tokeninfo',
                data=data
            )
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('errno') == 0:
                token_info = result['data']
                self.api_domain = token_info['api_domain']
                self.upload_domain = token_info.get('upload_domain', self.api_domain)
                
                return {
                    'status': 'success',
                    'api_domain': self.api_domain,
                    'upload_domain': self.upload_domain,
                    'user_id': token_info['user_id'],
                    'expires_in': token_info['expires_in']
                }
            else:
                return {'status': 'failed', 'message': f"Error {result.get('errno')}"}
                
        except Exception as e:
            log_error(e, "get_token_info")
            return {'status': 'failed', 'message': str(e)}
    
    def refresh_access_token(self) -> Dict[str, Any]:
        """Refresh expired access token"""
        if not self.refresh_token:
            return {'status': 'failed', 'message': 'No refresh token available'}
        
        timestamp = int(time.time())
        sign = self._generate_signature(timestamp)
        
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': self.refresh_token,
            'timestamp': timestamp,
            'sign': sign
        }
        
        try:
            response = self.session.post(
                'https://www.terabox.com/oauth/refreshtoken',
                data=data
            )
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('errno') == 0:
                token_data = result['data']
                self.access_token = token_data['access_token']
                self.refresh_token = token_data['refresh_token']
                
                return {
                    'status': 'success',
                    'access_token': self.access_token,
                    'refresh_token': self.refresh_token,
                    'expires_in': token_data['expires_in']
                }
            else:
                return {'status': 'failed', 'message': f"Error {result.get('errno')}"}
                
        except Exception as e:
            log_error(e, "refresh_access_token")
            return {'status': 'failed', 'message': str(e)}
    
    # ============================================================================
    # Device Code Flow (QR Code Authentication)
    # ============================================================================
    
    def get_device_code(self) -> Dict[str, Any]:
        """Get device code and QR code for authentication"""
        try:
            params = {'client_id': self.client_id}
            response = self.session.get(
                'https://www.terabox.com/oauth/devicecode',
                params=params
            )
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('errno') == 0:
                data = result['data']
                return {
                    'status': 'success',
                    'device_code': data['device_code'],
                    'qrcode_url': data['qrcode_url'],
                    'expires_in': data['expires_in'],
                    'interval': data['interval']
                }
            else:
                return {'status': 'failed', 'message': f"Error {result.get('errno')}"}
                
        except Exception as e:
            log_error(e, "get_device_code")
            return {'status': 'failed', 'message': str(e)}
    
    def poll_device_token(self, device_code: str) -> Dict[str, Any]:
        """Poll for access token using device code"""
        timestamp = int(time.time())
        sign = self._generate_signature(timestamp)
        
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'device_code',
            'code': device_code,
            'timestamp': timestamp,
            'sign': sign
        }
        
        try:
            response = self.session.post(
                'https://www.terabox.com/oauth/gettoken',
                data=data
            )
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('errno') == 0:
                token_data = result['data']
                self.access_token = token_data['access_token']
                self.refresh_token = token_data['refresh_token']
                
                return {
                    'status': 'success',
                    'access_token': self.access_token,
                    'refresh_token': self.refresh_token,
                    'expires_in': token_data['expires_in']
                }
            elif result.get('errno') == 400001:
                return {'status': 'pending', 'message': 'User has not completed authorization'}
            else:
                return {'status': 'failed', 'message': f"Error {result.get('errno')}"}
                
        except Exception as e:
            log_error(e, "poll_device_token")
            return {'status': 'failed', 'message': str(e)}
    
    # ============================================================================
    # User Information APIs
    # ============================================================================
    
    def get_user_info(self) -> Dict[str, Any]:
        """Get user basic information"""
        if not self.access_token:
            return {'status': 'failed', 'message': 'No access token'}
        
        try:
            params = {'access_token': self.access_token}
            response = self.session.get(
                f'https://{self.api_domain}/openapi/uinfo',
                params=params
            )
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('errno') == 0:
                return {
                    'status': 'success',
                    'username': result['uname'],
                    'avatar_url': result['avatar_url'],
                    'vip_type': result['vip_type'],
                    'uk': result['uk'],
                    'use_type': result['use_type'],
                    'user_type': result['user_type']
                }
            else:
                return {'status': 'failed', 'message': f"Error {result.get('errno')}"}
                
        except Exception as e:
            log_error(e, "get_user_info")
            return {'status': 'failed', 'message': str(e)}
    
    def get_quota_info(self) -> Dict[str, Any]:
        """Get user storage quota information"""
        if not self.access_token:
            return {'status': 'failed', 'message': 'No access token'}
        
        try:
            params = {'access_token': self.access_token}
            response = self.session.get(
                f'https://{self.api_domain}/openapi/api/quota',
                params=params
            )
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('errno') == 0:
                total_gb = result['total'] / (1024**3)
                used_gb = result['used'] / (1024**3)
                free_gb = total_gb - used_gb
                
                return {
                    'status': 'success',
                    'total': result['total'],
                    'used': result['used'],
                    'free': result['total'] - result['used'],
                    'total_gb': round(total_gb, 2),
                    'used_gb': round(used_gb, 2),
                    'free_gb': round(free_gb, 2),
                    'usage_percent': round((used_gb / total_gb) * 100, 1)
                }
            else:
                return {'status': 'failed', 'message': f"Error {result.get('errno')}"}
                
        except Exception as e:
            log_error(e, "get_quota_info")
            return {'status': 'failed', 'message': str(e)}
    
    def activate_external_link_sharing(self) -> Dict[str, Any]:
        """Activate external link sharing capability"""
        if not self.access_token:
            return {'status': 'failed', 'message': 'No access token'}
        
        try:
            params = {'access_token': self.access_token}
            response = self.session.get(
                f'https://{self.api_domain}/openapi/active',
                params=params
            )
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('errno') == 0:
                return {
                    'status': 'success',
                    'order_id': result['order_id']
                }
            else:
                return {'status': 'failed', 'message': f"Error {result.get('errno')}"}
                
        except Exception as e:
            log_error(e, "activate_external_link_sharing")
            return {'status': 'failed', 'message': str(e)}
    
    # ============================================================================
    # File Management APIs
    # ============================================================================
    
    def list_files(self, directory: str = "/", page: int = 1, num: int = 100, 
                   order: str = "time", desc: int = 1, web: int = 1) -> Dict[str, Any]:
        """List files in directory"""
        if not self.access_token:
            return {'status': 'failed', 'message': 'No access token'}
        
        try:
            params = {
                'access_token': self.access_token,
                'dir': directory,
                'page': page,
                'num': num,
                'order': order,
                'desc': desc,
                'web': web
            }
            
            response = self.session.get(
                f'https://{self.api_domain}/openapi/api/list',
                params=params
            )
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('errno') == 0:
                return {
                    'status': 'success',
                    'files': result['list'],
                    'guid': result.get('guid', 0)
                }
            else:
                return {'status': 'failed', 'message': f"Error {result.get('errno')}"}
                
        except Exception as e:
            log_error(e, "list_files")
            return {'status': 'failed', 'message': str(e)}
    
    def get_file_info(self, file_paths: List[str], include_download_link: bool = False) -> Dict[str, Any]:
        """Get file metadata information"""
        if not self.access_token:
            return {'status': 'failed', 'message': 'No access token'}
        
        try:
            # URL encode the file paths
            encoded_paths = [quote(path, safe='') for path in file_paths]
            target_param = json.dumps(encoded_paths)
            
            params = {
                'access_token': self.access_token,
                'target': target_param,
                'dlink': 1 if include_download_link else 0
            }
            
            response = self.session.get(
                f'https://{self.api_domain}/openapi/api/filemetas',
                params=params
            )
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('errno') == 0:
                return {
                    'status': 'success',
                    'files': result['info']
                }
            else:
                return {'status': 'failed', 'message': f"Error {result.get('errno')}"}
                
        except Exception as e:
            log_error(e, "get_file_info")
            return {'status': 'failed', 'message': str(e)}
    
    def search_files(self, keyword: str, page: int = 1, num: int = 100, 
                     order: str = "time", desc: int = 1) -> Dict[str, Any]:
        """Search files by keyword"""
        if not self.access_token:
            return {'status': 'failed', 'message': 'No access token'}
        
        try:
            params = {
                'access_token': self.access_token,
                'key': keyword,
                'page': page,
                'num': num,
                'order': order,
                'desc': desc,
                'recursion': 1
            }
            
            response = self.session.get(
                f'https://{self.api_domain}/openapi/api/search',
                params=params
            )
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('errno') == 0:
                return {
                    'status': 'success',
                    'files': result['list'],
                    'has_more': result['has_more']
                }
            else:
                return {'status': 'failed', 'message': f"Error {result.get('errno')}"}
                
        except Exception as e:
            log_error(e, "search_files")
            return {'status': 'failed', 'message': str(e)}
    
    def get_download_links(self, file_ids: List[str]) -> Dict[str, Any]:
        """Get download links for files"""
        if not self.access_token:
            return {'status': 'failed', 'message': 'No access token'}
        
        try:
            fidlist_param = json.dumps(file_ids)
            
            params = {
                'access_token': self.access_token,
                'fidlist': fidlist_param,
                'type': 'dlink'
            }
            
            response = self.session.get(
                f'https://{self.api_domain}/openapi/api/download',
                params=params
            )
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('errno') == 0:
                return {
                    'status': 'success',
                    'download_links': result['dlink']
                }
            else:
                return {'status': 'failed', 'message': f"Error {result.get('errno')}"}
                
        except Exception as e:
            log_error(e, "get_download_links")
            return {'status': 'failed', 'message': str(e)}
    
    def get_streaming_url(self, file_path: str, stream_type: str = "M3U8_AUTO_720") -> Dict[str, Any]:
        """Get streaming URL for video/audio files"""
        if not self.access_token:
            return {'status': 'failed', 'message': 'No access token'}
        
        try:
            params = {
                'access_token': self.access_token,
                'path': file_path,
                'type': stream_type
            }
            
            response = self.session.get(
                f'https://{self.api_domain}/openapi/api/streaming',
                params=params
            )
            response.raise_for_status()
            
            # Response is M3U8 content, not JSON
            return {
                'status': 'success',
                'streaming_url': response.url,
                'content': response.text
            }
                
        except Exception as e:
            log_error(e, "get_streaming_url")
            return {'status': 'failed', 'message': str(e)}
    
    # ============================================================================
    # Share Management APIs
    # ============================================================================
    
    def verify_share_password(self, short_url: str, password: str) -> Dict[str, Any]:
        """Verify share extraction password"""
        if not self.access_token:
            return {'status': 'failed', 'message': 'No access token'}
        
        try:
            params = {
                'access_token': self.access_token,
                'surl': short_url
            }
            
            data = {'pwd': password}
            
            response = self.session.post(
                f'https://{self.api_domain}/openapi/share/verify',
                params=params,
                data=data
            )
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('errno') == 0:
                # Extract BOXCLND cookie from response headers
                set_cookie = response.headers.get('Set-Cookie', '')
                boxclnd = None
                if 'BOXCLND' in set_cookie:
                    # Parse BOXCLND value from Set-Cookie header
                    import re
                    match = re.search(r'BOXCLND=([^;]+)', set_cookie)
                    if match:
                        boxclnd = match.group(1)
                
                return {
                    'status': 'success',
                    'randsk': result['randsk'],
                    'boxclnd': boxclnd
                }
            else:
                return {'status': 'failed', 'message': f"Error {result.get('errno')}"}
                
        except Exception as e:
            log_error(e, "verify_share_password")
            return {'status': 'failed', 'message': str(e)}
    
    def get_share_info(self, short_url: str, spd: str = None) -> Dict[str, Any]:
        """Get share details"""
        if not self.access_token:
            return {'status': 'failed', 'message': 'No access token'}
        
        try:
            params = {
                'access_token': self.access_token,
                'shorturl': short_url,
                'root': 1
            }
            
            if spd:
                params['spd'] = spd
            
            response = self.session.get(
                f'https://{self.api_domain}/openapi/api/shorturlinfo',
                params=params
            )
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('errno') == 0:
                return {
                    'status': 'success',
                    'share_info': result
                }
            else:
                return {'status': 'failed', 'message': f"Error {result.get('errno')}"}
                
        except Exception as e:
            log_error(e, "get_share_info")
            return {'status': 'failed', 'message': str(e)}
    
    def get_share_file_list(self, short_url: str, sekey: str, page: int = 1, 
                           num: int = 20, directory: str = "", root: int = 1) -> Dict[str, Any]:
        """Get file list from share"""
        if not self.access_token:
            return {'status': 'failed', 'message': 'No access token'}
        
        try:
            params = {
                'access_token': self.access_token,
                'shorturl': short_url,
                'sekey': sekey,
                'page': page,
                'num': num,
                'root': root
            }
            
            if directory and root != 1:
                params['dir'] = directory
            
            response = self.session.get(
                f'https://{self.api_domain}/openapi/share/list',
                params=params
            )
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('errno') == 0:
                return {
                    'status': 'success',
                    'files': result['list'],
                    'share_id': result['share_id'],
                    'uk': result['uk']
                }
            else:
                return {'status': 'failed', 'message': f"Error {result.get('errno')}"}
                
        except Exception as e:
            log_error(e, "get_share_file_list")
            return {'status': 'failed', 'message': str(e)}
    
    def get_share_download_links(self, share_id: str, file_ids: List[str], 
                                uk: str, sekey: str) -> Dict[str, Any]:
        """Get download links for shared files"""
        if not self.access_token:
            return {'status': 'failed', 'message': 'No access token'}
        
        try:
            params = {
                'access_token': self.access_token,
                'shareid': share_id,
                'fid_list': json.dumps(file_ids),
                'uk': uk,
                'sekey': sekey
            }
            
            response = self.session.get(
                f'https://{self.api_domain}/openapi/share/download',
                params=params
            )
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('errno') == 0:
                return {
                    'status': 'success',
                    'download_info': result
                }
            else:
                return {'status': 'failed', 'message': f"Error {result.get('errno')}"}
                
        except Exception as e:
            log_error(e, "get_share_download_links")
            return {'status': 'failed', 'message': str(e)}
    
    # ============================================================================
    # Utility Methods
    # ============================================================================
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return self.access_token is not None
    
    def get_credentials_status(self) -> Dict[str, bool]:
        """Get status of required credentials"""
        return {
            'client_id': bool(self.client_id),
            'client_secret': bool(self.client_secret),
            'private_secret': bool(self.private_secret),
            'access_token': bool(self.access_token),
            'refresh_token': bool(self.refresh_token)
        }

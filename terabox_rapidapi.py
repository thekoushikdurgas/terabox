"""
TeraBox RapidAPI Integration Module
Commercial API service for TeraBox file extraction

This module provides access to RapidAPI's TeraBox downloader service
which offers reliable, commercial-grade TeraBox file processing.
"""

import requests
import time
from typing import Dict, List, Any, Optional
from config import log_error, log_info

class TeraBoxRapidAPI:
    """RapidAPI-based TeraBox client for commercial service integration"""
    
    def __init__(self, rapidapi_key: str = None):
        self.rapidapi_key = rapidapi_key
        self.base_url = "https://terabox-downloader-direct-download-link-generator2.p.rapidapi.com"
        self.session = requests.Session()
        
        # Set up session headers
        if self.rapidapi_key:
            self.session.headers.update({
                'X-RapidAPI-Key': self.rapidapi_key,
                'X-RapidAPI-Host': 'terabox-downloader-direct-download-link-generator2.p.rapidapi.com',
                'User-Agent': 'TeraDL-RapidAPI-Client/1.0'
            })
    
    def set_api_key(self, api_key: str):
        """Set or update the RapidAPI key"""
        self.rapidapi_key = api_key
        self.session.headers.update({
            'X-RapidAPI-Key': api_key,
            'X-RapidAPI-Host': 'terabox-downloader-direct-download-link-generator2.p.rapidapi.com'
        })
        log_info("RapidAPI key updated successfully")
    
    def validate_api_key(self) -> Dict[str, Any]:
        """Validate if the current API key is working"""
        if not self.rapidapi_key:
            return {'status': 'failed', 'message': 'No API key provided'}
        
        try:
            # Test with a sample URL
            test_url = "https://www.terabox.app/sharing/link?surl=test"
            response = self.session.get(
                f"{self.base_url}/url",
                params={'url': test_url},
                timeout=10
            )
            
            if response.status_code == 200:
                return {'status': 'success', 'message': 'API key is valid'}
            elif response.status_code == 401:
                return {'status': 'failed', 'message': 'Invalid API key'}
            elif response.status_code == 403:
                return {'status': 'failed', 'message': 'API key access denied'}
            elif response.status_code == 429:
                return {'status': 'failed', 'message': 'Rate limit exceeded'}
            else:
                return {'status': 'failed', 'message': f'HTTP {response.status_code}'}
                
        except Exception as e:
            log_error(e, "validate_api_key")
            return {'status': 'failed', 'message': str(e)}
    
    def get_file_info(self, terabox_url: str) -> Dict[str, Any]:
        """
        Get file information from TeraBox URL using RapidAPI service
        Returns: direct_link, file_name, size, sizebytes, thumb, or error
        """
        if not self.rapidapi_key:
            return {'error': 'No RapidAPI key provided. Please configure your API key.'}
        
        try:
            log_info(f"Getting file info via RapidAPI for: {terabox_url}")
            
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
    
    def download_file(self, file_info: Dict[str, Any], save_path: str = None) -> Dict[str, Any]:
        """
        Download file using the direct link from RapidAPI
        Note: This uses the direct link, not the RapidAPI service for download
        """
        if 'error' in file_info:
            return file_info
        
        if not file_info.get('direct_link') and not file_info.get('download_link'):
            return {'error': 'No download link available'}
        
        try:
            import os
            
            # Prepare save path
            if save_path is None:
                save_path = os.getcwd()
            
            os.makedirs(save_path, exist_ok=True)
            
            file_name = file_info.get('file_name', 'downloaded_file')
            file_path = os.path.join(save_path, file_name)
            
            # Use direct link or download link
            download_url = file_info.get('direct_link') or file_info.get('download_link')
            
            log_info(f"Starting download via RapidAPI link: {file_name}")
            
            # Download with progress tracking
            response = requests.get(download_url, stream=True, timeout=60)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', file_info.get('sizebytes', 0)))
            downloaded = 0
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
            
            log_info(f"Download completed: {file_path}")
            return {'file_path': file_path, 'size': downloaded}
            
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

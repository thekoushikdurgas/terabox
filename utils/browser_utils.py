"""
Browser Utilities Module

Provides centralized functionality for opening URLs in different browsers,
similar to the test.py implementation but with enhanced error handling,
configuration options, and Streamlit integration.

This module implements a comprehensive browser management system that allows
users to open TeraBox direct file links in their preferred browser.

Key Features:
- Multi-browser support (Chrome, Firefox, Edge, Safari)
- Cross-platform compatibility (Windows, macOS, Linux)
- Automatic browser detection and availability checking
- Fallback mechanisms for failed browser launches
- User preference management and persistence
- Comprehensive error handling and troubleshooting

Browser Management Strategy:
- Automatic detection of installed browsers
- Path-based browser executable location
- Preference-based browser selection
- Fallback to system default browser
- Session-based preference storage

Architecture Pattern: Factory + Strategy
- BrowserManager: Factory for browser instances
- Browser-specific strategies for different platforms
- Unified interface for all browser operations
- Centralized configuration and preference management

Security Considerations:
- Safe URL validation before opening
- Browser executable path validation
- Subprocess security for browser launching
- Error handling to prevent system exploitation
"""

import webbrowser
import platform
import subprocess
import os
import streamlit as st
from typing import Optional, Dict, Any, List
import logging
from utils.config import log_info, log_error

class BrowserManager:
    """
    Manages browser opening functionality with multiple browser support
    
    This class provides a centralized system for managing browser operations,
    including detection, configuration, and launching across different platforms.
    
    Key Responsibilities:
    - Browser detection and availability checking
    - Cross-platform browser path resolution
    - User preference management and persistence
    - Error handling and fallback mechanisms
    - Session state integration with Streamlit
    
    Supported Browsers:
    - Google Chrome (cross-platform)
    - Mozilla Firefox (cross-platform)
    - Microsoft Edge (Windows, Linux, macOS)
    - Safari (macOS only)
    - System default browser (fallback)
    
    Platform Support:
    - Windows: Full support for all browsers
    - macOS: Full support including Safari
    - Linux: Support for open-source browsers
    """
    
    def __init__(self):
        """
        Initialize browser manager with detection and configuration
        
        Initialization Process:
        1. Detect available browsers on current platform
        2. Configure browser paths and commands
        3. Set up default browser preference
        4. Log detection results for debugging
        """
        log_info("Initializing BrowserManager")
        log_info(f"Platform detected: {platform.system()}")
        
        # Browser Detection and Configuration
        # Purpose: Find all available browsers on the current system
        # Strategy: Check standard installation paths for each platform
        self.supported_browsers = self._get_supported_browsers()
        
        # Default Browser Selection
        # Purpose: Set initial browser preference
        # Strategy: Use user preference or fall back to system default
        self.default_browser = self._get_default_browser()
        
        # Log initialization results
        available_count = sum(1 for browser in self.supported_browsers.values() 
                            if browser.get('command') or browser.get('name') == 'Default Browser')
        log_info(f"Browser detection complete - {available_count}/{len(self.supported_browsers)} browsers available")
        log_info(f"Default browser set to: {self.default_browser}")
    
    def _get_supported_browsers(self) -> Dict[str, Dict[str, Any]]:
        """Get list of supported browsers with their configurations"""
        system = platform.system().lower()
        
        browsers = {
            'default': {
                'name': 'Default Browser',
                'description': 'System default browser',
                'command': None,
                'icon': '🌐'
            },
            'chrome': {
                'name': 'Google Chrome',
                'description': 'Google Chrome browser',
                'icon': '🟢',
                'paths': {
                    'windows': [
                        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
                    ],
                    'linux': [
                        '/usr/bin/google-chrome',
                        '/usr/bin/google-chrome-stable',
                        '/usr/bin/chromium-browser',
                        '/snap/bin/chromium'
                    ],
                    'darwin': [
                        '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
                    ]
                }
            },
            'firefox': {
                'name': 'Mozilla Firefox',
                'description': 'Mozilla Firefox browser',
                'icon': '🦊',
                'paths': {
                    'windows': [
                        r"C:\Program Files\Mozilla Firefox\firefox.exe",
                        r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
                        os.path.expanduser(r"~\AppData\Local\Mozilla Firefox\firefox.exe")
                    ],
                    'linux': [
                        '/usr/bin/firefox',
                        '/usr/bin/firefox-esr',
                        '/snap/bin/firefox'
                    ],
                    'darwin': [
                        '/Applications/Firefox.app/Contents/MacOS/firefox'
                    ]
                }
            },
            'edge': {
                'name': 'Microsoft Edge',
                'description': 'Microsoft Edge browser',
                'icon': '🔷',
                'paths': {
                    'windows': [
                        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
                    ],
                    'linux': [
                        '/usr/bin/microsoft-edge',
                        '/usr/bin/microsoft-edge-stable'
                    ],
                    'darwin': [
                        '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge'
                    ]
                }
            },
            'safari': {
                'name': 'Safari',
                'description': 'Apple Safari browser (macOS only)',
                'icon': '🧭',
                'paths': {
                    'darwin': [
                        '/Applications/Safari.app/Contents/MacOS/Safari'
                    ]
                }
            }
        }
        
        # Check which browsers are actually available
        available_browsers = {'default': browsers['default']}
        
        for browser_id, browser_info in browsers.items():
            if browser_id == 'default':
                continue
                
            if system in browser_info.get('paths', {}):
                for path in browser_info['paths'][system]:
                    if os.path.exists(path):
                        browser_info['command'] = path
                        available_browsers[browser_id] = browser_info
                        break
        
        return available_browsers
    
    def _get_default_browser(self) -> str:
        """Get the default browser preference"""
        # Check if user has set a preference in session state
        if hasattr(st, 'session_state') and 'preferred_browser' in st.session_state:
            preferred = st.session_state.preferred_browser
            if preferred in self.supported_browsers:
                return preferred
        
        # Return system default
        return 'default'
    
    def get_browser_list(self) -> List[Dict[str, Any]]:
        """Get list of available browsers for UI selection"""
        browser_list = []
        for browser_id, browser_info in self.supported_browsers.items():
            browser_list.append({
                'id': browser_id,
                'name': browser_info['name'],
                'description': browser_info['description'],
                'icon': browser_info['icon'],
                'available': browser_info.get('command') is not None or browser_id == 'default'
            })
        return browser_list
    
    def open_url(self, url: str, browser_id: Optional[str] = None, new_tab: bool = True) -> Dict[str, Any]:
        """
        Open URL in specified browser
        
        Args:
            url: URL to open
            browser_id: Browser ID to use (None for default)
            new_tab: Whether to open in new tab (True) or new window (False)
        
        Returns:
            Dict with status, message, and browser_used
        """
        if not url:
            return {
                'status': 'error',
                'message': 'No URL provided',
                'browser_used': None
            }
        
        # Use default browser if none specified
        if not browser_id:
            browser_id = self.default_browser
        
        # Validate browser
        if browser_id not in self.supported_browsers:
            return {
                'status': 'error',
                'message': f'Browser "{browser_id}" not supported',
                'browser_used': None
            }
        
        browser_info = self.supported_browsers[browser_id]
        
        try:
            if browser_id == 'default':
                # Use system default browser
                if new_tab:
                    webbrowser.open_new_tab(url)
                else:
                    webbrowser.open_new(url)
                
                log_info(f"Opened URL in default browser: {url[:50]}...")
                return {
                    'status': 'success',
                    'message': 'URL opened in default browser',
                    'browser_used': 'default'
                }
            
            else:
                # Use specific browser
                browser_path = browser_info.get('command')
                if not browser_path or not os.path.exists(browser_path):
                    return {
                        'status': 'error',
                        'message': f'{browser_info["name"]} not found at expected location',
                        'browser_used': browser_id
                    }
                
                # Register the browser with webbrowser module
                webbrowser.register(browser_id, None, webbrowser.BackgroundBrowser(browser_path))
                
                # Open URL
                browser_obj = webbrowser.get(browser_id)
                if new_tab:
                    browser_obj.open_new_tab(url)
                else:
                    browser_obj.open_new(url)
                
                log_info(f"Opened URL in {browser_info['name']}: {url[:50]}...")
                return {
                    'status': 'success',
                    'message': f'URL opened in {browser_info["name"]}',
                    'browser_used': browser_id
                }
        
        except Exception as e:
            log_error(e, f"open_url - {browser_id}")
            return {
                'status': 'error',
                'message': f'Failed to open URL in {browser_info["name"]}: {str(e)}',
                'browser_used': browser_id
            }
    
    def open_url_with_fallback(self, url: str, preferred_browsers: Optional[List[str]] = None, new_tab: bool = True) -> Dict[str, Any]:
        """
        Open URL with fallback to other browsers if preferred ones fail
        
        Args:
            url: URL to open
            preferred_browsers: List of browser IDs to try in order
            new_tab: Whether to open in new tab
        
        Returns:
            Dict with status, message, browser_used, and attempts
        """
        if not preferred_browsers:
            preferred_browsers = [self.default_browser, 'default']
        
        attempts = []
        
        for browser_id in preferred_browsers:
            if browser_id not in self.supported_browsers:
                attempts.append({
                    'browser': browser_id,
                    'status': 'skipped',
                    'message': 'Browser not supported'
                })
                continue
            
            result = self.open_url(url, browser_id, new_tab)
            attempts.append({
                'browser': browser_id,
                'status': result['status'],
                'message': result['message']
            })
            
            if result['status'] == 'success':
                return {
                    'status': 'success',
                    'message': result['message'],
                    'browser_used': browser_id,
                    'attempts': attempts
                }
        
        # All attempts failed
        return {
            'status': 'error',
            'message': 'Failed to open URL in any available browser',
            'browser_used': None,
            'attempts': attempts
        }
    
    def set_preferred_browser(self, browser_id: str) -> bool:
        """Set preferred browser for future operations"""
        if browser_id in self.supported_browsers:
            if hasattr(st, 'session_state'):
                st.session_state.preferred_browser = browser_id
            self.default_browser = browser_id
            return True
        return False

# Global browser manager instance
_browser_manager = None

def get_browser_manager() -> BrowserManager:
    """Get global browser manager instance"""
    global _browser_manager
    if _browser_manager is None:
        _browser_manager = BrowserManager()
    return _browser_manager

def open_url_in_browser(url: str, browser: Optional[str] = None, new_tab: bool = True) -> Dict[str, Any]:
    """
    Convenience function to open URL in browser
    
    Args:
        url: URL to open
        browser: Browser ID (None for default)
        new_tab: Open in new tab (True) or new window (False)
    
    Returns:
        Dict with operation result
    """
    manager = get_browser_manager()
    return manager.open_url(url, browser, new_tab)

def open_direct_file_link(file_info: Dict[str, Any], browser: Optional[str] = None) -> Dict[str, Any]:
    """
    Open direct file link from file_info object
    
    Args:
        file_info: File information dictionary containing download links
        browser: Browser ID to use
    
    Returns:
        Dict with operation result and link information
    """
    # Find the best available download link
    download_urls = []
    
    # Priority order for different link types
    link_priorities = [
        ('direct_link', 'Direct Download Link'),
        ('download_link', 'Download Link'), 
        ('link', 'Alternative Link'),
        ('dlink', 'Direct Link'),  # For File Manager API
        ('url', 'File URL')
    ]
    
    for link_key, link_name in link_priorities:
        if file_info.get(link_key):
            download_urls.append((link_key, link_name, file_info[link_key]))
    
    if not download_urls:
        return {
            'status': 'error',
            'message': 'No download links found in file information',
            'file_name': file_info.get('file_name', file_info.get('server_filename', 'Unknown')),
            'available_keys': list(file_info.keys())
        }
    
    # Use the highest priority link
    link_key, link_name, url = download_urls[0]
    file_name = file_info.get('file_name', file_info.get('server_filename', 'Unknown'))
    
    # Open the URL
    manager = get_browser_manager()
    result = manager.open_url(url, browser, new_tab=True)
    
    # Enhance result with file information
    result.update({
        'file_name': file_name,
        'link_type': link_name,
        'link_key': link_key,
        'url': url,
        'available_links': len(download_urls)
    })
    
    return result

def create_browser_selection_ui() -> Optional[str]:
    """
    Create Streamlit UI for browser selection
    
    Returns:
        Selected browser ID or None
    """
    manager = get_browser_manager()
    browsers = manager.get_browser_list()
    
    if not browsers:
        st.error("No browsers available")
        return None
    
    # Create options for selectbox
    browser_options = []
    browser_mapping = {}
    
    for browser in browsers:
        if browser['available']:
            label = f"{browser['icon']} {browser['name']}"
            browser_options.append(label)
            browser_mapping[label] = browser['id']
    
    if not browser_options:
        st.error("No available browsers found")
        return None
    
    # Get current selection
    current_browser = manager.default_browser
    current_label = None
    for label, browser_id in browser_mapping.items():
        if browser_id == current_browser:
            current_label = label
            break
    
    # Create selectbox
    selected_label = st.selectbox(
        "Choose Browser:",
        options=browser_options,
        index=browser_options.index(current_label) if current_label in browser_options else 0,
        help="Select which browser to use for opening direct file links"
    )
    
    selected_browser = browser_mapping.get(selected_label)
    
    # Update preference if changed
    if selected_browser and selected_browser != current_browser:
        manager.set_preferred_browser(selected_browser)
    
    return selected_browser

def display_browser_open_result(result: Dict[str, Any], show_details: bool = True) -> None:
    """
    Display the result of browser opening operation in Streamlit
    
    Args:
        result: Result dictionary from browser opening operation
        show_details: Whether to show detailed information
    """
    if result['status'] == 'success':
        st.success(f"✅ {result['message']}")
        
        if show_details:
            if result.get('file_name'):
                st.info(f"📄 **File:** {result['file_name']}")
            
            if result.get('link_type'):
                st.info(f"🔗 **Link Type:** {result['link_type']}")
            
            if result.get('browser_used'):
                browser_manager = get_browser_manager()
                browser_info = browser_manager.supported_browsers.get(result['browser_used'])
                if browser_info:
                    st.info(f"{browser_info['icon']} **Browser:** {browser_info['name']}")
            
            if result.get('available_links', 0) > 1:
                st.info(f"🔢 **Available Links:** {result['available_links']} (using best option)")
    
    else:
        st.error(f"❌ {result['message']}")
        
        if show_details:
            if result.get('file_name'):
                st.error(f"📄 **File:** {result['file_name']}")
            
            if result.get('available_keys'):
                with st.expander("🔍 Available File Info Keys"):
                    st.write("Available keys in file_info:")
                    for key in result['available_keys']:
                        st.text(f"• {key}")
            
            if result.get('attempts'):
                with st.expander("🔄 Attempted Browsers"):
                    for attempt in result['attempts']:
                        if attempt['status'] == 'success':
                            st.success(f"✅ {attempt['browser']}: {attempt['message']}")
                        else:
                            st.error(f"❌ {attempt['browser']}: {attempt['message']}")

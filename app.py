"""
TeraDL Main Application
Streamlit-based TeraBox file downloader and streaming platform

This is the main entry point for the TeraDL application, providing a unified interface
for accessing TeraBox files through multiple methods:

Application Architecture:
- Multi-mode support: Unofficial, Cookie, Official API, RapidAPI
- State management: Centralized session state handling
- UI management: Responsive interface with progress tracking
- Error handling: Comprehensive error recovery and user guidance
- Browser integration: Direct file link opening in preferred browser

Design Patterns:
- Strategy Pattern: Different extraction modes with common interface
- State Pattern: Session state management for UI consistency
- Facade Pattern: Simplified interface hiding complexity
- Observer Pattern: Progress tracking and status updates

Key Features:
- Unified extraction interface across all modes
- Real-time progress tracking for long operations
- Intelligent error handling with user guidance
- Browser integration for direct file access
- File filtering and sorting capabilities
- Responsive design with mobile support
"""

import streamlit as st
import requests
import os
import tempfile
from urllib.parse import urlparse
from utils.terabox_core import TeraboxCore
from utils.terabox_official_api import TeraBoxOfficialAPI
from utils.terabox_cookie_api import TeraBoxCookieAPI
from utils.terabox_rapidapi import TeraBoxRapidAPI
import time
from typing import Dict, Any, List
import base64
import json
from utils.browser_utils import open_direct_file_link, display_browser_open_result, create_browser_selection_ui
from utils.state_manager import StateManager, BatchStateUpdate
from utils.ui_manager import UIManager, show_success_if, show_error_if
from utils.config import log_info, log_error

# Page configuration
st.set_page_config(
    page_title="TeraDL - TeraBox Downloader & Streaming",
    page_icon="📁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #586afa;
        font-size: 2.5rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        text-align: center;
        color: #212f99;
        font-size: 1rem;
        margin-bottom: 2rem;
    }
    .file-card {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .file-name {
        font-weight: 500;
        color: #6c79df;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }
    .file-info {
        color: #666;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
    }
    .download-section {
        margin-top: 1rem;
        padding-top: 1rem;
        border-top: 1px solid #eee;
    }
    .video-player {
        border-radius: 8px;
        margin: 1rem 0;
    }
    .mode-indicator {
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
        margin-bottom: 1rem;
    }
    .mode-1 { background: #ff7777; color: white; }
    .mode-2 { background: #77ff7e; color: black; }
    .mode-3 { background: #ffaa77; color: black; }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
# Purpose: Initialize critical application state variables
# Pattern: Defensive initialization to prevent KeyError exceptions
# Strategy: Only initialize if not already present to preserve user data
log_info("Initializing application session state")

if 'files_data' not in st.session_state:
    st.session_state.files_data = None
    log_info("Initialized files_data state")

if 'extraction_params' not in st.session_state:
    st.session_state.extraction_params = None
    log_info("Initialized extraction_params state")

if 'api_mode' not in st.session_state:
    st.session_state.api_mode = 'unofficial'  # Default to unofficial mode
    log_info("Initialized api_mode state with default: unofficial")

if 'official_api' not in st.session_state:
    st.session_state.official_api = None
    log_info("Initialized official_api state")

if 'cookie_api' not in st.session_state:
    st.session_state.cookie_api = None
    log_info("Initialized cookie_api state")

if 'rapidapi_client' not in st.session_state:
    st.session_state.rapidapi_client = None
    log_info("Initialized rapidapi_client state")

# Log current session state for debugging
active_apis = []
if st.session_state.official_api:
    active_apis.append("Official")
if st.session_state.cookie_api:
    active_apis.append("Cookie")
if st.session_state.rapidapi_client:
    active_apis.append("RapidAPI")

log_info(f"Session state initialization complete - Active APIs: {active_apis if active_apis else 'None'}, Mode: {st.session_state.api_mode}")

def display_header():
    """Display the main header"""
    st.markdown('<h1 class="main-header">TeraDL</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">TeraBox Video Downloader & Streaming Platform</p>', unsafe_allow_html=True)

def display_mode_indicator(mode: int):
    """Display current processing mode"""
    mode_info = {
        1: ("Mode 1: Dynamic Cookies", "mode-1", "Real-time scraping with dynamic cookies"),
        2: ("Mode 2: Static Cookies", "mode-2", "Static cookies from admin session"),
        3: ("Mode 3: External Service", "mode-3", "Uses external service for processing")
    }
    
    title, css_class, description = mode_info.get(mode, ("Unknown Mode", "mode-1", "Unknown processing mode"))
    
    st.markdown(f'''
    <div class="mode-indicator {css_class}">
        {title} - {description}
    </div>
    ''', unsafe_allow_html=True)

def extract_files_from_url(url: str, mode: int = None) -> Dict[str, Any]:
    """
    Extract files from TeraBox URL with comprehensive error handling and mode routing
    
    This function serves as the central dispatcher for file extraction across all
    supported modes, providing a unified interface regardless of the underlying method.
    
    Args:
        url: TeraBox share URL to process
        mode: Processing mode for unofficial extraction (1, 2, or 3)
        
    Returns:
        Dict containing extraction results or error information
        
    Processing Flow:
    1. Determine active API mode from session state
    2. Route to appropriate extraction method
    3. Handle mode-specific initialization and processing
    4. Provide unified result format across all modes
    5. Comprehensive error handling and user feedback
    
    Mode Routing:
    - unofficial: Uses TeraboxCore with configurable processing modes
    - official: Uses TeraBox Official API with OAuth authentication
    - cookie: Uses session cookie for authenticated requests
    - rapidapi: Uses commercial RapidAPI service
    """
    log_info(f"Starting file extraction - URL: {url[:100]}{'...' if len(url) > 100 else ''}")
    log_info(f"Extraction parameters - Mode: {mode}, Session API mode: {st.session_state.api_mode}")
    
    # UI Progress Tracking
    # Purpose: Provide visual feedback for long-running operations
    # Pattern: Progress bar + status text for detailed feedback
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # API Mode Determination
        # Purpose: Route request to appropriate extraction method
        # Source: Session state maintains user's mode selection
        api_mode = st.session_state.api_mode
        log_info(f"Routing extraction to {api_mode} mode")
        
        if api_mode == 'unofficial':
            # Unofficial Mode Processing
            # Strategy: Direct scraping using TeraboxCore
            # Benefits: No authentication required, works immediately
            # Limitations: May be blocked, limited to share links
            log_info(f"Processing with unofficial mode {mode}")
            
            status_text.text("🔧 Initializing TeraBox processor...")
            progress_bar.progress(20)
            
            # Initialize TeraBox core processor with specified mode
            terabox = TeraboxCore(mode=mode)
            log_info(f"TeraboxCore initialized successfully for mode {mode}")
            
            status_text.text("🔍 Extracting files from TeraBox URL...")
            progress_bar.progress(40)
            
            # Execute extraction with comprehensive logging
            extraction_start = time.time()
            result = terabox.extract_files(url)
            extraction_duration = time.time() - extraction_start
            
            log_info(f"Unofficial extraction completed in {extraction_duration:.2f}s - Status: {result.get('status', 'unknown')}")
            
        elif api_mode == 'official':  # Official API mode
            if not st.session_state.official_api or not st.session_state.official_api.is_authenticated():
                return {'status': 'failed', 'message': 'Official API not authenticated. Please configure in API Mode page.'}
            
            status_text.text("🔧 Initializing Official API...")
            progress_bar.progress(20)
            
            api = st.session_state.official_api
            
            status_text.text("🔍 Processing TeraBox URL with Official API...")
            progress_bar.progress(40)
            
            # Extract short URL from the full URL
            import re
            short_url_match = re.search(r'/s/([^/?]+)', url)
            if not short_url_match:
                return {'status': 'failed', 'message': 'Could not extract short URL from the provided link'}
            
            short_url = short_url_match.group(1)
            
            # Try to get share info
            share_info = api.get_share_info(short_url)
            
            if share_info.get('status') == 'success':
                share_data = share_info['share_info']
                
                # Convert to our standard format
                result = {
                    'status': 'success',
                    'uk': share_data.get('uk'),
                    'shareid': share_data.get('shareid'),
                    'sign': share_data.get('sign'),
                    'timestamp': share_data.get('timestamp'),
                    'list': []
                }
                
                # Process file list
                if 'list' in share_data:
                    for item in share_data['list']:
                        file_info = {
                            'is_dir': int(item.get('isdir', 0)),
                            'path': item.get('path', ''),
                            'fs_id': item.get('fs_id', ''),
                            'name': item.get('server_filename', ''),
                            'type': _get_file_type_from_category(item.get('category', '6')),
                            'size': item.get('size', '0'),
                            'image': item.get('thumbs', {}).get('url3', ''),
                            'list': []
                        }
                        result['list'].append(file_info)
            else:
                result = {'status': 'failed', 'message': share_info.get('message', 'Failed to get share info')}
        
        elif api_mode == 'cookie':  # Cookie mode
            if not st.session_state.cookie_api:
                return {'status': 'failed', 'message': 'Cookie API not configured. Please set up cookie in Cookie Mode page.'}
            
            status_text.text("🔧 Initializing Cookie API...")
            progress_bar.progress(20)
            
            cookie_api = st.session_state.cookie_api
            
            status_text.text("🔍 Processing TeraBox URL with Cookie...")
            progress_bar.progress(40)
            
            # Get file info using cookie API
            file_info = cookie_api.get_file_info(url)
            
            if 'error' in file_info:
                result = {'status': 'failed', 'message': file_info['error']}
            else:
                # Convert to our standard format
                result = {
                    'status': 'success',
                    'uk': file_info.get('uk', ''),
                    'shareid': file_info.get('shareid', ''),
                    'sign': '',  # Cookie mode doesn't need sign
                    'timestamp': str(int(time.time())),
                    'list': [{
                        'is_dir': 0,
                        'path': '/' + file_info.get('file_name', 'unknown'),
                        'fs_id': file_info.get('fs_id', ''),
                        'name': file_info.get('file_name', 'Unknown'),
                        'type': file_info.get('file_type', 'other'),
                        'size': str(file_info.get('sizebytes', 0)),
                        'image': file_info.get('thumbnail', ''),
                        'list': [],
                        'download_link': file_info.get('download_link', '')  # Cookie mode provides direct links
                    }]
                }
        
        elif api_mode == 'rapidapi':  # RapidAPI mode
            # RapidAPI Mode Processing
            # Strategy: Commercial API service for guaranteed reliability
            # Benefits: Professional support, SLA guarantees, no anti-bot issues
            # Requirements: Valid RapidAPI subscription and API key
            log_info("Processing with RapidAPI commercial service")
            
            # Pre-flight Validation
            # Purpose: Ensure RapidAPI client is properly configured
            # Failure Mode: Early exit with clear error message
            if not st.session_state.rapidapi_client:
                error_msg = 'RapidAPI client not configured. Please set up API key in RapidAPI Mode page.'
                log_info(f"RapidAPI processing failed - {error_msg}")
                return {'status': 'failed', 'message': error_msg}
            
            status_text.text("🔧 Initializing RapidAPI client...")
            progress_bar.progress(20)
            
            rapidapi_client = st.session_state.rapidapi_client
            log_info(f"RapidAPI client retrieved from session state - Cache enabled: {rapidapi_client.is_cache_enabled()}")
            
            status_text.text("🔍 Processing TeraBox URL via RapidAPI...")
            progress_bar.progress(40)
            
            # Execute RapidAPI File Information Request
            # Purpose: Get file metadata and download links from commercial service
            # Features: Automatic caching, multiple URL generation, error recovery
            api_start = time.time()
            file_info = rapidapi_client.get_file_info(url)
            api_duration = time.time() - api_start
            
            log_info(f"RapidAPI file info request completed in {api_duration:.2f}s")
            
            # Response Processing and Validation
            if 'error' in file_info:
                # API Error Handling
                # Purpose: Provide specific error feedback for API failures
                # Strategy: Log detailed error info for debugging
                error_message = file_info['error']
                log_error(Exception(f"RapidAPI error: {error_message}"), "extract_files_from_url")
                log_info(f"RapidAPI error details - URL: {url}, Error: {error_message}")
                
                result = {'status': 'failed', 'message': error_message}
            else:
                # Success Response Processing
                # Purpose: Convert RapidAPI response to unified format
                # Strategy: Preserve all RapidAPI data while standardizing interface
                log_info(f"RapidAPI success - File: {file_info.get('file_name', 'Unknown')}, Size: {file_info.get('size', 'Unknown')}")
                log_info(f"RapidAPI response features - Direct link: {bool(file_info.get('direct_link'))}, Thumbnail: {bool(file_info.get('thumbnail'))}")
                
                # Check if response was cached
                if file_info.get('_cache_info', {}).get('cached', False):
                    cache_age = file_info['_cache_info'].get('cache_age_hours', 0)
                    log_info(f"Response served from cache - Age: {cache_age:.1f} hours")
                else:
                    log_info("Response served from live API call - will be cached for future requests")
                
                # Convert to Unified Format
                # Purpose: Standardize response format across all modes
                # Strategy: Map RapidAPI fields to common interface
                result = {
                    'status': 'success',
                    'uk': '',  # RapidAPI doesn't provide these TeraBox internal IDs
                    'shareid': '',  # Not available in commercial API
                    'sign': '',  # Not needed for RapidAPI
                    'timestamp': str(int(time.time())),  # Current timestamp
                    'service': 'rapidapi',  # Service identifier
                    'list': [{
                        # File Metadata
                        'is_dir': 0,  # RapidAPI only handles files, not directories
                        'path': '/' + file_info.get('file_name', 'unknown'),  # Virtual path
                        'fs_id': '',  # Not provided by RapidAPI
                        'name': file_info.get('file_name', 'Unknown'),  # Display name
                        'type': file_info.get('file_type', 'other'),  # File category
                        'size': str(file_info.get('sizebytes', 0)),  # Size in bytes
                        'image': file_info.get('thumbnail', ''),  # Preview image
                        'list': [],  # No subdirectories in RapidAPI
                        
                        # Download Links (Multiple URLs for Redundancy)
                        'download_link': file_info.get('direct_link', ''),  # Primary download link
                        'rapidapi_link': file_info.get('download_link', ''),  # Alternative link
                        'backup_link': file_info.get('link', ''),  # Backup link
                        
                        # RapidAPI Specific Data
                        'rapidapi_data': file_info,  # Complete RapidAPI response for debugging
                        'service_info': {
                            'provider': 'RapidAPI',  # Service provider
                            'service': file_info.get('service', 'rapidapi'),  # Service type
                            'multiple_urls': bool(file_info.get('direct_link') and file_info.get('download_link')),  # URL redundancy
                            'has_thumbnail': bool(file_info.get('thumbnail')),  # Preview availability
                            'validated': True,  # Commercial service validation
                            'cache_status': 'cached' if file_info.get('_cache_info', {}).get('cached') else 'fresh'
                        }
                    }]
                }
                
                log_info(f"RapidAPI response converted to unified format - Files: {len(result['list'])}")
        
        else:
            return {'status': 'failed', 'message': f'Unknown API mode: {api_mode}'}
        
        progress_bar.progress(100)
        status_text.text("✅ Extraction completed!")
        
        # Clear progress indicators after a short delay
        time.sleep(1)
        progress_bar.empty()
        status_text.empty()
        
        return result
        
    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        return {'status': 'failed', 'message': f'Unexpected error: {str(e)}'}

def _get_file_type_from_category(category: str) -> str:
    """Convert TeraBox category to our file type"""
    category_map = {
        '1': 'video',
        '2': 'audio', 
        '3': 'image',
        '4': 'file',
        '5': 'file',
        '6': 'other',
        '7': 'file'
    }
    return category_map.get(str(category), 'other')

def flatten_file_list(files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Flatten nested file structure"""
    flat_files = []
    
    def process_files(file_list):
        for file_item in file_list:
            if file_item.get('is_dir') == 0:  # It's a file
                flat_files.append(file_item)
            elif file_item.get('list'):  # It's a directory with files
                process_files(file_item['list'])
    
    process_files(files)
    return flat_files

def display_file_card(file_info: Dict[str, Any], index: int):
    """Display individual file card with enhanced RapidAPI support"""
    file_type = file_info.get('type', 'other')
    file_size = file_info.get('size', 0)
    file_name = file_info.get('name', 'Unknown')
    
    # Convert size to MB
    size_mb = int(file_size) / (1024 * 1024) if file_size else 0
    
    # File type emoji
    type_emojis = {
        'video': '🎥',
        'image': '🖼️',
        'file': '📄',
        'other': '📁'
    }
    
    emoji = type_emojis.get(file_type, '📁')
    
    with st.container():
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown(f"**{emoji} {file_name}**")
            st.caption(f"Type: {file_type.title()} | Size: {size_mb:.1f} MB")
            
            # Show service info if available
            if file_info.get('service_info'):
                service_info = file_info['service_info']
                provider = service_info.get('provider', 'Unknown')
                if service_info.get('multiple_urls'):
                    st.success(f"🚀 {provider} - Multiple URLs")
                elif service_info.get('validated'):
                    st.info(f"🚀 {provider} - Validated")
                else:
                    st.caption(f"🚀 {provider}")
        
        with col2:
            # Show thumbnail if available
            if file_info.get('image'):
                try:
                    st.image(file_info['image'], width=80, caption="Preview")
                except:
                    st.caption("📷 Preview available")
        
        with col3:
            # Download button
            if st.button("📥 Download", key=f"download_{index}", help="Download this file"):
                download_file(file_info, index)
            
            # Open Direct File Link button
            if st.button("🌐 Open Link", key=f"open_link_{index}", help="Open direct file link in browser"):
                open_file_link(file_info, index)
            
            # Stream button for videos
            if file_type == 'video':
                if st.button("▶️ Stream", key=f"stream_{index}", help="Stream this video"):
                    stream_video(file_info, index)
            
            # Debug button for RapidAPI files
            if file_info.get('rapidapi_data'):
                if st.button("🔍 Debug", key=f"debug_{index}", help="Show RapidAPI debug info"):
                    with st.expander(f"Debug: {file_name}"):
                        st.json(file_info['rapidapi_data'])

def download_file(file_info: Dict[str, Any], index: int):
    """Download a specific file with enhanced RapidAPI support"""
    # Check if this is a RapidAPI file
    if file_info.get('rapidapi_data'):
        # Use RapidAPI download method
        download_rapidapi_file(file_info, index)
        return
    
    if not st.session_state.extraction_params:
        st.error("No extraction parameters available. Please extract files first.")
        return
    
    params = st.session_state.extraction_params
    terabox = TeraboxCore(mode=params.get('mode', 3))
    
    with st.spinner(f"🔗 Generating download links for {file_info['name']}..."):
        links_result = terabox.generate_download_links(
            fs_id=str(file_info['fs_id']),
            uk=str(params.get('uk', '')),
            shareid=str(params.get('shareid', '')),
            timestamp=str(params.get('timestamp', '')),
            sign=str(params.get('sign', '')),
            js_token=str(params.get('js_token', '')),
            cookie=str(params.get('cookie', ''))
        )
    
    if links_result.get('status') == 'success':
        download_links = links_result.get('download_link', {})
        
        st.success(f"✅ Generated {len(download_links)} download link(s)")
        
        for i, (key, url) in enumerate(download_links.items(), 1):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.text_input(f"Download URL {i}:", value=url, key=f"url_{index}_{i}")
            
            with col2:
                # Create download button with the actual file content
                try:
                    if st.button(f"⬇️ Option {i}", key=f"direct_download_{index}_{i}"):
                        download_file_direct(url, file_info['name'])
                except Exception as e:
                    st.error(f"Error creating download button: {e}")
    else:
        st.error("❌ Failed to generate download links")
        if 'message' in links_result:
            st.error(f"Error: {links_result['message']}")

def download_rapidapi_file(file_info: Dict[str, Any], index: int):
    """Download file using RapidAPI with enhanced progress tracking"""
    rapidapi_data = file_info['rapidapi_data']
    
    if not st.session_state.rapidapi_client:
        st.error("❌ RapidAPI client not available")
        return
    
    # Enhanced progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    speed_text = st.empty()
    
    # Progress callback function
    start_time = time.time()
    last_update = start_time
    
    def progress_callback(downloaded: int, total: int, percentage: float):
        nonlocal last_update
        current_time = time.time()
        
        # Update every 0.5 seconds to avoid too frequent updates
        if current_time - last_update >= 0.5:
            elapsed = current_time - start_time
            if elapsed > 0 and downloaded > 0:
                speed = downloaded / elapsed  # bytes per second
                speed_mb = speed / (1024 * 1024)  # MB per second
                
                # Estimate remaining time
                if speed > 0 and total > downloaded:
                    remaining_bytes = total - downloaded
                    eta_seconds = remaining_bytes / speed
                    eta_min = int(eta_seconds // 60)
                    eta_sec = int(eta_seconds % 60)
                    eta_str = f"{eta_min}m {eta_sec}s" if eta_min > 0 else f"{eta_sec}s"
                    
                    speed_text.text(f"⚡ Speed: {speed_mb:.1f} MB/s | ETA: {eta_str}")
                else:
                    speed_text.text(f"⚡ Speed: {speed_mb:.1f} MB/s")
            
            progress_bar.progress(percentage / 100)
            last_update = current_time
    
    try:
        status_text.text("📥 Starting RapidAPI download...")
        
        # Use the enhanced RapidAPI client's download method with callback
        result = st.session_state.rapidapi_client.download_file(
            rapidapi_data, 
            save_path=None,  # Will use default download/ directory
            callback=progress_callback
        )
        
        progress_bar.progress(100)
        status_text.text("✅ Download completed!")
        speed_text.empty()
        
        time.sleep(1)
        progress_bar.empty()
        status_text.empty()
        
        if 'error' in result:
            st.error(f"❌ Download failed: {result['error']}")
        else:
            st.success(f"✅ Downloaded successfully!")
            st.info(f"📁 File saved to: {result['file_path']}")
            
            # Show detailed download info
            if result.get('original_filename') != result.get('sanitized_filename'):
                st.info(f"📝 Saved as: {result.get('sanitized_filename', 'N/A')}")
            
            # Offer Streamlit download button
            try:
                with open(result['file_path'], 'rb') as f:
                    file_data = f.read()
                    
                st.download_button(
                    label=f"💾 Download {result.get('sanitized_filename', file_info['name'])}",
                    data=file_data,
                    file_name=result.get('sanitized_filename', file_info['name']),
                    mime="application/octet-stream",
                    key=f"rapidapi_download_{index}"
                )
                
            except Exception as e:
                st.warning(f"Could not create download button: {e}")
                
    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        speed_text.empty()
        st.error(f"❌ Unexpected error: {str(e)}")

def download_file_direct(url: str, filename: str):
    """Download file directly through Streamlit"""
    try:
        with st.spinner(f"📥 Downloading {filename}..."):
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Create download button with file content
            st.download_button(
                label=f"💾 Save {filename}",
                data=response.content,
                file_name=filename,
                mime="application/octet-stream",
                key=f"save_{filename}_{int(time.time())}"
            )
            
        st.success("✅ File ready for download!")
        
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Download failed: {e}")
    except Exception as e:
        st.error(f"❌ Unexpected error: {e}")

def stream_video(file_info: Dict[str, Any], index: int):
    """Stream video file"""
    if not st.session_state.extraction_params:
        st.error("No extraction parameters available. Please extract files first.")
        return
    
    params = st.session_state.extraction_params
    terabox = TeraboxCore(mode=params.get('mode', 3))
    
    with st.spinner(f"🎬 Preparing video stream for {file_info['name']}..."):
        links_result = terabox.generate_download_links(
            fs_id=str(file_info['fs_id']),
            uk=str(params.get('uk', '')),
            shareid=str(params.get('shareid', '')),
            timestamp=str(params.get('timestamp', '')),
            sign=str(params.get('sign', '')),
            js_token=str(params.get('js_token', '')),
            cookie=str(params.get('cookie', ''))
        )
    
    if links_result.get('status') == 'success':
        download_links = links_result.get('download_link', {})
        
        if download_links:
            # Use the first available link for streaming
            stream_url = list(download_links.values())[0]
            
            st.success("🎥 Video ready for streaming!")
            
            # Display video player
            try:
                st.video(stream_url)
            except Exception as e:
                st.error(f"❌ Could not load video player: {e}")
                st.info("💡 Try using one of the download links instead:")
                
                for i, (key, url) in enumerate(download_links.items(), 1):
                    st.text_input(f"Stream URL {i}:", value=url, key=f"stream_url_{index}_{i}")
        else:
            st.error("❌ No streaming links available")
    else:
        st.error("❌ Failed to generate streaming links")

def open_file_link(file_info: Dict[str, Any], index: int):
    """Open direct file link in browser"""
    # Get preferred browser
    preferred_browser = st.session_state.get('preferred_browser', None)
    
    # Try to open the link
    with st.spinner("🌐 Opening direct file link in browser..."):
        # For RapidAPI files, use the rapidapi_data
        if file_info.get('rapidapi_data'):
            result = open_direct_file_link(file_info['rapidapi_data'], browser=preferred_browser)
        else:
            # For other files, we need to generate the download link first
            if not st.session_state.extraction_params:
                st.error("❌ No extraction parameters available. Please extract files first.")
                return
            
            params = st.session_state.extraction_params
            terabox = TeraboxCore(mode=params.get('mode', 3))
            
            # Generate download links
            links_result = terabox.generate_download_links(
                fs_id=str(file_info['fs_id']),
                uk=str(params.get('uk', '')),
                shareid=str(params.get('shareid', '')),
                timestamp=str(params.get('timestamp', '')),
                sign=str(params.get('sign', '')),
                js_token=str(params.get('js_token', '')),
                cookie=str(params.get('cookie', ''))
            )
            
            if links_result.get('status') == 'success':
                download_links = links_result.get('download_link', {})
                if download_links:
                    # Use the first available download link
                    first_url = list(download_links.values())[0]
                    
                    # Create a file_info-like structure for the browser utility
                    link_info = {
                        'direct_link': first_url,
                        'file_name': file_info.get('name', 'Unknown'),
                        'download_link': first_url
                    }
                    
                    result = open_direct_file_link(link_info, browser=preferred_browser)
                else:
                    st.error("❌ No download links available")
                    return
            else:
                st.error("❌ Failed to generate download links")
                if 'message' in links_result:
                    st.error(f"Error: {links_result['message']}")
                return
    
    # Display result
    display_browser_open_result(result, show_details=True)
    
    if result['status'] == 'success':
        st.balloons()  # Celebrate success!

# Main app layout
def main():
    display_header()
    
    # Sidebar for settings
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # API Mode Display
        api_mode = st.session_state.api_mode
        if api_mode == 'unofficial':
            st.success("🎯 **Mode: Unofficial Scraping**")
            st.caption("Using scraping methods")
        elif api_mode == 'official':
            st.success("🏢 **Mode: Official API**")
            st.caption("Using TeraBox Open Platform API")
        elif api_mode == 'cookie':
            st.success("🍪 **Mode: Cookie Authentication**")
            st.caption("Using session cookie")
        elif api_mode == 'rapidapi':
            st.success("💳 **Mode: RapidAPI Service**")
            st.caption("Using commercial API service")
        
        mode_buttons = st.columns(2)
        with mode_buttons[0]:
            mode_select = st.selectbox(
                "Quick Switch:",
                options=['🔑 API Mode', '🍪 Cookie Mode', '💳 RapidAPI Mode', '📊 Compare All'],
                index=0
            )
        with mode_buttons[1]:
            if st.button("🔄 Switch Mode"):
                if mode_select == '🔑 API Mode':
                    st.switch_page("pages/🔑_API_Mode.py")
                elif mode_select == '🍪 Cookie Mode':
                    st.switch_page("pages/🍪_Cookie_Mode.py")
                elif mode_select == '💳 RapidAPI Mode':
                    st.switch_page("pages/💳_RapidAPI_Mode.py")
                elif mode_select == '📊 Compare All':
                    st.switch_page("pages/📊_Mode_Comparison.py")
        
        st.markdown("---")
        
        # Mode selection (only for unofficial mode)
        if api_mode == 'unofficial':
            mode = st.selectbox(
                "Processing Mode:",
                options=[1, 2, 3],
                index=2,  # Default to mode 3
                help="Select the TeraBox processing mode"
            )
            
            display_mode_indicator(mode)
        elif api_mode == 'official':
            mode = None
            if st.session_state.official_api and st.session_state.official_api.is_authenticated():
                st.info("🔐 **Authenticated**")
                st.caption("Ready to use Official API")
            else:
                st.warning("🔐 **Not Authenticated**")
                st.caption("Configure credentials in API Mode page")
        
        elif api_mode == 'cookie':
            mode = None
            if st.session_state.cookie_api:
                st.info("🍪 **Cookie Set**")
                st.caption("Ready to use Cookie API")
            else:
                st.warning("🍪 **No Cookie**")
                st.caption("Configure cookie in Cookie Mode page")
        
        elif api_mode == 'rapidapi':
            mode = None
            if st.session_state.rapidapi_client:
                st.info("💳 **API Key Set**")
                st.caption("Ready to use RapidAPI")
            else:
                st.warning("💳 **No API Key**")
                st.caption("Configure API key in RapidAPI Mode page")
        
        else:
            mode = None
        
        # Browser Selection
        st.header("🌐 Browser Settings")
        selected_browser = create_browser_selection_ui()
        if selected_browser:
            st.success(f"✅ Browser configured")
        
        st.markdown("---")
        
        # URL input
        st.header("📎 TeraBox URL")
        terabox_url = st.text_input(
            "Enter TeraBox Share Link:",
            placeholder="https://terabox.com/s/...",
            help="Paste your TeraBox share link here"
        )
        
        # Extract button
        extract_button = st.button("🔍 Extract Files", type="primary")
        
        # Clear button
        if st.button("🗑️ Clear Results"):
            st.session_state.files_data = None
            st.session_state.extraction_params = None
            # Results cleared - using state manager for clean updates
            StateManager.update_multiple_states({
                'files_data': None,
                'extraction_params': None
            }, "Results cleared successfully!")
    
    # Main content area
    if extract_button and terabox_url:
        # URL Validation
        # Purpose: Validate TeraBox URL before processing
        # Strategy: Check against known TeraBox domain patterns
        # Security: Prevent processing of non-TeraBox URLs
        log_info(f"User initiated file extraction - URL: {terabox_url}")
        
        # Enhanced Domain Validation
        # Purpose: Support all known TeraBox domains including new ones
        # Strategy: Check for domain keywords in URL
        valid_domains = ['terabox', '1024terabox', 'freeterabox', 'nephobox', 'terasharelink', 'terafileshare']
        
        if not any(domain in terabox_url.lower() for domain in valid_domains):
            error_msg = f"Invalid TeraBox URL - Domain not recognized: {terabox_url}"
            log_error(Exception(error_msg), "main - URL validation")
            st.error("❌ Please enter a valid TeraBox URL")
            
            # Show supported domains for user guidance
            with st.expander("📋 Supported TeraBox Domains"):
                st.markdown("""
                **Supported domains:**
                - terabox.com, terabox.app
                - 1024terabox.com, 1024tera.com
                - freeterabox.com, nephobox.com
                - terasharelink.com, terafileshare.com
                - And other TeraBox variants
                """)
            return
        
        log_info(f"URL validation passed - Domain recognized in: {terabox_url}")
        
        # Extract files
        result = extract_files_from_url(terabox_url, mode)
        
        if result.get('status') == 'success':
            st.session_state.files_data = result
            st.session_state.extraction_params = {
                'mode': mode,
                'uk': result.get('uk'),
                'shareid': result.get('shareid'),
                'timestamp': result.get('timestamp'),
                'sign': result.get('sign'),
                'js_token': result.get('js_token'),
                'cookie': result.get('cookie')
            }
            # Files extracted successfully - using state manager
            StateManager.update_state('files_extracted', True)
            # UI will update automatically to show the files
        else:
            error_msg = result.get('message', 'Unknown error occurred')
            
            # Provide specific error messages and solutions
            if 'ConnectionResetError' in error_msg or 'Connection aborted' in error_msg:
                st.error("🔌 Connection Issue Detected")
                st.warning("""
                **The TeraBox server closed the connection unexpectedly.**
                
                **Try these solutions:**
                1. Switch to **Mode 3** (most reliable)
                2. Wait 30 seconds and try again
                3. Check the **Network Diagnostics** page for detailed testing
                4. Try a different TeraBox URL to verify connectivity
                """)
                
                # Add quick retry button
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔄 Retry with Mode 3"):
                        st.session_state.retry_mode_3 = True
                        # Retry flag set - using state manager
                        StateManager.update_state('retry_mode_3', True)
                
                with col2:
                    if st.button("🔧 Open Diagnostics"):
                        st.switch_page("pages/🔧_Network_Diagnostics.py")
                
            elif 'timeout' in error_msg.lower():
                st.error("⏰ Request Timeout")
                st.info("The server is taking too long to respond. Try again in a few moments.")
                
            elif 'external service' in error_msg.lower():
                st.error("🌐 External Service Issue")
                st.info("The external service is temporarily unavailable. Try Mode 1 or 2 instead.")
                
            else:
                st.error("❌ Failed to extract files from TeraBox URL")
                st.error(f"Error details: {error_msg}")
            
            # Show raw error in expandable section for debugging
            with st.expander("🔍 Technical Details"):
                st.code(error_msg)
                st.markdown("**Troubleshooting:**")
                st.markdown("- Check if the TeraBox URL is valid and accessible")
                st.markdown("- Try different processing modes")
                st.markdown("- Verify your internet connection")
                st.markdown("- Use the Network Diagnostics page for detailed testing")
    
    # Display extracted files
    if st.session_state.files_data:
        files_list = st.session_state.files_data.get('list', [])
        flat_files = flatten_file_list(files_list)
        
        if flat_files:
            st.header(f"📁 Found {len(flat_files)} file(s)")
            
            # Filter options
            col1, col2 = st.columns([2, 1])
            with col1:
                file_type_filter = st.selectbox(
                    "Filter by type:",
                    options=['all', 'video', 'image', 'file', 'other'],
                    index=0
                )
            
            with col2:
                sort_by = st.selectbox(
                    "Sort by:",
                    options=['name', 'size', 'type'],
                    index=0
                )
            
            # Apply filters
            filtered_files = flat_files
            if file_type_filter != 'all':
                filtered_files = [f for f in flat_files if f.get('type') == file_type_filter]
            
            # Apply sorting
            if sort_by == 'name':
                filtered_files.sort(key=lambda x: x.get('name', '').lower())
            elif sort_by == 'size':
                filtered_files.sort(key=lambda x: int(x.get('size', 0)), reverse=True)
            elif sort_by == 'type':
                filtered_files.sort(key=lambda x: x.get('type', ''))
            
            # Display files
            st.write(f"Showing {len(filtered_files)} file(s)")
            
            for index, file_info in enumerate(filtered_files):
                with st.expander(f"{file_info.get('name', 'Unknown')}", expanded=False):
                    display_file_card(file_info, index)
        else:
            st.warning("⚠️ No files found in the provided TeraBox link")
    
    else:
        # Welcome message
        st.info("👋 Welcome to TeraDL! Enter a TeraBox URL in the sidebar to get started.")
        
        # Instructions
        with st.expander("📖 How to use TeraDL", expanded=True):
            st.markdown("""
            1. **Enter TeraBox URL**: Paste your TeraBox share link in the sidebar
            2. **Select Mode**: Choose the processing mode (Mode 3 recommended)
            3. **Extract Files**: Click the "Extract Files" button
            4. **Download or Stream**: Use the download or stream buttons for each file
            
            **Supported TeraBox domains:**
            - terabox.com
            - 1024terabox.com
            - freeterabox.com
            - nephobox.com
            
            **Features:**
            - 📥 Direct file downloads
            - 🎥 Video streaming
            - 📁 Folder exploration
            - 🔍 File filtering and sorting
            """)

if __name__ == "__main__":
    main()

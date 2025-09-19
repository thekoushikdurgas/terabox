import streamlit as st
import requests
import os
import tempfile
from urllib.parse import urlparse
from terabox_core import TeraboxCore
from terabox_official_api import TeraBoxOfficialAPI
from terabox_cookie_api import TeraBoxCookieAPI
from terabox_rapidapi import TeraBoxRapidAPI
import time
from typing import Dict, Any, List
import base64
import json

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

# Initialize session state
if 'files_data' not in st.session_state:
    st.session_state.files_data = None
if 'extraction_params' not in st.session_state:
    st.session_state.extraction_params = None
if 'api_mode' not in st.session_state:
    st.session_state.api_mode = 'unofficial'
if 'official_api' not in st.session_state:
    st.session_state.official_api = None
if 'cookie_api' not in st.session_state:
    st.session_state.cookie_api = None
if 'rapidapi_client' not in st.session_state:
    st.session_state.rapidapi_client = None

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
    """Extract files from TeraBox URL with enhanced error handling"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        api_mode = st.session_state.api_mode
        
        if api_mode == 'unofficial':
            status_text.text("🔧 Initializing TeraBox processor...")
            progress_bar.progress(20)
            
            terabox = TeraboxCore(mode=mode)
            
            status_text.text("🔍 Extracting files from TeraBox URL...")
            progress_bar.progress(40)
            
            result = terabox.extract_files(url)
            
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
            if not st.session_state.rapidapi_client:
                return {'status': 'failed', 'message': 'RapidAPI client not configured. Please set up API key in RapidAPI Mode page.'}
            
            status_text.text("🔧 Initializing RapidAPI client...")
            progress_bar.progress(20)
            
            rapidapi_client = st.session_state.rapidapi_client
            
            status_text.text("🔍 Processing TeraBox URL via RapidAPI...")
            progress_bar.progress(40)
            
            # Get file info using RapidAPI
            file_info = rapidapi_client.get_file_info(url)
            
            if 'error' in file_info:
                result = {'status': 'failed', 'message': file_info['error']}
            else:
                # Convert to our standard format
                result = {
                    'status': 'success',
                    'uk': '',  # RapidAPI doesn't provide these
                    'shareid': '',
                    'sign': '',
                    'timestamp': str(int(time.time())),
                    'list': [{
                        'is_dir': 0,
                        'path': '/' + file_info.get('file_name', 'unknown'),
                        'fs_id': '',  # RapidAPI doesn't provide fs_id
                        'name': file_info.get('file_name', 'Unknown'),
                        'type': file_info.get('file_type', 'other'),
                        'size': str(file_info.get('sizebytes', 0)),
                        'image': file_info.get('thumbnail', ''),
                        'list': [],
                        'download_link': file_info.get('direct_link', ''),  # RapidAPI provides direct links
                        'rapidapi_link': file_info.get('download_link', '')  # Alternative link
                    }]
                }
        
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
    """Display individual file card"""
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
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"**{emoji} {file_name}**")
            st.caption(f"Type: {file_type.title()} | Size: {size_mb:.1f} MB")
        
        with col2:
            # Download button
            if st.button("📥 Download", key=f"download_{index}", help="Download this file"):
                download_file(file_info, index)
            
            # Stream button for videos
            if file_type == 'video':
                if st.button("▶️ Stream", key=f"stream_{index}", help="Stream this video"):
                    stream_video(file_info, index)

def download_file(file_info: Dict[str, Any], index: int):
    """Download a specific file"""
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
            st.rerun()
    
    # Main content area
    if extract_button and terabox_url:
        # Validate URL
        if not any(domain in terabox_url.lower() for domain in ['terabox', '1024terabox', 'freeterabox', 'nephobox']):
            st.error("❌ Please enter a valid TeraBox URL")
            return
        
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
            st.rerun()
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
                        st.rerun()
                
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

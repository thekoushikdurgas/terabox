import streamlit as st
import json
import requests
from utils.terabox_official_api import TeraBoxOfficialAPI
from typing import Dict, List, Any
import time
from utils.browser_utils import open_direct_file_link, display_browser_open_result, create_browser_selection_ui

st.set_page_config(
    page_title="File Manager",
    page_icon="📁",
    layout="wide"
)

st.title("📁 TeraBox File Manager")
st.markdown("Manage your TeraBox files using the Official API")

# Check if official API is configured
if st.session_state.get('api_mode') != 'official':
    st.error("🚫 File Manager requires Official API mode")
    st.info("Please switch to Official API mode first.")
    if st.button("🔑 Go to API Mode"):
        st.switch_page("pages/🔑_API_Mode.py")
    st.stop()

if not st.session_state.get('official_api') or not st.session_state.official_api.is_authenticated():
    st.error("🔐 Not authenticated with TeraBox Official API")
    st.info("Please configure and authenticate with the Official API first.")
    if st.button("🔑 Go to API Mode"):
        st.switch_page("pages/🔑_API_Mode.py")
    st.stop()

# Get API instance
api: TeraBoxOfficialAPI = st.session_state.official_api

# Initialize session state for file manager
if 'current_directory' not in st.session_state:
    st.session_state.current_directory = "/"
if 'file_list' not in st.session_state:
    st.session_state.file_list = []
if 'selected_files' not in st.session_state:
    st.session_state.selected_files = []

# Browser Selection Section
with st.expander("🌐 Browser Settings", expanded=False):
    col_browser, col_info = st.columns([2, 1])
    
    with col_browser:
        selected_browser = create_browser_selection_ui()
        if selected_browser:
            st.success(f"✅ Browser configured")
    
    with col_info:
        st.info("""
        **Browser Selection:**
        Choose which browser to use when opening direct file links.
        """)

st.markdown("---")

# Header with user info and quota
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    st.subheader(f"📂 Current Directory: {st.session_state.current_directory}")

with col2:
    if st.button("🏠 Go Home"):
        st.session_state.current_directory = "/"
        st.rerun()

with col3:
    if st.button("🔄 Refresh"):
        st.rerun()

# User info and quota
with st.expander("👤 Account Information", expanded=False):
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("👤 Load User Info"):
            with st.spinner("Loading user information..."):
                user_info = api.get_user_info()
            
            if user_info.get('status') == 'success':
                st.success("✅ User Info Loaded")
                st.json({
                    "Username": user_info['username'],
                    "VIP Type": user_info['vip_type'],
                    "User ID": user_info['uk'],
                    "Account Type": "New User" if user_info['user_type'] == 0 else "Existing User"
                })
            else:
                st.error(f"Failed to load user info: {user_info.get('message')}")
    
    with col2:
        if st.button("💾 Load Storage Quota"):
            with st.spinner("Loading storage quota..."):
                quota_info = api.get_quota_info()
            
            if quota_info.get('status') == 'success':
                st.success("✅ Quota Info Loaded")
                
                # Display quota with progress bar
                st.metric("Total Storage", f"{quota_info['total_gb']} GB")
                st.metric("Used Storage", f"{quota_info['used_gb']} GB")
                st.metric("Free Storage", f"{quota_info['free_gb']} GB")
                
                st.progress(quota_info['usage_percent'] / 100)
                st.caption(f"Usage: {quota_info['usage_percent']}%")
            else:
                st.error(f"Failed to load quota: {quota_info.get('message')}")

# File operations toolbar
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📋 List Files"):
        with st.spinner(f"Loading files from {st.session_state.current_directory}..."):
            file_result = api.list_files(
                directory=st.session_state.current_directory,
                page=1,
                num=100,
                order="time",
                desc=1,
                web=1
            )
        
        if file_result.get('status') == 'success':
            st.session_state.file_list = file_result['files']
            st.success(f"✅ Loaded {len(st.session_state.file_list)} files")
        else:
            st.error(f"Failed to load files: {file_result.get('message')}")

with col2:
    search_term = st.text_input("🔍 Search Files", placeholder="Enter search term...")
    if search_term and st.button("Search"):
        with st.spinner(f"Searching for '{search_term}'..."):
            search_result = api.search_files(
                keyword=search_term,
                page=1,
                num=50
            )
        
        if search_result.get('status') == 'success':
            st.session_state.file_list = search_result['files']
            st.success(f"✅ Found {len(st.session_state.file_list)} files matching '{search_term}'")
        else:
            st.error(f"Search failed: {search_result.get('message')}")

with col3:
    if st.button("📊 Get File Details") and st.session_state.selected_files:
        selected_paths = [f['path'] for f in st.session_state.selected_files]
        
        with st.spinner("Getting detailed file information..."):
            detail_result = api.get_file_info(selected_paths, include_download_link=True)
        
        if detail_result.get('status') == 'success':
            st.success("✅ File details loaded")
            
            with st.expander("📋 Detailed File Information"):
                for file_detail in detail_result['files']:
                    st.json(file_detail)
        else:
            st.error(f"Failed to get file details: {detail_result.get('message')}")

with col4:
    if st.button("🔗 Get Download Links") and st.session_state.selected_files:
        selected_ids = [str(f['fs_id']) for f in st.session_state.selected_files]
        
        with st.spinner("Generating download links..."):
            download_result = api.get_download_links(selected_ids)
        
        if download_result.get('status') == 'success':
            st.success("✅ Download links generated")
            
            with st.expander("🔗 Download Links"):
                for link_info in download_result['download_links']:
                    st.markdown(f"**File ID:** {link_info['fs_id']}")
                    st.text_input("Download URL:", value=link_info['dlink'], key=f"dl_{link_info['fs_id']}")
                    st.markdown("---")
        else:
            st.error(f"Failed to generate download links: {download_result.get('message')}")

# File list display
st.markdown("---")
st.subheader("📁 Files and Directories")

if st.session_state.file_list:
    # File selection controls
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.write(f"📊 Total files: {len(st.session_state.file_list)}")
    
    with col2:
        if st.button("✅ Select All"):
            st.session_state.selected_files = st.session_state.file_list.copy()
            st.rerun()
    
    with col3:
        if st.button("❌ Clear Selection"):
            st.session_state.selected_files = []
            st.rerun()
    
    st.write(f"🎯 Selected: {len(st.session_state.selected_files)} files")
    
    # Display files
    for idx, file_info in enumerate(st.session_state.file_list):
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([0.5, 2, 1, 1, 1])
            
            with col1:
                # Selection checkbox
                is_selected = file_info in st.session_state.selected_files
                if st.checkbox("", value=is_selected, key=f"select_{idx}"):
                    if file_info not in st.session_state.selected_files:
                        st.session_state.selected_files.append(file_info)
                else:
                    if file_info in st.session_state.selected_files:
                        st.session_state.selected_files.remove(file_info)
            
            with col2:
                # File name and type
                is_dir = file_info.get('isdir', 0) == 1
                icon = "📁" if is_dir else get_file_icon(file_info.get('category', 6))
                filename = file_info.get('server_filename', 'Unknown')
                
                if is_dir:
                    if st.button(f"{icon} {filename}", key=f"dir_{idx}"):
                        # Navigate to directory
                        new_path = file_info.get('path', '/')
                        st.session_state.current_directory = new_path
                        st.session_state.file_list = []
                        st.rerun()
                else:
                    st.write(f"{icon} {filename}")
            
            with col3:
                # File size
                if not is_dir:
                    size_bytes = int(file_info.get('size', 0))
                    size_mb = size_bytes / (1024 * 1024) if size_bytes > 0 else 0
                    st.write(f"{size_mb:.1f} MB")
                else:
                    st.write("—")
            
            with col4:
                # File category
                category = file_info.get('category', 6)
                category_names = {
                    1: "Video", 2: "Audio", 3: "Image", 
                    4: "Document", 5: "App", 6: "Other", 7: "Torrent"
                }
                st.write(category_names.get(category, "Other"))
            
            with col5:
                # Actions
                if not is_dir:
                    file_category = file_info.get('category', 6)
                    if file_category == 1:  # Video file
                        if st.button("▶️", key=f"stream_{idx}", help="Stream video"):
                            stream_video_file(file_info)
                    
                    if st.button("📥", key=f"download_{idx}", help="Download file"):
                        download_single_file(file_info)
            
            st.markdown("---")

else:
    st.info("📂 No files loaded. Click 'List Files' to load files from the current directory.")

# Streaming functionality
def stream_video_file(file_info: Dict[str, Any]):
    """Stream a video file"""
    file_path = file_info.get('path', '')
    
    with st.spinner(f"Preparing video stream for {file_info['server_filename']}..."):
        stream_result = api.get_streaming_url(file_path, "M3U8_AUTO_720")
    
    if stream_result.get('status') == 'success':
        st.success("🎥 Video stream ready!")
        
        with st.expander(f"🎬 Streaming: {file_info['server_filename']}", expanded=True):
            # Display M3U8 content or streaming info
            st.text_area("M3U8 Content:", stream_result['content'], height=200)
            st.info("💡 Use the M3U8 URL in a compatible video player")
    else:
        st.error(f"Failed to get streaming URL: {stream_result.get('message')}")

def download_single_file(file_info: Dict[str, Any]):
    """Download a single file"""
    file_id = str(file_info.get('fs_id', ''))
    
    with st.spinner(f"Generating download link for {file_info['server_filename']}..."):
        download_result = api.get_download_links([file_id])
    
    if download_result.get('status') == 'success':
        download_links = download_result['download_links']
        if download_links:
            download_url = download_links[0]['dlink']
            
            st.success("✅ Download link generated!")
            st.text_input("Download URL:", value=download_url, key=f"single_dl_{file_id}")
            
            # Download and Open Link buttons
            col_dl, col_open = st.columns(2)
            
            with col_dl:
                # Try to create a direct download button
                try:
                    response = requests.get(download_url, stream=True)
                    if response.status_code == 200:
                        st.download_button(
                            label=f"💾 Download {file_info['server_filename']}",
                            data=response.content,
                            file_name=file_info['server_filename'],
                            mime="application/octet-stream"
                        )
                except Exception as e:
                    st.warning(f"Direct download failed: {e}")
                    st.info("Please use the download URL above")
            
            with col_open:
                # Open Direct File Link button
                if st.button(f"🌐 Open Link", key=f"open_single_{file_info['fs_id']}"):
                    preferred_browser = st.session_state.get('preferred_browser', None)
                    
                    # Create file info structure for browser utility
                    link_info = {
                        'dlink': download_url,
                        'file_name': file_info['server_filename'],
                        'download_link': download_url
                    }
                    
                    with st.spinner("🌐 Opening direct file link..."):
                        result = open_direct_file_link(link_info, browser=preferred_browser)
                    
                    display_browser_open_result(result, show_details=True)
                    if result['status'] == 'success':
                        st.balloons()
        else:
            st.error("No download links available")
    else:
        st.error(f"Failed to generate download link: {download_result.get('message')}")

def get_file_icon(category: int) -> str:
    """Get emoji icon for file category"""
    icons = {
        1: "🎥",  # Video
        2: "🎵",  # Audio
        3: "🖼️",  # Image
        4: "📄",  # Document
        5: "📱",  # Application
        6: "📁",  # Other
        7: "🧲"   # Torrent
    }
    return icons.get(category, "📄")

# Footer with tips
st.markdown("---")
with st.expander("💡 Tips for File Manager"):
    st.markdown("""
    **File Operations:**
    - Click on folder names to navigate into directories
    - Use checkboxes to select multiple files
    - Search works across your entire TeraBox storage
    
    **Download Options:**
    - Individual download buttons for single files
    - Bulk download link generation for selected files
    - Direct download when possible, URL fallback otherwise
    
    **Video Streaming:**
    - Video files show a play button (▶️)
    - Generates M3U8 streaming URLs
    - Use with compatible video players
    
    **Account Management:**
    - View storage quota and usage
    - Check account type and VIP status
    - Monitor available space
    """)

# Debug information
if st.checkbox("🔍 Show Debug Info"):
    st.subheader("Debug Information")
    
    debug_info = {
        "Current Directory": st.session_state.current_directory,
        "Files Loaded": len(st.session_state.file_list),
        "Selected Files": len(st.session_state.selected_files),
        "API Authenticated": api.is_authenticated(),
        "API Domain": api.api_domain
    }
    
    st.json(debug_info)

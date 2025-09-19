"""
RapidAPI Single File Processor Component

This component handles single TeraBox file processing including:
- URL input and validation
- File information retrieval
- Download link generation
- Direct link opening in browser
- Progress tracking and error handling

Component Features:
- Real-time URL validation
- Enhanced file information display
- Multiple download options
- Browser integration
- Comprehensive error handling
- Debug information display
"""

import streamlit as st
import time
from typing import Dict, Any, Optional
from utils.browser_utils import open_direct_file_link, display_browser_open_result
from utils.config import log_info, log_error


class RapidAPISingleFileProcessor:
    """
    Single File Processing Component for RapidAPI Mode
    
    Handles all aspects of single file processing including URL input,
    validation, file information retrieval, and download operations.
    
    Features:
    - URL input with validation
    - File information display
    - Multiple download options
    - Browser integration
    - Progress tracking
    - Error handling and recovery
    """
    
    def __init__(self):
        """Initialize the Single File Processor component"""
        log_info("Initializing RapidAPISingleFileProcessor component")
        
    def render_single_file_section(self) -> None:
        """
        Render the complete single file processing section
        
        This includes:
        - URL input field
        - File info retrieval button
        - File information display
        - Download options
        - Browser integration
        """
        log_info("Rendering single file processing section")
        
        st.subheader("🔗 Single File Processing")
        
        # URL input section
        terabox_url = self._render_url_input()
        
        # File info processing
        if st.button("📊 Get File Info", type="primary", key="get_file_info_btn"):
            if terabox_url:
                self._process_single_file(terabox_url)
            else:
                st.error("Please enter a TeraBox URL")
        
        # Direct link opening
        if st.button("📥 Open Direct File Link", key="open_direct_file_link"):
            self._handle_direct_link_opening()
    
    def _render_url_input(self) -> str:
        """Render URL input field with validation"""
        log_info("Rendering TeraBox URL input field")
        
        terabox_url = st.text_input(
            "TeraBox URL:",
            placeholder="https://www.terabox.app/sharing/link?surl=...",
            help="Paste any TeraBox share link",
            key="terabox_url_input"
        )
        
        # Real-time URL validation (optional)
        if terabox_url.strip():
            self._validate_url_format(terabox_url.strip())
        
        return terabox_url
    
    def _validate_url_format(self, url: str) -> None:
        """Validate TeraBox URL format in real-time"""
        log_info(f"Validating URL format: {url[:50]}...")
        
        # Basic URL validation
        if not url.lower().startswith(('http://', 'https://')):
            st.warning("⚠️ URL should start with http:// or https://")
            return
        
        # TeraBox domain validation
        terabox_domains = [
            'terabox.com', 'terabox.app', '1024terabox.com', '1024tera.com',
            'terasharelink.com', 'terafileshare.com', 'teraboxapp.com',
            'freeterabox.com', 'nephobox.com'
        ]
        
        is_valid_domain = any(domain in url.lower() for domain in terabox_domains)
        
        if is_valid_domain:
            st.success("✅ Valid TeraBox URL format")
        else:
            st.warning("⚠️ URL doesn't appear to be from a known TeraBox domain")
    
    def _process_single_file(self, terabox_url: str) -> None:
        """Process single TeraBox file and display results"""
        log_info(f"Processing single TeraBox file: {terabox_url}")
        
        # Check if force refresh is enabled
        force_refresh = st.session_state.get('force_refresh_next', False)
        
        if force_refresh:
            st.info("🔄 Force refresh enabled - bypassing cache")
            st.session_state.force_refresh_next = False  # Reset after use
        
        with st.spinner("Processing via RapidAPI..."):
            file_info = st.session_state.rapidapi_client.get_file_info(terabox_url, force_refresh=force_refresh)
        
        if 'error' in file_info:
            st.error(f"❌ Error: {file_info['error']}")
            log_error(Exception(file_info['error']), "single_file_processing")
        else:
            self._display_file_information(file_info)
            self._display_download_options(file_info)
    
    def _display_file_information(self, file_info: Dict[str, Any]) -> None:
        """Display comprehensive file information"""
        log_info(f"Displaying file information for: {file_info.get('file_name', 'Unknown')}")
        
        # Check if response was from cache
        if file_info.get('_cache_info', {}).get('cached', False):
            cache_age_hours = file_info['_cache_info'].get('cache_age_hours', 0)
            st.success(f"✅ File information retrieved from cache! (Age: {cache_age_hours:.1f}h)")
            st.info("🚀 **Lightning fast response from cache!** This saved time and API usage.")
        else:
            st.success("✅ File information retrieved from RapidAPI!")
            st.info("💾 **Response cached for future requests** - Next time will be instant!")
        
        # Store in session state for download
        st.session_state.current_file_info = file_info
        
        # Display file info in enhanced cards
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            st.metric("📄 File Name", file_info.get('file_name', 'Unknown'))
            st.metric("📏 File Size", file_info.get('size', 'Unknown'))
        
        with col_b:
            st.metric("📁 File Type", file_info.get('file_type', 'Unknown').title())
            st.metric("💾 Size (bytes)", f"{file_info.get('sizebytes', 0):,}")
        
        with col_c:
            # Thumbnail display
            if file_info.get('thumbnail'):
                try:
                    st.image(file_info['thumbnail'], caption="Thumbnail", width=150)
                except:
                    st.caption("📷 Thumbnail available")
            
            # Service indicator with cache status
            if file_info.get('_cache_info', {}).get('cached', False):
                st.info("💾 **Cached Response**")
                surl = file_info['_cache_info'].get('surl', 'Unknown')
                st.caption(f"SURL: {surl}")
            else:
                st.info("🚀 **RapidAPI Service**")
                st.caption("Fresh API response")
            
            # Validation status
            if file_info.get('direct_link') and file_info.get('download_link'):
                st.success("✅ Multiple download links")
            elif file_info.get('direct_link'):
                st.success("✅ Direct link ready")
            else:
                st.warning("⚠️ Limited download options")
    
    def _display_download_options(self, file_info: Dict[str, Any]) -> None:
        """Display enhanced download options"""
        log_info("Displaying enhanced download options")
        
        st.markdown("---")
        st.subheader("📥 Enhanced Download Options")
        
        # Show all available download URLs
        download_urls = []
        if file_info.get('direct_link'):
            download_urls.append(('Direct Link', file_info['direct_link']))
        if file_info.get('download_link') and file_info.get('download_link') != file_info.get('direct_link'):
            download_urls.append(('Alternative Link', file_info['download_link']))
        if file_info.get('link') and file_info.get('link') not in [file_info.get('direct_link'), file_info.get('download_link')]:
            download_urls.append(('Backup Link', file_info['link']))
        
        # Display download URLs
        for i, (label, url) in enumerate(download_urls):
            col_url, col_btn = st.columns([3, 1])
            with col_url:
                st.text_input(f"{label}:", value=url, key=f"rapid_url_{i}")
            with col_btn:
                if st.button(f"📥 Use {label.split()[0]}", key=f"rapid_btn_{i}"):
                    self._handle_download_with_progress(file_info)
        
        # Main download button
        st.markdown("---")
        col_download, col_debug = st.columns([2, 1])
        
        with col_download:
            if st.button("🚀 Smart Download (Try All URLs)", type="primary", key="smart_download"):
                self._handle_download_with_progress(file_info)
        
        with col_debug:
            if st.button("🔍 Debug Info", key="debug_info"):
                st.json(file_info.get('raw_response', {}))
    
    def _handle_direct_link_opening(self) -> None:
        """Handle opening direct file link in browser"""
        log_info("User requested direct file link opening")
        
        if 'current_file_info' in st.session_state and st.session_state.current_file_info:
            file_info = st.session_state.current_file_info
            
            # Get preferred browser
            preferred_browser = st.session_state.get('preferred_browser', None)
            
            with st.spinner("🌐 Opening direct file link in browser..."):
                result = open_direct_file_link(file_info, browser=preferred_browser)
            
            # Display result
            display_browser_open_result(result, show_details=True)
            
            # Log the action for debugging
            if result['status'] == 'success':
                st.balloons()  # Celebrate success!
                log_info(f"Successfully opened direct link for: {file_info.get('file_name', 'Unknown')}")
        else:
            st.error("❌ No file information available. Please get file info first.")
    
    def _handle_download_with_progress(self, file_info: Dict[str, Any]) -> None:
        """Handle file download with progress tracking"""
        log_info(f"Starting download with progress for: {file_info.get('file_name', 'Unknown')}")
        
        # Import the download function from the main file
        # This would need to be refactored to be a proper utility
        from pages.RapidAPI_Mode import download_file_with_progress
        download_file_with_progress(file_info)


def create_single_file_processor() -> RapidAPISingleFileProcessor:
    """Factory function to create Single File Processor component"""
    log_info("Creating RapidAPISingleFileProcessor component instance")
    return RapidAPISingleFileProcessor()

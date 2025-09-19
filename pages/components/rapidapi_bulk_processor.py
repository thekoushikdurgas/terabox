"""
RapidAPI Bulk File Processor Component

This component handles bulk processing of multiple TeraBox URLs including:
- Multiple URL input and validation
- Batch processing with progress tracking
- Result display and management
- Individual file actions
- Error handling and retry mechanisms

Component Features:
- Bulk URL input with validation
- Real-time progress tracking
- Success/failure categorization
- Individual file actions
- Comprehensive error reporting
- State management integration
"""

import streamlit as st
import time
from typing import Dict, Any, List
from utils.state_manager import StateManager
from utils.browser_utils import open_direct_file_link, display_browser_open_result
from utils.config import log_info, log_error


class RapidAPIBulkProcessor:
    """
    Bulk File Processing Component for RapidAPI Mode
    
    Handles batch processing of multiple TeraBox URLs with comprehensive
    progress tracking, error handling, and result management.
    
    Features:
    - Multi-URL input and validation
    - Batch processing with progress
    - Result categorization and display
    - Individual file actions
    - Error recovery and retry
    """
    
    def __init__(self):
        """Initialize the Bulk File Processor component"""
        log_info("Initializing RapidAPIBulkProcessor component")
    
    def render_bulk_processing_section(self) -> None:
        """
        Render the complete bulk file processing section
        
        This includes:
        - Multiple URL input area
        - Batch processing controls
        - Progress tracking display
        - Results presentation
        """
        log_info("Rendering bulk file processing section")
        
        st.subheader("📋 Bulk File Processing")
        
        # URL input area
        urls_input = self._render_urls_input()
        
        # Processing controls
        self._render_processing_controls(urls_input)
        
        # Display results if available
        self._display_bulk_results()
    
    def _render_urls_input(self) -> str:
        """Render multiple URLs input area"""
        log_info("Rendering multiple URLs input area")
        
        urls_input = st.text_area(
            "Enter multiple TeraBox URLs (one per line):",
            height=150,
            placeholder="https://www.terabox.app/sharing/link?surl=link1\nhttps://terabox.com/s/link2\nhttps://1024terabox.com/s/link3",
            key="bulk_urls_input",
            help="Enter one TeraBox URL per line. The system will process all URLs in batch."
        )
        
        # Show URL count and validation
        if urls_input.strip():
            urls = [url.strip() for url in urls_input.strip().split('\n') if url.strip()]
            valid_urls = self._validate_urls(urls)
            
            col_info1, col_info2 = st.columns(2)
            with col_info1:
                st.info(f"📊 **Total URLs:** {len(urls)}")
            with col_info2:
                st.info(f"✅ **Valid URLs:** {valid_urls}")
            
            if valid_urls < len(urls):
                st.warning(f"⚠️ {len(urls) - valid_urls} URLs may have format issues")
        
        return urls_input
    
    def _validate_urls(self, urls: List[str]) -> int:
        """Validate URLs and return count of valid ones"""
        log_info(f"Validating {len(urls)} URLs for bulk processing")
        
        valid_count = 0
        terabox_domains = [
            'terabox.com', 'terabox.app', '1024terabox.com', '1024tera.com',
            'terasharelink.com', 'terafileshare.com', 'teraboxapp.com',
            'freeterabox.com', 'nephobox.com'
        ]
        
        for url in urls:
            if url.lower().startswith(('http://', 'https://')):
                if any(domain in url.lower() for domain in terabox_domains):
                    valid_count += 1
        
        log_info(f"URL validation completed - Valid: {valid_count}/{len(urls)}")
        return valid_count
    
    def _render_processing_controls(self, urls_input: str) -> None:
        """Render bulk processing control buttons"""
        log_info("Rendering bulk processing controls")
        
        # Check if bulk processing is in progress
        bulk_processing_key = 'processing_bulk_files'
        
        if st.button("📊 Process All Files", type="primary", key="process_all_files_btn"):
            if urls_input.strip():
                urls = [url.strip() for url in urls_input.strip().split('\n') if url.strip()]
                
                if urls:
                    self._handle_bulk_processing(urls, bulk_processing_key)
                else:
                    st.error("No valid URLs found")
            else:
                st.error("Please enter at least one URL")
        
        # Show processing status if in progress
        elif st.session_state.get(bulk_processing_key, False):
            st.info("⏳ Bulk processing in progress... Please wait.")
    
    def _handle_bulk_processing(self, urls: List[str], processing_key: str) -> None:
        """Handle the bulk processing operation"""
        log_info(f"Starting bulk processing for {len(urls)} URLs")
        
        # Set processing flag
        st.session_state[processing_key] = True
        
        processing_container = st.container()
        
        with processing_container:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text(f"🔄 Processing {len(urls)} files via RapidAPI...")
            
            try:
                with st.spinner("Processing multiple files..."):
                    results = st.session_state.rapidapi_client.get_multiple_files_info(urls)
                
                progress_bar.progress(100)
                status_text.text("✅ Processing completed!")
                
                # Store results using StateManager
                StateManager.update_multiple_states({
                    'bulk_processing_results': results,
                    processing_key: False,
                    'bulk_processing_completed': True
                })
                
                time.sleep(0.5)
                progress_bar.empty()
                status_text.empty()
                
                st.success(f"✅ Successfully processed {len(results)} files!")
                log_info(f"Bulk processing completed successfully for {len(results)} files")
                
            except Exception as e:
                progress_bar.empty()
                status_text.empty()
                st.error(f"❌ Processing failed: {str(e)}")
                st.session_state[processing_key] = False
                log_error(e, "bulk_processing")
    
    def _display_bulk_results(self) -> None:
        """Display bulk processing results"""
        log_info("Displaying bulk processing results")
        
        # Show completion message if processing just finished
        if st.session_state.get('bulk_processing_completed', False):
            st.balloons()
            st.success("🎉 Bulk processing completed!")
            st.session_state['bulk_processing_completed'] = False
        
        if 'bulk_processing_results' in st.session_state and st.session_state.bulk_processing_results:
            results = st.session_state.bulk_processing_results
            
            # Display results summary
            successful = [r for r in results if 'error' not in r]
            failed = [r for r in results if 'error' in r]
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("✅ Successful", len(successful))
            with col_b:
                st.metric("❌ Failed", len(failed))
            
            # Show successful files
            if successful:
                self._display_successful_files(successful)
            
            # Show failed files
            if failed:
                self._display_failed_files(failed)
    
    def _display_successful_files(self, successful: List[Dict[str, Any]]) -> None:
        """Display successfully processed files"""
        log_info(f"Displaying {len(successful)} successful files")
        
        st.subheader("✅ Successfully Processed Files")
        
        for i, result in enumerate(successful):
            with st.expander(f"📄 {result.get('file_name', f'File {i+1}')} - {result.get('size', 'Unknown')}"):
                col_info, col_links, col_actions = st.columns([2, 2, 1])
                
                with col_info:
                    st.text(f"📄 Name: {result.get('file_name', 'Unknown')}")
                    st.text(f"📏 Size: {result.get('size', 'Unknown')}")
                    st.text(f"📁 Type: {result.get('file_type', 'Unknown')}")
                    st.text(f"💾 Bytes: {result.get('sizebytes', 0):,}")
                    
                    # Show thumbnail if available
                    if result.get('thumbnail'):
                        try:
                            st.image(result['thumbnail'], caption="Preview", width=100)
                        except:
                            st.caption("📷 Thumbnail available")
                
                with col_links:
                    # Show all available download URLs
                    if result.get('direct_link'):
                        st.text_input("Direct Link:", value=result['direct_link'], key=f"bulk_direct_{i}")
                    if result.get('download_link') and result.get('download_link') != result.get('direct_link'):
                        st.text_input("Alt Link:", value=result['download_link'], key=f"bulk_alt_{i}")
                    
                    # Show service info
                    st.caption(f"🚀 Service: {result.get('service', 'RapidAPI')}")
                
                with col_actions:
                    if st.button(f"📥 Download", key=f"rapid_dl_{i}"):
                        self._handle_individual_download(result)
                    
                    if st.button(f"🌐 Open Link", key=f"rapid_open_{i}"):
                        self._handle_individual_open(result)
                    
                    if st.button(f"🔍 Debug", key=f"rapid_debug_{i}"):
                        st.json(result.get('raw_response', result))
    
    def _display_failed_files(self, failed: List[Dict[str, Any]]) -> None:
        """Display failed files with error information"""
        log_info(f"Displaying {len(failed)} failed files")
        
        st.subheader("❌ Failed Files")
        for result in failed:
            st.error(f"URL: {result['original_url'][:50]}... - Error: {result['error']}")
    
    def _handle_individual_download(self, result: Dict[str, Any]) -> None:
        """Handle download for individual file"""
        log_info(f"Handling individual download for: {result.get('file_name', 'Unknown')}")
        
        # Import download function - this would need to be refactored
        from pages.RapidAPI_Mode import download_file_with_progress
        download_file_with_progress(result)
    
    def _handle_individual_open(self, result: Dict[str, Any]) -> None:
        """Handle opening individual file link"""
        log_info(f"Handling individual link opening for: {result.get('file_name', 'Unknown')}")
        
        preferred_browser = st.session_state.get('preferred_browser', None)
        with st.spinner("🌐 Opening link..."):
            open_result = open_direct_file_link(result, browser=preferred_browser)
        display_browser_open_result(open_result, show_details=False)
        if open_result['status'] == 'success':
            st.balloons()


def create_bulk_processor() -> RapidAPIBulkProcessor:
    """Factory function to create Bulk Processor component"""
    log_info("Creating RapidAPIBulkProcessor component instance")
    return RapidAPIBulkProcessor()

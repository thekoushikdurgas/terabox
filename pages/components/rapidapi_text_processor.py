"""
RapidAPI Text Processor Component

This component handles text processing to extract TeraBox links including:
- Text input with link extraction
- Pattern matching for various TeraBox domains
- Link validation and deduplication
- Bulk processing of extracted links
- CSV database integration
- Results display and management

Component Features:
- Advanced regex pattern matching
- Real-time link extraction
- Comprehensive validation
- Bulk processing capabilities
- CSV integration
- Progress tracking
"""

import streamlit as st
import pandas as pd
import time
from typing import Dict, Any, List
from utils.state_manager import StateManager
from utils.browser_utils import open_direct_file_link, display_browser_open_result
from utils.config import log_info, log_error


class RapidAPITextProcessor:
    """
    Text Processing Component for RapidAPI Mode
    
    Handles extraction of TeraBox links from text input and subsequent
    processing of those links with comprehensive validation and management.
    
    Features:
    - Advanced text processing
    - Link extraction and validation
    - Bulk processing integration
    - CSV database management
    - Results visualization
    - Individual file actions
    """
    
    def __init__(self):
        """Initialize the Text Processor component"""
        log_info("Initializing RapidAPITextProcessor component")
    
    def render_text_processor_section(self) -> None:
        """
        Render the complete text processing section
        
        This includes:
        - Text input area
        - Link extraction controls
        - Processing options
        - Results display
        """
        log_info("Rendering text processor section")
        
        st.subheader("📝 Text Processing - Extract TeraBox Links")
        
        # Description
        self._render_description()
        
        # Text input area
        text_input = self._render_text_input()
        
        # Processing controls
        self._render_processing_controls(text_input)
        
        # Display results
        self._display_processing_results()
    
    def _render_description(self) -> None:
        """Render component description"""
        st.info("""
        **📝 Text Processor** - Extract TeraBox links from any text:
        - ✅ Paste text containing TeraBox links
        - ✅ Automatically extract all valid TeraBox URLs
        - ✅ Get file info for all extracted links
        - ✅ Open direct links for all files
        - ✅ Bulk processing of multiple links
        """)
    
    def _render_text_input(self) -> str:
        """Render text input area with example"""
        log_info("Rendering text input area")
        
        text_input = st.text_area(
            "📝 Paste your text containing TeraBox links:",
            height=300,
            placeholder="""Example:
Video 👉https://terasharelink.com/s/1FQd8x4-bpyTN8TnV6APOLA

Click and watch 👇👇
Another video 🔥
Video 👉https://terasharelink.com/s/1OpCNKFvSE7dWu55KvT3w-g

Or any other text with TeraBox links...""",
            help="Paste any text containing TeraBox links. The system will automatically extract all valid links.",
            key="text_processor_input"
        )
        
        # Show text statistics
        if text_input.strip():
            text_stats = self._analyze_text_input(text_input)
            self._display_text_statistics(text_stats)
        
        return text_input
    
    def _analyze_text_input(self, text: str) -> Dict[str, Any]:
        """Analyze text input for statistics"""
        log_info(f"Analyzing text input - Length: {len(text)} characters")
        
        lines = text.split('\n')
        words = text.split()
        
        # Count potential URLs
        potential_urls = [line.strip() for line in lines if 'http' in line.lower()]
        
        stats = {
            'total_characters': len(text),
            'total_lines': len(lines),
            'total_words': len(words),
            'potential_urls': len(potential_urls),
            'has_terabox_keywords': any(keyword in text.lower() for keyword in ['terabox', 'terashare', 'terafile'])
        }
        
        log_info(f"Text analysis completed - {stats}")
        return stats
    
    def _display_text_statistics(self, stats: Dict[str, Any]) -> None:
        """Display text input statistics"""
        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
        
        with col_stat1:
            st.caption(f"📊 {stats['total_characters']} chars")
        with col_stat2:
            st.caption(f"📝 {stats['total_lines']} lines")
        with col_stat3:
            st.caption(f"🔗 {stats['potential_urls']} URLs")
        with col_stat4:
            if stats['has_terabox_keywords']:
                st.caption("✅ TeraBox content")
            else:
                st.caption("❓ No TeraBox keywords")
    
    def _render_processing_controls(self, text_input: str) -> None:
        """Render processing control buttons"""
        log_info("Rendering text processing controls")
        
        col_process, col_clear = st.columns([3, 1])
        
        with col_process:
            if st.button("🔍 Extract & Process Links", type="primary", key="extract_links_btn"):
                if text_input.strip():
                    self._handle_link_extraction(text_input)
                else:
                    st.error("Please enter some text to process")
        
        with col_clear:
            if st.button("🗑️ Clear", key="clear_text_btn"):
                self._handle_clear_data()
    
    def _handle_link_extraction(self, text_input: str) -> None:
        """Handle link extraction from text"""
        log_info(f"Handling link extraction from text (length: {len(text_input)})")
        
        # Extract links using the main extraction function
        with st.spinner("🔍 Extracting TeraBox links from text..."):
            from pages.RapidAPI_Mode import extract_terabox_links
            extracted_links = extract_terabox_links(text_input)
        
        if extracted_links:
            st.success(f"✅ Found {len(extracted_links)} TeraBox links!")
            
            # Save to CSV
            with st.spinner("💾 Saving links to terebox.csv..."):
                from pages.RapidAPI_Mode import save_links_to_csv
                csv_saved = save_links_to_csv(extracted_links)
            
            if csv_saved:
                st.success("💾 Links saved to terebox.csv successfully!")
            
            # Store in session state
            StateManager.update_multiple_states({
                'extracted_links': extracted_links,
                'text_processor_results': None,
                'links_extracted': True,
                'csv_saved': csv_saved
            })
            
            # Display extracted links
            self._display_extracted_links(extracted_links)
            
            # Processing button for extracted links
            self._render_process_extracted_links_button(extracted_links)
            
        else:
            self._show_no_links_found()
    
    def _display_extracted_links(self, extracted_links: List[str]) -> None:
        """Display extracted links in table format"""
        log_info(f"Displaying {len(extracted_links)} extracted links")
        
        st.subheader("🔗 Extracted Links")
        
        # Create table data
        table_data = []
        for i, link in enumerate(extracted_links, 1):
            # Extract SURL from link for easier identification
            surl = link.split('/')[-1] if '/' in link else link
            
            table_data.append({
                '#': i,
                'SURL': surl,
                'Full Link': link,
                'Domain': link.split('/')[2] if '/' in link else 'Unknown'
            })
        
        # Display as dataframe table
        df = pd.DataFrame(table_data)
        st.dataframe(
            df,
            width='stretch',
            hide_index=True,
            column_config={
                "#": st.column_config.NumberColumn("No.", width="small"),
                "SURL": st.column_config.TextColumn("SURL", width="medium"),
                "Full Link": st.column_config.LinkColumn("Full Link", width="large"),
                "Domain": st.column_config.TextColumn("Domain", width="medium")
            }
        )
        
        # Summary info
        self._display_extraction_summary(table_data)
    
    def _display_extraction_summary(self, table_data: List[Dict]) -> None:
        """Display extraction summary statistics"""
        col_summary1, col_summary2, col_summary3 = st.columns(3)
        
        with col_summary1:
            st.metric("📊 Total Links", len(table_data))
        with col_summary2:
            unique_domains = len(set(row['Domain'] for row in table_data))
            st.metric("🌐 Unique Domains", unique_domains)
        with col_summary3:
            st.metric("🔗 Ready to Process", len(table_data))
    
    def _render_process_extracted_links_button(self, extracted_links: List[str]) -> None:
        """Render button to process all extracted links"""
        st.markdown("---")
        
        processing_key = 'processing_extracted_links'
        
        if st.button("📊 Get File Info for All Links", type="primary", key="process_all_extracted"):
            self._handle_extracted_links_processing(extracted_links, processing_key)
        elif st.session_state.get(processing_key, False):
            st.info("⏳ Processing in progress... Please wait.")
    
    def _handle_extracted_links_processing(self, extracted_links: List[str], processing_key: str) -> None:
        """Handle processing of extracted links"""
        log_info(f"Processing {len(extracted_links)} extracted links")
        
        # Set processing flag
        st.session_state[processing_key] = True
        
        processing_container = st.container()
        
        with processing_container:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text(f"🔄 Processing {len(extracted_links)} extracted links via RapidAPI...")
            
            try:
                with st.spinner("Processing all extracted links..."):
                    results = st.session_state.rapidapi_client.get_multiple_files_info(extracted_links)
                
                progress_bar.progress(100)
                status_text.text("✅ Processing completed!")
                
                # Store results
                StateManager.update_multiple_states({
                    'text_processor_results': results,
                    processing_key: False,
                    'processing_completed': True
                })
                
                time.sleep(0.5)
                progress_bar.empty()
                status_text.empty()
                
                st.success(f"✅ Successfully processed {len(results)} links! Scroll down to see results.")
                
                # Add visual separator
                st.markdown("---")
                st.markdown("👇 **Results are displayed below** 👇")
                st.markdown("---")
                
                log_info(f"Extracted links processing completed successfully")
                
            except Exception as e:
                progress_bar.empty()
                status_text.empty()
                st.error(f"❌ Processing failed: {str(e)}")
                st.session_state[processing_key] = False
                log_error(e, "extracted_links_processing")
    
    def _show_no_links_found(self) -> None:
        """Show message when no links are found"""
        st.warning("⚠️ No TeraBox links found in the provided text.")
        st.info("""
        **Supported link formats:**
        - `https://terasharelink.com/s/...`
        - `https://terabox.com/s/...`
        - `https://www.terabox.app/sharing/link?surl=...`
        - `https://1024terabox.com/s/...`
        - And other TeraBox variations
        """)
    
    def _handle_clear_data(self) -> None:
        """Handle clearing text processor data"""
        log_info("Clearing text processor data")
        
        StateManager.update_multiple_states({
            'extracted_links': None,
            'text_processor_results': None,
            'data_cleared': True
        })
        st.success("🗑️ Text processor data cleared!")
    
    def _display_processing_results(self) -> None:
        """Display text processing results if available"""
        log_info("Checking for text processing results to display")
        
        # Show completion message if processing just finished
        if st.session_state.get('processing_completed', False):
            st.balloons()
            st.success("🎉 Processing completed! Results are shown below.")
            st.session_state['processing_completed'] = False
        
        if 'text_processor_results' in st.session_state and st.session_state.text_processor_results:
            self._render_detailed_results()
        elif 'extracted_links' in st.session_state and st.session_state.extracted_links:
            # Show extracted links if available but not processed
            if st.session_state.get('processing_extracted_links', False):
                st.info("⏳ Processing extracted links... Results will appear here when complete.")
            else:
                st.info("👆 Click 'Get File Info for All Links' above to process the extracted links")
    
    def _render_detailed_results(self) -> None:
        """Render detailed processing results"""
        results = st.session_state.text_processor_results
        log_info(f"Rendering detailed results for {len(results)} processed links")
        
        # Summary statistics
        successful = [r for r in results if 'error' not in r]
        failed = [r for r in results if 'error' in r]
        
        st.markdown("---")
        st.subheader("📊 Processing Results")
        
        col_success, col_fail, col_total = st.columns(3)
        with col_success:
            st.metric("✅ Successful", len(successful))
        with col_fail:
            st.metric("❌ Failed", len(failed))
        with col_total:
            st.metric("📊 Total Links", len(results))
        
        # Display successful files
        if successful:
            self._display_successful_results(successful)
        
        # Display failed files
        if failed:
            self._display_failed_results(failed)
    
    def _display_successful_results(self, successful: List[Dict[str, Any]]) -> None:
        """Display successful processing results"""
        log_info(f"Displaying {len(successful)} successful results")
        
        st.subheader("✅ Successfully Processed Files")
        
        # Bulk actions
        self._render_bulk_actions(successful)
        
        # Results table
        self._render_results_table(successful)
        
        # Individual file actions
        self._render_individual_file_actions(successful)
    
    def _render_bulk_actions(self, successful: List[Dict[str, Any]]) -> None:
        """Render bulk action buttons"""
        col_bulk1, col_bulk2 = st.columns(2)
        
        with col_bulk1:
            if st.button("🌐 Open All Direct Links", key="open_all_text_links"):
                self._handle_open_all_links(successful)
        
        with col_bulk2:
            if st.button("📥 Download All Files", key="download_all_text_files"):
                st.info("💡 Click individual download buttons below to download files")
    
    def _handle_open_all_links(self, successful: List[Dict[str, Any]]) -> None:
        """Handle opening all direct links"""
        log_info(f"Opening all direct links for {len(successful)} files")
        
        preferred_browser = st.session_state.get('preferred_browser', None)
        success_count = 0
        
        progress_bar = st.progress(0)
        
        for i, result in enumerate(successful):
            progress_bar.progress((i + 1) / len(successful))
            
            with st.spinner(f"Opening link {i+1}/{len(successful)}..."):
                open_result = open_direct_file_link(result, browser=preferred_browser)
            
            if open_result['status'] == 'success':
                success_count += 1
            
            time.sleep(0.5)  # Small delay between opens
        
        progress_bar.empty()
        
        if success_count == len(successful):
            st.success(f"✅ Successfully opened all {success_count} links!")
            st.balloons()
        else:
            st.warning(f"⚠️ Opened {success_count} out of {len(successful)} links")
        
        log_info(f"Bulk link opening completed - {success_count}/{len(successful)} successful")
    
    def _render_results_table(self, successful: List[Dict[str, Any]]) -> None:
        """Render results in table format"""
        log_info("Rendering results table")
        
        st.markdown("### 📋 File Results Table")
        
        results_table_data = []
        for i, result in enumerate(successful):
            # Extract SURL from original URL for identification
            original_url = result.get('original_url', '')
            surl = original_url.split('/')[-1] if '/' in original_url else f'File {i+1}'
            
            # Cache status
            cache_status = "💾 Cached" if result.get('_cache_info', {}).get('cached', False) else "🚀 Fresh"
            
            results_table_data.append({
                '#': i + 1,
                'SURL': surl,
                'File Name': result.get('file_name', 'Unknown')[:30] + ('...' if len(result.get('file_name', '')) > 30 else ''),
                'Size': result.get('size', 'Unknown'),
                'Type': result.get('file_type', 'Unknown').upper(),
                'Status': cache_status,
                'Has Direct Link': '✅' if result.get('direct_link') else '❌',
                'Has Thumbnail': '🖼️' if result.get('thumbnail') else '📄'
            })
        
        # Display results table
        results_df = pd.DataFrame(results_table_data)
        
        # Custom column configuration
        column_config = {
            "#": st.column_config.NumberColumn("No.", width="small"),
            "SURL": st.column_config.TextColumn("SURL", width="medium"),
            "File Name": st.column_config.TextColumn("File Name", width="large"),
            "Size": st.column_config.TextColumn("Size", width="small"),
            "Type": st.column_config.TextColumn("Type", width="small"),
            "Status": st.column_config.TextColumn("Status", width="small"),
            "Has Direct Link": st.column_config.TextColumn("Direct Link", width="small"),
            "Has Thumbnail": st.column_config.TextColumn("Preview", width="small")
        }
        
        st.dataframe(
            results_df,
            width='stretch',
            hide_index=True,
            column_config=column_config
        )
    
    def _render_individual_file_actions(self, successful: List[Dict[str, Any]]) -> None:
        """Render individual file action sections"""
        log_info(f"Rendering individual file actions for {len(successful)} files")
        
        st.markdown("### 🎯 Individual File Actions")
        
        for i, result in enumerate(successful):
            file_name = result.get('file_name', f'File {i+1}')
            file_size = result.get('size', 'Unknown')
            
            with st.expander(f"📄 {file_name} - {file_size}", expanded=False):
                col_info, col_actions = st.columns([3, 2])
                
                with col_info:
                    self._display_file_details(result)
                    self._display_file_links(result, i)
                    self._display_service_info(result)
                
                with col_actions:
                    self._render_file_action_buttons(result, i)
                    self._display_file_stats(result, i)
    
    def _display_file_details(self, result: Dict[str, Any]) -> None:
        """Display detailed file information"""
        st.markdown("**📋 File Details:**")
        st.text(f"📄 Name: {result.get('file_name', 'Unknown')}")
        st.text(f"📏 Size: {result.get('size', 'Unknown')}")
        st.text(f"📁 Type: {result.get('file_type', 'Unknown')}")
        st.text(f"💾 Bytes: {result.get('sizebytes', 0):,}")
        
        # Show thumbnail if available
        if result.get('thumbnail'):
            try:
                st.image(result['thumbnail'], caption="Preview", width=150)
            except:
                st.caption("📷 Thumbnail available but couldn't load")
    
    def _display_file_links(self, result: Dict[str, Any], index: int) -> None:
        """Display file download links"""
        if result.get('direct_link'):
            st.text_input("🔗 Direct Link:", value=result['direct_link'], key=f"text_direct_{index}")
        if result.get('download_link') and result.get('download_link') != result.get('direct_link'):
            st.text_input("🔗 Alt Link:", value=result['download_link'], key=f"text_alt_{index}")
    
    def _display_service_info(self, result: Dict[str, Any]) -> None:
        """Display service and cache information"""
        service_info = f"🚀 Service: {result.get('service', 'RapidAPI')}"
        if result.get('_cache_info', {}).get('cached', False):
            cache_age = result['_cache_info'].get('cache_age_hours', 0)
            service_info += f" | 💾 Cached ({cache_age:.1f}h ago)"
        st.caption(service_info)
    
    def _render_file_action_buttons(self, result: Dict[str, Any], index: int) -> None:
        """Render action buttons for individual files"""
        st.markdown("**🎯 Actions:**")
        
        if st.button(f"📊 Get File Info", key=f"text_info_{index}", width='stretch'):
            st.json(result)
        
        if st.button(f"📥 Download File", key=f"text_dl_{index}", width='stretch'):
            from pages.RapidAPI_Mode import download_file_with_progress
            download_file_with_progress(result)
        
        if st.button(f"🌐 Open Direct Link", key=f"text_open_{index}", width='stretch'):
            preferred_browser = st.session_state.get('preferred_browser', None)
            with st.spinner("🌐 Opening link..."):
                open_result = open_direct_file_link(result, browser=preferred_browser)
            display_browser_open_result(open_result, show_details=False)
            if open_result['status'] == 'success':
                st.balloons()
    
    def _display_file_stats(self, result: Dict[str, Any], index: int) -> None:
        """Display quick file statistics"""
        st.markdown("**📊 Quick Stats:**")
        st.caption(f"Index: #{index+1}")
        st.caption(f"Direct Link: {'✅ Yes' if result.get('direct_link') else '❌ No'}")
        st.caption(f"Thumbnail: {'🖼️ Yes' if result.get('thumbnail') else '📄 No'}")
    
    def _display_failed_results(self, failed: List[Dict[str, Any]]) -> None:
        """Display failed processing results"""
        log_info(f"Displaying {len(failed)} failed results")
        
        st.subheader("❌ Failed Files")
        
        # Create failed files table
        failed_table_data = []
        for i, result in enumerate(failed):
            original_url = result.get('original_url', 'Unknown')
            surl = original_url.split('/')[-1] if '/' in original_url else f'Failed {i+1}'
            error_msg = result.get('error', 'Unknown error')
            
            failed_table_data.append({
                '#': i + 1,
                'SURL': surl,
                'Error': error_msg[:50] + ('...' if len(error_msg) > 50 else ''),
                'URL': original_url[:40] + ('...' if len(original_url) > 40 else ''),
                'Status': '❌ Failed'
            })
        
        # Display failed files table
        failed_df = pd.DataFrame(failed_table_data)
        
        failed_column_config = {
            "#": st.column_config.NumberColumn("No.", width="small"),
            "SURL": st.column_config.TextColumn("SURL", width="medium"),
            "Error": st.column_config.TextColumn("Error", width="large"),
            "URL": st.column_config.TextColumn("URL", width="large"),
            "Status": st.column_config.TextColumn("Status", width="small")
        }
        
        st.dataframe(
            failed_df,
            width='stretch',
            hide_index=True,
            column_config=failed_column_config
        )
        
        # Individual retry options
        self._render_retry_options(failed)
    
    def _render_retry_options(self, failed: List[Dict[str, Any]]) -> None:
        """Render retry options for failed files"""
        st.markdown("### 🔄 Retry Failed Files")
        
        for i, result in enumerate(failed):
            with st.expander(f"❌ Failed Link {i+1}: {result.get('error', 'Unknown error')[:30]}...", expanded=False):
                col_error, col_retry = st.columns([2, 1])
                
                with col_error:
                    st.error(f"**Error:** {result['error']}")
                    st.text(f"**URL:** {result['original_url']}")
                    
                    if 'details' in result:
                        st.caption(f"Details: {result['details']}")
                
                with col_retry:
                    if st.button(f"🔄 Retry Link {i+1}", key=f"retry_failed_{i}", width='stretch'):
                        with st.spinner("Retrying..."):
                            retry_result = st.session_state.rapidapi_client.get_file_info(result['original_url'])
                        
                        if 'error' not in retry_result:
                            st.success("✅ Retry successful!")
                            st.json(retry_result)
                        else:
                            st.error(f"❌ Retry failed: {retry_result['error']}")
                    
                    st.caption(f"Link #{i+1}")
                    st.caption("Click to retry")


def create_text_processor() -> RapidAPITextProcessor:
    """Factory function to create Text Processor component"""
    log_info("Creating RapidAPITextProcessor component instance")
    return RapidAPITextProcessor()

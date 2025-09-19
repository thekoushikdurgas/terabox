"""
RapidAPI Download Utilities Component

This component provides enhanced download functionality including:
- Progress tracking with real-time updates
- Multiple download URL fallback support
- Comprehensive error handling and recovery
- Speed calculation and ETA estimation
- File validation and sanitization

Component Features:
- Real-time progress tracking
- Speed and ETA calculations
- Multiple URL fallback
- Enhanced error handling
- File validation
- Download optimization
"""

import streamlit as st
import time
import os
from typing import Dict, Any, List, Optional, Callable
from utils.config import log_info, log_error


class RapidAPIDownloadUtils:
    """
    Download Utilities Component for RapidAPI Mode
    
    Provides enhanced download functionality with progress tracking,
    error handling, and optimization features.
    
    Features:
    - Real-time progress tracking
    - Speed and ETA calculations
    - Multiple download URL support
    - Comprehensive error handling
    - File validation and sanitization
    - Download optimization
    """
    
    def __init__(self):
        """Initialize the Download Utils component"""
        log_info("Initializing RapidAPIDownloadUtils component")
    
    def download_file_with_enhanced_progress(self, file_info: Dict[str, Any]) -> None:
        """
        Download file with enhanced progress tracking and comprehensive error handling
        
        Args:
            file_info: File information dictionary from RapidAPI response
            
        Features:
        - Real-time progress tracking with speed calculation
        - ETA (Estimated Time of Arrival) calculation
        - Multiple download URL fallback support
        - Comprehensive error handling and recovery
        - Detailed logging for debugging and monitoring
        
        Progress Tracking Algorithm:
        - Updates every 0.5 seconds to avoid UI lag
        - Calculates download speed in MB/s
        - Estimates remaining time based on current speed
        - Provides visual progress bar and status updates
        
        Error Recovery:
        - Validates file info before starting download
        - Handles network errors with detailed feedback
        - Provides debug information for failed downloads
        - Offers alternative download options when available
        """
        log_info("Starting enhanced download with comprehensive progress tracking")
        log_info(f"File info validation - Name: {file_info.get('file_name', 'Unknown')}, Size: {file_info.get('sizebytes', 0)} bytes")
        
        # Pre-download Validation
        # Purpose: Validate file info before starting download process
        # Strategy: Check for errors and required fields early to prevent wasted effort
        validation_result = self._validate_file_info(file_info)
        if not validation_result['valid']:
            st.error(f"❌ Cannot download: {validation_result['reason']}")
            log_error(Exception(validation_result['reason']), "download_validation")
            return
        
        log_info("File info validation passed - proceeding with download")
        
        # Download Link Validation and Prioritization
        # Purpose: Ensure we have at least one download URL available
        # Strategy: Check multiple possible link fields in order of preference
        available_links = self._get_available_download_links(file_info)
        
        if not available_links:
            error_msg = "No download links available in file information"
            log_error(Exception(error_msg), "download_link_validation")
            st.error(f"❌ {error_msg}")
            return
        
        log_info(f"Download links validation passed - {len(available_links)} URLs available")
        
        # Enhanced Progress Tracking Setup
        # Purpose: Provide real-time feedback to user during download
        # Components: Progress bar, status text, speed indicator, ETA display
        progress_components = self._setup_progress_tracking()
        
        # Progress Callback Function
        # Purpose: Handle progress updates during download
        # Features: Speed calculation, ETA estimation, UI updates
        progress_tracker = self._create_progress_tracker(progress_components)
        
        try:
            # Initialize download status
            progress_components['status_text'].text("📥 Initializing enhanced download...")
            log_info("Download initialization completed - starting file transfer")
            
            # Use the enhanced RapidAPI client's download method with callback
            # Purpose: Leverage existing download infrastructure with progress tracking
            # Benefits: Reuses tested download logic, adds progress visualization
            download_result = st.session_state.rapidapi_client.download_file(
                file_info, 
                save_path=None,  # Will use default download/ directory
                callback=progress_tracker['callback']
            )
            
            # Download Completion Handling
            # Purpose: Process download results and provide user feedback
            # Strategy: Handle both success and error cases with detailed feedback
            self._handle_download_completion(download_result, progress_components, file_info)
            
        except Exception as e:
            # Unexpected Error Handling
            # Purpose: Handle any unexpected errors during download process
            # Strategy: Clean up UI, log error, provide debug information
            self._handle_download_error(e, progress_components, file_info)
    
    def _validate_file_info(self, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate file information before starting download
        
        Args:
            file_info: File information dictionary
            
        Returns:
            Dict with validation result and reason
        """
        log_info("Validating file info for download readiness")
        
        # Check for error in file info
        if 'error' in file_info:
            return {
                'valid': False,
                'reason': file_info['error']
            }
        
        # Check for required fields
        required_fields = ['file_name']
        missing_fields = [field for field in required_fields if not file_info.get(field)]
        
        if missing_fields:
            return {
                'valid': False,
                'reason': f"Missing required fields: {', '.join(missing_fields)}"
            }
        
        # Check for download links
        link_fields = ['direct_link', 'download_link', 'link']
        has_download_link = any(file_info.get(field) for field in link_fields)
        
        if not has_download_link:
            return {
                'valid': False,
                'reason': "No download links available"
            }
        
        log_info("File info validation successful - all required fields present")
        return {'valid': True, 'reason': 'Valid file info'}
    
    def _get_available_download_links(self, file_info: Dict[str, Any]) -> List[tuple]:
        """
        Get available download links in order of preference
        
        Args:
            file_info: File information dictionary
            
        Returns:
            List of tuples (field_name, url) in order of preference
        """
        log_info("Extracting available download links")
        
        available_links = []
        link_fields = [
            ('direct_link', 'Direct Download Link'),
            ('download_link', 'Alternative Download Link'),
            ('link', 'Backup Download Link')
        ]
        
        for field, description in link_fields:
            if file_info.get(field):
                available_links.append((description, file_info[field]))
                log_info(f"Found {description}: {file_info[field][:50]}...")
        
        log_info(f"Download link extraction completed - {len(available_links)} links found")
        return available_links
    
    def _setup_progress_tracking(self) -> Dict[str, Any]:
        """
        Set up progress tracking UI components
        
        Returns:
            Dict containing progress tracking components
        """
        log_info("Setting up enhanced progress tracking components")
        
        components = {
            'progress_bar': st.progress(0),
            'status_text': st.empty(),
            'speed_text': st.empty(),
            'eta_text': st.empty(),
            'start_time': time.time(),
            'last_update': time.time()
        }
        
        log_info("Progress tracking components initialized successfully")
        return components
    
    def _create_progress_tracker(self, components: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create progress tracking callback and utilities
        
        Args:
            components: Progress tracking UI components
            
        Returns:
            Dict containing progress tracker callback and utilities
        """
        log_info("Creating enhanced progress tracker with speed and ETA calculation")
        
        def progress_callback(downloaded: int, total: int, percentage: float):
            """
            Enhanced progress callback with speed and ETA calculation
            
            Args:
                downloaded: Bytes downloaded so far
                total: Total bytes to download
                percentage: Download percentage (0-100)
            """
            nonlocal components
            current_time = time.time()
            
            # Update every 0.5 seconds to avoid too frequent updates
            # Purpose: Balance between responsiveness and performance
            if current_time - components['last_update'] >= 0.5:
                elapsed = current_time - components['start_time']
                
                # Speed Calculation
                # Algorithm: bytes_downloaded / elapsed_time = bytes_per_second
                # Display: Convert to MB/s for user-friendly format
                if elapsed > 0 and downloaded > 0:
                    speed_bps = downloaded / elapsed  # bytes per second
                    speed_mbps = speed_bps / (1024 * 1024)  # MB per second
                    
                    # ETA Calculation
                    # Algorithm: (remaining_bytes / current_speed) = estimated_seconds
                    # Display: Format as minutes and seconds for readability
                    if speed_bps > 0 and total > downloaded:
                        remaining_bytes = total - downloaded
                        eta_seconds = remaining_bytes / speed_bps
                        eta_min = int(eta_seconds // 60)
                        eta_sec = int(eta_seconds % 60)
                        eta_str = f"{eta_min}m {eta_sec}s" if eta_min > 0 else f"{eta_sec}s"
                        
                        components['speed_text'].text(f"⚡ Speed: {speed_mbps:.1f} MB/s")
                        components['eta_text'].text(f"⏰ ETA: {eta_str}")
                        
                        log_info(f"Progress update - Speed: {speed_mbps:.1f} MB/s, ETA: {eta_str}, Progress: {percentage:.1f}%")
                    else:
                        components['speed_text'].text(f"⚡ Speed: {speed_mbps:.1f} MB/s")
                        components['eta_text'].text("⏰ ETA: Calculating...")
                
                # Update progress bar
                # Purpose: Visual representation of download progress
                components['progress_bar'].progress(percentage / 100)
                components['last_update'] = current_time
        
        return {
            'callback': progress_callback,
            'components': components
        }
    
    def _handle_download_completion(self, download_result: Dict[str, Any], 
                                  progress_components: Dict[str, Any], 
                                  file_info: Dict[str, Any]) -> None:
        """
        Handle download completion - both success and failure cases
        
        Args:
            download_result: Result from download operation
            progress_components: Progress tracking UI components
            file_info: Original file information
        """
        log_info("Handling download completion")
        
        # Complete progress bar and clean up
        progress_components['progress_bar'].progress(100)
        progress_components['status_text'].text("✅ Download completed!")
        progress_components['speed_text'].empty()
        progress_components['eta_text'].empty()
        
        # Brief pause to show completion
        time.sleep(1)
        
        # Clean up progress components
        progress_components['progress_bar'].empty()
        progress_components['status_text'].empty()
        
        # Handle download result
        if 'error' in download_result:
            # Download Failed
            # Purpose: Provide detailed error information and debug data
            st.error(f"❌ Download failed: {download_result['error']}")
            log_error(Exception(download_result['error']), "download_completion")
            
            # Show debug information for failed downloads
            with st.expander("🔍 Debug Information"):
                st.text("File Info:")
                st.json(file_info)
                st.text("Download Result:")
                st.json(download_result)
        else:
            # Download Successful
            # Purpose: Show success information and provide download options
            self._handle_successful_download(download_result, file_info)
    
    def _handle_successful_download(self, download_result: Dict[str, Any], file_info: Dict[str, Any]) -> None:
        """Handle successful download completion"""
        log_info(f"Download successful - File: {download_result.get('file_path', 'Unknown')}")
        
        st.success(f"✅ Downloaded successfully!")
        
        # Show detailed download information
        col_info1, col_info2 = st.columns(2)
        
        with col_info1:
            st.info(f"📁 File saved to: {download_result['file_path']}")
            st.info(f"📏 Downloaded size: {download_result['size']:,} bytes")
        
        with col_info2:
            # Show filename information if sanitized
            if download_result.get('original_filename') != download_result.get('sanitized_filename'):
                st.info(f"📝 Original: {download_result.get('original_filename', 'N/A')}")
                st.info(f"📝 Saved as: {download_result.get('sanitized_filename', 'N/A')}")
            
            # Show download URL used
            if download_result.get('download_url_used'):
                st.caption(f"🔗 Used: {download_result['download_url_used'][:50]}...")
        
        # Streamlit Download Button
        # Purpose: Provide browser-based download option
        # Benefits: Direct download without file system access
        self._create_streamlit_download_button(download_result, file_info)
    
    def _create_streamlit_download_button(self, download_result: Dict[str, Any], file_info: Dict[str, Any]) -> None:
        """Create Streamlit download button for browser download"""
        log_info("Creating Streamlit download button")
        
        try:
            file_path = download_result['file_path']
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            # Create download button
            st.download_button(
                label=f"💾 Download {download_result.get('sanitized_filename', file_info['file_name'])}",
                data=file_data,
                file_name=download_result.get('sanitized_filename', file_info['file_name']),
                mime="application/octet-stream",
                width='stretch',
                key="streamlit_download_btn"
            )
            
            # Show file size confirmation
            st.success(f"🎉 File ready for download ({len(file_data):,} bytes)")
            log_info(f"Streamlit download button created successfully - Size: {len(file_data):,} bytes")
            
        except Exception as e:
            # Fallback: Show error but don't fail the entire download
            st.warning(f"⚠️ Could not create download button: {e}")
            st.info("💡 The file was downloaded to the server, but couldn't be prepared for browser download.")
            log_error(e, "streamlit_download_button_creation")
    
    def _handle_download_error(self, error: Exception, progress_components: Dict[str, Any], 
                              file_info: Dict[str, Any]) -> None:
        """
        Handle unexpected download errors
        
        Args:
            error: Exception that occurred
            progress_components: Progress tracking UI components
            file_info: Original file information
        """
        log_error(error, "download_unexpected_error")
        
        # Clean up progress components
        progress_components['progress_bar'].empty()
        progress_components['status_text'].empty()
        progress_components['speed_text'].empty()
        if 'eta_text' in progress_components:
            progress_components['eta_text'].empty()
        
        # Show error to user
        st.error(f"❌ Unexpected download error: {str(error)}")
        
        # Show debug information for unexpected errors
        with st.expander("🔍 Debug Information"):
            st.text("Error Details:")
            st.code(str(error))
            st.text("File Info:")
            st.json(file_info)
            st.text("Error Type:")
            st.text(f"{type(error).__name__}")
    
    def create_download_options_display(self, file_info: Dict[str, Any]) -> None:
        """
        Create enhanced download options display
        
        Args:
            file_info: File information with download links
            
        Features:
        - Multiple download URL display
        - Individual URL testing
        - Smart download option
        - Debug information access
        """
        log_info("Creating enhanced download options display")
        
        st.markdown("---")
        st.subheader("📥 Enhanced Download Options")
        
        # Get and display all available download URLs
        download_urls = self._get_available_download_links(file_info)
        
        if download_urls:
            # Display individual download URLs
            for i, (label, url) in enumerate(download_urls):
                col_url, col_btn = st.columns([3, 1])
                
                with col_url:
                    st.text_input(f"{label}:", value=url, key=f"download_url_{i}")
                
                with col_btn:
                    if st.button(f"📥 Use {label.split()[0]}", key=f"use_url_{i}"):
                        log_info(f"User selected specific download URL: {label}")
                        self.download_file_with_enhanced_progress(file_info)
            
            # Main download section
            st.markdown("---")
            col_download, col_debug = st.columns([2, 1])
            
            with col_download:
                if st.button("🚀 Smart Download (Try All URLs)", type="primary", key="smart_download_btn"):
                    log_info("User initiated smart download with all URLs")
                    self.download_file_with_enhanced_progress(file_info)
            
            with col_debug:
                if st.button("🔍 Debug Info", key="download_debug_info_btn"):
                    log_info("User requested download debug information")
                    st.json(file_info.get('raw_response', {}))
        else:
            st.error("❌ No download links available")
            log_error(Exception("No download links available"), "download_options_display")
    
    def create_file_info_display(self, file_info: Dict[str, Any]) -> None:
        """
        Create enhanced file information display
        
        Args:
            file_info: File information from API response
            
        Features:
        - Comprehensive file metadata
        - Cache status indication
        - Service information
        - Validation status
        - Thumbnail display
        """
        log_info(f"Creating file info display for: {file_info.get('file_name', 'Unknown')}")
        
        # Cache status notification
        self._display_cache_status(file_info)
        
        # Store in session state for other operations
        st.session_state.current_file_info = file_info
        
        # File information cards
        self._create_file_info_cards(file_info)
    
    def _display_cache_status(self, file_info: Dict[str, Any]) -> None:
        """Display cache status information"""
        if file_info.get('_cache_info', {}).get('cached', False):
            cache_age_hours = file_info['_cache_info'].get('cache_age_hours', 0)
            st.success(f"✅ File information retrieved from cache! (Age: {cache_age_hours:.1f}h)")
            st.info("🚀 **Lightning fast response from cache!** This saved time and API usage.")
            log_info(f"Cache hit displayed - Age: {cache_age_hours:.1f}h")
        else:
            st.success("✅ File information retrieved from RapidAPI!")
            st.info("💾 **Response cached for future requests** - Next time will be instant!")
            log_info("Fresh API response displayed - cached for future use")
    
    def _create_file_info_cards(self, file_info: Dict[str, Any]) -> None:
        """Create file information display cards"""
        log_info("Creating file information display cards")
        
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            # Basic file information
            st.metric("📄 File Name", file_info.get('file_name', 'Unknown'))
            st.metric("📏 File Size", file_info.get('size', 'Unknown'))
        
        with col_b:
            # File type and size details
            st.metric("📁 File Type", file_info.get('file_type', 'Unknown').title())
            st.metric("💾 Size (bytes)", f"{file_info.get('sizebytes', 0):,}")
        
        with col_c:
            # Thumbnail and service information
            self._display_thumbnail_and_service_info(file_info)
    
    def _display_thumbnail_and_service_info(self, file_info: Dict[str, Any]) -> None:
        """Display thumbnail and service information"""
        # Thumbnail display
        if file_info.get('thumbnail'):
            try:
                st.image(file_info['thumbnail'], caption="Thumbnail", width=150)
                log_info("Thumbnail displayed successfully")
            except Exception as e:
                st.caption("📷 Thumbnail available")
                log_error(e, "thumbnail_display")
        
        # Service indicator with cache status
        if file_info.get('_cache_info', {}).get('cached', False):
            st.info("💾 **Cached Response**")
            surl = file_info['_cache_info'].get('surl', 'Unknown')
            st.caption(f"SURL: {surl}")
        else:
            st.info("🚀 **RapidAPI Service**")
            st.caption("Fresh API response")
        
        # Download link validation status
        if file_info.get('direct_link') and file_info.get('download_link'):
            st.success("✅ Multiple download links")
        elif file_info.get('direct_link'):
            st.success("✅ Direct link ready")
        else:
            st.warning("⚠️ Limited download options")
    
    def create_download_progress_display(self, total_files: int, current_index: int, 
                                       current_file: str) -> Dict[str, Any]:
        """
        Create download progress display for bulk operations
        
        Args:
            total_files: Total number of files to download
            current_index: Current file index (0-based)
            current_file: Current file name
            
        Returns:
            Dict containing progress display components
        """
        log_info(f"Creating bulk download progress display - File {current_index + 1}/{total_files}")
        
        # Progress calculation
        progress_percentage = ((current_index + 1) / total_files) * 100
        
        # Create progress components
        progress_bar = st.progress(progress_percentage / 100)
        status_text = st.empty()
        file_counter = st.empty()
        
        # Update displays
        status_text.text(f"📥 Downloading: {current_file[:40]}...")
        file_counter.text(f"File {current_index + 1} of {total_files}")
        
        log_info(f"Bulk progress display updated - {progress_percentage:.1f}% complete")
        
        return {
            'progress_bar': progress_bar,
            'status_text': status_text,
            'file_counter': file_counter,
            'progress_percentage': progress_percentage
        }
    
    def cleanup_progress_display(self, progress_components: Dict[str, Any]) -> None:
        """
        Clean up progress display components
        
        Args:
            progress_components: Progress display components to clean up
        """
        log_info("Cleaning up progress display components")
        
        # Clean up all progress components
        for component_name, component in progress_components.items():
            if hasattr(component, 'empty'):
                component.empty()
        
        log_info("Progress display cleanup completed")


def create_download_utils() -> RapidAPIDownloadUtils:
    """Factory function to create Download Utils component"""
    log_info("Creating RapidAPIDownloadUtils component instance")
    return RapidAPIDownloadUtils()

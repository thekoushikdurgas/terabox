"""
RapidAPI Mode Page - Refactored with Component Architecture

This is the refactored version of the RapidAPI Mode page that uses a component-based
architecture for better organization, maintainability, and reusability.

Refactoring Benefits:
- Modular component design for better organization
- Enhanced debugging and logging throughout
- Improved error handling and recovery
- Better separation of concerns
- Increased code reusability
- Enhanced performance monitoring

Component Architecture:
- RapidAPIMainInterface: Main orchestrator component
- RapidAPIKeyManager: API key management and validation
- RapidAPISingleFileProcessor: Single file processing
- RapidAPIBulkProcessor: Bulk file processing
- RapidAPITextProcessor: Text processing and link extraction
- RapidAPICSVManager: CSV database management
- RapidAPICacheManager: Cache management operations
- RapidAPIKeyMonitor: Key monitoring and analytics

Enhanced Features:
- Comprehensive debug logging at every operation
- Detailed performance monitoring and statistics
- Enhanced error handling with user-friendly messages
- Improved state management and synchronization
- Better user experience with real-time feedback
- Advanced analytics and monitoring capabilities
"""

import streamlit as st
import time
import os
from datetime import datetime
from typing import Dict, Any, List
from utils.terabox_rapidapi import TeraBoxRapidAPI
from utils.terabox_config import get_config_manager
from utils.state_manager import StateManager
from utils.config import log_info, log_error
from utils.rapidapi_utils import (
    extract_terabox_links_enhanced, 
    save_links_to_csv_enhanced,
    monitor_component_performance,
    create_enhanced_error_info
)
from utils.rerun_handler import (
    handle_rerun_exception,
    prevent_rerun_loops,
    optimized_rerun,
    show_rerun_stats
)
from utils.performance_monitor import (
    record_page_load,
    record_component_timing,
    take_memory_snapshot,
    show_performance_dashboard
)

# Import component modules
from pages.components.rapidapi_main_interface import create_rapidapi_main_interface
from pages.components.rapidapi_download_utils import create_download_utils


def download_file_with_progress(file_info: Dict[str, Any]) -> None:
    """
    Enhanced download function with comprehensive progress tracking and error handling
    
    This function has been refactored to use the download utilities component
    while maintaining backward compatibility with existing code.
    
    Args:
        file_info: File information dictionary from RapidAPI response
        
    Enhanced Features:
    - Component-based download utilities
    - Comprehensive error handling
    - Performance monitoring
    - Detailed logging
    - User feedback optimization
    """
    log_info("[REFACTORED] Starting enhanced download with component-based utilities")
    log_info(f"Download request - File: {file_info.get('file_name', 'Unknown')}, Size: {file_info.get('sizebytes', 0)} bytes")
    
    try:
        # Use component-based download utilities
        with monitor_component_performance('DownloadUtils', 'enhanced_download'):
            download_utils = create_download_utils()
            download_utils.download_file_with_enhanced_progress(file_info)
        
        log_info("[REFACTORED] Enhanced download completed successfully using component architecture")
        
    except Exception as e:
        # Enhanced error handling with detailed information
        error_info = create_enhanced_error_info(
            error=e,
            context="download_file_with_progress",
            file_name=file_info.get('file_name', 'Unknown'),
            file_size=file_info.get('sizebytes', 0),
            has_direct_link=bool(file_info.get('direct_link')),
            component='DownloadUtils'
        )
        
        log_error(e, "[REFACTORED] Enhanced download failed")
        st.error(f"❌ Download failed: {str(e)}")
        
        # Show enhanced error details
        with st.expander("🔍 Enhanced Error Details", expanded=False):
            st.json(error_info)


def extract_terabox_links(text: str) -> List[str]:
    """
    Enhanced link extraction function (backward compatibility wrapper)
    
    This function maintains backward compatibility while using the enhanced
    extraction utilities with improved logging and performance monitoring.
    
    Args:
        text: Input text containing potential TeraBox links
        
    Returns:
        List of unique TeraBox links found in the text
    """
    log_info("[REFACTORED] Starting enhanced TeraBox link extraction")
    log_info(f"Extraction request - Text length: {len(text)} characters")
    
    try:
        with monitor_component_performance('TextProcessor', 'link_extraction'):
            # Use enhanced extraction utilities
            extracted_links = extract_terabox_links_enhanced(text)
        
        log_info(f"[REFACTORED] Enhanced link extraction completed - {len(extracted_links)} links found")
        return extracted_links
        
    except Exception as e:
        # Enhanced error handling
        error_info = create_enhanced_error_info(
            error=e,
            context="extract_terabox_links",
            text_length=len(text),
            text_lines=len(text.splitlines()),
            component='TextProcessor'
        )
        
        log_error(e, "[REFACTORED] Enhanced link extraction failed")
        
        # Fallback to basic extraction if enhanced fails
        log_info("Attempting fallback to basic extraction method")
        try:
            # Import original function as fallback
            from pages.RapidAPI_Mode import extract_terabox_links as original_extract
            return original_extract(text)
        except Exception as fallback_error:
            log_error(fallback_error, "fallback_link_extraction")
            return []


def save_links_to_csv(links: List[str], csv_path: str = "utils/terebox.csv") -> bool:
    """
    Enhanced CSV saving function (backward compatibility wrapper)
    
    This function maintains backward compatibility while using enhanced
    CSV utilities with improved validation and statistics.
    
    Args:
        links: List of TeraBox links to save
        csv_path: Path to CSV database file
        
    Returns:
        bool: True if saved successfully, False otherwise
    """
    log_info("[REFACTORED] Starting enhanced CSV save operation")
    log_info(f"CSV save request - {len(links)} links, Target: {csv_path}")
    
    try:
        with monitor_component_performance('CSVManager', 'enhanced_save'):
            # Use enhanced CSV utilities
            save_result = save_links_to_csv_enhanced(links, csv_path)
        
        success = save_result.get('success', False)
        log_info(f"[REFACTORED] Enhanced CSV save completed - Success: {success}")
        
        if success:
            st.success(f"✅ Successfully saved {save_result['new_records_added']} new links to CSV")
            log_info(f"CSV save statistics: {save_result}")
        else:
            st.error(f"❌ CSV save failed: {save_result.get('error', 'Unknown error')}")
        
        return success
        
    except Exception as e:
        # Enhanced error handling
        error_info = create_enhanced_error_info(
            error=e,
            context="save_links_to_csv",
            links_count=len(links),
            csv_path=csv_path,
            component='CSVManager'
        )
        
        log_error(e, "[REFACTORED] Enhanced CSV save failed")
        st.error(f"❌ Error saving to CSV: {str(e)}")
        return False


# ============================================================================
# BACKWARD COMPATIBILITY FUNCTIONS
# ============================================================================

# Import remaining functions from original file for backward compatibility
# These will be gradually refactored into components

def load_links_from_csv(csv_path: str = "utils/terebox.csv") -> List[Dict]:
    """Load links from CSV (backward compatibility)"""
    log_info("[REFACTORED] Loading links from CSV with enhanced logging")
    
    try:
        # Import original function
        from pages.RapidAPI_Mode import load_links_from_csv as original_load
        
        with monitor_component_performance('CSVManager', 'load_links'):
            result = original_load(csv_path)
        
        log_info(f"[REFACTORED] CSV loading completed - {len(result)} records loaded")
        return result
        
    except Exception as e:
        log_error(e, "[REFACTORED] CSV loading failed")
        return []


def update_csv_with_response(link: str, response_data: Dict[str, Any], csv_path: str = "utils/terebox.csv") -> bool:
    """Update CSV with response data (backward compatibility)"""
    log_info(f"[REFACTORED] Updating CSV with response data for link: {link[:50]}...")
    
    try:
        # Import original function
        from pages.RapidAPI_Mode import update_csv_with_response as original_update
        
        with monitor_component_performance('CSVManager', 'update_response'):
            result = original_update(link, response_data, csv_path)
        
        log_info(f"[REFACTORED] CSV update completed - Success: {result}")
        return result
        
    except Exception as e:
        log_error(e, "[REFACTORED] CSV update failed")
        return False


def reset_failed_links_to_pending(csv_path: str = "utils/terebox.csv") -> bool:
    """Reset failed links to pending (backward compatibility)"""
    log_info("[REFACTORED] Resetting failed links to pending status")
    
    try:
        # Import original function
        from pages.RapidAPI_Mode import reset_failed_links_to_pending as original_reset
        
        with monitor_component_performance('CSVManager', 'reset_failed_links'):
            result = original_reset(csv_path)
        
        log_info(f"[REFACTORED] Failed links reset completed - Success: {result}")
        return result
        
    except Exception as e:
        log_error(e, "[REFACTORED] Failed links reset failed")
        return False


# ============================================================================
# MAIN PAGE RENDERING
# ============================================================================

@handle_rerun_exception
@prevent_rerun_loops
def main():
    """
    OPTIMIZED Main function for the refactored RapidAPI Mode page
    
    This function initializes and renders the complete RapidAPI interface
    using the component-based architecture with performance optimizations:
    
    OPTIMIZATIONS APPLIED:
    - Cached interface instance to prevent re-initialization
    - Reduced API validation calls
    - Optimized component loading
    - Enhanced session state management
    - Performance monitoring and logging
    - Intelligent rerun handling and optimization
    - RerunException prevention and graceful handling
    """
    log_info("=== REFACTORED RAPIDAPI MODE PAGE STARTING ===")
    log_info(f"Page load timestamp: {datetime.now().isoformat()}")
    
    # Take initial memory snapshot
    take_memory_snapshot("page_start")
    
    # Page configuration (only set once per session)
    if 'page_config_set' not in st.session_state:
        st.set_page_config(
            page_title="RapidAPI Mode - Optimized",
            page_icon="💳",
            layout="wide"
        )
        st.session_state.page_config_set = True
        log_info("Page configuration set for the first time")
    
    try:
        # Performance monitoring for page load
        page_start_time = time.time()
        
        with monitor_component_performance('MainInterface', 'page_render'):
            # Get cached interface instance or create new one
            main_interface = get_cached_rapidapi_interface()
            
            # Check if components were cached
            components_cached = 'rapidapi_components_cache' in st.session_state
            
            main_interface.render_complete_interface()
        
        # Record page load performance
        page_load_time = time.time() - page_start_time
        record_page_load("RapidAPI_Mode", page_load_time, components_cached)
        
        log_info("=== REFACTORED RAPIDAPI MODE PAGE COMPLETED SUCCESSFULLY ===")
        log_info(f"Page load completed in {page_load_time:.3f}s (cached: {components_cached})")
        
        # Take final memory snapshot
        take_memory_snapshot("page_end")
        
        # Show monitoring options in sidebar
        st.sidebar.markdown("---")
        st.sidebar.subheader("🔧 Monitoring & Debug")
        
        if st.sidebar.checkbox("🔄 Show Rerun Stats", value=False, key="show_rerun_stats"):
            show_rerun_stats()
        
        if st.sidebar.checkbox("📊 Show Performance Dashboard", value=False, key="show_perf_dashboard"):
            with st.sidebar:
                show_performance_dashboard()
        
    except Exception as e:
        # Enhanced error handling for page-level errors
        error_info = create_enhanced_error_info(
            error=e,
            context="main_page_render",
            page="RapidAPI_Mode_Optimized",
            timestamp=datetime.now().isoformat()
        )
        
        log_error(e, "=== REFACTORED RAPIDAPI MODE PAGE FAILED ===")
        
        # Show user-friendly error message
        st.error("❌ An error occurred while loading the RapidAPI Mode page")
        
        # Provide detailed error information
        with st.expander("🔍 Technical Error Details", expanded=False):
            st.json(error_info)
        
        # Provide recovery options
        st.info("💡 **Recovery Options:**")
        st.markdown("""
        - Refresh the page to try again
        - Check your internet connection
        - Verify your RapidAPI key configuration
        - Clear session cache using the button below
        - Contact support if the problem persists
        """)
        
        # Add cache clearing option
        if st.button("🗑️ Clear Session Cache", key="clear_cache_error"):
            clear_rapidapi_session_cache()
            optimized_rerun("clear_cache_error")


def get_cached_rapidapi_interface():
    """
    Get cached RapidAPI interface instance or create new one
    
    This function implements caching at the page level to prevent
    unnecessary re-initialization of the main interface.
    
    Returns:
        RapidAPIMainInterface: Cached or new interface instance
    """
    # Check if interface is cached in session state
    if 'rapidapi_main_interface_cache' in st.session_state:
        log_info("Using cached RapidAPI main interface")
        return st.session_state.rapidapi_main_interface_cache
    
    # Create new interface and cache it
    log_info("Creating new RapidAPI main interface")
    main_interface = create_rapidapi_main_interface()
    st.session_state.rapidapi_main_interface_cache = main_interface
    
    return main_interface


def clear_rapidapi_session_cache():
    """
    Clear all RapidAPI-related session cache
    
    This function clears all cached components and interface instances
    to force fresh initialization on next page load.
    """
    log_info("Clearing RapidAPI session cache")
    
    cache_keys = [
        'rapidapi_components_cache',
        'rapidapi_main_interface_cache',
        'rapidapi_session_initialized',
        'rapidapi_client',
        'rapidapi_validated',
        'rapidapi_last_validation'
    ]
    
    cleared_count = 0
    for key in cache_keys:
        if key in st.session_state:
            del st.session_state[key]
            cleared_count += 1
    
    log_info(f"Cleared {cleared_count} cached items from session state")
    st.success(f"✅ Cleared {cleared_count} cached items. Page will refresh with fresh components.")


# ============================================================================
# PAGE EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Execute main function when page is loaded
    main()
else:
    # Execute main function when imported as module
    main()

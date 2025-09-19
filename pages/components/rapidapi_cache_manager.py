"""
RapidAPI Cache Manager Component

This component handles cache management operations including:
- Cache status and statistics display
- Cache cleanup and maintenance
- Cache configuration management
- Performance monitoring
- Storage optimization

Component Features:
- Real-time cache statistics
- Automatic cleanup operations
- Configuration management
- Performance metrics
- Storage monitoring
- Cache health reporting
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, List
from utils.config import log_info, log_error


class RapidAPICacheManager:
    """
    Cache Management Component for RapidAPI Mode
    
    Provides comprehensive cache management functionality including
    statistics, cleanup operations, and configuration management.
    
    Features:
    - Cache statistics and monitoring
    - Cleanup and maintenance operations
    - Configuration management
    - Performance optimization
    - Storage monitoring
    - Health reporting
    """
    
    def __init__(self):
        """Initialize the Cache Manager component"""
        log_info("Initializing RapidAPICacheManager component")
    
    def render_cache_manager_section(self) -> None:
        """
        Render the complete cache management section
        
        This includes:
        - Cache status and information
        - Statistics display
        - Management operations
        - Configuration options
        """
        log_info("Rendering cache manager section")
        
        st.subheader("💾 Cache Management")
        
        # Check if caching is enabled
        if self._is_cache_enabled():
            self._render_cache_enabled_interface()
        else:
            self._render_cache_disabled_interface()
    
    def _is_cache_enabled(self) -> bool:
        """Check if caching is enabled"""
        if not st.session_state.get('rapidapi_client'):
            return False
        
        cache_info = st.session_state.rapidapi_client.get_cache_info()
        return cache_info.get('enabled', False)
    
    def _render_cache_enabled_interface(self) -> None:
        """Render interface when caching is enabled"""
        log_info("Rendering cache enabled interface")
        
        # Cache statistics section
        self._render_cache_statistics()
        
        # Cache management actions
        self._render_cache_actions()
        
        # Force refresh option
        self._render_force_refresh_option()
    
    def _render_cache_statistics(self) -> None:
        """Render cache statistics section"""
        log_info("Rendering cache statistics")
        
        if st.button("📊 Get Cache Statistics", key="get_cache_stats_btn"):
            with st.spinner("Loading cache statistics..."):
                cache_stats = st.session_state.rapidapi_client.get_cache_stats()
            
            if 'error' not in cache_stats:
                self._display_cache_stats(cache_stats)
            else:
                st.error(f"❌ Error getting cache stats: {cache_stats.get('error', 'Unknown error')}")
    
    def _display_cache_stats(self, cache_stats: Dict[str, Any]) -> None:
        """Display cache statistics in organized format"""
        log_info(f"Displaying cache statistics - {cache_stats.get('total_files', 0)} files")
        
        # Main statistics
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        
        with col_stat1:
            st.metric("📄 Total Files", cache_stats.get('total_files', 0))
            st.metric("✅ Valid Files", cache_stats.get('valid_files', 0))
        
        with col_stat2:
            st.metric("⚠️ Expired Files", cache_stats.get('expired_files', 0))
            st.metric("💾 Total Size", f"{cache_stats.get('total_size_mb', 0):.2f} MB")
        
        with col_stat3:
            # Cache efficiency calculation
            total_files = cache_stats.get('total_files', 0)
            valid_files = cache_stats.get('valid_files', 0)
            efficiency = (valid_files / total_files * 100) if total_files > 0 else 0
            st.metric("🎯 Cache Efficiency", f"{efficiency:.1f}%")
        
        # Detailed file list
        if cache_stats.get('files'):
            self._display_cache_file_details(cache_stats['files'])
    
    def _display_cache_file_details(self, files: List[Dict[str, Any]]) -> None:
        """Display detailed cache file information"""
        log_info(f"Displaying cache file details for {len(files)} files")
        
        st.markdown("---")
        st.subheader("📋 Cache Files Details")
        
        # Create dataframe for better display
        files_data = []
        for file_info in files[:10]:  # Show only first 10
            files_data.append({
                'SURL': file_info.get('surl', 'Unknown')[:15] + '...' if len(file_info.get('surl', '')) > 15 else file_info.get('surl', 'Unknown'),
                'Age (hours)': f"{file_info.get('age_hours', 0):.1f}",
                'Size (KB)': f"{file_info.get('size_kb', 0):.1f}",
                'Status': '✅ Valid' if file_info.get('is_valid', False) else '⚠️ Expired',
                'Created': file_info.get('created_at', 'Unknown')[:10] if file_info.get('created_at') else 'Unknown'
            })
        
        if files_data:
            df = pd.DataFrame(files_data)
            st.dataframe(df, width='stretch', hide_index=True)
            
            if len(files) > 10:
                st.caption(f"Showing first 10 of {len(files)} cache files")
    
    def _render_cache_actions(self) -> None:
        """Render cache management action buttons"""
        log_info("Rendering cache management actions")
        
        st.markdown("---")
        st.subheader("🛠️ Cache Actions")
        
        col_action1, col_action2, col_action3 = st.columns(3)
        
        with col_action1:
            self._render_clean_expired_button()
        
        with col_action2:
            self._render_clear_all_button()
        
        with col_action3:
            self._render_cache_info_button()
    
    def _render_clean_expired_button(self) -> None:
        """Render clean expired cache button"""
        if st.button("🧹 Clean Expired Cache", type="secondary", key="clean_expired_cache_btn"):
            log_info("User initiated expired cache cleanup")
            
            with st.spinner("Cleaning expired cache files..."):
                cleanup_result = st.session_state.rapidapi_client.cleanup_expired_cache()
            
            if cleanup_result.get('status') == 'success':
                cleaned_files = cleanup_result.get('cleaned_files', 0)
                if cleaned_files > 0:
                    st.success(f"✅ Cleaned {cleaned_files} expired cache files")
                    log_info(f"Cache cleanup completed - {cleaned_files} files cleaned")
                else:
                    st.info("ℹ️ No expired cache files found")
            else:
                st.error(f"❌ Cleanup failed: {cleanup_result.get('message', 'Unknown error')}")
                log_error(Exception(cleanup_result.get('message', 'Unknown error')), "cache_cleanup")
    
    def _render_clear_all_button(self) -> None:
        """Render clear all cache button"""
        if st.button("🗑️ Clear All Cache", type="secondary", key="clear_all_cache_btn"):
            if st.session_state.get('confirm_clear_cache', False):
                log_info("User confirmed cache clearing operation")
                
                with st.spinner("Clearing all cache files..."):
                    clear_result = st.session_state.rapidapi_client.clear_cache()
                
                if clear_result.get('status') == 'success':
                    cleared_files = clear_result.get('cleared', 0)
                    st.success(f"✅ Cleared {cleared_files} cache files")
                    log_info(f"Cache clearing completed - {cleared_files} files cleared")
                else:
                    st.error(f"❌ Clear failed: {clear_result.get('message', 'Unknown error')}")
                    log_error(Exception(clear_result.get('message', 'Unknown error')), "cache_clear")
                
                st.session_state.confirm_clear_cache = False
            else:
                st.session_state.confirm_clear_cache = True
                st.warning("⚠️ Click again to confirm clearing all cache")
    
    def _render_cache_info_button(self) -> None:
        """Render cache information button"""
        if st.button("ℹ️ Cache Info", key="cache_info_btn"):
            cache_info = st.session_state.rapidapi_client.get_cache_info()
            
            st.markdown("**💾 Cache Configuration:**")
            st.json(cache_info)
    
    def _render_force_refresh_option(self) -> None:
        """Render force refresh configuration"""
        log_info("Rendering force refresh option")
        
        col_action3 = st.container()
        with col_action3:
            st.markdown("**🔄 Force Refresh:**")
            st.caption("Next request will bypass cache")
            
            if 'force_refresh_next' not in st.session_state:
                st.session_state.force_refresh_next = False
            
            force_refresh_enabled = st.checkbox(
                "Force refresh next request", 
                value=st.session_state.force_refresh_next,
                key="force_refresh_checkbox"
            )
            
            if force_refresh_enabled != st.session_state.force_refresh_next:
                st.session_state.force_refresh_next = force_refresh_enabled
                if force_refresh_enabled:
                    st.info("ℹ️ Next request will bypass cache")
                    log_info("Force refresh enabled for next request")
                else:
                    log_info("Force refresh disabled")
    
    def _render_cache_disabled_interface(self) -> None:
        """Render interface when caching is disabled"""
        log_info("Rendering cache disabled interface")
        
        st.warning("⚠️ **Cache Status: Disabled**")
        st.info("Caching is not enabled for this RapidAPI client instance.")
        
        with st.expander("ℹ️ About Caching", expanded=False):
            self._render_cache_information()
    
    def _render_cache_information(self) -> None:
        """Render cache information and benefits"""
        st.markdown("""
        **What is Response Caching?**
        
        Response caching stores API responses locally to improve performance and reduce API usage:
        
        - **Faster Access**: Previously fetched files load instantly
        - **Cost Savings**: Reduces RapidAPI calls and associated costs
        - **Better Experience**: No waiting for repeated requests
        - **Offline Access**: Access cached data even without internet
        
        **How It Works:**
        1. First request fetches data from RapidAPI and caches it
        2. Subsequent requests for the same TeraBox link return cached data
        3. Cache expires after 24 hours (configurable)
        4. Expired cache is automatically cleaned up
        
        **Cache Storage:**
        - Files stored in `output/sessions/` directory
        - Named using TeraBox link identifier (surl)
        - JSON format with metadata and response data
        - Automatic cleanup of expired entries
        """)


def create_cache_manager() -> RapidAPICacheManager:
    """Factory function to create Cache Manager component"""
    log_info("Creating RapidAPICacheManager component instance")
    return RapidAPICacheManager()

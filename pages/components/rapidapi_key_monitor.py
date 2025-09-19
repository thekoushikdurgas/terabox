"""
RapidAPI Key Monitor Component

This component handles monitoring and management of multiple RapidAPI keys including:
- Key status monitoring and health tracking
- Performance analytics and statistics
- Key rotation and availability management
- Rate limit detection and recovery
- Configuration and control operations

Component Features:
- Real-time key health monitoring
- Performance analytics dashboard
- Individual key management
- Rate limit tracking
- Configuration controls
- Export and analysis tools
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from utils.config import log_info, log_error


class RapidAPIKeyMonitor:
    """
    Key Monitoring Component for RapidAPI Mode
    
    Provides comprehensive monitoring and management of multiple RapidAPI keys
    with health tracking, performance analytics, and control operations.
    
    Features:
    - Multi-key status monitoring
    - Performance analytics
    - Rate limit tracking
    - Key control operations
    - Export functionality
    - Configuration management
    """
    
    def __init__(self):
        """Initialize the Key Monitor component"""
        log_info("Initializing RapidAPIKeyMonitor component")
    
    def render_key_monitor_section(self) -> None:
        """
        Render the complete key monitoring section
        
        This includes:
        - Key manager overview
        - Individual key status
        - Management actions
        - Configuration settings
        """
        log_info("Rendering key monitor section")
        
        st.subheader("🔑 API Key Management & Monitoring")
        st.markdown("Monitor and manage multiple RapidAPI keys with rotation and rate limit handling.")
        
        # Check if key manager is available
        if self._has_key_manager():
            self._render_key_manager_interface()
        else:
            self._render_no_key_manager_interface()
    
    def _has_key_manager(self) -> bool:
        """Check if key manager is available"""
        client = st.session_state.get('rapidapi_client')
        return (client and 
                hasattr(client, 'key_manager') and 
                client.key_manager is not None)
    
    def _render_key_manager_interface(self) -> None:
        """Render key manager interface when available"""
        log_info("Rendering key manager interface")
        
        key_manager = st.session_state.rapidapi_client.key_manager
        
        # Manager overview
        self._render_manager_overview(key_manager)
        
        # Individual key status
        self._render_individual_key_status(key_manager)
        
        # Management actions
        self._render_management_actions(key_manager)
        
        # Configuration settings
        self._render_configuration_settings(key_manager)
    
    def _render_manager_overview(self, key_manager) -> None:
        """Render key manager overview statistics"""
        log_info("Rendering key manager overview")
        
        st.markdown("### 📊 Key Manager Overview")
        
        manager_stats = key_manager.get_manager_stats()
        
        # Main statistics row
        col_stat1, col_stat2, col_stat3, col_stat4, col_stat5 = st.columns(5)
        
        with col_stat1:
            st.metric("🔑 Total Keys", manager_stats.get('total_keys', 0))
        with col_stat2:
            st.metric("✅ Available Keys", manager_stats.get('available_keys', 0))
        with col_stat3:
            st.metric("⚠️ Rate Limited", manager_stats.get('rate_limited_keys', 0))
        with col_stat4:
            st.metric("❌ Failed Keys", manager_stats.get('failed_keys', 0))
        with col_stat5:
            success_rate = manager_stats.get('success_rate', 0)
            st.metric("🎯 Success Rate", f"{success_rate:.1f}%")
        
        # Additional statistics row
        col_stat6, col_stat7, col_stat8, col_stat9 = st.columns(4)
        
        with col_stat6:
            st.metric("📈 Total Requests", manager_stats.get('total_requests', 0))
        with col_stat7:
            st.metric("✅ Successful", manager_stats.get('successful_requests', 0))
        with col_stat8:
            st.metric("🔄 Key Rotations", manager_stats.get('key_rotations', 0))
        with col_stat9:
            session_duration = manager_stats.get('session_duration', '0:00:00')
            st.metric("⏱️ Session Time", str(session_duration).split('.')[0])
    
    def _render_individual_key_status(self, key_manager) -> None:
        """Render individual key status table"""
        log_info("Rendering individual key status")
        
        st.markdown("---")
        st.markdown("### 🔍 Individual Key Status")
        
        all_keys_status = key_manager.get_all_keys_status()
        
        if all_keys_status:
            # Create table view of key statuses
            key_data = []
            for key_id, status in all_keys_status.items():
                # Determine status display
                status_value = status.get('status', 'unknown')
                status_display = self._get_status_display(status_value)
                
                key_data.append({
                    'Key ID': key_id,
                    'Status': status_display,
                    'Available': '✅ Yes' if status.get('is_available', False) else '❌ No',
                    'Total Requests': status.get('total_requests', 0),
                    'Success Rate': f"{status.get('success_rate', 0):.1f}%",
                    'Rate Limited Count': status.get('rate_limit_count', 0),
                    'Consecutive Failures': status.get('consecutive_failures', 0),
                    'Avg Response Time': f"{status.get('average_response_time', 0):.2f}s"
                })
            
            if key_data:
                df = pd.DataFrame(key_data)
                st.dataframe(df, width='stretch', hide_index=True)
            
            # Detailed key information
            self._render_detailed_key_info(all_keys_status)
    
    def _get_status_display(self, status_value: str) -> str:
        """Get display string for key status"""
        status_mapping = {
            'healthy': "✅ Healthy",
            'rate_limited': "⚠️ Rate Limited",
            'failed': "❌ Failed",
            'invalid': "🚫 Invalid",
            'recovering': "🔄 Recovering"
        }
        return status_mapping.get(status_value, f"❓ {status_value.title()}")
    
    def _render_detailed_key_info(self, all_keys_status: Dict[str, Dict[str, Any]]) -> None:
        """Render detailed information for selected key"""
        log_info("Rendering detailed key information")
        
        st.markdown("### 📋 Detailed Key Information")
        
        selected_key = st.selectbox(
            "Select a key for detailed information:",
            options=list(all_keys_status.keys()),
            key="key_detail_selector"
        )
        
        if selected_key:
            self._display_key_details(selected_key, all_keys_status[selected_key])
    
    def _display_key_details(self, key_id: str, key_detail: Dict[str, Any]) -> None:
        """Display detailed information for specific key"""
        log_info(f"Displaying details for key: {key_id}")
        
        col_detail1, col_detail2 = st.columns(2)
        
        with col_detail1:
            st.markdown("**📊 Usage Statistics:**")
            st.text(f"Total Requests: {key_detail.get('total_requests', 0)}")
            st.text(f"Successful Requests: {key_detail.get('successful_requests', 0)}")
            st.text(f"Failed Requests: {key_detail.get('failed_requests', 0)}")
            st.text(f"Success Rate: {key_detail.get('success_rate', 0):.1f}%")
            st.text(f"Rate Limited Count: {key_detail.get('rate_limit_count', 0)}")
            st.text(f"Consecutive Failures: {key_detail.get('consecutive_failures', 0)}")
            st.text(f"Average Response Time: {key_detail.get('average_response_time', 0):.2f}s")
        
        with col_detail2:
            st.markdown("**⏰ Timing Information:**")
            last_used = key_detail.get('last_used')
            last_success = key_detail.get('last_success')
            last_failure = key_detail.get('last_failure')
            rate_limited_until = key_detail.get('rate_limited_until')
            
            st.text(f"Last Used: {last_used[:19] if last_used else 'Never'}")
            st.text(f"Last Success: {last_success[:19] if last_success else 'Never'}")
            st.text(f"Last Failure: {last_failure[:19] if last_failure else 'Never'}")
            st.text(f"Rate Limited Until: {rate_limited_until[:19] if rate_limited_until else 'Not Limited'}")
            
            # Show key status
            status_value = key_detail.get('status', 'unknown')
            is_available = key_detail.get('is_available', False)
            
            if is_available:
                st.success(f"✅ Key is available for use")
            else:
                st.error(f"❌ Key is not available ({status_value})")
    
    def _render_management_actions(self, key_manager) -> None:
        """Render key management action controls"""
        log_info("Rendering key management actions")
        
        st.markdown("---")
        st.markdown("### 🛠️ Key Management Actions")
        
        col_action1, col_action2, col_action3 = st.columns(3)
        
        with col_action1:
            self._render_reset_operations(key_manager)
        
        with col_action2:
            self._render_control_operations(key_manager)
        
        with col_action3:
            self._render_export_operations(key_manager)
    
    def _render_reset_operations(self, key_manager) -> None:
        """Render reset operation controls"""
        st.markdown("**🔄 Reset Operations:**")
        
        if st.button("🔄 Reset All Keys", key="reset_all_keys"):
            log_info("User initiated reset all keys operation")
            if key_manager.reset_all_keys():
                st.success("✅ All keys reset to healthy state!")
                log_info("All keys reset successfully")
                st.rerun()
            else:
                st.error("❌ Failed to reset keys")
                log_error(Exception("Failed to reset all keys"), "reset_all_keys")
        
        # Reset individual key
        all_keys_status = key_manager.get_all_keys_status()
        if all_keys_status:
            reset_key = st.selectbox(
                "Reset specific key:",
                options=['Select key...'] + list(all_keys_status.keys()),
                key="reset_key_selector"
            )
            
            if reset_key != 'Select key...' and st.button("🔄 Reset Key", key="reset_single_key"):
                log_info(f"User initiated reset for key: {reset_key}")
                if key_manager.reset_key(reset_key):
                    st.success(f"✅ Key {reset_key} reset!")
                    log_info(f"Key {reset_key} reset successfully")
                    st.rerun()
                else:
                    st.error("❌ Failed to reset key")
                    log_error(Exception(f"Failed to reset key {reset_key}"), "reset_single_key")
    
    def _render_control_operations(self, key_manager) -> None:
        """Render key control operations"""
        st.markdown("**🎛️ Control Operations:**")
        
        all_keys_status = key_manager.get_all_keys_status()
        if all_keys_status:
            control_key = st.selectbox(
                "Control specific key:",
                options=['Select key...'] + list(all_keys_status.keys()),
                key="control_key_selector"
            )
            
            if control_key != 'Select key...':
                key_status = all_keys_status[control_key]
                is_disabled = key_status.get('status') == 'disabled'
                
                col_enable, col_disable = st.columns(2)
                
                with col_enable:
                    if st.button("✅ Enable", key="enable_key", disabled=not is_disabled):
                        log_info(f"User enabled key: {control_key}")
                        if key_manager.enable_key(control_key):
                            st.success(f"✅ Key {control_key} enabled!")
                            st.rerun()
                
                with col_disable:
                    if st.button("❌ Disable", key="disable_key", disabled=is_disabled):
                        log_info(f"User disabled key: {control_key}")
                        if key_manager.disable_key(control_key):
                            st.success(f"❌ Key {control_key} disabled!")
                            st.rerun()
    
    def _render_export_operations(self, key_manager) -> None:
        """Render export and analysis operations"""
        st.markdown("**📊 Export & Analysis:**")
        
        if st.button("📊 Export Key Statistics", key="export_key_stats"):
            log_info("User initiated key statistics export")
            
            stats_data = key_manager.export_stats()
            stats_json = json.dumps(stats_data, indent=2, default=str)
            
            st.download_button(
                label="💾 Download Statistics",
                data=stats_json,
                file_name=f"rapidapi_key_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                key="download_key_stats"
            )
        
        if st.button("🔍 Show Raw Manager Data", key="show_raw_manager"):
            with st.expander("Raw Key Manager Data", expanded=True):
                stats_data = key_manager.export_stats()
                st.json(stats_data)
    
    def _render_configuration_settings(self, key_manager) -> None:
        """Render key rotation configuration settings"""
        log_info("Rendering configuration settings")
        
        st.markdown("---")
        st.markdown("### ⚙️ Key Rotation Configuration")
        
        col_config1, col_config2 = st.columns(2)
        
        with col_config1:
            self._display_current_settings(key_manager)
        
        with col_config2:
            self._display_rate_limit_detection(key_manager)
    
    def _display_current_settings(self, key_manager) -> None:
        """Display current configuration settings"""
        st.markdown("**Current Settings:**")
        config = key_manager.config
        
        settings_info = [
            f"Rotation Enabled: {'✅ Yes' if config.get('enable_rotation', True) else '❌ No'}",
            f"Rate Limit Retry Delay: {config.get('rate_limit_retry_delay', 60)} seconds",
            f"Rotate on Error: {'✅ Yes' if config.get('key_rotation_on_error', True) else '❌ No'}",
            f"Max Key Retries: {config.get('max_key_retries', 2)}",
            f"Max Consecutive Failures: {config.get('max_consecutive_failures', 3)}"
        ]
        
        for setting in settings_info:
            st.text(setting)
    
    def _display_rate_limit_detection(self, key_manager) -> None:
        """Display rate limit detection configuration"""
        st.markdown("**Rate Limit Detection:**")
        config = key_manager.config
        keywords = config.get('rate_limit_detection_keywords', [])
        
        st.text("Detection Keywords:")
        for keyword in keywords[:5]:  # Show first 5
            st.text(f"  • {keyword}")
        if len(keywords) > 5:
            st.text(f"  ... and {len(keywords) - 5} more")
    
    def _render_no_key_manager_interface(self) -> None:
        """Render interface when key manager is not available"""
        log_info("Rendering no key manager interface")
        
        st.info("🔑 **Key Manager Not Available**")
        st.markdown("""
        The Key Manager is available when you have a RapidAPI client with multiple keys configured.
        
        **To access Key Manager:**
        1. Configure and validate your first RapidAPI key above
        2. Add additional keys using the "Manage API Keys" section
        3. The Key Manager will automatically handle rotation and rate limit detection
        
        **Key Manager Features:**
        - **Automatic Rotation**: Seamlessly switches between keys when rate limited
        - **Health Monitoring**: Tracks key performance and availability
        - **Rate Limit Detection**: Intelligent detection of rate limit responses
        - **Recovery Management**: Monitors when rate-limited keys become available again
        - **Performance Analytics**: Detailed statistics for each key
        """)
        
        if st.button("🚀 Go to Key Configuration", key="goto_key_config"):
            log_info("User requested navigation to key configuration")
            st.rerun()
    
    def render_key_performance_dashboard(self) -> None:
        """Render comprehensive key performance dashboard"""
        log_info("Rendering key performance dashboard")
        
        if not self._has_key_manager():
            return
        
        key_manager = st.session_state.rapidapi_client.key_manager
        all_keys_status = key_manager.get_all_keys_status()
        
        if not all_keys_status:
            return
        
        st.markdown("### 📈 Key Performance Dashboard")
        
        # Performance metrics chart
        self._render_performance_chart(all_keys_status)
        
        # Response time comparison
        self._render_response_time_chart(all_keys_status)
        
        # Success rate comparison
        self._render_success_rate_chart(all_keys_status)
    
    def _render_performance_chart(self, all_keys_status: Dict[str, Dict[str, Any]]) -> None:
        """Render performance metrics chart"""
        log_info("Rendering performance metrics chart")
        
        # Create performance data
        performance_data = []
        for key_id, status in all_keys_status.items():
            performance_data.append({
                'Key': key_id,
                'Total Requests': status.get('total_requests', 0),
                'Successful': status.get('successful_requests', 0),
                'Failed': status.get('failed_requests', 0),
                'Rate Limited': status.get('rate_limit_count', 0)
            })
        
        if performance_data:
            df = pd.DataFrame(performance_data)
            st.bar_chart(df.set_index('Key')[['Successful', 'Failed', 'Rate Limited']])
    
    def _render_response_time_chart(self, all_keys_status: Dict[str, Dict[str, Any]]) -> None:
        """Render response time comparison chart"""
        log_info("Rendering response time chart")
        
        response_data = []
        for key_id, status in all_keys_status.items():
            avg_time = status.get('average_response_time', 0)
            if avg_time > 0:
                response_data.append({
                    'Key': key_id,
                    'Avg Response Time (s)': avg_time
                })
        
        if response_data:
            st.markdown("**⏱️ Average Response Times:**")
            df = pd.DataFrame(response_data)
            st.bar_chart(df.set_index('Key'))
    
    def _render_success_rate_chart(self, all_keys_status: Dict[str, Dict[str, Any]]) -> None:
        """Render success rate comparison chart"""
        log_info("Rendering success rate chart")
        
        success_data = []
        for key_id, status in all_keys_status.items():
            success_rate = status.get('success_rate', 0)
            success_data.append({
                'Key': key_id,
                'Success Rate (%)': success_rate
            })
        
        if success_data:
            st.markdown("**🎯 Success Rates:**")
            df = pd.DataFrame(success_data)
            st.bar_chart(df.set_index('Key'))


def create_key_monitor() -> RapidAPIKeyMonitor:
    """Factory function to create Key Monitor component"""
    log_info("Creating RapidAPIKeyMonitor component instance")
    return RapidAPIKeyMonitor()

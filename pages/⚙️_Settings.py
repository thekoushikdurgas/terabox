import streamlit as st
import json
from utils.terabox_config import get_config_manager, AppConfig, UnofficialConfig, OfficialAPIConfig
from typing import Dict, Any
from utils.browser_utils import get_browser_manager, create_browser_selection_ui

# Import time for file modification display
import time
st.set_page_config(
    page_title="Settings",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ TeraDL Settings")
st.markdown("Configure TeraDL application settings, API credentials, and preferences.")

# Get configuration manager
config_mgr = get_config_manager()

# Tabs for different settings categories
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(["🎯 General", "🌐 Browser", "💳 RapidAPI", "🎪 Unofficial Mode", "🏢 Official API", "🔧 Advanced", "📊 Status", "💾 Cache"])

# ============================================================================
# General Settings Tab
# ============================================================================
with tab1:
    st.header("🎯 General Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎨 Appearance")
        
        current_theme = config_mgr.app_config.theme
        theme = st.selectbox(
            "Theme:",
            options=["light", "dark"],
            index=0 if current_theme == "light" else 1,
            help="Choose the application theme"
        )
        
        current_lang = config_mgr.app_config.language
        language = st.selectbox(
            "Language:",
            options=["en", "es", "fr", "de", "zh"],
            index=["en", "es", "fr", "de", "zh"].index(current_lang) if current_lang in ["en", "es", "fr", "de", "zh"] else 0,
            help="Select interface language"
        )
    
    with col2:
        st.subheader("📁 File Handling")
        
        max_file_size = st.number_input(
            "Max File Size (MB):",
            min_value=1,
            max_value=10000,
            value=config_mgr.app_config.max_file_size_mb,
            help="Maximum file size for downloads"
        )
        
        enable_streaming = st.checkbox(
            "Enable Video Streaming",
            value=config_mgr.app_config.enable_streaming,
            help="Allow video streaming functionality"
        )
        
        enable_debug = st.checkbox(
            "Enable Debug Mode",
            value=config_mgr.app_config.enable_debug,
            help="Show debug information and logs"
        )
        
        download_dir = st.text_input(
            "Download Directory:",
            value=config_mgr.app_config.default_download_dir,
            help="Directory where downloaded files will be saved"
        )
    
    if st.button("💾 Save General Settings", type="primary"):
        config_mgr.update_app_config(
            theme=theme,
            language=language,
            max_file_size_mb=max_file_size,
            enable_streaming=enable_streaming,
            enable_debug=enable_debug,
            default_download_dir=download_dir
        )
        st.success("✅ General settings saved!")
        st.rerun()

# ============================================================================
# Browser Settings Tab
# ============================================================================
with tab2:
    st.header("🌐 Browser Settings")
    st.markdown("Configure browser preferences for opening direct file links.")
    
    # Get browser manager
    browser_manager = get_browser_manager()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔧 Browser Configuration")
        
        # Browser selection
        selected_browser = create_browser_selection_ui()
        
        if selected_browser:
            browser_info = browser_manager.supported_browsers.get(selected_browser)
            if browser_info:
                st.success(f"✅ **Selected:** {browser_info['icon']} {browser_info['name']}")
                st.info(f"📝 **Description:** {browser_info['description']}")
        
        # Test browser functionality
        st.subheader("🧪 Test Browser")
        test_url = st.text_input(
            "Test URL:",
            value="https://www.google.com",
            help="Enter a URL to test browser opening functionality"
        )
        
        if st.button("🌐 Test Open Browser", type="secondary"):
            if test_url:
                with st.spinner("Opening test URL..."):
                    result = browser_manager.open_url(test_url, selected_browser, new_tab=True)
                
                if result['status'] == 'success':
                    st.success(f"✅ {result['message']}")
                    st.balloons()
                else:
                    st.error(f"❌ {result['message']}")
            else:
                st.error("Please enter a test URL")
    
    with col2:
        st.subheader("📋 Available Browsers")
        
        # Show available browsers
        browsers = browser_manager.get_browser_list()
        
        for browser in browsers:
            if browser['available']:
                st.success(f"{browser['icon']} **{browser['name']}** - Available")
                st.caption(browser['description'])
            else:
                st.warning(f"{browser['icon']} **{browser['name']}** - Not Found")
                st.caption(browser['description'])
        
        st.markdown("---")
        
        st.subheader("💡 Browser Information")
        st.info("""
        **How Browser Selection Works:**
        
        • **Default Browser**: Uses your system's default browser
        • **Specific Browsers**: Opens links in the selected browser
        • **Fallback**: If selected browser fails, falls back to default
        • **Cross-Platform**: Works on Windows, macOS, and Linux
        
        **When is this used?**
        • "Open Direct File Link" buttons in all modes
        • Direct access to TeraBox file URLs
        • Quick preview without downloading
        """)
        
        # Show current session browser preference
        current_pref = st.session_state.get('preferred_browser', 'default')
        if current_pref != 'default':
            browser_info = browser_manager.supported_browsers.get(current_pref)
            if browser_info:
                st.success(f"🎯 **Current Session Preference:** {browser_info['icon']} {browser_info['name']}")
        else:
            st.info("🎯 **Current Session Preference:** System Default")

# ============================================================================
# RapidAPI Settings Tab  
# ============================================================================
with tab3:
    st.header("💳 RapidAPI Configuration")
    st.markdown("Configure RapidAPI settings for commercial TeraBox service access")
    
    # Get RapidAPI configuration
    rapidapi_config = config_mgr.get_rapidapi_config()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔑 API Settings")
        
        # API Key (encrypted in storage)
        current_key_display = "••••••••••••••••" if rapidapi_config.api_key else ""
        api_key = st.text_input(
            "RapidAPI Key:",
            value=current_key_display,
            type="password",
            help="Your RapidAPI key for TeraBox service access"
        )
        
        base_url = st.text_input(
            "Base URL:",
            value=rapidapi_config.base_url,
            help="RapidAPI service base URL"
        )
        
        host = st.text_input(
            "API Host:",
            value=rapidapi_config.host,
            help="RapidAPI host header value"
        )
    
    with col2:
        st.subheader("⚙️ Request Settings")
        
        timeout = st.number_input(
            "Request Timeout (seconds):",
            min_value=5,
            max_value=120,
            value=rapidapi_config.timeout,
            help="Timeout for API requests"
        )
        
        max_retries = st.number_input(
            "Max Retries:",
            min_value=1,
            max_value=10,
            value=rapidapi_config.max_retries,
            help="Maximum retry attempts for failed requests"
        )
        
        retry_delay = st.number_input(
            "Retry Delay (seconds):",
            min_value=0.5,
            max_value=10.0,
            value=rapidapi_config.retry_delay,
            step=0.5,
            help="Delay between retry attempts"
        )
    
    st.subheader("💾 Cache Settings")
    col3, col4 = st.columns(2)
    
    with col3:
        enable_cache = st.checkbox(
            "Enable RapidAPI Caching",
            value=rapidapi_config.enable_cache,
            help="Cache API responses to reduce API calls"
        )
    
    with col4:
        cache_ttl_hours = st.number_input(
            "Cache TTL (hours):",
            min_value=1,
            max_value=168,  # 1 week
            value=rapidapi_config.cache_ttl_hours,
            help="How long to cache API responses"
        )
    
    if st.button("💾 Save RapidAPI Settings", type="primary"):
        # Only update API key if it's not the masked display value
        update_kwargs = {
            'base_url': base_url,
            'host': host,
            'timeout': timeout,
            'max_retries': max_retries,
            'retry_delay': retry_delay,
            'enable_cache': enable_cache,
            'cache_ttl_hours': cache_ttl_hours
        }
        
        if api_key and api_key != current_key_display:
            update_kwargs['api_key'] = api_key
        
        config_mgr.update_rapidapi_config(**update_kwargs)
        st.success("✅ RapidAPI settings saved!")
        st.rerun()
    
    # API Key Management
    st.subheader("🔐 API Key Management")
    col5, col6 = st.columns(2)
    
    with col5:
        if st.button("🔍 Test API Key"):
            if config_mgr.has_rapidapi_key():
                with st.spinner("Testing API key..."):
                    from utils.terabox_rapidapi import TeraBoxRapidAPI
                    client = TeraBoxRapidAPI()
                    result = client.validate_api_key()
                    
                    if result['status'] == 'success':
                        st.success(f"✅ {result['message']}")
                    else:
                        st.error(f"❌ {result['message']}")
            else:
                st.warning("⚠️ No API key configured")
    
    with col6:
        if st.button("🗑️ Clear API Key"):
            config_mgr.clear_rapidapi_key()
            st.success("🗑️ API key cleared!")
            st.rerun()
    
    # Configuration Status
    st.subheader("📊 Configuration Status")
    status_col1, status_col2 = st.columns(2)
    
    with status_col1:
        st.metric("API Key Status", "Configured" if config_mgr.has_rapidapi_key() else "Not Set")
        st.metric("Cache Status", "Enabled" if rapidapi_config.enable_cache else "Disabled")
    
    with status_col2:
        st.metric("Base URL", "✅ Set" if rapidapi_config.base_url else "❌ Missing")
        st.metric("Timeout", f"{rapidapi_config.timeout}s")

# ============================================================================
# Unofficial Mode Settings Tab
# ============================================================================
with tab4:
    st.header("🎪 Unofficial Mode Settings")
    st.info("Configure settings for the unofficial scraping mode")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔧 Processing Settings")
        
        default_mode = st.selectbox(
            "Default Processing Mode:",
            options=[1, 2, 3],
            index=[1, 2, 3].index(config_mgr.unofficial_config.default_mode),
            help="Default mode for TeraBox extraction"
        )
        
        max_retries = st.number_input(
            "Max Retries:",
            min_value=1,
            max_value=10,
            value=config_mgr.unofficial_config.max_retries,
            help="Maximum number of retry attempts"
        )
        
        retry_delay = st.number_input(
            "Retry Delay (seconds):",
            min_value=0.1,
            max_value=10.0,
            value=config_mgr.unofficial_config.retry_delay,
            step=0.1,
            help="Delay between retry attempts"
        )
    
    with col2:
        st.subheader("🌐 Network Settings")
        
        timeout_seconds = st.number_input(
            "Request Timeout (seconds):",
            min_value=5,
            max_value=120,
            value=config_mgr.unofficial_config.timeout_seconds,
            help="Timeout for network requests"
        )
        
        user_agents_rotation = st.checkbox(
            "Enable User Agent Rotation",
            value=config_mgr.unofficial_config.user_agents_rotation,
            help="Rotate user agents to avoid detection"
        )
        
        enable_logging = st.checkbox(
            "Enable Request Logging",
            value=config_mgr.unofficial_config.enable_logging,
            help="Log network requests for debugging"
        )
    
    if st.button("💾 Save Unofficial Settings", type="primary"):
        config_mgr.update_unofficial_config(
            default_mode=default_mode,
            max_retries=max_retries,
            retry_delay=retry_delay,
            timeout_seconds=timeout_seconds,
            user_agents_rotation=user_agents_rotation,
            enable_logging=enable_logging
        )
        st.success("✅ Unofficial mode settings saved!")
        st.rerun()
    
    # Mode descriptions
    with st.expander("ℹ️ Processing Mode Details"):
        st.markdown("""
        **Mode 1: Dynamic Cookies**
        - Real-time scraping with dynamic cookie extraction
        - Most reliable but slower
        - Good for development and testing
        
        **Mode 2: Static Cookies**
        - Uses pre-configured static cookies
        - Faster but requires valid session cookies
        - Best for production with maintained sessions
        
        **Mode 3: External Service**
        - Uses external service for sign/timestamp generation
        - Most stable and feature-complete
        - Recommended for production use
        """)

# ============================================================================
# Official API Settings Tab
# ============================================================================
with tab5:
    st.header("🏢 Official API Settings")
    st.info("Configure TeraBox Official API credentials and settings")
    
    # Credentials section
    st.subheader("🔐 API Credentials")
    
    has_credentials = config_mgr.has_official_credentials()
    
    if has_credentials:
        st.success("✅ API credentials are configured")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔑 Update Credentials"):
                st.session_state.show_credential_form = True
        
        with col2:
            if st.button("🗑️ Clear Credentials", type="secondary"):
                config_mgr.clear_official_credentials()
                st.success("✅ Credentials cleared!")
                st.rerun()
    else:
        st.warning("⚠️ No API credentials configured")
        st.session_state.show_credential_form = True
    
    # Credential form
    if st.session_state.get('show_credential_form', False):
        with st.form("credentials_form"):
            st.markdown("**Enter your TeraBox API credentials:**")
            
            client_id = st.text_input(
                "Client ID (AppKey):",
                type="password",
                help="The AppKey provided by TeraBox"
            )
            
            client_secret = st.text_input(
                "Client Secret (SecretKey):",
                type="password",
                help="The SecretKey provided by TeraBox"
            )
            
            private_secret = st.text_input(
                "Private Secret:",
                type="password",
                help="The private secret for signature generation"
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.form_submit_button("💾 Save Credentials", type="primary"):
                    if client_id and client_secret and private_secret:
                        config_mgr.set_official_credentials(client_id, client_secret, private_secret)
                        st.success("✅ Credentials saved successfully!")
                        st.session_state.show_credential_form = False
                        st.rerun()
                    else:
                        st.error("❌ Please fill in all credential fields")
            
            with col2:
                if st.form_submit_button("❌ Cancel"):
                    st.session_state.show_credential_form = False
                    st.rerun()
    
    # API Settings
    st.subheader("🔧 API Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        api_domain = st.text_input(
            "API Domain:",
            value=config_mgr.official_config.api_domain,
            help="TeraBox API domain"
        )
        
        default_stream_quality = st.selectbox(
            "Default Stream Quality:",
            options=["M3U8_AUTO_480", "M3U8_AUTO_720", "M3U8_AUTO_1080", "M3U8_MP3_128"],
            index=["M3U8_AUTO_480", "M3U8_AUTO_720", "M3U8_AUTO_1080", "M3U8_MP3_128"].index(
                config_mgr.official_config.default_stream_quality
            ) if config_mgr.official_config.default_stream_quality in ["M3U8_AUTO_480", "M3U8_AUTO_720", "M3U8_AUTO_1080", "M3U8_MP3_128"] else 1,
            help="Default quality for video streaming"
        )
    
    with col2:
        enable_token_refresh = st.checkbox(
            "Enable Automatic Token Refresh",
            value=config_mgr.official_config.enable_token_refresh,
            help="Automatically refresh expired tokens"
        )
        
        token_refresh_threshold = st.number_input(
            "Token Refresh Threshold (seconds):",
            min_value=300,
            max_value=7200,
            value=config_mgr.official_config.token_refresh_threshold,
            help="Refresh token when it expires within this time"
        )
    
    if st.button("💾 Save API Settings", type="primary"):
        config_mgr.update_official_config(
            api_domain=api_domain,
            default_stream_quality=default_stream_quality,
            enable_token_refresh=enable_token_refresh,
            token_refresh_threshold=token_refresh_threshold
        )
        st.success("✅ API settings saved!")
        st.rerun()

# ============================================================================
# Advanced Settings Tab
# ============================================================================
with tab6:
    st.header("🔧 Advanced Settings")
    st.warning("⚠️ Advanced settings for experienced users only")
    
    # Configuration export/import
    st.subheader("📦 Configuration Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Export Configuration:**")
        if st.button("📤 Export Config"):
            config_data = config_mgr.export_config()
            config_json = json.dumps(config_data, indent=2)
            
            st.download_button(
                label="💾 Download Config File",
                data=config_json,
                file_name="teradl_config.json",
                mime="application/json"
            )
    
    with col2:
        st.markdown("**Import Configuration:**")
        uploaded_file = st.file_uploader(
            "Choose config file",
            type=['json'],
            help="Upload a previously exported configuration file"
        )
        
        if uploaded_file is not None:
            try:
                config_data = json.load(uploaded_file)
                
                if st.button("📥 Import Config"):
                    if config_mgr.import_config(config_data):
                        st.success("✅ Configuration imported successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to import configuration")
            except Exception as e:
                st.error(f"❌ Invalid config file: {e}")
    
    # Reset settings
    st.subheader("🔄 Reset Settings")
    st.markdown("Reset all settings to default values")
    
    if st.button("🔄 Reset to Defaults", type="secondary"):
        if st.button("⚠️ Confirm Reset", type="secondary"):
            config_mgr.reset_to_defaults()
            st.success("✅ Settings reset to defaults!")
            st.rerun()
    
    # Environment variables
    st.subheader("🌍 Environment Variables")
    
    with st.expander("📋 Supported Environment Variables"):
        st.markdown("""
        **Application Settings:**
        - `TERADL_API_MODE`: API mode (unofficial/official)
        - `TERADL_THEME`: Theme (light/dark)
        - `TERADL_LANGUAGE`: Language code
        - `TERADL_MAX_FILE_SIZE`: Max file size in MB
        - `TERADL_ENABLE_STREAMING`: Enable streaming (true/false)
        - `TERADL_ENABLE_DEBUG`: Enable debug mode (true/false)
        - `TERADL_DOWNLOAD_DIR`: Default download directory
        
        **Unofficial Mode:**
        - `TERADL_DEFAULT_MODE`: Default processing mode (1/2/3)
        - `TERADL_MAX_RETRIES`: Maximum retry attempts
        - `TERADL_RETRY_DELAY`: Delay between retries
        - `TERADL_TIMEOUT`: Request timeout in seconds
        
        **Official API:**
        - `TERABOX_CLIENT_ID`: TeraBox Client ID
        - `TERABOX_CLIENT_SECRET`: TeraBox Client Secret
        - `TERABOX_PRIVATE_SECRET`: TeraBox Private Secret
        - `TERABOX_API_DOMAIN`: API domain
        - `TERABOX_STREAM_QUALITY`: Default stream quality
        """)

# ============================================================================
# Status Tab
# ============================================================================
with tab7:
    st.header("📊 Configuration Status")
    st.markdown("Current configuration overview and system status")
    
    # Configuration summary
    st.subheader("📋 Configuration Summary")
    
    config_summary = config_mgr.get_config_summary()
    
    col1, col2 = st.columns(2)
    
    with col1:
        for i, (key, value) in enumerate(list(config_summary.items())[:len(config_summary)//2]):
            st.metric(key, value)
    
    with col2:
        for key, value in list(config_summary.items())[len(config_summary)//2:]:
            st.metric(key, value)
    
    # System information
    st.subheader("💻 System Information")
    
    import sys
    import platform
    
    system_info = {
        "Python Version": sys.version.split()[0],
        "Platform": platform.platform(),
        "Streamlit Version": st.__version__,
        "Config File": "✅ Found" if config_mgr.config_file else "❌ Not Found"
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        for key, value in list(system_info.items())[:2]:
            st.text(f"{key}: {value}")
    
    with col2:
        for key, value in list(system_info.items())[2:]:
            st.text(f"{key}: {value}")
    
    # Raw configuration (for debugging)
    with st.expander("🔍 Raw Configuration (Debug)"):
        if config_mgr.app_config.enable_debug:
            st.json(config_mgr.export_config())
        else:
            st.info("Enable debug mode in General settings to view raw configuration")
    
    # Configuration file status
    st.subheader("📁 Configuration File")
    
    import os
    
    if os.path.exists(config_mgr.config_file):
        file_stat = os.stat(config_mgr.config_file)
        st.success(f"✅ Configuration file found: {config_mgr.config_file}")
        st.text(f"Size: {file_stat.st_size} bytes")
        st.text(f"Modified: {time.ctime(file_stat.st_mtime)}")
    else:
        st.warning("⚠️ Configuration file not found - using defaults")
    
    # Quick actions
    st.subheader("⚡ Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Reload Config"):
            config_mgr._load_config()
            st.success("✅ Configuration reloaded!")
            st.rerun()
    
    with col2:
        if st.button("💾 Save Config"):
            if config_mgr.save_config():
                st.success("✅ Configuration saved!")
            else:
                st.error("❌ Failed to save configuration")
    
    with col3:
        if st.button("🧹 Clear Cache"):
            st.cache_data.clear()
            st.success("✅ Cache cleared!")

# ============================================================================
# Cache Management Tab
# ============================================================================
with tab8:
    st.header("💾 Cache Management")
    st.markdown("Manage RapidAPI response caching and performance optimization.")
    
    # Check if RapidAPI client is available in session state
    if 'rapidapi_client' in st.session_state and st.session_state.rapidapi_client:
        rapidapi_client = st.session_state.rapidapi_client
        
        # Cache Status Overview
        st.subheader("📊 Cache Status Overview")
        
        cache_info = rapidapi_client.get_cache_info()
        
        if cache_info.get('enabled'):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.success("✅ **Cache Enabled**")
                st.info(f"📁 Directory: `{cache_info.get('cache_directory', 'Unknown')}`")
            
            with col2:
                st.info(f"⏰ TTL: {cache_info.get('ttl_hours', 24)} hours")
                st.info(f"🔧 Version: {cache_info.get('cache_version', '1.0')}")
            
            with col3:
                # Get quick stats
                cache_stats = rapidapi_client.get_cache_stats()
                if 'error' not in cache_stats:
                    st.metric("📄 Total Files", cache_stats.get('total_files', 0))
                    st.metric("💾 Size", f"{cache_stats.get('total_size_mb', 0):.2f} MB")
            
            # Detailed Cache Statistics
            st.markdown("---")
            st.subheader("📈 Detailed Statistics")
            
            if st.button("🔄 Refresh Cache Stats"):
                with st.spinner("Loading cache statistics..."):
                    cache_stats = rapidapi_client.get_cache_stats()
                
                if 'error' not in cache_stats:
                    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
                    
                    with col_stat1:
                        st.metric("📄 Total Files", cache_stats.get('total_files', 0))
                    
                    with col_stat2:
                        st.metric("✅ Valid Files", cache_stats.get('valid_files', 0))
                    
                    with col_stat3:
                        st.metric("⚠️ Expired Files", cache_stats.get('expired_files', 0))
                    
                    with col_stat4:
                        total_files = cache_stats.get('total_files', 0)
                        valid_files = cache_stats.get('valid_files', 0)
                        efficiency = (valid_files / total_files * 100) if total_files > 0 else 0
                        st.metric("🎯 Efficiency", f"{efficiency:.1f}%")
                    
                    # Show file list if available
                    if cache_stats.get('files'):
                        st.markdown("### 📋 Cache Files")
                        
                        # Create a more detailed table
                        import pandas as pd
                        
                        files_data = []
                        for file_info in cache_stats['files']:
                            files_data.append({
                                'SURL': file_info.get('surl', 'Unknown'),
                                'Age (hours)': f"{file_info.get('age_hours', 0):.1f}",
                                'Size (KB)': f"{file_info.get('size_kb', 0):.1f}",
                                'Status': '✅ Valid' if file_info.get('is_valid', False) else '⚠️ Expired',
                                'Created': file_info.get('created_at', 'Unknown')[:16] if file_info.get('created_at') else 'Unknown',
                                'TeraBox URL': file_info.get('terabox_url', 'Unknown')[:50] + '...' if len(file_info.get('terabox_url', '')) > 50 else file_info.get('terabox_url', 'Unknown')
                            })
                        
                        if files_data:
                            df = pd.DataFrame(files_data)
                            st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.error(f"❌ Error getting cache stats: {cache_stats.get('error', 'Unknown error')}")
            
            # Cache Management Actions
            st.markdown("---")
            st.subheader("🛠️ Cache Management Actions")
            
            col_action1, col_action2, col_action3 = st.columns(3)
            
            with col_action1:
                st.markdown("**🧹 Cleanup Operations**")
                
                if st.button("Clean Expired Cache", type="secondary", key="settings_clean_expired"):
                    with st.spinner("Cleaning expired cache files..."):
                        cleanup_result = rapidapi_client.cleanup_expired_cache()
                    
                    if cleanup_result.get('status') == 'success':
                        cleaned_files = cleanup_result.get('cleaned_files', 0)
                        if cleaned_files > 0:
                            st.success(f"✅ Cleaned {cleaned_files} expired files")
                        else:
                            st.info("ℹ️ No expired files found")
                    else:
                        st.error(f"❌ Cleanup failed: {cleanup_result.get('message', 'Unknown error')}")
            
            with col_action2:
                st.markdown("**🗑️ Clear Operations**")
                
                if st.button("Clear All Cache", type="secondary", key="settings_clear_all"):
                    if st.session_state.get('settings_confirm_clear', False):
                        with st.spinner("Clearing all cache files..."):
                            clear_result = rapidapi_client.clear_cache()
                        
                        if clear_result.get('status') == 'success':
                            cleared_files = clear_result.get('cleared', 0)
                            st.success(f"✅ Cleared {cleared_files} files")
                        else:
                            st.error(f"❌ Clear failed: {clear_result.get('message', 'Unknown error')}")
                        
                        st.session_state.settings_confirm_clear = False
                    else:
                        st.session_state.settings_confirm_clear = True
                        st.warning("⚠️ Click again to confirm")
            
            with col_action3:
                st.markdown("**📊 Information**")
                
                if st.button("View Cache Directory", key="settings_view_dir"):
                    import os
                    cache_dir = cache_info.get('cache_directory', '')
                    if os.path.exists(cache_dir):
                        st.success(f"📁 Cache directory exists: `{cache_dir}`")
                        
                        # Show directory contents
                        try:
                            files = [f for f in os.listdir(cache_dir) if f.startswith('teraboxlink_') and f.endswith('.json')]
                            st.info(f"Found {len(files)} cache files")
                        except Exception as e:
                            st.error(f"Error reading directory: {e}")
                    else:
                        st.warning("📁 Cache directory does not exist")
            
            # Cache Configuration
            st.markdown("---")
            st.subheader("⚙️ Cache Configuration")
            
            col_config1, col_config2 = st.columns(2)
            
            with col_config1:
                st.markdown("**Current Settings:**")
                st.info(f"Cache TTL: {cache_info.get('ttl_hours', 24)} hours")
                st.info(f"Cache Directory: `{cache_info.get('cache_directory', 'Unknown')}`")
                st.info(f"Cache Version: {cache_info.get('cache_version', '1.0')}")
            
            with col_config2:
                st.markdown("**Cache Benefits:**")
                st.success("⚡ Faster response times")
                st.success("💰 Reduced API costs")
                st.success("📊 Better user experience")
                st.success("🔄 Automatic expiry management")
        
        else:
            st.warning("⚠️ **Cache is Disabled**")
            st.info("Caching is not enabled for the current RapidAPI client.")
            
            with st.expander("ℹ️ How to Enable Caching"):
                st.markdown("""
                To enable caching for RapidAPI responses:
                
                1. **Go to RapidAPI Mode** - Navigate to the 💳 RapidAPI Mode page
                2. **Configure API Key** - Enter and validate your RapidAPI key
                3. **Caching Auto-Enabled** - Caching is automatically enabled when you create a RapidAPI client
                4. **Use Cache Manager** - Access cache controls in the Cache Manager tab
                
                **Cache Features:**
                - Automatic response caching using TeraBox link identifiers (surl)
                - Configurable TTL (Time To Live) - default 24 hours
                - Automatic cleanup of expired entries
                - Cache statistics and monitoring
                - Manual cache management controls
                """)
    
    else:
        st.info("ℹ️ **RapidAPI Client Not Available**")
        st.markdown("""
        Cache management is available when you have an active RapidAPI client session.
        
        **To access cache management:**
        1. Go to the 💳 RapidAPI Mode page
        2. Configure and validate your RapidAPI key
        3. Return to this settings page for cache management
        
        **What is Response Caching?**
        
        Response caching stores RapidAPI responses locally to:
        - Provide instant access to previously fetched files
        - Reduce API usage and associated costs
        - Improve user experience with faster response times
        - Enable offline access to cached data
        """)
        
        if st.button("🚀 Go to RapidAPI Mode"):
            st.switch_page("pages/💳_RapidAPI_Mode.py")

# Footer
st.markdown("---")
st.info("💡 **Tip:** Changes are automatically saved when you click the save buttons. Some changes may require restarting the application to take effect.")


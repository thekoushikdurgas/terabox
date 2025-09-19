import streamlit as st
import json
from terabox_config import get_config_manager, AppConfig, UnofficialConfig, OfficialAPIConfig
from typing import Dict, Any

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
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎯 General", "🎪 Unofficial Mode", "🏢 Official API", "🔧 Advanced", "📊 Status"])

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
    
    if st.button("💾 Save General Settings", type="primary"):
        config_mgr.update_app_config(
            theme=theme,
            language=language,
            max_file_size_mb=max_file_size,
            enable_streaming=enable_streaming,
            enable_debug=enable_debug
        )
        st.success("✅ General settings saved!")
        st.rerun()

# ============================================================================
# Unofficial Mode Settings Tab
# ============================================================================
with tab2:
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
with tab3:
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
with tab4:
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
with tab5:
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

# Footer
st.markdown("---")
st.info("💡 **Tip:** Changes are automatically saved when you click the save buttons. Some changes may require restarting the application to take effect.")

# Import time for file modification display
import time

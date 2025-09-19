"""
RapidAPI Main Interface Component

This component orchestrates all RapidAPI components and provides the main interface
for the RapidAPI Mode page. It handles component initialization, tab management,
and overall page layout.

Component Responsibilities:
- Component initialization and management
- Tab-based interface coordination
- State management and synchronization
- Browser integration setup
- Error handling and user feedback
- Performance monitoring and logging

Interface Architecture:
- Tab-based organization for different functionalities
- Component-based design for modularity
- State management integration
- Comprehensive error handling
- Performance monitoring
"""

import streamlit as st
from typing import Dict, Any, Optional
from utils.terabox_config import get_config_manager
from utils.state_manager import StateManager
from utils.config import log_info, log_error
from utils.browser_utils import create_browser_selection_ui

# Import all RapidAPI components
from .rapidapi_api_key_manager import create_rapidapi_key_manager
from .rapidapi_single_file_processor import create_single_file_processor
from .rapidapi_bulk_processor import create_bulk_processor
from .rapidapi_text_processor import create_text_processor
from .rapidapi_csv_manager import create_csv_manager
from .rapidapi_cache_manager import create_cache_manager
from .rapidapi_key_monitor import create_key_monitor


class RapidAPIMainInterface:
    """
    Main Interface Orchestrator for RapidAPI Mode - OPTIMIZED VERSION
    
    Coordinates all RapidAPI components and provides the main user interface
    with tab-based organization and comprehensive functionality.
    
    PERFORMANCE OPTIMIZATIONS:
    - Component caching in session state to prevent re-initialization
    - Lazy loading of components only when needed
    - Singleton pattern for interface instance
    - Reduced API validation calls
    - Optimized state management
    
    Features:
    - Component lifecycle management with caching
    - Tab-based interface organization
    - State synchronization across components
    - Browser integration setup
    - Error handling and recovery
    - Performance monitoring and optimization
    """
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to prevent multiple instances"""
        if cls._instance is None:
            log_info("Creating new RapidAPIMainInterface instance")
            cls._instance = super().__new__(cls)
        else:
            log_info("Reusing existing RapidAPIMainInterface instance")
        return cls._instance
    
    def __init__(self):
        """Initialize the main RapidAPI interface with caching optimization"""
        # Prevent re-initialization if already initialized
        if hasattr(self, '_initialized'):
            log_info("RapidAPIMainInterface already initialized, skipping re-initialization")
            return
            
        log_info("Initializing RapidAPIMainInterface orchestrator")
        
        # Load configuration
        self.config_mgr = get_config_manager()
        self.rapidapi_config = self.config_mgr.get_rapidapi_config()
        
        # Initialize components with caching
        self.components = self._initialize_components_cached()
        
        # Initialize session state
        self._initialize_session_state()
        
        # Mark as initialized
        self._initialized = True
        
        log_info("RapidAPIMainInterface initialization completed")
    
    def _initialize_components_cached(self) -> Dict[str, Any]:
        """Initialize all RapidAPI components with session state caching"""
        log_info("Initializing all RapidAPI components")
        
        # Check if components are already cached in session state
        if 'rapidapi_components_cache' in st.session_state:
            log_info("Using cached RapidAPI components from session state")
            return st.session_state.rapidapi_components_cache
        
        # Create components for the first time
        log_info("Creating RapidAPI components for the first time")
        components = {}
        
        # Initialize components with individual logging
        component_creators = [
            ('key_manager', create_rapidapi_key_manager, 'RapidAPIKeyManager'),
            ('single_processor', create_single_file_processor, 'RapidAPISingleFileProcessor'),
            ('bulk_processor', create_bulk_processor, 'RapidAPIBulkProcessor'),
            ('text_processor', create_text_processor, 'RapidAPITextProcessor'),
            ('csv_manager', create_csv_manager, 'RapidAPICSVManager'),
            ('cache_manager', create_cache_manager, 'RapidAPICacheManager'),
            ('key_monitor', create_key_monitor, 'RapidAPIKeyMonitor')
        ]
        
        for key, creator_func, component_name in component_creators:
            try:
                log_info(f"Creating {component_name} component instance")
                components[key] = creator_func()
                log_info(f"Initializing {component_name} component")
                log_info(f"{component_name} component initialized successfully")
            except Exception as e:
                log_error(e, f"Failed to initialize {component_name} component")
                # Continue with other components even if one fails
                components[key] = None
        
        # Cache components in session state for reuse
        st.session_state.rapidapi_components_cache = components
        
        log_info(f"All {len(components)} RapidAPI components initialized successfully")
        return components
    
    def _initialize_session_state(self) -> None:
        """Initialize RapidAPI-specific session state variables with optimization"""
        log_info("Initializing RapidAPI session state variables")
        
        # Check if session state is already initialized
        if 'rapidapi_session_initialized' in st.session_state:
            log_info("RapidAPI session state already initialized, updating only if needed")
            self._update_session_state_if_needed()
            return
        
        # First-time session state initialization with defaults
        session_defaults = {
            'rapidapi_client': None,
            'rapidapi_validated': False,
            'current_rapidapi_key': self.rapidapi_config.api_key or "",
            'rapidapi_last_validation': None,
            'rapidapi_session_initialized': True
        }
        
        for key, default_value in session_defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
                log_info(f"Initialized session state: {key}")
        
        # Log current session state for debugging
        state_summary = {
            'client_available': bool(st.session_state.rapidapi_client),
            'validated': st.session_state.rapidapi_validated,
            'key_length': len(st.session_state.current_rapidapi_key)
        }
        log_info(f"RapidAPI session state summary: {state_summary}")
    
    def _update_session_state_if_needed(self) -> None:
        """Update session state only if configuration has changed"""
        current_key = self.rapidapi_config.api_key or ""
        stored_key = st.session_state.get('current_rapidapi_key', '')
        
        # Only update if configuration has changed
        if current_key != stored_key:
            log_info("Configuration change detected, updating session state")
            st.session_state.current_rapidapi_key = current_key
            # Reset validation status if key changed
            st.session_state.rapidapi_validated = False
            st.session_state.rapidapi_client = None
        else:
            log_info("No configuration changes detected, preserving session state")
    
    def render_complete_interface(self) -> None:
        """
        Render the complete RapidAPI interface
        
        This is the main entry point that renders the entire RapidAPI Mode page
        with all components and functionality.
        """
        log_info("Rendering complete RapidAPI interface")
        
        # Page configuration
        self._configure_page()
        
        # Header and service information
        self._render_header_section()
        
        # API key configuration section
        self._render_api_key_section()
        
        # Main functionality (only if API key is validated)
        if st.session_state.rapidapi_client and st.session_state.rapidapi_validated:
            self._render_main_functionality()
        else:
            self._render_getting_started_section()
    
    def _configure_page(self) -> None:
        """Configure Streamlit page settings"""
        log_info("Configuring RapidAPI page settings")
        
        # Page configuration is already set in the main file
        # This method can be used for additional page-specific configuration
        pass
    
    def _render_header_section(self) -> None:
        """Render page header and service information"""
        log_info("Rendering header and service information")
        
        # Main header
        st.title("💳 RapidAPI TeraBox Service")
        st.markdown("Commercial TeraBox API service for reliable, professional-grade file extraction")
        
        # Service overview
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.info("""
            **💳 RapidAPI Mode** provides commercial-grade TeraBox access:
            - ✅ Professional reliability and uptime
            - ✅ No complex setup or authentication
            - ✅ Direct download links guaranteed
            - ✅ Commercial support and SLA
            - 💰 Requires RapidAPI subscription
            """)
        
        with col2:
            if st.button("🔄 Switch to Other Modes", key="switch_modes_btn"):
                st.switch_page("pages/📊_Mode_Comparison.py")
    
    def _render_api_key_section(self) -> None:
        """Render API key configuration section"""
        log_info("Rendering API key configuration section")
        
        st.header("🔑 RapidAPI Configuration")
        
        # API key setup instructions
        self._render_api_key_instructions()
        
        # API key management interface
        self.components['key_manager'].render_key_input_section()
        
        # API status display
        self.components['key_manager'].render_api_status_section()
    
    def _render_api_key_instructions(self) -> None:
        """Render API key setup instructions"""
        with st.expander("📋 How to Get RapidAPI Key", expanded=not st.session_state.rapidapi_validated):
            st.markdown("""
            ### Step 1: Create RapidAPI Account
            1. Go to [RapidAPI.com](https://rapidapi.com)
            2. Sign up for a free account
            3. Verify your email address
           
            ### Step 2: Subscribe to TeraBox Service
            1. Search for "terabox-downloader-direct-download-link-generator2"
            2. Choose a subscription plan:
               - **Basic Plan**: Limited requests per month
               - **Pro Plan**: Higher request limits
               - **Ultra Plan**: Unlimited requests
            3. Subscribe to your chosen plan
           
            ### Step 3: Get Your API Key
            1. Go to your RapidAPI dashboard
            2. Find the TeraBox service in your subscriptions
            3. Copy your X-RapidAPI-Key
            4. Paste it in the configuration below
           
            ### Step 4: Test Your Setup
            1. Enter your API key below
            2. Click "Validate API Key"
            3. Test with sample URLs
            4. Start using the service!
           
            **💡 Tip:** Keep your API key secure and don't share it publicly.
            """)
    
    def _render_main_functionality(self) -> None:
        """Render main functionality when API key is validated"""
        log_info("Rendering main RapidAPI functionality")
        
        st.header("📁 File Processing")
        
        # Browser selection section
        self._render_browser_section()
        
        # Main tab interface
        self._render_tab_interface()
    
    def _render_browser_section(self) -> None:
        """Render browser configuration section"""
        log_info("Rendering browser configuration section")
        
        with st.expander("🌐 Browser Settings", expanded=False):
            col_browser, col_info = st.columns([2, 1])
            
            with col_browser:
                selected_browser = create_browser_selection_ui()
                if selected_browser:
                    st.success(f"✅ Browser configured")
                    log_info(f"Browser configured: {selected_browser}")
            
            with col_info:
                st.info("""
                **Browser Selection:**
                Choose which browser to use when opening direct file links.
                The selected browser will be used for all "Open Direct File Link" operations.
                """)
    
    def _render_tab_interface(self) -> None:
        """Render main tab-based interface"""
        log_info("Rendering main tab interface")
        
        # Create tabs for different functionalities
        tab_names = [
            "🔗 Single File", 
            "📋 Multiple Files", 
            "📝 Text Processor", 
            "📊 CSV Manager", 
            "🧪 Test & Debug", 
            "📊 Usage Info", 
            "💾 Cache Manager", 
            "🔑 Key Manager"
        ]
        
        tabs = st.tabs(tab_names)
        
        # Render content for each tab
        with tabs[0]:  # Single File
            self.components['single_processor'].render_single_file_section()
        
        with tabs[1]:  # Multiple Files
            self.components['bulk_processor'].render_bulk_processing_section()
        
        with tabs[2]:  # Text Processor
            self.components['text_processor'].render_text_processor_section()
        
        with tabs[3]:  # CSV Manager
            self.components['csv_manager'].render_csv_manager_section()
        
        with tabs[4]:  # Test & Debug
            self._render_test_debug_section()
        
        with tabs[5]:  # Usage Info
            self._render_usage_info_section()
        
        with tabs[6]:  # Cache Manager
            self.components['cache_manager'].render_cache_manager_section()
        
        with tabs[7]:  # Key Manager
            self.components['key_monitor'].render_key_monitor_section()
    
    def _render_test_debug_section(self) -> None:
        """Render testing and debugging section"""
        log_info("Rendering test and debug section")
        
        st.subheader("🧪 Testing & Debugging")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**API Testing:**")
            
            if st.button("🔍 Test API Key", key="test_api_key_btn"):
                with st.spinner("Testing API key..."):
                    validation = st.session_state.rapidapi_client.validate_api_key()
                st.json(validation)
            
            if st.button("🧪 Test with Sample URLs", key="test_sample_urls_btn"):
                with st.spinner("Testing with sample URLs..."):
                    test_results = st.session_state.rapidapi_client.test_with_sample_url()
                st.json(test_results)
        
        with col2:
            st.markdown("**Service Information:**")
            
            if st.button("📊 Get API Status", key="get_api_status_btn"):
                api_status = st.session_state.rapidapi_client.get_api_status()
                st.json(api_status)
            
            if st.button("📈 Get Usage Info", key="get_usage_info_btn"):
                usage_info = st.session_state.rapidapi_client.get_usage_info()
                st.json(usage_info)
        
        # Custom URL testing
        st.markdown("**Custom URL Testing:**")
        test_url = st.text_input(
            "Test URL:", 
            placeholder="https://terabox.com/s/your_test_link",
            key="custom_test_url"
        )
        
        if st.button("🧪 Test Custom URL", key="test_custom_url_btn"):
            if test_url:
                with st.spinner("Testing custom URL..."):
                    result = st.session_state.rapidapi_client.get_file_info(test_url)
                
                if 'error' in result:
                    st.error(f"❌ Test failed: {result['error']}")
                else:
                    st.success("✅ Test successful!")
                    st.json(result)
            else:
                st.error("Please enter a test URL")
    
    def _render_usage_info_section(self) -> None:
        """Render usage information section"""
        log_info("Rendering usage information section")
        
        st.subheader("📊 Usage Information")
        
        # Pricing information
        pricing_info = st.session_state.rapidapi_client.get_pricing_info()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**💰 Pricing Model:**")
            st.info(pricing_info['pricing_model'])
            
            st.markdown("**✅ Benefits:**")
            for benefit in pricing_info['benefits']:
                st.text(f"• {benefit}")
        
        with col2:
            st.markdown("**⚠️ Considerations:**")
            for consideration in pricing_info['considerations']:
                st.text(f"• {consideration}")
            
            if st.button("🌐 Open RapidAPI Dashboard", key="open_dashboard_btn"):
                st.markdown(f"[Open Dashboard]({pricing_info['dashboard']})")
        
        # Supported formats
        st.markdown("**🔗 Supported URL Formats:**")
        supported_formats = st.session_state.rapidapi_client.get_supported_formats()
        
        for format_url in supported_formats:
            st.code(format_url)
    
    def _render_getting_started_section(self) -> None:
        """Render getting started section when not configured"""
        log_info("Rendering getting started section")
        
        st.header("🚀 Getting Started with RapidAPI")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### ✅ Why Choose RapidAPI Mode:
            - **Professional Reliability** - Commercial-grade uptime and performance
            - **No Complex Setup** - Just need an API key, no OAuth or cookies
            - **Guaranteed Results** - Professional service with SLA
            - **Scalable** - Handle high-volume requests
            - **Support** - Commercial support available
            - **No Anti-Bot Issues** - Service handles all technical challenges
            """)
        
        with col2:
            st.markdown("""
            ### 💰 Cost Considerations:
            - **Pay-per-Use** - Only pay for what you use
            - **Subscription Plans** - Various tiers available
            - **Free Tier** - Usually includes some free requests
            - **Business Plans** - Higher limits for commercial use
            - **Transparent Pricing** - Clear pricing on RapidAPI marketplace
            - **No Hidden Costs** - What you see is what you pay
            """)
        
        # Quick comparison
        self._render_quick_comparison()
        
        # Sample API response
        self._render_sample_response()
    
    def _render_quick_comparison(self) -> None:
        """Render quick mode comparison"""
        st.subheader("📊 Quick Comparison")
        
        comparison_data = {
            "Aspect": ["Setup", "Cost", "Reliability", "Support", "Rate Limits"],
            "🎪 Unofficial": ["None", "Free", "Variable", "Community", "May hit blocks"],
            "🍪 Cookie": ["Cookie needed", "Free", "Good", "Community", "Account limits"],
            "🏢 Official API": ["Complex", "Free*", "Excellent", "Official", "API limits"],
            "💳 RapidAPI": ["API key only", "Paid", "Excellent", "Commercial", "Plan-based"]
        }
        
        import pandas as pd
        df = pd.DataFrame(comparison_data)
        st.dataframe(df, width='stretch', hide_index=True)
    
    def _render_sample_response(self) -> None:
        """Render sample API response"""
        st.subheader("📋 Sample API Response")
        
        with st.expander("📄 Example Response Format"):
            sample_response = {
                "direct_link": "https://data.1024tera.com/file/fa17446224904abdcb3c052c69d1a7e2?bkt=...",
                "file_name": "Richh(1)(1)(1)(1).mp4", 
                "link": "https://d.1024tera.com/file/fa17446224904abdcb3c052c69d1a7e2?fid=...",
                "size": "16.00 MB",
                "sizebytes": 16775878,
                "thumb": "https://data.1024tera.com/thumbnail/fa17446224904abdcb3c052c69d1a7e2?fid=..."
            }
            st.json(sample_response)
    
    def render_pricing_section(self) -> None:
        """Render pricing and plans section"""
        log_info("Rendering pricing and plans section")
        
        st.markdown("---")
        st.header("💰 RapidAPI Pricing & Plans")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **🆓 Basic Plan**
            - Limited requests/month
            - Good for testing
            - Personal projects
            - Low volume usage
            """)
        
        with col2:
            st.markdown("""
            **💼 Pro Plan**
            - Higher request limits
            - Business applications
            - Regular usage
            - Priority support
            """)
        
        with col3:
            st.markdown("""
            **🚀 Ultra Plan**
            - Unlimited requests
            - Enterprise usage
            - High-volume processing
            - Premium support
            """)
        
        st.info("💡 **Note:** Visit the RapidAPI marketplace for current pricing and plan details.")
    
    def render_footer_section(self) -> None:
        """Render footer section"""
        log_info("Rendering footer section")
        
        st.markdown("---")
        st.info("""
        💳 **RapidAPI Mode Summary:**
        - Professional commercial service for TeraBox access
        - Simple API key authentication
        - Reliable direct download links
        - Commercial support and SLA
        - Perfect for business applications and high-volume usage
        - Requires RapidAPI subscription but offers guaranteed reliability
        """)
    
    def handle_component_error(self, component_name: str, error: Exception, context: str = "") -> None:
        """
        Handle errors from components with comprehensive logging and user feedback
        
        Args:
            component_name: Name of the component that had an error
            error: Exception that occurred
            context: Additional context about the error
        """
        log_error(error, f"Component error in {component_name} - {context}")
        
        # Create user-friendly error message
        error_message = f"❌ Error in {component_name}: {str(error)}"
        
        # Show error to user
        st.error(error_message)
        
        # Provide debug information in expander
        with st.expander("🔍 Error Details", expanded=False):
            st.text(f"Component: {component_name}")
            st.text(f"Context: {context}")
            st.text(f"Error Type: {type(error).__name__}")
            st.text(f"Error Message: {str(error)}")
            st.text(f"Timestamp: {datetime.now().isoformat()}")
    
    def get_interface_status(self) -> Dict[str, Any]:
        """
        Get comprehensive interface status for monitoring
        
        Returns:
            Dict with interface status information
        """
        status = {
            'interface_initialized': True,
            'components_loaded': len(self.components),
            'api_key_configured': bool(st.session_state.get('rapidapi_client')),
            'api_key_validated': st.session_state.get('rapidapi_validated', False),
            'session_state_keys': len(st.session_state.keys()),
            'timestamp': datetime.now().isoformat()
        }
        
        log_info(f"Interface status: {status}")
        return status


def create_rapidapi_main_interface() -> RapidAPIMainInterface:
    """Factory function to create main RapidAPI interface"""
    log_info("Creating RapidAPIMainInterface instance")
    return RapidAPIMainInterface()

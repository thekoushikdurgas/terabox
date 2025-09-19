"""
RapidAPI Key Management Component

This component handles all aspects of RapidAPI key management including:
- API key input and validation
- Multiple key management
- Real-time format validation
- Live API testing
- Key rotation and status monitoring

Component Architecture:
- Modular design for reusability
- Comprehensive error handling
- Real-time validation feedback
- State management integration
- Enhanced debugging and logging
"""

import streamlit as st
import time
from typing import Dict, Any, Optional, List
from utils.terabox_rapidapi import TeraBoxRapidAPI
from utils.terabox_config import get_config_manager
from utils.state_manager import StateManager
from utils.config import log_info, log_error


class RapidAPIKeyManager:
    """
    RapidAPI Key Management Component
    
    Handles all key management operations including validation, storage,
    and multi-key rotation functionality.
    
    Features:
    - Single and multiple key management
    - Real-time format validation
    - Live API testing
    - Key status monitoring
    - Configuration persistence
    """
    
    def __init__(self):
        """Initialize the RapidAPI Key Manager component"""
        log_info("Initializing RapidAPIKeyManager component")
        
        # Load configuration manager for key operations
        self.config_mgr = get_config_manager()
        self.rapidapi_config = self.config_mgr.get_rapidapi_config()
        
        log_info("RapidAPIKeyManager component initialized successfully")
    
    def render_key_input_section(self) -> None:
        """
        Render the API key input and validation section
        
        This section provides:
        - API key input field with format validation
        - Real-time format checking
        - Validation buttons and status display
        - Help text and format requirements
        """
        log_info("Rendering RapidAPI key input section")
        
        # Check if multiple keys are configured
        configured_keys = self.config_mgr.get_rapidapi_keys()
        has_multiple_keys = len(configured_keys) > 1
        
        if has_multiple_keys:
            # Multiple keys interface
            self._render_multiple_keys_interface(configured_keys)
        else:
            # Single key interface
            self._render_single_key_interface()
    
    def _render_single_key_interface(self) -> None:
        """Render single API key input interface"""
        log_info("Rendering single API key interface")
        
        # API key input field
        api_key_input = st.text_input(
            "Enter your RapidAPI Key:",
            type="password",
            value=st.session_state.get('current_rapidapi_key', ''),
            placeholder=self.rapidapi_config.api_key or "298bbd7e09msh8c672d04ba26de4p154bc9jsn9de6459d8a13",
            help="Your X-RapidAPI-Key from the RapidAPI dashboard (Format: [alphanumeric]msh[alphanumeric]jsn[alphanumeric], 50 characters)",
            key="rapidapi_key_input"
        )
        
        # Real-time format validation
        if api_key_input.strip():
            self._show_format_validation(api_key_input.strip())
        
        # Action buttons
        self._render_validation_buttons(api_key_input)
    
    def _render_multiple_keys_interface(self, configured_keys: List[str]) -> None:
        """Render multiple API keys management interface"""
        log_info(f"Rendering multiple API keys interface with {len(configured_keys)} keys")
        
        st.info(f"✅ **Multiple API Keys Configured:** {len(configured_keys)} keys available for rotation")
        
        # Show key management interface
        with st.expander("🔑 Manage API Keys", expanded=False):
            st.markdown("**📋 Current API Keys:**")
            
            # Display existing keys with validation status
            for i, key in enumerate(configured_keys):
                col_key, col_status, col_remove = st.columns([3, 1, 1])
                
                with col_key:
                    masked_key = f"{key[:8]}...{key[-8:]}" if len(key) >= 16 else "***"
                    st.text_input(f"Key {i+1}:", value=masked_key, disabled=True, key=f"existing_key_{i}")
                
                with col_status:
                    # Show validation status for each key
                    self._show_key_validation_status(key, i)
                
                with col_remove:
                    if len(configured_keys) > 1:  # Don't allow removing the last key
                        if st.button(f"🗑️", key=f"remove_key_{i}", help=f"Remove key {i+1}"):
                            if self.config_mgr.remove_rapidapi_key(key):
                                st.success(f"Key {i+1} removed!")
                                st.rerun()
                            else:
                                st.error("Failed to remove key")
                    else:
                        st.caption("Last key")
            
            # Management actions
            st.markdown("**🔧 Management Actions:**")
            col_test_all, col_clear_cache = st.columns(2)
            
            with col_test_all:
                if st.button("🧪 Test All Keys", key="test_all_keys"):
                    self._test_all_keys(configured_keys)
            
            with col_clear_cache:
                if st.button("🗑️ Clear Test Cache", key="clear_validation_cache"):
                    self._clear_validation_cache()
                    st.success("Validation cache cleared!")
                    st.rerun()
            
            # Add new key section
            st.markdown("**➕ Add New API Key:**")
            new_api_key = st.text_input(
                "Additional RapidAPI Key:",
                type="password",
                placeholder="298bbd7e09msh8c672d04ba26de4p154bc9jsn9de6459d8a13",
                help="Add another RapidAPI key for rotation",
                key="new_api_key_input"
            )
            
            col_add, col_validate = st.columns(2)
            with col_add:
                if st.button("➕ Add Key", key="add_new_key"):
                    if new_api_key.strip():
                        if self.config_mgr.add_rapidapi_key(new_api_key.strip()):
                            st.success("New API key added successfully!")
                            st.rerun()
                        else:
                            st.warning("Key already exists or failed to add")
                    else:
                        st.error("Please enter a valid API key")
            
            with col_validate:
                if st.button("🔍 Add & Test", key="add_and_test_key"):
                    if new_api_key.strip():
                        # First add the key
                        if self.config_mgr.add_rapidapi_key(new_api_key.strip()):
                            st.success("New API key added!")
                            # Then test it
                            with st.spinner("Testing new key..."):
                                try:
                                    temp_client = TeraBoxRapidAPI(new_api_key.strip())
                                    validation_result = temp_client.validate_api_key()
                                    
                                    if validation_result['status'] == 'success':
                                        st.success("✅ New key is valid and working!")
                                    else:
                                        st.warning(f"⚠️ New key added but validation failed: {validation_result.get('message', '')}")
                                except Exception as e:
                                    st.error(f"❌ New key added but testing failed: {str(e)}")
                            st.rerun()
                        else:
                            st.warning("Key already exists or failed to add")
                    else:
                        st.error("Please enter a valid API key")
    
    def _show_format_validation(self, api_key: str) -> None:
        """Show real-time format validation for API key"""
        log_info(f"Performing real-time format validation for API key (length: {len(api_key)})")
        
        temp_client = TeraBoxRapidAPI()
        format_check = temp_client.quick_validate_api_key_format(api_key)
        
        if format_check['status'] == 'success':
            st.success("✅ API key format is valid")
            with st.expander("📋 Format Details", expanded=False):
                st.json(format_check['details'])
        else:
            st.warning(f"⚠️ Format Issue: {format_check['message']}")
            if 'details' in format_check:
                st.info(f"💡 {format_check['details']}")
                
            # Show format requirements
            self._show_format_requirements()
    
    def _show_format_requirements(self) -> None:
        """Show RapidAPI key format requirements"""
        with st.expander("📋 RapidAPI Key Format Requirements", expanded=True):
            st.markdown("""
            **Valid RapidAPI Key Format:**
            - **Length**: Exactly 50 characters
            - **Pattern**: Contains 'msh' and 'jsn' markers
            - **Characters**: Only letters (a-z, A-Z) and numbers (0-9)
            - **Example**: `298bbd7e09msh8c672d04ba26de4p154bc9jsn9de6459d8a13`
            
            **Common Issues:**
            - ❌ Wrong length (not 50 characters)
            - ❌ Missing 'msh' or 'jsn' markers
            - ❌ Contains special characters or spaces
            - ❌ Copy-paste errors or truncated key
            """)
    
    def _show_key_validation_status(self, api_key: str, key_index: int) -> None:
        """
        Show validation status for a specific API key
        
        Args:
            api_key: The API key to validate
            key_index: Index of the key for unique button keys
        """
        log_info(f"Displaying validation status for key {key_index + 1}")
        
        # Check if this key is currently active
        current_key = st.session_state.get('current_rapidapi_key', '')
        is_active_key = (api_key == current_key)
        
        # Get cached validation status if available
        validation_cache_key = f"key_validation_{key_index}"
        cached_status = st.session_state.get(validation_cache_key, None)
        
        if is_active_key and st.session_state.get('rapidapi_validated', False):
            # Currently active and validated key
            st.success("✅ Active")
            st.caption("Currently in use")
        elif cached_status:
            # Show cached validation status
            if cached_status['status'] == 'valid':
                st.success("✅ Valid")
            elif cached_status['status'] == 'invalid':
                st.error("❌ Invalid")
            elif cached_status['status'] == 'warning':
                st.warning("⚠️ Warning")
            else:
                st.info("❓ Unknown")
        else:
            # No cached status - show validation button
            if st.button("🔍 Test", key=f"test_key_{key_index}", help=f"Test API key {key_index + 1}"):
                self._test_individual_key(api_key, key_index)
    
    def _test_individual_key(self, api_key: str, key_index: int) -> None:
        """
        Test an individual API key and cache the result
        
        Args:
            api_key: The API key to test
            key_index: Index of the key for caching
        """
        log_info(f"Testing individual API key {key_index + 1}")
        
        validation_cache_key = f"key_validation_{key_index}"
        
        with st.spinner(f"Testing key {key_index + 1}..."):
            try:
                # Create temporary client for testing
                temp_client = TeraBoxRapidAPI(api_key)
                validation_result = temp_client.validate_api_key()
                
                # Cache the validation result
                cache_data = {
                    'status': validation_result['status'],
                    'message': validation_result.get('message', ''),
                    'timestamp': time.time()
                }
                st.session_state[validation_cache_key] = cache_data
                
                # Show immediate feedback
                if validation_result['status'] == 'success':
                    st.success(f"✅ Key {key_index + 1} is valid!")
                elif validation_result['status'] == 'warning':
                    st.warning(f"⚠️ Key {key_index + 1} has warnings: {validation_result.get('message', '')}")
                else:
                    st.error(f"❌ Key {key_index + 1} is invalid: {validation_result.get('message', '')}")
                
                log_info(f"Key {key_index + 1} validation completed - Status: {validation_result['status']}")
                
                # Trigger rerun to show updated status
                time.sleep(1)  # Brief pause to show the message
                st.rerun()
                
            except Exception as e:
                log_error(e, f"individual_key_validation_{key_index}")
                
                # Cache error status
                cache_data = {
                    'status': 'error',
                    'message': str(e),
                    'timestamp': time.time()
                }
                st.session_state[validation_cache_key] = cache_data
                
                st.error(f"❌ Error testing key {key_index + 1}: {str(e)}")
                st.rerun()
    
    def _test_all_keys(self, configured_keys: List[str]) -> None:
        """
        Test all configured API keys
        
        Args:
            configured_keys: List of API keys to test
        """
        log_info(f"Testing all {len(configured_keys)} API keys")
        
        with st.spinner(f"Testing all {len(configured_keys)} API keys..."):
            for i, key in enumerate(configured_keys):
                try:
                    # Create temporary client for testing
                    temp_client = TeraBoxRapidAPI(key)
                    validation_result = temp_client.validate_api_key()
                    
                    # Cache the validation result
                    validation_cache_key = f"key_validation_{i}"
                    cache_data = {
                        'status': validation_result['status'],
                        'message': validation_result.get('message', ''),
                        'timestamp': time.time()
                    }
                    st.session_state[validation_cache_key] = cache_data
                    
                    log_info(f"Key {i + 1} test completed - Status: {validation_result['status']}")
                    
                except Exception as e:
                    log_error(e, f"bulk_key_validation_{i}")
                    
                    # Cache error status
                    validation_cache_key = f"key_validation_{i}"
                    cache_data = {
                        'status': 'error',
                        'message': str(e),
                        'timestamp': time.time()
                    }
                    st.session_state[validation_cache_key] = cache_data
        
        st.success(f"✅ Completed testing all {len(configured_keys)} API keys!")
        log_info("Bulk API key testing completed")
        st.rerun()
    
    def _clear_validation_cache(self) -> None:
        """Clear all cached validation results"""
        log_info("Clearing validation cache")
        
        # Find and remove all validation cache keys
        keys_to_remove = [key for key in st.session_state.keys() if key.startswith('key_validation_')]
        
        for key in keys_to_remove:
            del st.session_state[key]
        
        log_info(f"Cleared {len(keys_to_remove)} validation cache entries")
    
    def _render_validation_buttons(self, api_key_input: str) -> None:
        """Render validation action buttons"""
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            if st.button("🔍 Validate API Key", type="primary", key="validate_api_key_btn"):
                self._handle_api_key_validation(api_key_input)
        
        with col_b:
            if st.button("⚡ Quick Format Check", key="quick_format_check_btn"):
                self._handle_quick_format_check(api_key_input)
        
        with col_c:
            if st.button("🗑️ Clear API Key", key="clear_api_key_btn"):
                self._handle_clear_api_key()
    
    def _handle_api_key_validation(self, api_key_input: str) -> None:
        """Handle full API key validation process with caching optimization"""
        log_info("User initiated comprehensive API key validation")
        
        if not api_key_input.strip():
            st.error("Please enter an API key")
            return
        
        user_key = api_key_input.strip()
        log_info(f"Validating API key - Length: {len(user_key)} characters")
        
        # Check if this key was recently validated (cache for 5 minutes)
        cache_key = f"validation_cache_{hash(user_key)}"
        current_time = time.time()
        
        if cache_key in st.session_state:
            cached_validation = st.session_state[cache_key]
            cache_age = current_time - cached_validation['timestamp']
            
            # Use cached result if less than 5 minutes old
            if cache_age < 300:  # 5 minutes
                log_info(f"Using cached validation result (age: {cache_age:.1f}s)")
                self._apply_cached_validation_result(cached_validation, user_key)
                return
            else:
                log_info(f"Cached validation expired (age: {cache_age:.1f}s), performing fresh validation")
        
        with st.spinner("Validating RapidAPI key..."):
            # Create RapidAPI client for validation
            validation_start = time.time()
            client = TeraBoxRapidAPI(user_key)
            validation_result = client.validate_api_key()
            validation_duration = time.time() - validation_start
            
            # Cache the validation result
            validation_cache = {
                'result': validation_result,
                'timestamp': current_time,
                'client': client if validation_result['status'] == 'success' else None,
                'duration': validation_duration
            }
            st.session_state[cache_key] = validation_cache
        
        log_info(f"API key validation completed in {validation_duration:.2f}s - Status: {validation_result['status']}")
        
        if validation_result['status'] == 'success':
            # Successful validation
            log_info("API key validation successful - updating session state")
            
            st.session_state.rapidapi_client = client
            st.session_state.rapidapi_validated = True
            st.session_state.current_rapidapi_key = user_key
            st.session_state.rapidapi_last_validation = current_time
            
            st.success("✅ API key is valid and working!")
            
            # Show validation details
            with st.expander("🔍 Validation Details", expanded=False):
                st.write("**Format Validation:**")
                st.json(validation_result.get('format_check', {}))
                st.write("**Live API Test:**")
                st.json(validation_result.get('live_test', {}))
                st.write(f"**Validation Duration:** {validation_duration:.2f}s")
            
            # Update state manager
            StateManager.update_state('api_validation_completed', True)
            log_info("API validation completion state updated")
            
        elif validation_result['status'] == 'warning':
            # Handle warnings
            st.warning(f"⚠️ {validation_result['message']}")
            if 'details' in validation_result:
                st.info(f"Details: {validation_result['details']}")
            
            # Ask user if they want to proceed anyway
            if st.button("✅ Use API Key Anyway", key="use_key_anyway"):
                client = TeraBoxRapidAPI(api_key_input.strip())
                st.session_state.rapidapi_client = client
                st.session_state.rapidapi_validated = True
                st.session_state.current_rapidapi_key = api_key_input.strip()
                st.success("✅ API key configured (with warnings)")
                StateManager.update_state('api_key_configured_with_warnings', True)
        else:
            # Validation failed
            st.error(f"❌ {validation_result['message']}")
            if 'details' in validation_result:
                st.info(f"Details: {validation_result['details']}")
    
    def _apply_cached_validation_result(self, cached_validation: Dict[str, Any], user_key: str) -> None:
        """Apply cached validation result to avoid redundant API calls"""
        validation_result = cached_validation['result']
        client = cached_validation.get('client')
        cache_age = time.time() - cached_validation['timestamp']
        
        if validation_result['status'] == 'success' and client:
            st.session_state.rapidapi_client = client
            st.session_state.rapidapi_validated = True
            st.session_state.current_rapidapi_key = user_key
            st.session_state.rapidapi_last_validation = cached_validation['timestamp']
            
            st.success(f"✅ API key is valid! (cached result, {cache_age:.0f}s old)")
            
            # Show cached validation details
            with st.expander("🔍 Cached Validation Details", expanded=False):
                st.write("**Format Validation:**")
                st.json(validation_result.get('format_check', {}))
                st.write("**Live API Test:**")
                st.json(validation_result.get('live_test', {}))
                st.write(f"**Original Duration:** {cached_validation['duration']:.2f}s")
                st.write(f"**Cache Age:** {cache_age:.0f}s")
            
            StateManager.update_state('api_validation_completed', True)
            log_info("Cached API validation applied successfully")
        else:
            log_info("Cached validation result not applicable, performing fresh validation")
            # Remove invalid cache entry
            cache_key = f"validation_cache_{hash(user_key)}"
            if cache_key in st.session_state:
                del st.session_state[cache_key]
    
    def _handle_quick_format_check(self, api_key_input: str) -> None:
        """Handle quick format check"""
        log_info("User initiated quick format check")
        
        if not api_key_input.strip():
            st.error("Please enter an API key")
            return
        
        temp_client = TeraBoxRapidAPI()
        format_result = temp_client.quick_validate_api_key_format(api_key_input.strip())
        
        if format_result['status'] == 'success':
            st.success("✅ Format is valid!")
        else:
            st.error(f"❌ {format_result['message']}")
    
    def _handle_clear_api_key(self) -> None:
        """Handle clearing API key"""
        log_info("User initiated API key clearing")
        
        st.session_state.rapidapi_client = None
        st.session_state.rapidapi_validated = False
        st.session_state.current_rapidapi_key = ""
        st.success("API key cleared!")
        
        # Update state manager
        StateManager.update_multiple_states({
            'rapidapi_client': None,
            'rapidapi_validated': False,
            'current_rapidapi_key': ''
        })
        log_info("API key cleared and session state updated")
    
    def render_api_status_section(self) -> None:
        """Render API status and information section"""
        if st.session_state.get('rapidapi_client'):
            st.success("💳 **API Status: Active**")
            
            # Show API status
            api_status = st.session_state.rapidapi_client.get_api_status()
            
            if api_status['api_key_status'] == 'success':
                st.success("✅ Valid API Key")
            else:
                st.error("❌ Invalid API Key")
        else:
            st.info("💳 **API Status: Not Configured**")
            st.caption("Please configure and validate your RapidAPI key above.")


def create_rapidapi_key_manager() -> RapidAPIKeyManager:
    """Factory function to create RapidAPI Key Manager component"""
    log_info("Creating RapidAPIKeyManager component instance")
    return RapidAPIKeyManager()

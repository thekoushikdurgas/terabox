import streamlit as st
import qrcode
from io import BytesIO
import base64
import time
from terabox_official_api import TeraBoxOfficialAPI
from terabox_core import TeraboxCore
import json

st.set_page_config(
    page_title="API Mode Selection",
    page_icon="🔑",
    layout="wide"
)

st.title("🔑 API Mode Selection")
st.markdown("Choose between unofficial scraping methods and official TeraBox API integration.")

# Initialize session state
if 'api_mode' not in st.session_state:
    st.session_state.api_mode = 'unofficial'
if 'official_api' not in st.session_state:
    st.session_state.official_api = None
if 'credentials_configured' not in st.session_state:
    st.session_state.credentials_configured = False

# Mode selection
col1, col2 = st.columns(2)

with col1:
    st.header("🎯 Unofficial Mode (Current)")
    st.info("""
    **What it does:**
    - Scrapes TeraBox share links directly
    - No API keys required
    - Works with public share links
    - 3 different extraction modes
    
    **Pros:**
    - ✅ No registration required
    - ✅ Works immediately
    - ✅ Free to use
    - ✅ Handles most share links
    
    **Cons:**
    - ❌ May be blocked by anti-bot measures
    - ❌ Limited to share link extraction
    - ❌ No file management features
    - ❌ Connection issues possible
    """)
    
    if st.button("🎯 Use Unofficial Mode", type="secondary"):
        st.session_state.api_mode = 'unofficial'
        st.success("✅ Switched to Unofficial Mode")
        st.rerun()

with col2:
    st.header("🏢 Official API Mode")
    st.info("""
    **What it does:**
    - Uses official TeraBox Open Platform APIs
    - Requires API credentials from TeraBox
    - Full file management capabilities
    - OAuth 2.0 authentication
    
    **Pros:**
    - ✅ Official support and stability
    - ✅ Full file management (upload, download, search)
    - ✅ User account integration
    - ✅ Streaming APIs
    - ✅ Share management
    
    **Cons:**
    - ❌ Requires API registration
    - ❌ Need client credentials
    - ❌ May have usage limits
    """)
    
    if st.button("🏢 Use Official API Mode", type="primary"):
        st.session_state.api_mode = 'official'
        st.success("✅ Switched to Official API Mode")
        st.rerun()

# Display current mode
st.markdown("---")
current_mode = st.session_state.api_mode
if current_mode == 'unofficial':
    st.success("🎯 **Current Mode: Unofficial Scraping**")
    st.markdown("You're using the unofficial scraping methods. This works with TeraBox share links without requiring API credentials.")
else:
    st.success("🏢 **Current Mode: Official API**")
    st.markdown("You're using the official TeraBox API. This provides full functionality but requires API credentials.")

# Official API Configuration
if st.session_state.api_mode == 'official':
    st.header("🔧 Official API Configuration")
    
    with st.expander("📋 How to Get API Credentials", expanded=not st.session_state.credentials_configured):
        st.markdown("""
        To use the official TeraBox API, you need to apply for API credentials:
        
        ### Step 1: Apply for API Access
        1. Contact TeraBox support or business team
        2. Provide your application details:
           - Application name
           - Product logo
           - URL schemes (if mobile)
           - Use case description
        
        ### Step 2: Get Credentials
        You'll receive:
        - **Client ID** (AppKey)
        - **Client Secret** (SecretKey) 
        - **Private Secret** (for signatures)
        
        ### Step 3: Configure Below
        Enter your credentials in the form below to start using the official API.
        
        **Note:** This is for legitimate business use cases. Individual users should use the unofficial mode.
        """)
    
    # Credentials input
    st.subheader("🔐 Enter API Credentials")
    
    col1, col2 = st.columns(2)
    
    with col1:
        client_id = st.text_input(
            "Client ID (AppKey)",
            type="password",
            help="The AppKey provided by TeraBox"
        )
        
        client_secret = st.text_input(
            "Client Secret (SecretKey)",
            type="password", 
            help="The SecretKey provided by TeraBox"
        )
    
    with col2:
        private_secret = st.text_input(
            "Private Secret",
            type="password",
            help="The private secret used for signature generation"
        )
        
        if st.button("💾 Save Credentials"):
            if client_id and client_secret and private_secret:
                st.session_state.official_api = TeraBoxOfficialAPI(
                    client_id=client_id,
                    client_secret=client_secret,
                    private_secret=private_secret
                )
                st.session_state.credentials_configured = True
                st.success("✅ Credentials saved successfully!")
                st.rerun()
            else:
                st.error("❌ Please fill in all credential fields")
    
    # Authentication status
    if st.session_state.credentials_configured and st.session_state.official_api:
        st.subheader("🔐 Authentication Status")
        
        api = st.session_state.official_api
        cred_status = api.get_credentials_status()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Credentials Status:**")
            for key, status in cred_status.items():
                if key in ['client_id', 'client_secret', 'private_secret']:
                    icon = "✅" if status else "❌"
                    st.text(f"{icon} {key.replace('_', ' ').title()}: {'Set' if status else 'Missing'}")
        
        with col2:
            st.markdown("**Authentication Status:**")
            auth_status = api.is_authenticated()
            st.text(f"{'✅' if auth_status else '❌'} Access Token: {'Active' if auth_status else 'Not Set'}")
            
            if auth_status:
                # Get token info
                token_info = api.get_token_info()
                if token_info.get('status') == 'success':
                    st.text(f"🌐 API Domain: {token_info['api_domain']}")
                    st.text(f"👤 User ID: {token_info['user_id']}")
        
        # Authentication methods
        if not api.is_authenticated():
            st.subheader("🔓 Authentication Methods")
            
            auth_method = st.radio(
                "Choose authentication method:",
                ["Authorization Code Flow", "Device Code Flow (QR Code)"],
                help="Authorization Code Flow requires a web browser, Device Code Flow uses QR codes"
            )
            
            if auth_method == "Authorization Code Flow":
                st.markdown("**Authorization Code Flow:**")
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    auth_url = api.get_authorization_url()
                    st.markdown(f"1. Click the link below to authorize your application:")
                    st.markdown(f"[🔗 Authorize Application]({auth_url})")
                    
                    st.markdown("2. After authorization, you'll receive an authorization code.")
                    auth_code = st.text_input("Enter Authorization Code:")
                
                with col2:
                    if st.button("🔐 Exchange for Token"):
                        if auth_code:
                            with st.spinner("Exchanging code for access token..."):
                                result = api.exchange_code_for_token(auth_code)
                            
                            if result.get('status') == 'success':
                                st.success("✅ Authentication successful!")
                                st.balloons()
                                st.rerun()
                            else:
                                st.error(f"❌ Authentication failed: {result.get('message')}")
                        else:
                            st.error("Please enter the authorization code")
            
            else:  # Device Code Flow
                st.markdown("**Device Code Flow (QR Code):**")
                
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    if st.button("📱 Generate QR Code"):
                        with st.spinner("Generating QR code..."):
                            device_result = api.get_device_code()
                        
                        if device_result.get('status') == 'success':
                            st.session_state.device_code = device_result['device_code']
                            st.session_state.qr_expires = time.time() + device_result['expires_in']
                            
                            # Display QR code
                            qr_data = device_result['qrcode_url']
                            if qr_data.startswith('data:image/png;base64,'):
                                qr_image_data = qr_data.split(',')[1]
                                qr_image = base64.b64decode(qr_image_data)
                                st.image(qr_image, caption="Scan with TeraBox app", width=200)
                            
                            st.success("✅ QR code generated! Scan with TeraBox app to authorize.")
                        else:
                            st.error(f"❌ Failed to generate QR code: {device_result.get('message')}")
                
                with col2:
                    if 'device_code' in st.session_state:
                        if st.button("🔄 Check Authorization Status"):
                            with st.spinner("Checking authorization..."):
                                poll_result = api.poll_device_token(st.session_state.device_code)
                            
                            if poll_result.get('status') == 'success':
                                st.success("✅ Authorization successful!")
                                st.balloons()
                                st.rerun()
                            elif poll_result.get('status') == 'pending':
                                st.info("⏳ Waiting for user authorization...")
                            else:
                                st.error(f"❌ Authorization failed: {poll_result.get('message')}")
        
        else:
            # User is authenticated - show user info
            st.subheader("👤 User Information")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📊 Get User Info"):
                    with st.spinner("Loading user information..."):
                        user_info = api.get_user_info()
                    
                    if user_info.get('status') == 'success':
                        st.json(user_info)
                    else:
                        st.error(f"Failed to get user info: {user_info.get('message')}")
            
            with col2:
                if st.button("💾 Get Storage Quota"):
                    with st.spinner("Loading storage quota..."):
                        quota_info = api.get_quota_info()
                    
                    if quota_info.get('status') == 'success':
                        st.metric("Total Storage", f"{quota_info['total_gb']} GB")
                        st.metric("Used Storage", f"{quota_info['used_gb']} GB")
                        st.metric("Free Storage", f"{quota_info['free_gb']} GB")
                        st.progress(quota_info['usage_percent'] / 100)
                    else:
                        st.error(f"Failed to get quota: {quota_info.get('message')}")

# Mode comparison
st.markdown("---")
st.header("📊 Mode Comparison")

comparison_data = {
    "Feature": [
        "Setup Difficulty",
        "API Keys Required",
        "File Extraction",
        "File Management", 
        "User Authentication",
        "Upload Files",
        "Search Files",
        "Streaming Support",
        "Rate Limits",
        "Reliability",
        "Cost"
    ],
    "Unofficial Mode": [
        "🟢 Easy",
        "🟢 None",
        "🟢 Share links only",
        "🔴 None",
        "🔴 None", 
        "🔴 No",
        "🔴 No",
        "🟡 Limited",
        "🟡 May hit limits",
        "🟡 Depends on anti-bot",
        "🟢 Free"
    ],
    "Official API Mode": [
        "🔴 Complex",
        "🔴 Required",
        "🟢 Full access",
        "🟢 Complete",
        "🟢 OAuth 2.0",
        "🟢 Yes",
        "🟢 Yes", 
        "🟢 Full support",
        "🟡 API limits",
        "🟢 High",
        "🟡 May have costs"
    ]
}

st.table(comparison_data)

# Usage recommendations
st.header("💡 Usage Recommendations")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 🎯 Use Unofficial Mode If:
    - You just want to download from share links
    - You don't want to register for API access
    - You're using this for personal use
    - You need a quick solution
    - You don't need file management features
    """)

with col2:
    st.markdown("""
    ### 🏢 Use Official API Mode If:
    - You're building a business application
    - You need full file management capabilities
    - You want reliable, supported access
    - You need user authentication
    - You're willing to go through API approval process
    """)

st.markdown("---")
st.info("💡 **Tip:** You can switch between modes anytime using this page. Your settings will be remembered during your session.")

# Debug information
with st.expander("🔍 Debug Information"):
    st.json({
        "current_mode": st.session_state.api_mode,
        "credentials_configured": st.session_state.credentials_configured,
        "official_api_initialized": st.session_state.official_api is not None,
        "session_keys": list(st.session_state.keys())
    })

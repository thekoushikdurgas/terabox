import streamlit as st
import pandas as pd
from typing import Dict, Any

st.set_page_config(
    page_title="Mode Comparison",
    page_icon="📊",
    layout="wide"
)

st.title("📊 TeraDL Mode Comparison")
st.markdown("Comprehensive comparison of all three TeraBox access methods")

# Mode overview cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div style="border: 2px solid #ff6b6b; border-radius: 10px; padding: 15px; text-align: center; background: #fff5f5;">
        <h4 style="color: #ff6b6b; margin: 0;">🎯 Unofficial</h4>
        <p style="margin: 8px 0; font-size: 0.9em;"><strong>Scraping</strong></p>
        <p style="font-size: 0.8em; color: #666;">Direct scraping methods</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="border: 2px solid #4ecdc4; border-radius: 10px; padding: 15px; text-align: center; background: #f0fdfc;">
        <h4 style="color: #4ecdc4; margin: 0;">🍪 Cookie</h4>
        <p style="margin: 8px 0; font-size: 0.9em;"><strong>Session</strong></p>
        <p style="font-size: 0.8em; color: #666;">Browser cookie auth</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style="border: 2px solid #45b7d1; border-radius: 10px; padding: 15px; text-align: center; background: #f0f9ff;">
        <h4 style="color: #45b7d1; margin: 0;">🏢 Official</h4>
        <p style="margin: 8px 0; font-size: 0.9em;"><strong>OAuth 2.0</strong></p>
        <p style="font-size: 0.8em; color: #666;">Platform API</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div style="border: 2px solid #9b59b6; border-radius: 10px; padding: 15px; text-align: center; background: #f8f5ff;">
        <h4 style="color: #9b59b6; margin: 0;">💳 RapidAPI</h4>
        <p style="margin: 8px 0; font-size: 0.9em;"><strong>Commercial</strong></p>
        <p style="font-size: 0.8em; color: #666;">Paid service</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Detailed comparison table
st.header("🔍 Detailed Feature Comparison")

comparison_data = {
    "Feature": [
        "Setup Complexity",
        "Authentication Required", 
        "API Keys/Credentials",
        "Account Access",
        "File Extraction",
        "Download Links",
        "File Management",
        "Upload Files",
        "Search Files",
        "User Information",
        "Storage Quota",
        "Video Streaming",
        "Progress Tracking",
        "Bulk Operations",
        "Rate Limiting",
        "Reliability",
        "Error Handling",
        "Session Management",
        "Cross-Platform",
        "Privacy Level",
        "Business Use",
        "Support Level",
        "Cost",
        "Development Effort"
    ],
    "🎯 Unofficial": [
        "🟢 Easy - No setup",
        "🟢 None required",
        "🟢 Not needed",
        "🔴 No account access",
        "🟡 Share links only",
        "🟡 Generated links",
        "🔴 None",
        "🔴 No",
        "🔴 No",
        "🔴 No",
        "🔴 No",
        "🟡 Basic support",
        "🟢 Built-in",
        "🟡 Limited",
        "🟡 May hit limits",
        "🟡 Variable",
        "🟢 Good",
        "🔴 None",
        "🟢 Yes",
        "🟢 High (no account)",
        "🟡 Limited",
        "🟡 Community only",
        "🟢 Free",
        "🟢 Minimal"
    ],
    "🍪 Cookie": [
        "🟡 Medium - Cookie needed",
        "🟡 Session cookie",
        "🟢 Not needed",
        "🟢 Full access",
        "🟢 Any accessible file",
        "🟢 Direct links",
        "🟡 Basic operations",
        "🔴 No",
        "🔴 No",
        "🟡 Limited",
        "🔴 No",
        "🟢 Good support",
        "🟢 Advanced",
        "🟢 Supported",
        "🟡 Account limits",
        "🟢 Good",
        "🟢 Excellent",
        "🟡 Cookie-based",
        "🟢 Yes",
        "🟡 Medium (uses account)",
        "🟢 Good",
        "🟡 Community + docs",
        "🟢 Free",
        "🟡 Moderate"
    ],
    "🏢 Official": [
        "🔴 Complex - API setup",
        "🔴 OAuth 2.0 required",
        "🔴 Required",
        "🟢 Full integration",
        "🟢 Complete access",
        "🟢 Official links",
        "🟢 Complete",
        "🟢 Yes",
        "🟢 Yes",
        "🟢 Complete",
        "🟢 Yes",
        "🟢 Full support",
        "🟢 Advanced",
        "🟢 Full support",
        "🟢 Official limits",
        "🟢 Excellent",
        "🟢 Comprehensive",
        "🟢 Token-based",
        "🟢 Yes",
        "🟢 High (OAuth)",
        "🟢 Excellent",
        "🟢 Official support",
        "🟡 May have costs",
        "🔴 High"
    ],
    "💳 RapidAPI": [
        "🟢 Easy - API key only",
        "🟢 API key only",
        "🟡 RapidAPI key needed",
        "🔴 No account access",
        "🟢 Share links",
        "🟢 Guaranteed direct links",
        "🔴 None",
        "🔴 No",
        "🔴 No",
        "🔴 No",
        "🔴 No",
        "🟡 Link-based only",
        "🟢 Advanced",
        "🟢 Supported",
        "🟢 Commercial limits",
        "🟢 Excellent",
        "🟢 Professional",
        "🔴 None",
        "🟢 Yes",
        "🟢 High (commercial)",
        "🟢 Excellent",
        "🟢 Commercial support",
        "🔴 Paid service",
        "🟢 Minimal"
    ]
}

# Create and display the comparison table
df = pd.DataFrame(comparison_data)
st.dataframe(df, width='stretch', hide_index=True)

st.markdown("---")

# Use case recommendations
st.header("🎯 Use Case Recommendations")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.subheader("🎯 Choose Unofficial Mode If:")
    st.markdown("""
    - ✅ You just want to download from share links
    - ✅ You don't want any setup or registration
    - ✅ You're using this occasionally/personally
    - ✅ You don't need file management features
    - ✅ You want maximum privacy (no account needed)
    - ✅ You're okay with potential reliability issues
    - ✅ You want the simplest possible solution
    
    **Best For:** Quick downloads, personal use, testing
    """)

with col2:
    st.subheader("🍪 Choose Cookie Mode If:")
    st.markdown("""
    - ✅ You have a TeraBox account
    - ✅ You want reliable downloads
    - ✅ You need direct download links
    - ✅ You can extract browser cookies
    - ✅ You want better success rates than scraping
    - ✅ You need progress tracking
    - ✅ You don't want to register for API access
    
    **Best For:** Regular users, reliable downloads, personal projects
    """)

with col3:
    st.subheader("🏢 Choose Official API If:")
    st.markdown("""
    - ✅ Building business application
    - ✅ Need full file management
    - ✅ Want official support
    - ✅ Need user authentication
    - ✅ Can get API approval
    - ✅ Need enterprise features
    
    **Best For:** Enterprise apps
    """)

with col4:
    st.subheader("💳 Choose RapidAPI If:")
    st.markdown("""
    - ✅ Need commercial reliability
    - ✅ Want guaranteed uptime
    - ✅ Building paid applications
    - ✅ Need professional support
    - ✅ Want simple integration
    - ✅ Can afford subscription costs
    
    **Best For:** Commercial apps, SaaS
    """)

st.markdown("---")

# Performance comparison
st.header("⚡ Performance Comparison")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Speed & Reliability")
    
    speed_data = {
        "Metric": ["Setup Time", "First Download", "Subsequent Downloads", "Error Recovery", "Large Files"],
        "🎯 Unofficial": ["Instant", "Slow", "Medium", "Poor", "Variable"],
        "🍪 Cookie": ["5 minutes", "Fast", "Fast", "Good", "Excellent"],
        "🏢 Official": ["1+ hours", "Medium", "Fast", "Excellent", "Excellent"]
    }
    
    speed_df = pd.DataFrame(speed_data)
    st.dataframe(speed_df, width='stretch', hide_index=True)

with col2:
    st.subheader("🛡️ Security & Privacy")
    
    security_data = {
        "Aspect": ["Data Privacy", "Account Security", "API Security", "Session Management", "Credential Storage"],
        "🎯 Unofficial": ["Excellent", "N/A", "N/A", "None", "None"],
        "🍪 Cookie": ["Good", "Uses Account", "N/A", "Cookie-based", "Browser"],
        "🏢 Official": ["Good", "OAuth Protected", "Excellent", "Token-based", "Encrypted"]
    }
    
    security_df = pd.DataFrame(security_data)
    st.dataframe(security_df, width='stretch', hide_index=True)

st.markdown("---")

# Technical implementation details
st.header("🔧 Technical Implementation")

tab1, tab2, tab3 = st.tabs(["🎯 Unofficial Mode", "🍪 Cookie Mode", "🏢 Official API"])

with tab1:
    st.subheader("Unofficial Mode Technical Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **How it Works:**
        - Direct HTTP requests to TeraBox URLs
        - HTML parsing and data extraction
        - Multiple extraction strategies (3 modes)
        - User agent rotation and retry logic
        - No authentication required
        
        **Technologies Used:**
        - `requests` library for HTTP
        - `BeautifulSoup` for HTML parsing
        - `cloudscraper` for anti-bot bypass
        - Regular expressions for data extraction
        - Custom retry mechanisms
        """)
    
    with col2:
        st.markdown("""
        **Advantages:**
        - No setup required
        - Works immediately
        - No account needed
        - Maximum privacy
        - Free to use
        
        **Disadvantages:**
        - May be blocked by anti-bot measures
        - Limited to share links only
        - No file management
        - Variable reliability
        - Connection issues possible
        """)

with tab2:
    st.subheader("Cookie Mode Technical Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **How it Works:**
        - Uses your browser's TeraBox session cookie
        - Authenticated requests to TeraBox APIs
        - Direct access to file information
        - Progress tracking with callbacks
        - Automatic error handling and retries
        
        **Technologies Used:**
        - `requests` with session cookies
        - JSON API parsing
        - Progress callback system
        - File type detection
        - Download progress tracking
        """)
    
    with col2:
        st.markdown("""
        **Advantages:**
        - More reliable than scraping
        - Direct download links
        - Progress tracking
        - File metadata access
        - Good error handling
        
        **Disadvantages:**
        - Requires cookie extraction
        - Session-dependent
        - Uses personal account
        - Cookie expires
        - Browser-specific setup
        """)

with tab3:
    st.subheader("Official API Technical Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **How it Works:**
        - OAuth 2.0 authentication flow
        - Official TeraBox Open Platform APIs
        - Token-based authentication
        - Complete REST API implementation
        - Enterprise-grade security
        
        **Technologies Used:**
        - OAuth 2.0 standard
        - JWT tokens
        - REST API calls
        - Signature-based authentication
        - Official SDK patterns
        """)
    
    with col2:
        st.markdown("""
        **Advantages:**
        - Official support
        - Complete functionality
        - Enterprise security
        - Long-term stability
        - Full feature access
        
        **Disadvantages:**
        - Complex setup
        - API registration required
        - May have usage costs
        - High development effort
        - Business approval needed
        """)

st.markdown("---")

# Migration guide
st.header("🔄 Migration Between Modes")

st.markdown("""
### 📈 Recommended Migration Path:

1. **Start with Unofficial Mode** 
   - Test basic functionality
   - Understand your requirements
   - Evaluate download needs

2. **Move to Cookie Mode**
   - If you need more reliability
   - When scraping becomes unreliable
   - For regular usage patterns

3. **Upgrade to Official API**
   - For business applications
   - When building for others
   - For enterprise requirements

### 🔄 Easy Switching:
TeraDL allows you to switch between modes anytime:
- All modes work with the same interface
- No data loss when switching
- Settings are preserved per mode
- Can test multiple modes with same URLs
""")

# Current mode status
st.markdown("---")
st.header("📍 Current Mode Status")

current_mode = st.session_state.get('api_mode', 'unofficial')
col1, col2, col3, col4 = st.columns(4)

with col1:
    if current_mode == 'unofficial':
        st.success("🎯 **Currently Active**")
    else:
        st.info("🎯 Available")
    st.caption("Unofficial Scraping")

with col2:
    if current_mode == 'cookie':
        st.success("🍪 **Currently Active**")
    else:
        st.info("🍪 Available")
    st.caption("Cookie Authentication")
    
    if st.session_state.get('cookie_api'):
        st.caption("✅ Cookie configured")
    else:
        st.caption("⚠️ Cookie not set")

with col3:
    if current_mode == 'official':
        st.success("🏢 **Currently Active**")
    else:
        st.info("🏢 Available")
    st.caption("Official API")
    
    if st.session_state.get('official_api') and st.session_state.official_api.is_authenticated():
        st.caption("✅ Authenticated")
    else:
        st.caption("⚠️ Not authenticated")

with col4:
    if current_mode == 'rapidapi':
        st.success("💳 **Currently Active**")
    else:
        st.info("💳 Available")
    st.caption("RapidAPI Service")
    
    if st.session_state.get('rapidapi_client'):
        st.caption("✅ API key set")
    else:
        st.caption("⚠️ No API key")

# Quick mode switching
st.markdown("---")
st.header("⚡ Quick Mode Switching")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🎯 Unofficial", type="secondary"):
        st.session_state.api_mode = 'unofficial'
        st.success("Switched to Unofficial!")
        st.rerun()

with col2:
    if st.button("🍪 Cookie", type="secondary"):
        st.session_state.api_mode = 'cookie'
        st.success("Switched to Cookie!")
        st.rerun()

with col3:
    if st.button("🏢 Official", type="secondary"):
        st.session_state.api_mode = 'official'
        st.success("Switched to Official!")
        st.rerun()

with col4:
    if st.button("💳 RapidAPI", type="secondary"):
        st.session_state.api_mode = 'rapidapi'
        st.success("Switched to RapidAPI!")
        st.rerun()

# Footer with summary
st.markdown("---")
st.info("""
📋 **Summary:** 
- **🎯 Unofficial Mode**: Best for quick, simple downloads with no setup
- **🍪 Cookie Mode**: Best balance of reliability and ease of use  
- **🏢 Official API**: Best for business applications and full features
- **💳 RapidAPI**: Best for commercial applications needing guaranteed reliability

Choose the mode that best fits your needs, and remember you can always switch between them!
""")

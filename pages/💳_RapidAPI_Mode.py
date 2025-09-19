import streamlit as st
import time
from terabox_rapidapi import TeraBoxRapidAPI
from typing import Dict, Any

st.set_page_config(
    page_title="RapidAPI Mode",
    page_icon="💳",
    layout="wide"
)

st.title("💳 RapidAPI TeraBox Service")
st.markdown("Commercial TeraBox API service for reliable, professional-grade file extraction")

# Initialize session state
if 'rapidapi_client' not in st.session_state:
    st.session_state.rapidapi_client = None
if 'rapidapi_validated' not in st.session_state:
    st.session_state.rapidapi_validated = False
if 'current_rapidapi_key' not in st.session_state:
    st.session_state.current_rapidapi_key = ""

# Header with service info
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
    if st.button("🔄 Switch to Other Modes"):
        st.switch_page("pages/📊_Mode_Comparison.py")

# Service Overview
st.header("🏢 RapidAPI TeraBox Service Overview")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **🎯 What it is:**
    - Commercial API service
    - Hosted on RapidAPI marketplace
    - Professional TeraBox integration
    - Pay-per-use or subscription model
    """)

with col2:
    st.markdown("""
    **✅ Benefits:**
    - Guaranteed uptime
    - No anti-bot issues
    - Simple API integration
    - Professional support
    """)

with col3:
    st.markdown("""
    **📊 Use Cases:**
    - Business applications
    - High-volume processing
    - Reliability requirements
    - Commercial projects
    """)

# API Key Configuration
st.header("🔑 RapidAPI Configuration")

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

# API Key Input
col1, col2 = st.columns([2, 1])

with col1:
    api_key_input = st.text_input(
        "Enter your RapidAPI Key:",
        type="password",
        value=st.session_state.current_rapidapi_key,
        placeholder="298bbd7e09msh8c672d04ba26de4p154bc9jsn9de6459d8a13",
        help="Your X-RapidAPI-Key from the RapidAPI dashboard"
    )
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        if st.button("🔍 Validate API Key", type="primary"):
            if api_key_input.strip():
                with st.spinner("Validating RapidAPI key..."):
                    client = TeraBoxRapidAPI(api_key_input.strip())
                    validation_result = client.validate_api_key()
                
                if validation_result['status'] == 'success':
                    st.session_state.rapidapi_client = client
                    st.session_state.rapidapi_validated = True
                    st.session_state.current_rapidapi_key = api_key_input.strip()
                    st.success("✅ API key is valid!")
                    st.rerun()
                else:
                    st.error(f"❌ {validation_result['message']}")
            else:
                st.error("Please enter an API key")
    
    with col_b:
        if st.button("🗑️ Clear API Key"):
            st.session_state.rapidapi_client = None
            st.session_state.rapidapi_validated = False
            st.session_state.current_rapidapi_key = ""
            st.success("API key cleared!")
            st.rerun()

with col2:
    if st.session_state.rapidapi_client:
        st.success("💳 **API Status: Active**")
        
        # Show API status
        api_status = st.session_state.rapidapi_client.get_api_status()
        
        if api_status['api_key_status'] == 'success':
            st.success("✅ Valid API Key")
        else:
            st.error("❌ Invalid API Key")
        
        with st.expander("🔍 API Details"):
            st.json(api_status)
    else:
        st.warning("💳 **API Status: Not Configured**")
        st.caption("Enter and validate your API key above")

# File Processing Section
if st.session_state.rapidapi_client and st.session_state.rapidapi_validated:
    st.header("📁 File Processing")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🔗 Single File", "📋 Multiple Files", "🧪 Test & Debug", "📊 Usage Info"])
    
    with tab1:
        st.subheader("🔗 Single File Processing")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            terabox_url = st.text_input(
                "TeraBox URL:",
                placeholder="https://www.terabox.app/sharing/link?surl=...",
                help="Paste any TeraBox share link"
            )
        
        with col2:
            if st.button("📊 Get File Info", type="primary"):
                if terabox_url:
                    with st.spinner("Processing via RapidAPI..."):
                        file_info = st.session_state.rapidapi_client.get_file_info(terabox_url)
                    
                    if 'error' in file_info:
                        st.error(f"❌ Error: {file_info['error']}")
                    else:
                        st.success("✅ File information retrieved!")
                        
                        # Store in session state for download
                        st.session_state.current_file_info = file_info
                        
                        # Display file info in cards
                        col_a, col_b, col_c = st.columns(3)
                        
                        with col_a:
                            st.metric("📄 File Name", file_info.get('file_name', 'Unknown'))
                            st.metric("📏 File Size", file_info.get('size', 'Unknown'))
                        
                        with col_b:
                            st.metric("📁 File Type", file_info.get('file_type', 'Unknown').title())
                            st.metric("💾 Size (bytes)", f"{file_info.get('sizebytes', 0):,}")
                        
                        with col_c:
                            if file_info.get('thumbnail'):
                                try:
                                    st.image(file_info['thumbnail'], caption="Thumbnail", width=150)
                                except:
                                    st.caption("📷 Thumbnail available")
                            
                            if file_info.get('direct_link'):
                                st.success("✅ Direct link ready")
                        
                        # Download section
                        st.markdown("---")
                        st.subheader("📥 Download Options")
                        
                        col_x, col_y, col_z = st.columns(3)
                        
                        with col_x:
                            st.text_input("Direct Download URL:", value=file_info.get('direct_link', ''))
                        
                        with col_y:
                            if file_info.get('download_link') != file_info.get('direct_link'):
                                st.text_input("Alternative URL:", value=file_info.get('download_link', ''))
                        
                        with col_z:
                            if st.button("📥 Download File"):
                                download_file_with_progress(file_info)
                else:
                    st.error("Please enter a TeraBox URL")
    
    with tab2:
        st.subheader("📋 Bulk File Processing")
        
        urls_input = st.text_area(
            "Enter multiple TeraBox URLs (one per line):",
            height=150,
            placeholder="https://www.terabox.app/sharing/link?surl=link1\nhttps://terabox.com/s/link2\nhttps://1024terabox.com/s/link3"
        )
        
        if st.button("📊 Process All Files", type="primary"):
            if urls_input.strip():
                urls = [url.strip() for url in urls_input.strip().split('\n') if url.strip()]
                
                if urls:
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    status_text.text(f"Processing {len(urls)} files via RapidAPI...")
                    
                    with st.spinner("Processing multiple files..."):
                        results = st.session_state.rapidapi_client.get_multiple_files_info(urls)
                    
                    progress_bar.progress(100)
                    status_text.text("✅ Processing completed!")
                    
                    time.sleep(1)
                    progress_bar.empty()
                    status_text.empty()
                    
                    # Display results
                    successful = [r for r in results if 'error' not in r]
                    failed = [r for r in results if 'error' in r]
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("✅ Successful", len(successful))
                    with col_b:
                        st.metric("❌ Failed", len(failed))
                    
                    # Show successful files
                    if successful:
                        st.subheader("✅ Successfully Processed Files")
                        for i, result in enumerate(successful):
                            with st.expander(f"📄 {result.get('file_name', f'File {i+1}')}"):
                                col_info, col_download = st.columns([2, 1])
                                
                                with col_info:
                                    st.text(f"Name: {result.get('file_name', 'Unknown')}")
                                    st.text(f"Size: {result.get('size', 'Unknown')}")
                                    st.text(f"Type: {result.get('file_type', 'Unknown')}")
                                    st.text_input("Direct Link:", value=result.get('direct_link', ''), key=f"rapid_url_{i}")
                                
                                with col_download:
                                    if st.button(f"📥 Download", key=f"rapid_dl_{i}"):
                                        download_file_with_progress(result)
                    
                    # Show failed files
                    if failed:
                        st.subheader("❌ Failed Files")
                        for result in failed:
                            st.error(f"URL: {result['original_url'][:50]}... - Error: {result['error']}")
                else:
                    st.error("No valid URLs found")
            else:
                st.error("Please enter at least one URL")
    
    with tab3:
        st.subheader("🧪 Testing & Debugging")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**API Testing:**")
            
            if st.button("🔍 Test API Key"):
                with st.spinner("Testing API key..."):
                    validation = st.session_state.rapidapi_client.validate_api_key()
                st.json(validation)
            
            if st.button("🧪 Test with Sample URLs"):
                with st.spinner("Testing with sample URLs..."):
                    test_results = st.session_state.rapidapi_client.test_with_sample_url()
                st.json(test_results)
        
        with col2:
            st.markdown("**Service Information:**")
            
            if st.button("📊 Get API Status"):
                api_status = st.session_state.rapidapi_client.get_api_status()
                st.json(api_status)
            
            if st.button("📈 Get Usage Info"):
                usage_info = st.session_state.rapidapi_client.get_usage_info()
                st.json(usage_info)
        
        # Custom URL testing
        st.markdown("**Custom URL Testing:**")
        test_url = st.text_input("Test URL:", placeholder="https://terabox.com/s/your_test_link")
        
        if st.button("🧪 Test Custom URL"):
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
    
    with tab4:
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
            
            if st.button("🌐 Open RapidAPI Dashboard"):
                st.markdown(f"[Open Dashboard]({pricing_info['dashboard']})")
        
        # Supported formats
        st.markdown("**🔗 Supported URL Formats:**")
        supported_formats = st.session_state.rapidapi_client.get_supported_formats()
        
        for format_url in supported_formats:
            st.code(format_url)

else:
    # Getting started section
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
    
    # Comparison with other modes
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
    
    # Sample API response
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

def download_file_with_progress(file_info: Dict[str, Any]):
    """Download file with progress tracking"""
    if 'error' in file_info:
        st.error(f"Cannot download: {file_info['error']}")
        return
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        status_text.text("📥 Starting download...")
        
        # Use the RapidAPI client's download method
        result = st.session_state.rapidapi_client.download_file(file_info, save_path="downloads/")
        
        progress_bar.progress(100)
        status_text.text("✅ Download completed!")
        
        time.sleep(1)
        progress_bar.empty()
        status_text.empty()
        
        if 'error' in result:
            st.error(f"❌ Download failed: {result['error']}")
        else:
            st.success(f"✅ Downloaded successfully!")
            st.info(f"📁 File saved to: {result['file_path']}")
            
            # Offer Streamlit download button
            try:
                with open(result['file_path'], 'rb') as f:
                    st.download_button(
                        label=f"💾 Download {file_info['file_name']}",
                        data=f.read(),
                        file_name=file_info['file_name'],
                        mime="application/octet-stream"
                    )
            except Exception as e:
                st.warning(f"Could not create download button: {e}")
                
    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        st.error(f"❌ Unexpected error: {str(e)}")

# Pricing and plans section
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

# Footer
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

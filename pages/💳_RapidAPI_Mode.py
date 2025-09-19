import streamlit as st
import time
from utils.terabox_rapidapi import TeraBoxRapidAPI
from typing import Dict, Any
from utils.browser_utils import open_direct_file_link, display_browser_open_result, create_browser_selection_ui
from utils.terabox_config import get_config_manager

def download_file_with_progress(file_info: Dict[str, Any]):
    """Download file with enhanced progress tracking and error handling"""
    if 'error' in file_info:
        st.error(f"Cannot download: {file_info['error']}")
        return
    
    # Enhanced progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    speed_text = st.empty()
    
    # Progress callback function
    start_time = time.time()
    last_update = start_time
    
    def progress_callback(downloaded: int, total: int, percentage: float):
        nonlocal last_update
        current_time = time.time()
        
        # Update every 0.5 seconds to avoid too frequent updates
        if current_time - last_update >= 0.5:
            elapsed = current_time - start_time
            if elapsed > 0 and downloaded > 0:
                speed = downloaded / elapsed  # bytes per second
                speed_mb = speed / (1024 * 1024)  # MB per second
                
                # Estimate remaining time
                if speed > 0 and total > downloaded:
                    remaining_bytes = total - downloaded
                    eta_seconds = remaining_bytes / speed
                    eta_min = int(eta_seconds // 60)
                    eta_sec = int(eta_seconds % 60)
                    eta_str = f"{eta_min}m {eta_sec}s" if eta_min > 0 else f"{eta_sec}s"
                    
                    speed_text.text(f"⚡ Speed: {speed_mb:.1f} MB/s | ETA: {eta_str}")
                else:
                    speed_text.text(f"⚡ Speed: {speed_mb:.1f} MB/s")
            
            progress_bar.progress(percentage / 100)
            last_update = current_time
    
    try:
        status_text.text("📥 Initializing download...")
        
        # Use the enhanced RapidAPI client's download method with callback
        result = st.session_state.rapidapi_client.download_file(
            file_info, 
            save_path=None,  # Will use default download/ directory
            callback=progress_callback
        )
        
        progress_bar.progress(100)
        status_text.text("✅ Download completed!")
        speed_text.empty()
        
        time.sleep(1)
        progress_bar.empty()
        status_text.empty()
        
        if 'error' in result:
            st.error(f"❌ Download failed: {result['error']}")
            
            # Show debug information for failed downloads
            with st.expander("🔍 Debug Information"):
                st.text("File Info:")
                st.json(file_info)
                st.text("Download Result:")
                st.json(result)
        else:
            st.success(f"✅ Downloaded successfully!")
            
            # Show detailed download info
            col_info1, col_info2 = st.columns(2)
            with col_info1:
                st.info(f"📁 File saved to: {result['file_path']}")
                st.info(f"📏 Downloaded size: {result['size']:,} bytes")
            
            with col_info2:
                if result.get('original_filename') != result.get('sanitized_filename'):
                    st.info(f"📝 Original: {result.get('original_filename', 'N/A')}")
                    st.info(f"📝 Saved as: {result.get('sanitized_filename', 'N/A')}")
                
                if result.get('download_url_used'):
                    st.caption(f"🔗 Used: {result['download_url_used'][:50]}...")
            
            # Offer Streamlit download button
            try:
                with open(result['file_path'], 'rb') as f:
                    file_data = f.read()
                    
                st.download_button(
                    label=f"💾 Download {result.get('sanitized_filename', file_info['file_name'])}",
                    data=file_data,
                    file_name=result.get('sanitized_filename', file_info['file_name']),
                    mime="application/octet-stream",
                    use_container_width=True
                )
                
                # Show file size confirmation
                st.success(f"🎉 File ready for download ({len(file_data):,} bytes)")
                
            except Exception as e:
                st.warning(f"⚠️ Could not create download button: {e}")
                st.info("💡 The file was downloaded to the server, but couldn't be prepared for browser download.")
                
    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        speed_text.empty()
        st.error(f"❌ Unexpected error: {str(e)}")
        
        # Show debug information for unexpected errors
        with st.expander("🔍 Debug Information"):
            st.text("Error Details:")
            st.code(str(e))
            st.text("File Info:")
            st.json(file_info)

st.set_page_config(
    page_title="RapidAPI Mode",
    page_icon="💳",
    layout="wide"
)

# st.title("💳 RapidAPI TeraBox Service")
# st.markdown("Commercial TeraBox API service for reliable, professional-grade file extraction")

# Get configuration manager
config_mgr = get_config_manager()
rapidapi_config = config_mgr.get_rapidapi_config()

# Initialize session state
if 'rapidapi_client' not in st.session_state:
    st.session_state.rapidapi_client = None
if 'rapidapi_validated' not in st.session_state:
    st.session_state.rapidapi_validated = False
if 'current_rapidapi_key' not in st.session_state:
    # Try to load from config
    st.session_state.current_rapidapi_key = rapidapi_config.api_key or ""

# Header with service info
col1, col2 = st.columns([3, 1])

# with col1:
#     st.info("""
#     **💳 RapidAPI Mode** provides commercial-grade TeraBox access:
#     - ✅ Professional reliability and uptime
#     - ✅ No complex setup or authentication
#     - ✅ Direct download links guaranteed
#     - ✅ Commercial support and SLA
#     - 💰 Requires RapidAPI subscription
#     """)

# with col2:
#     if st.button("🔄 Switch to Other Modes"):
#         st.switch_page("pages/📊_Mode_Comparison.py")

# Service Overview
# st.header("🏢 RapidAPI TeraBox Service Overview")

# col1, col2, col3 = st.columns(3)

# with col1:
#     st.markdown("""
#     **🎯 What it is:**
#     - Commercial API service
#     - Hosted on RapidAPI marketplace
#     - Professional TeraBox integration
#     - Pay-per-use or subscription model
#     """)

# with col2:
#     st.markdown("""
#     **✅ Benefits:**
#     - Guaranteed uptime
#     - No anti-bot issues
#     - Simple API integration
#     - Professional support
#     """)

# with col3:
#     st.markdown("""
#     **📊 Use Cases:**
#     - Business applications
#     - High-volume processing
#     - Reliability requirements
#     - Commercial projects
#     """)

# API Key Configuration
# st.header("🔑 RapidAPI Configuration")

# with st.expander("📋 How to Get RapidAPI Key", expanded=not st.session_state.rapidapi_validated):
#     st.markdown("""
#     ### Step 1: Create RapidAPI Account
#     1. Go to [RapidAPI.com](https://rapidapi.com)
#     2. Sign up for a free account
#     3. Verify your email address
    
#     ### Step 2: Subscribe to TeraBox Service
#     1. Search for "terabox-downloader-direct-download-link-generator2"
#     2. Choose a subscription plan:
#        - **Basic Plan**: Limited requests per month
#        - **Pro Plan**: Higher request limits
#        - **Ultra Plan**: Unlimited requests
#     3. Subscribe to your chosen plan
    
#     ### Step 3: Get Your API Key
#     1. Go to your RapidAPI dashboard
#     2. Find the TeraBox service in your subscriptions
#     3. Copy your X-RapidAPI-Key
#     4. Paste it in the configuration below
    
#     ### Step 4: Test Your Setup
#     1. Enter your API key below
#     2. Click "Validate API Key"
#     3. Test with sample URLs
#     4. Start using the service!
    
#     **💡 Tip:** Keep your API key secure and don't share it publicly.
#     """)

# API Key Input
# col1, col2 = st.columns([2, 1])

# with col1:

# with col2:
if st.session_state.rapidapi_client:
        # st.success("💳 **API Status: Active**")
        
        # Show API status
        api_status = st.session_state.rapidapi_client.get_api_status()
        
        if api_status['api_key_status'] == 'success':
            st.success("✅ Valid API Key")
        else:
            st.error("❌ Invalid API Key")
        
        # with st.expander("🔍 API Details"):
        #     st.json(api_status)
else:
    api_key_input = st.text_input(
            "Enter your RapidAPI Key:",
            type="password",
            value=st.session_state.current_rapidapi_key,
            placeholder=rapidapi_config.api_key or "298bbd7e09msh8c672d04ba26de4p154bc9jsn9de6459d8a13",
            help="Your X-RapidAPI-Key from the RapidAPI dashboard (Format: [alphanumeric]msh[alphanumeric]jsn[alphanumeric], 50 characters)"
    )
    
    # Real-time format validation
    if api_key_input.strip():
        temp_client = TeraBoxRapidAPI()
        format_check = temp_client.quick_validate_api_key_format(api_key_input.strip())
        
        if format_check['status'] == 'success':
            st.success("✅ API key format is valid")
            with st.expander("📋 Format Details", expanded=False):
                st.json(format_check['details'])
        else:
            st.warning(f"⚠️ Format Issue: {format_check['message']}")
            if 'details' in format_check:
                st.info(f"💡 {format_check['details']}")
                
            # Show format requirements
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
        
    col_a, col_b, col_c = st.columns(3)
        
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
                        st.success("✅ API key is valid and working!")
                        
                        # Show validation details
                        with st.expander("🔍 Validation Details", expanded=False):
                            st.write("**Format Validation:**")
                            st.json(validation_result.get('format_check', {}))
                            st.write("**Live API Test:**")
                            st.json(validation_result.get('live_test', {}))
                        
                        st.rerun()
                    elif validation_result['status'] == 'warning':
                        # Handle warnings (like network issues)
                        st.warning(f"⚠️ {validation_result['message']}")
                        if 'details' in validation_result:
                            st.info(f"Details: {validation_result['details']}")
                        
                        # Ask user if they want to proceed anyway
                        if st.button("✅ Use API Key Anyway"):
                            client = TeraBoxRapidAPI(api_key_input.strip())
                            st.session_state.rapidapi_client = client
                            st.session_state.rapidapi_validated = True
                            st.session_state.current_rapidapi_key = api_key_input.strip()
                            st.success("✅ API key configured (with warnings)")
                            st.rerun()
                    else:
                        st.error(f"❌ {validation_result['message']}")
                        if 'details' in validation_result:
                            st.info(f"Details: {validation_result['details']}")
                else:
                    st.error("Please enter an API key")
    
    with col_b:
        if st.button("⚡ Quick Format Check"):
            if api_key_input.strip():
                temp_client = TeraBoxRapidAPI()
                format_result = temp_client.quick_validate_api_key_format(api_key_input.strip())
                
                if format_result['status'] == 'success':
                    st.success("✅ Format is valid!")
                else:
                    st.error(f"❌ {format_result['message']}")
            else:
                st.error("Please enter an API key")
        
    with col_c:
            if st.button("🗑️ Clear API Key"):
                st.session_state.rapidapi_client = None
                st.session_state.rapidapi_validated = False
                st.session_state.current_rapidapi_key = ""
                st.success("API key cleared!")
                st.rerun()
    st.warning("💳 **API Status: Not Configured**")
    st.caption("Enter and validate your API key above")


# File Processing Section
if st.session_state.rapidapi_client and st.session_state.rapidapi_validated:
    st.header("📁 File Processing")
    
    # Browser Selection Section
    with st.expander("🌐 Browser Settings", expanded=False):
        col_browser, col_info = st.columns([2, 1])
        
        with col_browser:
            selected_browser = create_browser_selection_ui()
            if selected_browser:
                st.success(f"✅ Browser configured")
        
        with col_info:
            st.info("""
            **Browser Selection:**
            Choose which browser to use when opening direct file links.
            The selected browser will be used for all "Open Direct File Link" operations.
            """)
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🔗 Single File", "📋 Multiple Files", "🧪 Test & Debug", "📊 Usage Info", "💾 Cache Manager"])
    
    with tab1:
        st.subheader("🔗 Single File Processing")
        
        # col1, col2 = st.columns([2, 1])
        
        # with col1:
        terabox_url = st.text_input(
                "TeraBox URL:",
                placeholder="https://www.terabox.app/sharing/link?surl=...",
                help="Paste any TeraBox share link"
        )
        
        # with col2:
        if st.button("📊 Get File Info", type="primary"):
                if terabox_url:
                    # Check if force refresh is enabled
                    force_refresh = st.session_state.get('force_refresh_next', False)
                    
                    if force_refresh:
                        st.info("🔄 Force refresh enabled - bypassing cache")
                        st.session_state.force_refresh_next = False  # Reset after use
                    
                    with st.spinner("Processing via RapidAPI..."):
                        file_info = st.session_state.rapidapi_client.get_file_info(terabox_url, force_refresh=force_refresh)
                    
                    if 'error' in file_info:
                        st.error(f"❌ Error: {file_info['error']}")
                    else:
                        # Check if response was from cache
                        if file_info.get('_cache_info', {}).get('cached', False):
                            cache_age_hours = file_info['_cache_info'].get('cache_age_hours', 0)
                            st.success(f"✅ File information retrieved from cache! (Age: {cache_age_hours:.1f}h)")
                            st.info("🚀 **Lightning fast response from cache!** This saved time and API usage.")
                        else:
                            st.success("✅ File information retrieved from RapidAPI!")
                            st.info("💾 **Response cached for future requests** - Next time will be instant!")
                        
                        # Store in session state for download
                        st.session_state.current_file_info = file_info
                        
                        # Display file info in enhanced cards
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
                            
                            # Show service indicator with cache status
                            if file_info.get('_cache_info', {}).get('cached', False):
                                st.info("💾 **Cached Response**")
                                surl = file_info['_cache_info'].get('surl', 'Unknown')
                                st.caption(f"SURL: {surl}")
                            else:
                                st.info("🚀 **RapidAPI Service**")
                                st.caption("Fresh API response")
                            
                            # Show validation status
                            if file_info.get('direct_link') and file_info.get('download_link'):
                                st.success("✅ Multiple download links")
                            elif file_info.get('direct_link'):
                                st.success("✅ Direct link ready")
                            else:
                                st.warning("⚠️ Limited download options")
                        
                        # Enhanced download section
                        st.markdown("---")
                        st.subheader("📥 Enhanced Download Options")
                        
                        # Show all available download URLs
                        download_urls = []
                        if file_info.get('direct_link'):
                            download_urls.append(('Direct Link', file_info['direct_link']))
                        if file_info.get('download_link') and file_info.get('download_link') != file_info.get('direct_link'):
                            download_urls.append(('Alternative Link', file_info['download_link']))
                        if file_info.get('link') and file_info.get('link') not in [file_info.get('direct_link'), file_info.get('download_link')]:
                            download_urls.append(('Backup Link', file_info['link']))
                        
                        # Display download URLs
                        for i, (label, url) in enumerate(download_urls):
                            col_url, col_btn = st.columns([3, 1])
                            with col_url:
                                st.text_input(f"{label}:", value=url, key=f"rapid_url_{i}")
                            with col_btn:
                                if st.button(f"📥 Use {label.split()[0]}", key=f"rapid_btn_{i}"):
                                    download_file_with_progress(file_info)
                        
                        # Main download button
                        st.markdown("---")
                        col_download, col_debug = st.columns([2, 1])
                        
                        with col_download:
                            if st.button("🚀 Smart Download (Try All URLs)", type="primary", key="smart_download"):
                                download_file_with_progress(file_info)
                        
                        with col_debug:
                            if st.button("🔍 Debug Info", key="debug_info"):
                                st.json(file_info.get('raw_response', {}))
                else:
                    st.error("Please enter a TeraBox URL")
        if st.button("📥 Open Direct File Link", key="open_direct_file_link"):
                        # Open Direct File Link after fetch Direct Link
                        if 'current_file_info' in st.session_state and st.session_state.current_file_info:
                            file_info = st.session_state.current_file_info
                            
                            # Get preferred browser
                            preferred_browser = st.session_state.get('preferred_browser', None)
                            
                            with st.spinner("🌐 Opening direct file link in browser..."):
                                result = open_direct_file_link(file_info, browser=preferred_browser)
                            
                            # Display result
                            display_browser_open_result(result, show_details=True)
                            
                            # Log the action for debugging
                            if result['status'] == 'success':
                                st.balloons()  # Celebrate success!
                        else:
                            st.error("❌ No file information available. Please get file info first.")
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
                    
                    # Show successful files with enhanced display
                    if successful:
                        st.subheader("✅ Successfully Processed Files")
                        for i, result in enumerate(successful):
                            with st.expander(f"📄 {result.get('file_name', f'File {i+1}')} - {result.get('size', 'Unknown')}"):
                                col_info, col_links, col_actions = st.columns([2, 2, 1])
                                
                                with col_info:
                                    st.text(f"📄 Name: {result.get('file_name', 'Unknown')}")
                                    st.text(f"📏 Size: {result.get('size', 'Unknown')}")
                                    st.text(f"📁 Type: {result.get('file_type', 'Unknown')}")
                                    st.text(f"💾 Bytes: {result.get('sizebytes', 0):,}")
                                    
                                    # Show thumbnail if available
                                    if result.get('thumbnail'):
                                        try:
                                            st.image(result['thumbnail'], caption="Preview", width=100)
                                        except:
                                            st.caption("📷 Thumbnail available")
                                
                                with col_links:
                                    # Show all available download URLs
                                    if result.get('direct_link'):
                                        st.text_input("Direct Link:", value=result['direct_link'], key=f"bulk_direct_{i}")
                                    if result.get('download_link') and result.get('download_link') != result.get('direct_link'):
                                        st.text_input("Alt Link:", value=result['download_link'], key=f"bulk_alt_{i}")
                                    
                                    # Show service info
                                    st.caption(f"🚀 Service: {result.get('service', 'RapidAPI')}")
                                
                                with col_actions:
                                    if st.button(f"📥 Download", key=f"rapid_dl_{i}"):
                                        download_file_with_progress(result)
                                    
                                    if st.button(f"🌐 Open Link", key=f"rapid_open_{i}"):
                                        preferred_browser = st.session_state.get('preferred_browser', None)
                                        with st.spinner("🌐 Opening link..."):
                                            open_result = open_direct_file_link(result, browser=preferred_browser)
                                        display_browser_open_result(open_result, show_details=False)
                                        if open_result['status'] == 'success':
                                            st.balloons()
                                    
                                    if st.button(f"🔍 Debug", key=f"rapid_debug_{i}"):
                                        st.json(result.get('raw_response', result))
                    
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
    
    with tab5:
        st.subheader("💾 Cache Management")
        
        # Cache status and information
        cache_info = st.session_state.rapidapi_client.get_cache_info()
        
        if cache_info.get('enabled'):
            # st.success("✅ **Cache Status: Enabled**")
            
            # col1, col2 = st.columns(2)
            
            # with col1:
            #     st.info(f"📁 **Cache Directory:** `{cache_info.get('cache_directory', 'Unknown')}`")
            #     st.info(f"⏰ **Cache TTL:** {cache_info.get('ttl_hours', 24)} hours")
            
            # with col2:
            # Cache statistics
            if st.button("📊 Get Cache Statistics"):
                    with st.spinner("Loading cache statistics..."):
                        cache_stats = st.session_state.rapidapi_client.get_cache_stats()
                    
                    if 'error' not in cache_stats:
                        col_stat1, col_stat2, col_stat3 = st.columns(3)
                        
                        with col_stat1:
                            st.metric("📄 Total Files", cache_stats.get('total_files', 0))
                            st.metric("✅ Valid Files", cache_stats.get('valid_files', 0))
                        
                        with col_stat2:
                            st.metric("⚠️ Expired Files", cache_stats.get('expired_files', 0))
                            st.metric("💾 Total Size", f"{cache_stats.get('total_size_mb', 0):.2f} MB")
                        
                        with col_stat3:
                            # Show cache efficiency
                            total_files = cache_stats.get('total_files', 0)
                            valid_files = cache_stats.get('valid_files', 0)
                            efficiency = (valid_files / total_files * 100) if total_files > 0 else 0
                            st.metric("🎯 Cache Efficiency", f"{efficiency:.1f}%")
                        
                        # Show detailed file list
                        if cache_stats.get('files'):
                            st.markdown("---")
                            st.subheader("📋 Cache Files Details")
                            
                            # Create a dataframe for better display
                            import pandas as pd
                            
                            files_data = []
                            for file_info in cache_stats['files'][:10]:  # Show only first 10
                                files_data.append({
                                    'SURL': file_info.get('surl', 'Unknown')[:15] + '...' if len(file_info.get('surl', '')) > 15 else file_info.get('surl', 'Unknown'),
                                    'Age (hours)': f"{file_info.get('age_hours', 0):.1f}",
                                    'Size (KB)': f"{file_info.get('size_kb', 0):.1f}",
                                    'Status': '✅ Valid' if file_info.get('is_valid', False) else '⚠️ Expired',
                                    'Created': file_info.get('created_at', 'Unknown')[:10] if file_info.get('created_at') else 'Unknown'
                                })
                            
                            if files_data:
                                df = pd.DataFrame(files_data)
                                st.dataframe(df, use_container_width=True, hide_index=True)
                                
                                if len(cache_stats['files']) > 10:
                                    st.caption(f"Showing first 10 of {len(cache_stats['files'])} cache files")
                    else:
                        st.error(f"❌ Error getting cache stats: {cache_stats.get('error', 'Unknown error')}")
            
            # Cache management actions
            st.markdown("---")
            st.subheader("🛠️ Cache Actions")
            
            col_action1, col_action2, col_action3 = st.columns(3)
            
            with col_action1:
                if st.button("🧹 Clean Expired Cache", type="secondary"):
                    with st.spinner("Cleaning expired cache files..."):
                        cleanup_result = st.session_state.rapidapi_client.cleanup_expired_cache()
                    
                    if cleanup_result.get('status') == 'success':
                        cleaned_files = cleanup_result.get('cleaned_files', 0)
                        if cleaned_files > 0:
                            st.success(f"✅ Cleaned {cleaned_files} expired cache files")
                        else:
                            st.info("ℹ️ No expired cache files found")
                    else:
                        st.error(f"❌ Cleanup failed: {cleanup_result.get('message', 'Unknown error')}")
            
            with col_action2:
                if st.button("🗑️ Clear All Cache", type="secondary"):
                    if st.session_state.get('confirm_clear_cache', False):
                        with st.spinner("Clearing all cache files..."):
                            clear_result = st.session_state.rapidapi_client.clear_cache()
                        
                        if clear_result.get('status') == 'success':
                            cleared_files = clear_result.get('cleared', 0)
                            st.success(f"✅ Cleared {cleared_files} cache files")
                        else:
                            st.error(f"❌ Clear failed: {clear_result.get('message', 'Unknown error')}")
                        
                        st.session_state.confirm_clear_cache = False
                    else:
                        st.session_state.confirm_clear_cache = True
                        st.warning("⚠️ Click again to confirm clearing all cache")
            
            with col_action3:
                # Force refresh option
                st.markdown("**🔄 Force Refresh:**")
                st.caption("Next request will bypass cache")
                if 'force_refresh_next' not in st.session_state:
                    st.session_state.force_refresh_next = False
                
                if st.checkbox("Force refresh next request", value=st.session_state.force_refresh_next):
                    st.session_state.force_refresh_next = True
                    st.info("ℹ️ Next request will bypass cache")
                else:
                    st.session_state.force_refresh_next = False
            
            # # Cache configuration
            # st.markdown("---")
            # st.subheader("⚙️ Cache Configuration")
            
            # current_ttl = cache_info.get('ttl_hours', 24)
            # st.info(f"Current cache TTL: {current_ttl} hours")
            # st.caption("Cache TTL (Time To Live) determines how long responses are cached before expiring.")
            
            # # Show cache benefits
            # with st.expander("💡 Cache Benefits"):
            #     st.markdown("""
            #     **✅ Performance Benefits:**
            #     - Faster response times for repeated requests
            #     - Reduced API usage and costs
            #     - Better user experience with instant results
            #     - Offline access to previously fetched data
                
            #     **📊 Usage Optimization:**
            #     - Automatic cleanup of expired files
            #     - Configurable cache duration
            #     - Smart cache key generation using SURL
            #     - Detailed cache statistics and monitoring
                
            #     **🔧 Management Features:**
            #     - Force refresh to bypass cache
            #     - Selective or complete cache clearing
            #     - Cache file inspection and monitoring
            #     - Automatic expiry based on TTL
            #     """)
        
        else:
            st.warning("⚠️ **Cache Status: Disabled**")
            st.info("Caching is not enabled for this RapidAPI client instance.")
            
            with st.expander("ℹ️ About Caching"):
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

# else:
#     # Getting started section
#     st.header("🚀 Getting Started with RapidAPI")
    
#     col1, col2 = st.columns(2)
    
#     with col1:
#         st.markdown("""
#         ### ✅ Why Choose RapidAPI Mode:
#         - **Professional Reliability** - Commercial-grade uptime and performance
#         - **No Complex Setup** - Just need an API key, no OAuth or cookies
#         - **Guaranteed Results** - Professional service with SLA
#         - **Scalable** - Handle high-volume requests
#         - **Support** - Commercial support available
#         - **No Anti-Bot Issues** - Service handles all technical challenges
#         """)
    
#     with col2:
#         st.markdown("""
#         ### 💰 Cost Considerations:
#         - **Pay-per-Use** - Only pay for what you use
#         - **Subscription Plans** - Various tiers available
#         - **Free Tier** - Usually includes some free requests
#         - **Business Plans** - Higher limits for commercial use
#         - **Transparent Pricing** - Clear pricing on RapidAPI marketplace
#         - **No Hidden Costs** - What you see is what you pay
#         """)
    
#     # Comparison with other modes
#     st.subheader("📊 Quick Comparison")
    
#     comparison_data = {
#         "Aspect": ["Setup", "Cost", "Reliability", "Support", "Rate Limits"],
#         "🎪 Unofficial": ["None", "Free", "Variable", "Community", "May hit blocks"],
#         "🍪 Cookie": ["Cookie needed", "Free", "Good", "Community", "Account limits"],
#         "🏢 Official API": ["Complex", "Free*", "Excellent", "Official", "API limits"],
#         "💳 RapidAPI": ["API key only", "Paid", "Excellent", "Commercial", "Plan-based"]
#     }
    
#     import pandas as pd
#     df = pd.DataFrame(comparison_data)
#     st.dataframe(df, width='stretch', hide_index=True)
    
#     # Sample API response
#     st.subheader("📋 Sample API Response")
    
#     with st.expander("📄 Example Response Format"):
#         sample_response = {
#             "direct_link": "https://data.1024tera.com/file/fa17446224904abdcb3c052c69d1a7e2?bkt=...",
#             "file_name": "Richh(1)(1)(1)(1).mp4", 
#             "link": "https://d.1024tera.com/file/fa17446224904abdcb3c052c69d1a7e2?fid=...",
#             "size": "16.00 MB",
#             "sizebytes": 16775878,
#             "thumb": "https://data.1024tera.com/thumbnail/fa17446224904abdcb3c052c69d1a7e2?fid=..."
#         }
#         st.json(sample_response)

# # Pricing and plans section
# st.markdown("---")
# st.header("💰 RapidAPI Pricing & Plans")

# col1, col2, col3 = st.columns(3)

# with col1:
#     st.markdown("""
#     **🆓 Basic Plan**
#     - Limited requests/month
#     - Good for testing
#     - Personal projects
#     - Low volume usage
#     """)

# with col2:
#     st.markdown("""
#     **💼 Pro Plan**
#     - Higher request limits
#     - Business applications
#     - Regular usage
#     - Priority support
#     """)

# with col3:
#     st.markdown("""
#     **🚀 Ultra Plan**
#     - Unlimited requests
#     - Enterprise usage
#     - High-volume processing
#     - Premium support
#     """)

# st.info("💡 **Note:** Visit the RapidAPI marketplace for current pricing and plan details.")

# # Footer
# st.markdown("---")
# st.info("""
# 💳 **RapidAPI Mode Summary:**
# - Professional commercial service for TeraBox access
# - Simple API key authentication
# - Reliable direct download links
# - Commercial support and SLA
# - Perfect for business applications and high-volume usage
# - Requires RapidAPI subscription but offers guaranteed reliability
# """)

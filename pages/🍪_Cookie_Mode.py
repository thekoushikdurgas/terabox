import streamlit as st
import json
import time
import re
from utils.terabox_cookie_api import TeraBoxCookieAPI
from typing import Dict, Any, List
from utils.browser_utils import open_direct_file_link, display_browser_open_result, create_browser_selection_ui

def parse_tabular_cookies(cookie_data: str) -> Dict[str, str]:
    """
    Parse cookies from tabular format (browser export format)
    
    Expected format (tab-separated):
    name    value    domain    path    expires    size    httpOnly    secure    sameSite    priority
    
    Args:
        cookie_data (str): Raw cookie data in tabular format
        
    Returns:
        Dict[str, str]: Dictionary of cookie name-value pairs
    """
    cookies = {}
    lines = cookie_data.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Split by tabs (most common) or multiple spaces
        fields = re.split(r'\t+|\s{2,}', line)
        
        if len(fields) >= 2:
            cookie_name = fields[0].strip()
            cookie_value = fields[1].strip()
            
            # Skip empty names or values
            if cookie_name and cookie_value:
                cookies[cookie_name] = cookie_value
    
    return cookies

def filter_terabox_cookies(cookies: Dict[str, str]) -> Dict[str, str]:
    """
    Filter cookies to get only TeraBox-relevant ones
    
    Args:
        cookies (Dict[str, str]): All parsed cookies
        
    Returns:
        Dict[str, str]: Filtered TeraBox cookies
    """
    # Important TeraBox cookies
    important_cookies = ['ndus', 'BDUSS', 'STOKEN', 'csrfToken', 'lang']
    
    # TeraBox domain patterns
    terabox_domains = ['terabox.com', '1024terabox.com', 'terabox.app']
    
    filtered = {}
    
    for name, value in cookies.items():
        # Include important cookies regardless of domain
        if name in important_cookies:
            filtered[name] = value
        # Include cookies that might be TeraBox related
        elif any(domain in name.lower() for domain in ['terabox', '1024']):
            filtered[name] = value
        # Include session-related cookies
        elif name.lower() in ['sessionid', 'session', 'auth', 'token']:
            filtered[name] = value
        # Include bid cookies (common in TeraBox)
        elif 'bid' in name.lower():
            filtered[name] = value
        # Include stripe cookies (payment-related)
        elif 'stripe' in name.lower():
            filtered[name] = value
    
    return filtered

def format_cookie_string(cookies: Dict[str, str]) -> str:
    """
    Format cookies dictionary into a proper cookie string
    
    Args:
        cookies (Dict[str, str]): Cookie name-value pairs
        
    Returns:
        str: Formatted cookie string
    """
    cookie_pairs = []
    for name, value in cookies.items():
        # Clean the value (remove quotes if present)
        clean_value = value.strip('"\'')
        cookie_pairs.append(f"{name}={clean_value}")
    
    return "; ".join(cookie_pairs)

def auto_detect_cookie_format(cookie_input: str) -> str:
    """
    Auto-detect cookie format and parse accordingly
    
    Args:
        cookie_input (str): Raw cookie input
        
    Returns:
        str: Formatted cookie string
    """
    cookie_input = cookie_input.strip()
    
    # Check if it's already in cookie string format (name=value; name2=value2)
    if '=' in cookie_input and (';' in cookie_input or '\n' not in cookie_input):
        return cookie_input
    
    # Check if it's tabular format (multiple lines with tabs/spaces)
    if '\n' in cookie_input and '\t' in cookie_input:
        parsed_cookies = parse_tabular_cookies(cookie_input)
        filtered_cookies = filter_terabox_cookies(parsed_cookies)
        return format_cookie_string(filtered_cookies)
    
    # Check if it's a simple list format (one cookie per line)
    if '\n' in cookie_input:
        lines = cookie_input.split('\n')
        cookies = {}
        for line in lines:
            line = line.strip()
            if '=' in line:
                parts = line.split('=', 1)
                if len(parts) == 2:
                    cookies[parts[0].strip()] = parts[1].strip()
        
        if cookies:
            filtered_cookies = filter_terabox_cookies(cookies)
            return format_cookie_string(filtered_cookies)
    
    # Return as-is if no format detected
    return cookie_input

def show_connection_troubleshooting():
    """Show troubleshooting tips for connection errors"""
    with st.expander("🔧 Connection Troubleshooting Tips", expanded=True):
        st.markdown("""
        **Connection Error Solutions:**
        
        🌐 **Network Issues:**
        - Check your internet connection
        - Try switching to a different network (mobile hotspot, different WiFi)
        - Disable VPN/proxy temporarily if using one
        
        🔄 **Rate Limiting:**
        - Wait 1-2 minutes before trying again
        - TeraBox may be limiting requests from your IP
        - Try using a different IP address or network
        
        🍪 **Cookie Issues:**
        - Get a fresh cookie from your browser
        - Make sure you're logged into TeraBox in your browser
        - Clear browser cookies and log in again
        
        🛡️ **Firewall/Security:**
        - Check if your firewall is blocking the connection
        - Try disabling antivirus temporarily
        - Some corporate networks block TeraBox
        
        ⏰ **Server Issues:**
        - TeraBox servers might be temporarily down
        - Try again in a few minutes
        - Check TeraBox website status
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔍 Test Network Connection"):
                test_network_connection()
        with col2:
            if st.button("📊 Check TeraBox Status"):
                check_terabox_status()

def test_network_connection():
    """Test network connectivity to various endpoints"""
    import requests
    import time
    
    endpoints = [
        ("Google", "https://www.google.com"),
        ("TeraBox Main", "https://www.terabox.com"),
        ("TeraBox API", "https://www.terabox.com/api/user/info")
    ]
    
    st.subheader("🔍 Network Connection Test")
    
    for name, url in endpoints:
        with st.spinner(f"Testing {name}..."):
            try:
                start_time = time.time()
                response = requests.get(url, timeout=10)
                end_time = time.time()
                
                response_time = round((end_time - start_time) * 1000)  # ms
                
                if response.status_code == 200:
                    st.success(f"✅ {name}: OK ({response_time}ms)")
                else:
                    st.warning(f"⚠️ {name}: HTTP {response.status_code} ({response_time}ms)")
                    
            except requests.exceptions.ConnectionError:
                st.error(f"❌ {name}: Connection failed")
            except requests.exceptions.Timeout:
                st.error(f"❌ {name}: Timeout (>10s)")
            except Exception as e:
                st.error(f"❌ {name}: {str(e)}")
            
            time.sleep(0.5)  # Small delay between tests

def check_terabox_status():
    """Check TeraBox service status"""
    st.subheader("📊 TeraBox Service Status")
    
    try:
        import requests
        response = requests.get("https://www.terabox.com", timeout=10)
        
        if response.status_code == 200:
            st.success("✅ TeraBox main website is accessible")
            
            # Check for maintenance messages
            content = response.text.lower()
            if any(word in content for word in ['maintenance', 'temporarily', 'unavailable']):
                st.warning("⚠️ TeraBox may be under maintenance")
            else:
                st.info("ℹ️ TeraBox appears to be operating normally")
        else:
            st.error(f"❌ TeraBox returned HTTP {response.status_code}")
            
    except Exception as e:
        st.error(f"❌ Cannot reach TeraBox: {str(e)}")
    
    st.info("💡 You can also check TeraBox's official social media or support channels for service updates")

def download_file_with_progress(file_info: Dict[str, Any], save_path: str):
    """Download file with Streamlit progress tracking"""
    if 'error' in file_info:
        st.error(f"Cannot download: {file_info['error']}")
        return
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    def progress_callback(downloaded: int, total: int, percentage: float):
        progress_bar.progress(percentage / 100)
        status_text.text(f"Downloaded: {downloaded:,} / {total:,} bytes ({percentage:.1f}%)")
    
    try:
        with st.spinner("Starting download..."):
            result = st.session_state.cookie_api.download(
                file_info, 
                save_path=save_path,
                callback=progress_callback
            )
        
        progress_bar.empty()
        status_text.empty()
        
        if 'error' in result:
            st.error(f"❌ Download failed: {result['error']}")
        else:
            st.success(f"✅ Downloaded successfully!")
            st.info(f"📁 File saved to: {result['file_path']}")
            
            # Offer download button for the file
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

st.set_page_config(
    page_title="Cookie Mode",
    page_icon="🍪",
    layout="wide"
)

st.title("🍪 TeraBox Cookie Mode")
st.markdown("Use your TeraBox session cookie for reliable file access - inspired by terabox-downloader PyPI package")

# Initialize session state
if 'cookie_api' not in st.session_state:
    st.session_state.cookie_api = None
if 'cookie_validated' not in st.session_state:
    st.session_state.cookie_validated = False
if 'current_cookie' not in st.session_state:
    st.session_state.current_cookie = ""
if 'raw_cookie_input' not in st.session_state:
    st.session_state.raw_cookie_input = ""

# Header with mode info
col1, col2 = st.columns([3, 1])

with col1:
    st.info("""
    **🍪 Cookie Mode** provides a middle ground between unofficial scraping and official API:
    - ✅ More reliable than pure scraping
    - ✅ No API registration required  
    - ✅ Direct download links
    - ✅ File metadata access
    - ⚠️ Requires your TeraBox session cookie
    """)

with col2:
    if st.button("🔄 Switch to Other Modes"):
        st.switch_page("pages/🔑_API_Mode.py")

# Cookie Tutorial Section
st.header("📚 How to Get Your TeraBox Cookie")

with st.expander("📖 Step-by-Step Cookie Extraction Tutorial", expanded=not st.session_state.cookie_validated):
    
    tab1, tab2, tab3, tab4 = st.tabs(["🌐 Chrome", "🦊 Firefox", "📱 Mobile", "📋 Tabular Format"])
    
    with tab1:
        st.markdown("""
        ### Google Chrome Cookie Extraction:
        
        1. **Open TeraBox Website**
           - Go to [https://www.terabox.com](https://www.terabox.com)
           - Log in to your account
        
        2. **Open Developer Tools**
           - Press `F12` or `Ctrl+Shift+I`
           - Or right-click → "Inspect"
        
        3. **Go to Application Tab**
           - Click on "Application" tab in developer tools
           - If you don't see it, click the `>>` arrow
        
        4. **Find Cookies**
           - In left sidebar, expand "Cookies"
           - Click on "https://www.terabox.com"
        
        5. **Copy Important Cookies**
           - Look for cookies named: `ndus`, `BDUSS`, `STOKEN`
           - Copy the entire cookie string from the browser
           - Format: `name1=value1; name2=value2; name3=value3`
        
        6. **Alternative Method**
           - Right-click on the page → Inspect
           - Go to Network tab
           - Refresh the page
           - Click any request to terabox.com
           - Copy the "Cookie" header value
        """)
    
    with tab2:
        st.markdown("""
        ### Firefox Cookie Extraction:
        
        1. **Open TeraBox Website**
           - Go to [https://www.terabox.com](https://www.terabox.com)
           - Log in to your account
        
        2. **Open Developer Tools**
           - Press `F12`
           - Or right-click → "Inspect Element"
        
        3. **Go to Storage Tab**
           - Click on "Storage" tab
           - Expand "Cookies" in the left sidebar
           - Click on "https://www.terabox.com"
        
        4. **Copy Cookie Values**
           - Look for: `ndus`, `BDUSS`, `STOKEN`
           - Right-click on each → "Copy Value"
           - Format as: `name1=value1; name2=value2`
        
        5. **Network Method**
           - Go to "Network" tab
           - Refresh the page
           - Click any terabox.com request
           - Copy "Cookie" from request headers
        """)
    
    with tab3:
        st.markdown("""
        ### Mobile Cookie Extraction:
        
        **Android Chrome:**
        1. Open TeraBox in Chrome browser
        2. Log in to your account
        3. Type in address bar: `chrome://settings/cookies`
        4. Search for "terabox.com"
        5. Copy cookie values
        
        **iPhone Safari:**
        1. Open TeraBox in Safari
        2. Log in to your account
        3. Go to Settings → Safari → Advanced → Website Data
        4. Search for "terabox"
        5. Note: iOS makes this more difficult
        
        **Easier Mobile Method:**
        - Use desktop browser to get cookie
        - TeraBox cookies work across devices
        - Just ensure you're logged into the same account
        """)
    
    with tab4:
        st.markdown("""
        ### 📋 Tabular Format (Browser Cookie Export):
        
        **What is Tabular Format?**
        - Raw cookie data exported from browser developer tools
        - Tab-separated values with cookie properties
        - Common format from cookie management extensions
        
        **How to Export in Tabular Format:**
        
        **Method 1: Chrome Developer Tools**
        1. Open TeraBox and log in
        2. Press F12 → Application → Cookies → https://www.terabox.com
        3. Select all cookies (Ctrl+A)
        4. Copy the table data (Ctrl+C)
        5. Paste directly into the input field
        
        **Method 2: Cookie Export Extensions**
        1. Install "Cookie Editor" or similar extension
        2. Navigate to TeraBox.com while logged in
        3. Open extension and export cookies
        4. Choose "Tab-separated" or "Raw" format
        5. Copy the exported data
        
        **Sample Tabular Format:**
        ```
        __bid_n	1995f6d331f9b86c584207	.1024terabox.com	/	2026-10-24T01:41:32.686Z
        ndus	your_ndus_value_here	.terabox.com	/	2025-12-31T23:59:59.999Z
        BDUSS	your_bduss_value_here	.terabox.com	/	2025-12-31T23:59:59.999Z
        ```
        
        **Advantages:**
        - ✅ Preserves all cookie metadata
        - ✅ Automatic filtering of relevant cookies
        - ✅ Handles complex cookie structures
        - ✅ Works with cookie export tools
        
        **Tips:**
        - The parser automatically filters TeraBox-relevant cookies
        - Use "Preview Parsed Cookies" to see what will be extracted
        - Most important cookies: `ndus`, `BDUSS`, `STOKEN`
        - Domain doesn't matter for parsing - we filter by cookie names
        """)

# Cookie Input and Validation
st.header("🔐 Cookie Configuration")

col1, col2 = st.columns([2, 1])

with col1:
    # Add format selection
    cookie_format = st.selectbox(
        "Cookie Input Format:",
        ["Auto-detect", "Cookie String (name=value; name2=value2)", "Tabular Format (Browser Export)", "Line-by-line"],
        help="Choose the format of your cookie data"
    )
    
    # Adjust placeholder based on format
    if cookie_format == "Tabular Format (Browser Export)":
        placeholder_text = "__bid_n\t1995f6d331f9b86c584207\t.1024terabox.com\t/\t2026-10-24T01:41:32.686Z\nndus\tyour_ndus_value\t.terabox.com\t/\t2025-12-31T23:59:59.999Z"
        help_text = "Paste tabular cookie data from browser export (tab-separated values)"
        height = 150
    elif cookie_format == "Line-by-line":
        placeholder_text = "ndus=your_value_here\nBDUSS=another_value\nSTOKEN=token_value"
        help_text = "Enter one cookie per line in name=value format"
        height = 120
    else:
        placeholder_text = "ndus=your_value_here; BDUSS=another_value; STOKEN=token_value; ..."
        help_text = "Paste the complete cookie string from your browser"
        height = 100
    
    cookie_input = st.text_area(
        "Enter your TeraBox Cookie:",
        value=st.session_state.current_cookie,
        height=height,
        placeholder=placeholder_text,
        help=help_text
    )
    
    # Add a preview button for tabular format
    if cookie_format == "Tabular Format (Browser Export)" and cookie_input.strip():
        if st.button("👀 Preview Parsed Cookies"):
            try:
                parsed_cookies = parse_tabular_cookies(cookie_input.strip())
                filtered_cookies = filter_terabox_cookies(parsed_cookies)
                
                if parsed_cookies:
                    st.success(f"✅ Found {len(parsed_cookies)} cookies total, {len(filtered_cookies)} TeraBox-relevant cookies")
                    
                    col_preview1, col_preview2 = st.columns(2)
                    
                    with col_preview1:
                        st.markdown("**All Parsed Cookies:**")
                        for name, value in list(parsed_cookies.items())[:10]:  # Show first 10
                            st.text(f"{name}: {value[:50]}{'...' if len(value) > 50 else ''}")
                        if len(parsed_cookies) > 10:
                            st.caption(f"... and {len(parsed_cookies) - 10} more")
                    
                    with col_preview2:
                        st.markdown("**TeraBox-Relevant Cookies:**")
                        if filtered_cookies:
                            for name, value in filtered_cookies.items():
                                st.text(f"{name}: {value[:50]}{'...' if len(value) > 50 else ''}")
                        else:
                            st.warning("No TeraBox-relevant cookies found")
                    
                    # Show the final cookie string
                    if filtered_cookies:
                        final_cookie = format_cookie_string(filtered_cookies)
                        st.markdown("**Final Cookie String:**")
                        st.code(final_cookie[:200] + ('...' if len(final_cookie) > 200 else ''))
                else:
                    st.error("No cookies could be parsed from the input")
            except Exception as e:
                st.error(f"Error parsing cookies: {str(e)}")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        if st.button("🔍 Validate Cookie", type="primary"):
            if cookie_input.strip():
                with st.spinner("Parsing and validating cookie..."):
                    # Parse the cookie based on format
                    if cookie_format == "Auto-detect":
                        processed_cookie = auto_detect_cookie_format(cookie_input.strip())
                    elif cookie_format == "Tabular Format (Browser Export)":
                        parsed_cookies = parse_tabular_cookies(cookie_input.strip())
                        filtered_cookies = filter_terabox_cookies(parsed_cookies)
                        processed_cookie = format_cookie_string(filtered_cookies)
                    elif cookie_format == "Line-by-line":
                        lines = cookie_input.strip().split('\n')
                        cookies = {}
                        for line in lines:
                            line = line.strip()
                            if '=' in line:
                                parts = line.split('=', 1)
                                if len(parts) == 2:
                                    cookies[parts[0].strip()] = parts[1].strip()
                        filtered_cookies = filter_terabox_cookies(cookies)
                        processed_cookie = format_cookie_string(filtered_cookies)
                    else:
                        processed_cookie = cookie_input.strip()
                    
                    # Show parsed cookie info
                    if processed_cookie != cookie_input.strip():
                        st.info(f"🔄 Parsed cookie: `{processed_cookie[:100]}{'...' if len(processed_cookie) > 100 else ''}`")
                    
                    api = TeraBoxCookieAPI(processed_cookie)
                    validation_result = api.validate_cookie()
                
                if validation_result['status'] == 'success':
                    st.session_state.cookie_api = api
                    st.session_state.cookie_validated = True
                    st.session_state.current_cookie = processed_cookie
                    st.session_state.raw_cookie_input = cookie_input.strip()
                    st.success("✅ Cookie is valid!")
                    st.rerun()
                elif validation_result['status'] == 'warning':
                    st.session_state.cookie_api = api
                    st.session_state.current_cookie = processed_cookie
                    st.session_state.raw_cookie_input = cookie_input.strip()
                    st.warning(f"⚠️ {validation_result['message']}")
                    
                    # Show additional info for warnings
                    if 'suggestion' in validation_result:
                        st.info(f"💡 Suggestion: {validation_result['suggestion']}")
                else:
                    st.error(f"❌ {validation_result['message']}")
                    
                    # Show troubleshooting tips for connection errors
                    if 'Connection' in validation_result['message'] or 'ConnectionError' in validation_result['message']:
                        show_connection_troubleshooting()
                    elif 'suggestion' in validation_result:
                        st.info(f"💡 {validation_result['suggestion']}")
            else:
                st.error("Please enter a cookie string")
    
    with col_b:
        if st.button("🗑️ Clear Cookie"):
            st.session_state.cookie_api = None
            st.session_state.cookie_validated = False
            st.session_state.current_cookie = ""
            st.session_state.raw_cookie_input = ""
            st.success("Cookie cleared!")
            st.rerun()

with col2:
    if st.session_state.cookie_api:
        st.success("🍪 **Cookie Status: Active**")
        
        # Show cookie info
        cookie_info = st.session_state.cookie_api.get_cookie_info()
        
        if cookie_info['status'] == 'valid':
            st.success("✅ Valid Cookie")
        elif cookie_info['status'] == 'incomplete':
            st.warning("⚠️ Incomplete Cookie")
        else:
            st.error("❌ Invalid Cookie")
        
        with st.expander("🔍 Cookie Details"):
            st.json({
                "Status": cookie_info['status'],
                "Components": cookie_info.get('components', []),
                "Has NDUS": cookie_info.get('has_ndus', False),
                "Has BDUSS": cookie_info.get('has_bduss', False),
                "Cookie Length": cookie_info.get('cookie_length', 0)
            })
    else:
        st.warning("🍪 **Cookie Status: Not Set**")
        st.caption("Enter and validate your cookie above")

# File Processing Section
if st.session_state.cookie_api and st.session_state.cookie_validated:
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
    
    tab1, tab2, tab3 = st.tabs(["🔗 Single File", "📋 Multiple Files", "🧪 Test & Debug"])
    
    with tab1:
        st.subheader("🔗 Single File Download")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            terabox_url = st.text_input(
                "TeraBox File URL:",
                placeholder="https://www.terabox.com/s/your_link_here",
                help="Paste a TeraBox share link"
            )
        
        with col2:
            if st.button("📊 Get File Info", type="primary"):
                if terabox_url:
                    with st.spinner("Getting file information..."):
                        file_info = st.session_state.cookie_api.get_file_info(terabox_url)
                    
                    if 'error' in file_info:
                        st.error(f"❌ Error: {file_info['error']}")
                    else:
                        st.success("✅ File information retrieved!")
                        
                        # Store in session state for download
                        st.session_state.current_file_info = file_info
                        
                        # Display file info
                        col_a, col_b = st.columns(2)
                        
                        with col_a:
                            st.metric("File Name", file_info.get('file_name', 'Unknown'))
                            st.metric("File Size", file_info.get('file_size', 'Unknown'))
                            st.metric("File Type", file_info.get('file_type', 'Unknown'))
                        
                        with col_b:
                            if file_info.get('thumbnail'):
                                try:
                                    st.image(file_info['thumbnail'], caption="Thumbnail", width=150)
                                except:
                                    st.caption("Thumbnail not available")
                            
                            if file_info.get('download_link'):
                                st.success("✅ Download link available")
                            else:
                                st.warning("⚠️ No download link")
                        
                        # Download section
                        if file_info.get('download_link'):
                            st.markdown("---")
                            st.subheader("📥 Download Options")
                            
                            col_x, col_y = st.columns(2)
                            
                            with col_x:
                                save_path = st.text_input("Save Directory:", value="download/")
                            
                            with col_y:
                                if st.button("📥 Download File"):
                                    download_file_with_progress(file_info, save_path)
                            
                            # Direct download link
                            st.text_input("Direct Download URL:", value=file_info['download_link'])
                            
                            # Open Direct File Link button
                            col_open, col_space = st.columns([2, 1])
                            with col_open:
                                if st.button("📥 Open Direct File Link", key="cookie_open_direct_link"):
                                    preferred_browser = st.session_state.get('preferred_browser', None)
                                    
                                    with st.spinner("🌐 Opening direct file link in browser..."):
                                        result = open_direct_file_link(file_info, browser=preferred_browser)
                                    
                                    # Display result
                                    display_browser_open_result(result, show_details=True)
                                    
                                    if result['status'] == 'success':
                                        st.balloons()  # Celebrate success!
                else:
                    st.error("Please enter a TeraBox URL")
    
    with tab2:
        st.subheader("📋 Multiple Files Processing")
        
        urls_input = st.text_area(
            "Enter multiple TeraBox URLs (one per line):",
            height=150,
            placeholder="https://www.terabox.com/s/link1\nhttps://www.terabox.com/s/link2\nhttps://www.terabox.com/s/link3"
        )
        
        if st.button("📊 Process All Files", type="primary"):
            if urls_input.strip():
                urls = [url.strip() for url in urls_input.strip().split('\n') if url.strip()]
                
                if urls:
                    with st.spinner(f"Processing {len(urls)} files..."):
                        results = st.session_state.cookie_api.get_multiple_files_info(urls)
                    
                    st.success(f"✅ Processed {len(results)} files!")
                    
                    # Display results
                    for i, result in enumerate(results):
                        with st.expander(f"📄 File {i+1}: {result.get('file_name', 'Unknown')}"):
                            
                            if 'error' in result:
                                st.error(f"❌ Error: {result['error']}")
                            else:
                                col_a, col_b = st.columns(2)
                                
                                with col_a:
                                    st.text(f"Name: {result.get('file_name', 'Unknown')}")
                                    st.text(f"Size: {result.get('file_size', 'Unknown')}")
                                    st.text(f"Type: {result.get('file_type', 'Unknown')}")
                                
                                with col_b:
                                    if result.get('download_link'):
                                        st.text_input("Download URL:", value=result['download_link'], key=f"url_{i}")
                                        
                                        col_dl, col_open = st.columns(2)
                                        with col_dl:
                                            if st.button(f"📥 Download", key=f"dl_{i}"):
                                                download_file_with_progress(result, "download/")
                                        
                                        with col_open:
                                            if st.button(f"🌐 Open Link", key=f"cookie_open_{i}"):
                                                preferred_browser = st.session_state.get('preferred_browser', None)
                                                with st.spinner("🌐 Opening link..."):
                                                    open_result = open_direct_file_link(result, browser=preferred_browser)
                                                display_browser_open_result(open_result, show_details=False)
                                                if open_result['status'] == 'success':
                                                    st.balloons()
                                    else:
                                        st.warning("No download link available")
                else:
                    st.error("No valid URLs found")
            else:
                st.error("Please enter at least one URL")
    
    with tab3:
        st.subheader("🧪 Test & Debug")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Cookie Testing:**")
            
            if st.button("🔍 Test Cookie Validation"):
                with st.spinner("Testing cookie..."):
                    validation = st.session_state.cookie_api.validate_cookie()
                st.json(validation)
            
            if st.button("📊 Get Cookie Information"):
                cookie_info = st.session_state.cookie_api.get_cookie_info()
                st.json(cookie_info)
        
        with col2:
            st.markdown("**Download Testing:**")
            
            test_url = st.text_input("Test URL:", placeholder="https://www.terabox.com/s/test_link")
            
            if st.button("🧪 Test Download Capability"):
                if test_url:
                    with st.spinner("Testing download capability..."):
                        test_result = st.session_state.cookie_api.test_download_capability(test_url)
                    st.json(test_result)
                else:
                    st.error("Please enter a test URL")
        
        # Debug information
        with st.expander("🔍 Debug Information"):
            debug_info = {
                "Cookie API Initialized": st.session_state.cookie_api is not None,
                "Cookie Validated": st.session_state.cookie_validated,
                "Current Cookie Length": len(st.session_state.current_cookie),
                "Session State Keys": list(st.session_state.keys())
            }
            st.json(debug_info)

else:
    # Show getting started section
    st.header("🚀 Getting Started with Cookie Mode")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### ✅ Advantages:
        - **No API Registration** - Just use your existing account
        - **Reliable Downloads** - Direct access to files
        - **File Metadata** - Get names, sizes, thumbnails
        - **Progress Tracking** - Built-in download progress
        - **Multiple Files** - Process multiple links at once
        - **Simple Setup** - Just copy-paste your cookie
        """)
    
    with col2:
        st.markdown("""
        ### ⚠️ Considerations:
        - **Cookie Required** - Must extract from browser
        - **Session Dependent** - Cookie expires with session
        - **Account Access** - Uses your personal account
        - **Rate Limiting** - TeraBox may limit requests
        - **Browser Dependent** - Different browsers, different steps
        - **Privacy** - Cookie contains account information
        """)
    
    # Sample cookie format
    st.subheader("📝 Cookie Format Example")
    st.code("""
    ndus=your_ndus_value_here; BDUSS=your_bduss_value; STOKEN=your_stoken; 
    lang=en; csrfToken=your_csrf_token; other_cookies=values;
    """)
    
    st.info("💡 **Tip:** The most important cookies are `ndus`, `BDUSS`, and `STOKEN`. Make sure your cookie string includes these.")

# Footer
st.markdown("---")
st.info("""
💡 **Cookie Mode Tips:**
- Keep your cookie private and secure
- Cookies expire when you log out of TeraBox
- If downloads fail, try getting a fresh cookie
- This mode works similarly to the popular terabox-downloader PyPI package
- For business use, consider the Official API mode instead
""")

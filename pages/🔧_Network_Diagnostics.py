import streamlit as st
import requests
import time
import socket
from urllib.parse import urlparse
from utils.terabox_core import TeraboxCore
import json

st.set_page_config(
    page_title="Network Diagnostics",
    page_icon="🔧",
    layout="wide"
)

st.title("🔧 Network Diagnostics & Connection Testing")
st.markdown("Diagnose connection issues and test TeraBox extraction with detailed logging.")

# Test URLs
TEST_URLS = {
    "Sample 1": "https://1024terabox.com/s/1eBHBOzcEI-VpUGA_xIcGQg",
    "Sample 2": "https://1024terabox.com/s/1bEQ7FfUlCoeVXeDr6BTBxQ", 
    "Sample 3": "https://terasharelink.com/s/1QHHiN_C2wyDbckF_V3ssIw"
}

# Network diagnostics section
st.header("🌐 Network Connectivity Tests")

col1, col2 = st.columns(2)

with col1:
    st.subheader("DNS Resolution Test")
    if st.button("Test DNS Resolution"):
        domains = [
            "1024terabox.com",
            "terabox.com", 
            "www.terabox.com",
            "terabox.hnn.workers.dev"
        ]
        
        dns_results = {}
        for domain in domains:
            try:
                start_time = time.time()
                ip = socket.gethostbyname(domain)
                resolve_time = (time.time() - start_time) * 1000
                dns_results[domain] = {"ip": ip, "time": f"{resolve_time:.2f}ms", "status": "✅"}
            except socket.gaierror as e:
                dns_results[domain] = {"ip": "N/A", "time": "N/A", "status": f"❌ {e}"}
        
        for domain, result in dns_results.items():
            st.text(f"{result['status']} {domain}: {result['ip']} ({result['time']})")

with col2:
    st.subheader("HTTP Connectivity Test")
    if st.button("Test HTTP Connections"):
        test_urls = [
            "https://1024terabox.com",
            "https://www.terabox.com",
            "https://terabox.hnn.workers.dev"
        ]
        
        for url in test_urls:
            try:
                start_time = time.time()
                response = requests.get(url, timeout=10, allow_redirects=True)
                response_time = (time.time() - start_time) * 1000
                st.success(f"✅ {url}: {response.status_code} ({response_time:.0f}ms)")
            except requests.exceptions.RequestException as e:
                st.error(f"❌ {url}: {str(e)}")

# Connection test with different configurations
st.header("🔗 Connection Configuration Testing")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Standard Requests")
    if st.button("Test Standard Connection"):
        url = "https://1024terabox.com/s/1eBHBOzcEI-VpUGA_xIcGQg"
        try:
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            start_time = time.time()
            response = session.get(url, timeout=15, allow_redirects=True)
            duration = time.time() - start_time
            
            st.success(f"✅ Status: {response.status_code}")
            st.info(f"⏱️ Time: {duration:.2f}s")
            st.info(f"📍 Final URL: {response.url}")
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

with col2:
    st.subheader("Enhanced Headers")
    if st.button("Test Enhanced Headers"):
        url = "https://1024terabox.com/s/1eBHBOzcEI-VpUGA_xIcGQg"
        try:
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            })
            
            start_time = time.time()
            response = session.get(url, timeout=15, allow_redirects=True)
            duration = time.time() - start_time
            
            st.success(f"✅ Status: {response.status_code}")
            st.info(f"⏱️ Time: {duration:.2f}s")
            st.info(f"📍 Final URL: {response.url}")
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

with col3:
    st.subheader("CloudScraper")
    if st.button("Test CloudScraper"):
        url = "https://1024terabox.com/s/1eBHBOzcEI-VpUGA_xIcGQg"
        try:
            import cloudscraper
            scraper = cloudscraper.create_scraper()
            
            start_time = time.time()
            response = scraper.get(url, timeout=15, allow_redirects=True)
            duration = time.time() - start_time
            
            st.success(f"✅ Status: {response.status_code}")
            st.info(f"⏱️ Time: {duration:.2f}s")
            st.info(f"📍 Final URL: {response.url}")
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# TeraBox extraction testing
st.header("📦 TeraBox Extraction Testing")

col1, col2 = st.columns([2, 1])

with col1:
    test_url = st.selectbox("Select test URL:", options=list(TEST_URLS.keys()))
    selected_url = TEST_URLS[test_url]
    st.text_input("URL:", value=selected_url, disabled=True)

with col2:
    test_mode = st.selectbox("Test Mode:", options=[1, 2, 3], index=2)
    st.info(f"Using Mode {test_mode}")

if st.button("🧪 Run Extraction Test", type="primary"):
    st.subheader("Test Results")
    
    # Create progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Initialize TeraBox core
        status_text.text("🔧 Initializing TeraBox core...")
        progress_bar.progress(20)
        
        terabox = TeraboxCore(mode=test_mode)
        
        # Start extraction
        status_text.text("🔍 Extracting files...")
        progress_bar.progress(40)
        
        start_time = time.time()
        result = terabox.extract_files(selected_url)
        duration = time.time() - start_time
        
        progress_bar.progress(100)
        status_text.text("✅ Extraction completed!")
        
        # Display results
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Status", result.get('status', 'unknown'))
        
        with col2:
            st.metric("Duration", f"{duration:.2f}s")
        
        with col3:
            files_count = len(result.get('list', []))
            st.metric("Files Found", files_count)
        
        # Detailed results
        if result.get('status') == 'success':
            st.success("🎉 Extraction successful!")
            
            with st.expander("📊 Extraction Details"):
                details = {
                    "Mode": test_mode,
                    "URL": selected_url,
                    "ShareID": result.get('shareid'),
                    "UK": result.get('uk'),
                    "Sign": result.get('sign', 'N/A')[:20] + "..." if result.get('sign') else 'N/A',
                    "Timestamp": result.get('timestamp')
                }
                
                for key, value in details.items():
                    st.text(f"{key}: {value}")
            
            # File list
            files = result.get('list', [])
            if files:
                st.subheader(f"📁 Found {len(files)} file(s)")
                
                for i, file_info in enumerate(files[:5]):  # Show first 5 files
                    with st.expander(f"📄 {file_info.get('name', 'Unknown')}"):
                        file_details = {
                            "Type": file_info.get('type', 'unknown'),
                            "Size": f"{int(file_info.get('size', 0)) / (1024*1024):.1f} MB" if file_info.get('size') else 'Unknown',
                            "FS ID": file_info.get('fs_id'),
                            "Is Directory": "Yes" if file_info.get('is_dir') else "No"
                        }
                        
                        for key, value in file_details.items():
                            st.text(f"{key}: {value}")
                
                if len(files) > 5:
                    st.info(f"... and {len(files) - 5} more files")
        
        else:
            st.error("❌ Extraction failed!")
            error_msg = result.get('message', 'Unknown error')
            st.error(f"Error: {error_msg}")
        
        # Raw response
        with st.expander("🔍 Raw Response Data"):
            st.json(result)
            
    except Exception as e:
        progress_bar.progress(100)
        status_text.text("❌ Test failed!")
        st.error(f"Test failed with error: {str(e)}")
        
        # Show traceback for debugging
        import traceback
        with st.expander("🐛 Error Traceback"):
            st.code(traceback.format_exc())

# System information
st.header("💻 System Information")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Python Environment")
    import sys
    import platform
    
    sys_info = {
        "Python Version": sys.version,
        "Platform": platform.platform(),
        "Architecture": platform.architecture()[0],
        "Processor": platform.processor() or "Unknown"
    }
    
    for key, value in sys_info.items():
        st.text(f"{key}: {value}")

with col2:
    st.subheader("Network Modules")
    
    modules = ['requests', 'urllib3', 'cloudscraper', 'socket', 'ssl']
    
    for module in modules:
        try:
            mod = __import__(module)
            version = getattr(mod, '__version__', 'Unknown')
            st.success(f"✅ {module}: {version}")
        except ImportError:
            st.error(f"❌ {module}: Not available")

# Connection tips
st.header("💡 Connection Troubleshooting Tips")

tips = [
    "**Use Mode 3** - It's the most stable and uses external services",
    "**Check your internet connection** - Ensure stable connectivity",
    "**Try different URLs** - Some TeraBox links may be expired or invalid",
    "**Wait between attempts** - Avoid rapid successive requests",
    "**Check firewall/antivirus** - They might block the connections",
    "**Use VPN if needed** - Some regions might have restrictions",
    "**Update dependencies** - Ensure you have the latest versions"
]

for i, tip in enumerate(tips, 1):
    st.markdown(f"{i}. {tip}")

# Advanced diagnostics
with st.expander("🔬 Advanced Diagnostics"):
    st.markdown("""
    **Common Error Codes:**
    - `ConnectionResetError(10054)`: Remote host closed connection
    - `TimeoutError`: Request took too long
    - `ConnectionError`: Network connectivity issue
    - `HTTPError 403`: Access forbidden (possible bot detection)
    - `HTTPError 429`: Rate limited (too many requests)
    
    **Solutions:**
    - Use different user agents and headers
    - Implement retry logic with delays
    - Use proxy or VPN services
    - Switch between different processing modes
    """)

st.markdown("---")
st.markdown("*Use this page to diagnose and troubleshoot connection issues with TeraBox extraction.*")

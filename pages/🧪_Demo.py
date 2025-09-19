import streamlit as st
from terabox_core import TeraboxCore
import json

st.set_page_config(
    page_title="TeraDL Demo",
    page_icon="🧪",
    layout="wide"
)

st.title("🧪 TeraDL Demo & Testing")
st.markdown("Test the TeraBox extraction functionality with sample URLs and different modes.")

# Sample URLs for testing
SAMPLE_URLS = {
    "Sample Video Collection": "https://1024terabox.com/s/1eBHBOzcEI-VpUGA_xIcGQg",
    "Mixed Files": "https://terasharelink.com/s/1QHHiN_C2wyDbckF_V3ssIw",
    "Archive Files": "https://www.terabox.com/wap/share/filelist?surl=cmi8P-_NCAHAzxj7MtzZAw"
}

# Demo section
st.header("📋 Sample TeraBox URLs")
st.info("These are example URLs from the original TeraDL documentation for testing purposes.")

col1, col2 = st.columns([2, 1])

with col1:
    selected_sample = st.selectbox(
        "Choose a sample URL:",
        options=list(SAMPLE_URLS.keys()),
        help="Select a sample URL to test the extraction functionality"
    )
    
    sample_url = SAMPLE_URLS[selected_sample]
    st.text_input("Sample URL:", value=sample_url, disabled=True)

with col2:
    st.markdown("**URL Description:**")
    descriptions = {
        "Sample Video Collection": "Collection of video files for testing video streaming",
        "Mixed Files": "Mixed collection of videos and images",
        "Archive Files": "Archive and document files for download testing"
    }
    st.write(descriptions[selected_sample])

# Testing section
st.header("🔧 Mode Testing")
st.markdown("Test different extraction modes to see which works best for your use case.")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Mode 1: Dynamic")
    st.markdown("""
    - Real-time cookie scraping
    - Most reliable but slower
    - Good for development
    """)
    if st.button("Test Mode 1", key="test_mode1"):
        with st.spinner("Testing Mode 1..."):
            terabox = TeraboxCore(mode=1)
            result = terabox.extract_files(sample_url)
            st.json(result, expanded=False)

with col2:
    st.subheader("Mode 2: Static")
    st.markdown("""
    - Pre-configured cookies
    - Faster processing
    - Requires valid session
    """)
    if st.button("Test Mode 2", key="test_mode2"):
        with st.spinner("Testing Mode 2..."):
            terabox = TeraboxCore(mode=2)
            result = terabox.extract_files(sample_url)
            st.json(result, expanded=False)

with col3:
    st.subheader("Mode 3: External")
    st.markdown("""
    - External service integration
    - Most stable (recommended)
    - Multiple download options
    """)
    if st.button("Test Mode 3", key="test_mode3"):
        with st.spinner("Testing Mode 3..."):
            terabox = TeraboxCore(mode=3)
            result = terabox.extract_files(sample_url)
            st.json(result, expanded=False)

# Custom URL testing
st.header("🔗 Custom URL Testing")
st.markdown("Test your own TeraBox URLs here.")

custom_url = st.text_input(
    "Enter your TeraBox URL:",
    placeholder="https://terabox.com/s/...",
    help="Paste any valid TeraBox share link"
)

test_mode = st.selectbox(
    "Select test mode:",
    options=[1, 2, 3],
    index=2,
    help="Choose which mode to use for testing"
)

if st.button("🧪 Test Custom URL", type="primary"):
    if custom_url:
        # Validate URL
        supported_domains = ['terabox', '1024terabox', 'freeterabox', 'nephobox', 'terasharelink']
        if not any(domain in custom_url.lower() for domain in supported_domains):
            st.error("❌ Please enter a valid TeraBox URL")
        else:
            with st.spinner(f"Testing custom URL with Mode {test_mode}..."):
                try:
                    terabox = TeraboxCore(mode=test_mode)
                    result = terabox.extract_files(custom_url)
                    
                    if result.get('status') == 'success':
                        st.success("✅ Extraction successful!")
                        
                        # Display summary
                        files = result.get('list', [])
                        total_files = len([f for f in files if f.get('is_dir') == 0])
                        st.metric("Files Found", total_files)
                        
                        # Show detailed results
                        with st.expander("📊 Detailed Results", expanded=False):
                            st.json(result)
                    else:
                        st.error(f"❌ Extraction failed: {result.get('message', 'Unknown error')}")
                        with st.expander("🔍 Error Details"):
                            st.json(result)
                            
                except Exception as e:
                    st.error(f"❌ Test failed: {str(e)}")
    else:
        st.warning("⚠️ Please enter a URL to test")

# Performance comparison
st.header("⚡ Performance Comparison")
st.markdown("Compare the performance of different modes side by side.")

if st.button("🏃‍♂️ Run Performance Test"):
    if sample_url:
        results = {}
        
        # Test all three modes
        for mode in [1, 2, 3]:
            with st.spinner(f"Testing Mode {mode}..."):
                try:
                    import time
                    start_time = time.time()
                    
                    terabox = TeraboxCore(mode=mode)
                    result = terabox.extract_files(sample_url)
                    
                    end_time = time.time()
                    duration = end_time - start_time
                    
                    results[f"Mode {mode}"] = {
                        "duration": f"{duration:.2f}s",
                        "status": result.get('status', 'failed'),
                        "files_found": len(result.get('list', [])) if result.get('status') == 'success' else 0
                    }
                    
                except Exception as e:
                    results[f"Mode {mode}"] = {
                        "duration": "Error",
                        "status": "failed",
                        "files_found": 0,
                        "error": str(e)
                    }
        
        # Display results
        st.subheader("📊 Performance Results")
        
        col1, col2, col3 = st.columns(3)
        
        for i, (mode, data) in enumerate(results.items()):
            col = [col1, col2, col3][i]
            
            with col:
                st.metric(
                    label=mode,
                    value=data["duration"],
                    delta=f"{data['files_found']} files" if data["status"] == "success" else "Failed"
                )
                
                if data["status"] == "success":
                    st.success("✅ Success")
                else:
                    st.error("❌ Failed")
                    if "error" in data:
                        st.caption(data["error"][:50] + "...")

# Debug information
with st.expander("🔍 Debug Information"):
    st.markdown("**System Information:**")
    import sys
    import platform
    
    debug_info = {
        "Python Version": sys.version,
        "Platform": platform.platform(),
        "Streamlit Version": st.__version__,
    }
    
    for key, value in debug_info.items():
        st.text(f"{key}: {value}")
    
    st.markdown("**Available Modules:**")
    try:
        import requests
        st.text(f"requests: {requests.__version__}")
    except ImportError:
        st.text("requests: Not available")
    
    try:
        import cloudscraper
        st.text("cloudscraper: Available")
    except ImportError:
        st.text("cloudscraper: Not available")

# Footer
st.markdown("---")
st.markdown("*This demo page helps test and debug the TeraDL functionality. Use it to verify that the extraction is working correctly before using the main application.*")

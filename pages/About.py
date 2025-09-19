import streamlit as st
import datetime

st.set_page_config(
    page_title="About TeraDL",
    page_icon="ℹ️",
    layout="wide"
)

# Header
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
    <div style="text-align: center;">
        <h1 style="color: #586afa; font-size: 3rem; margin-bottom: 0;">TeraDL</h1>
        <p style="color: #212f99; font-size: 1.2rem; margin-top: 0;">TeraBox Video Downloader & Streaming Platform</p>
        <p style="color: #666; font-size: 1rem;">Streamlit Edition</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# About section
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📖 About TeraDL")
    st.markdown("""
    **TeraDL** is a modern web application built with Streamlit that allows you to download and stream files from TeraBox share links. This is a Python-based reimplementation of the original TeraDL project with enhanced features and a user-friendly interface.
    
    ### 🎯 Purpose
    TeraDL was created to provide an easy-to-use interface for accessing TeraBox files without requiring users to install the TeraBox application. Simply paste a share link, and you can download or stream the content directly through your web browser.
    
    ### ✨ Key Features
    - **Multi-mode Processing**: Three different extraction modes for maximum compatibility
    - **Direct Downloads**: Download files directly through the web interface
    - **Video Streaming**: Stream videos directly in your browser
    - **Folder Navigation**: Browse through nested folders and directories
    - **File Management**: Filter, sort, and organize files by type, name, or size
    - **Modern UI**: Clean, responsive interface built with Streamlit
    - **Cross-platform**: Works on Windows, macOS, and Linux
    """)

with col2:
    st.header("📊 Features")
    
    # Feature metrics
    features = [
        ("🔍", "Processing Modes", "3"),
        ("📁", "File Types Supported", "10+"),
        ("🎥", "Video Streaming", "Yes"),
        ("📱", "Mobile Friendly", "Yes"),
        ("🔧", "Open Source", "Yes")
    ]
    
    for emoji, feature, value in features:
        st.metric(
            label=f"{emoji} {feature}",
            value=value
        )

# Technical details
st.header("🛠️ Technical Information")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("🏗️ Built With")
    st.markdown("""
    - **Python 3.8+**
    - **Streamlit** - Web framework
    - **Requests** - HTTP library
    - **CloudScraper** - Anti-bot bypass
    - **Modern CSS** - Responsive design
    """)

with col2:
    st.subheader("🔧 Processing Modes")
    st.markdown("""
    **Mode 1: Dynamic Cookies**
    - Real-time web scraping
    - Most reliable method
    - Slower but thorough
    
    **Mode 2: Static Cookies**
    - Pre-configured sessions
    - Faster processing
    - Requires maintenance
    
    **Mode 3: External Service**
    - Third-party integration
    - Most stable (recommended)
    - Multiple download options
    """)

with col3:
    st.subheader("📋 Supported Platforms")
    st.markdown("""
    **TeraBox Domains:**
    - terabox.com
    - 1024terabox.com
    - freeterabox.com
    - nephobox.com
    - terasharelink.com
    
    **File Types:**
    - Videos (MP4, AVI, MKV, etc.)
    - Images (JPG, PNG, GIF, etc.)
    - Documents (PDF, DOCX, etc.)
    - Archives (ZIP, RAR, 7Z, etc.)
    """)

# Version information
st.header("📋 Version Information")

col1, col2 = st.columns(2)

with col1:
    version_info = {
        "TeraDL Streamlit Version": "1.0.0",
        "Based on TeraDL": "v1.5.5",
        "Python Version Required": "3.8+",
        "Last Updated": datetime.datetime.now().strftime("%Y-%m-%d"),
        "License": "Educational Use"
    }
    
    for key, value in version_info.items():
        st.text(f"{key}: {value}")

with col2:
    st.subheader("📈 Changelog")
    st.markdown("""
    **Version 1.0.0 (Current)**
    - ✅ Initial Streamlit implementation
    - ✅ Three processing modes
    - ✅ Video streaming support
    - ✅ Modern responsive UI
    - ✅ File filtering and sorting
    - ✅ Error handling and logging
    - ✅ Demo and testing pages
    """)

# Credits and acknowledgments
st.header("🙏 Credits & Acknowledgments")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Original Project")
    st.markdown("""
    This Streamlit version is based on the original **TeraDL** project:
    
    - **Author**: Dapunta Khurayra X
    - **Original Version**: 1.5.5
    - **Technology**: Flask + HTML/CSS/JavaScript
    - **GitHub**: [Original TeraDL Repository](https://github.com/Dapunta/TeraDL)
    """)

with col2:
    st.subheader("Streamlit Implementation")
    st.markdown("""
    Streamlit adaptation features:
    
    - **Framework**: Streamlit for Python
    - **Enhanced UI**: Modern, responsive design
    - **Better UX**: Improved user experience
    - **Error Handling**: Comprehensive error management
    - **Documentation**: Detailed guides and help
    """)

# Disclaimer
st.header("⚠️ Important Disclaimer")

st.warning("""
**Legal and Ethical Use Only**

This tool is provided for educational and personal use only. Users are responsible for:

- ✅ Only downloading content they have permission to access
- ✅ Respecting TeraBox's terms of service
- ✅ Not abusing the service or overloading servers
- ✅ Using the tool responsibly and ethically

The developers are not responsible for any misuse of this tool or any legal consequences that may arise from its use.
""")

# Support and contact
st.header("🆘 Support & Contact")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Getting Help")
    st.markdown("""
    If you encounter issues:
    
    1. **Check the Demo page** - Test different modes
    2. **Review the logs** - Check `teradl.log` file
    3. **Try different URLs** - Some links may be expired
    4. **Switch modes** - Different modes work better for different links
    5. **Check your connection** - Ensure stable internet
    """)

with col2:
    st.subheader("Troubleshooting")
    st.markdown("""
    Common solutions:
    
    - **URL not working**: Try Mode 3 (recommended)
    - **Download fails**: Check file size limits
    - **Streaming issues**: Try downloading instead
    - **Connection errors**: Check internet stability
    - **Module errors**: Reinstall requirements
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p>Made with ❤️ using Streamlit</p>
    <p>Based on the original TeraDL project by Dapunta Khurayra X</p>
    <p style="font-size: 0.8rem;">For educational and personal use only • Please respect TeraBox's terms of service</p>
</div>
""", unsafe_allow_html=True)

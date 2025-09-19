# TeraDL - Streamlit TeraBox Downloader

A modern Streamlit web application for downloading and streaming files from TeraBox links. This is a Python-based implementation of the original TeraDL project with enhanced features and user interface.

![TeraDL Logo](https://img.shields.io/badge/TeraDL-Streamlit-blue?style=for-the-badge&logo=streamlit)

## 🌟 Features

- **🔍 Smart File Extraction**: Extract files from TeraBox URLs with 3 different processing modes
- **📥 Direct Downloads**: Download files directly through the web interface
- **🎥 Video Streaming**: Stream videos directly in the browser
- **📁 Folder Support**: Navigate through nested folders and directories
- **🔧 Multiple Processing Modes**:
  - Mode 1: Dynamic cookies (real-time scraping)
  - Mode 2: Static cookies (admin session)
  - Mode 3: External service integration (recommended)
- **🎨 Modern UI**: Clean, responsive Streamlit interface
- **🔍 File Management**: Filter and sort files by type, name, or size
- **⚡ Fast Performance**: Optimized for speed and reliability

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone or download the project files:**

   ```bash
   # If you have git
   git clone <repository-url>
   cd teradl-streamlit
   
   # Or download and extract the files manually
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**

   ```bash
   streamlit run app.py
   ```

4. **Open your browser:**
   - The app will automatically open at `http://localhost:8501`
   - If it doesn't open automatically, navigate to the URL manually

## 📖 How to Use

### Step 1: Enter TeraBox URL

1. Open the application in your browser
2. In the sidebar, paste your TeraBox share link
3. Supported domains:
   - terabox.com
   - 1024terabox.com
   - freeterabox.com
   - nephobox.com
   - terasharelink.com

### Step 2: Select Processing Mode

Choose from three processing modes:

- **Mode 1**: Dynamic cookies with real-time scraping
- **Mode 2**: Static cookies from admin session  
- **Mode 3**: External service integration (recommended)

### Step 3: Extract Files

Click the "🔍 Extract Files" button to analyze the TeraBox link and retrieve the file list.

### Step 4: Download or Stream

- **Download**: Click the "📥 Download" button next to any file
- **Stream Videos**: Click the "▶️ Stream" button for video files
- **Filter**: Use the filter options to find specific file types
- **Sort**: Sort files by name, size, or type

## 🛠️ Technical Details

### File Structure

```
teradl-streamlit/
├── app.py              # Main Streamlit application
├── terabox_core.py     # Core TeraBox processing logic
├── config.py           # Configuration and error handling
├── requirements.txt    # Python dependencies
├── README_STREAMLIT.md # This file
└── teradl.log         # Application logs (created at runtime)
```

### Processing Modes Explained

**Mode 1: Dynamic Cookies**

- Uses real-time web scraping to obtain authentication cookies
- Most reliable but slower
- Good for testing and development

**Mode 2: Static Cookies**

- Uses pre-configured admin session cookies
- Faster but requires valid session cookies
- Best for production with maintained sessions

**Mode 3: External Service (Recommended)**

- Uses external service (terabox.hnn.workers.dev) for processing
- Most stable and feature-complete
- Includes multiple download URL options

### Supported File Types

- **Videos**: .mp4, .mov, .m4v, .mkv, .asf, .avi, .wmv, .m2ts, .3g2
- **Images**: .jpg, .jpeg, .png, .gif, .webp, .svg
- **Documents**: .pdf, .docx, .zip, .rar, .7z
- **Other**: All other file types

## 🔧 Configuration

### Environment Variables

You can customize the application by setting these environment variables:

```bash
# Maximum file size for downloads (in MB)
export TERADL_MAX_FILE_SIZE=500

# Request timeout (in seconds)
export TERADL_TIMEOUT=30

# Maximum retries for failed requests
export TERADL_MAX_RETRIES=3
```

### Logging

The application creates a `teradl.log` file for debugging and monitoring. Log levels can be adjusted in `config.py`.

## 🐛 Troubleshooting

### Common Issues

**1. "Invalid TeraBox URL" Error**

- Ensure the URL is from a supported TeraBox domain
- Check that the URL is complete and properly formatted
- Try copying the URL again from the source

**2. "Failed to extract files" Error**

- The TeraBox link might be expired or invalid
- Try switching to a different processing mode
- Check your internet connection

**3. "Download failed" Error**

- Try using a different download URL option
- Check if the file size exceeds limits
- Verify your internet connection stability

**4. Video streaming not working**

- Some video formats may not be supported by the browser
- Try downloading the video file instead
- Check if the video URL is accessible

### Getting Help

1. Check the application logs in `teradl.log`
2. Try different processing modes
3. Verify the TeraBox URL is valid and accessible
4. Ensure all dependencies are properly installed

## 📝 Development

### Adding New Features

1. Fork the project
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Code Structure

- `app.py`: Main Streamlit UI and user interactions
- `terabox_core.py`: Core TeraBox API integration
- `config.py`: Configuration, error handling, and utilities

## ⚠️ Important Notes

- **Legal Usage**: Only use this tool for downloading content you have permission to access
- **Rate Limiting**: Be respectful of TeraBox servers and don't abuse the service
- **Privacy**: The application doesn't store or log your TeraBox URLs or downloaded files
- **Reliability**: External services may have downtime; try different modes if one fails

## 🔄 Updates and Maintenance

This Streamlit version is based on the original TeraDL project and includes:

- Enhanced error handling and logging
- Modern, responsive UI
- Better file management
- Improved reliability and performance

For the latest updates and features, check the original TeraDL project repository.

## 📄 License

This project is for educational and personal use only. Please respect TeraBox's terms of service and only download content you have permission to access.

---

**Made with ❤️ using Streamlit**

*Based on the original TeraDL project by Dapunta Khurayra X*

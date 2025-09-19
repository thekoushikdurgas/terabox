# TeraDL - Complete TeraBox Integration Guide

The ultimate TeraBox downloader with **three different access methods** - choose the one that best fits your needs!

![TeraDL Modes](https://img.shields.io/badge/Modes-3-blue?style=for-the-badge) ![Python](https://img.shields.io/badge/Python-3.8+-green?style=for-the-badge) ![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red?style=for-the-badge)

## 🎯 Three Ways to Access TeraBox

### 🎪 Unofficial Mode - Quick & Simple

- **No setup required** - works immediately
- **No account needed** - maximum privacy
- **Share links only** - perfect for occasional downloads
- **Free forever** - no costs or limits

### 🍪 Cookie Mode - Reliable & Fast  

- **Session-based** - uses your TeraBox login
- **Direct downloads** - reliable file access
- **Progress tracking** - advanced download features
- **Easy setup** - just copy browser cookie

### 🏢 Official API - Enterprise Grade

- **OAuth 2.0** - official authentication
- **Full features** - complete file management
- **Business ready** - enterprise support
- **API credentials** - requires registration

## 🚀 Quick Start

### Installation

```bash
# Clone or download the project
git clone <repository-url>
cd teradl

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

### First Time Usage

1. **Open your browser** - Navigate to `http://localhost:8501`
2. **Choose your mode** - Pick from Unofficial, Cookie, or Official API
3. **Configure if needed** - Some modes require setup
4. **Start downloading** - Paste TeraBox links and go!

## 📖 Detailed Mode Guide

### 🎪 Unofficial Mode

**Perfect for: Quick downloads, testing, maximum privacy**

#### How it Works

- Scrapes TeraBox share links directly
- Uses multiple extraction strategies
- No authentication required
- Works with public share links only

#### Setup

1. **No setup needed!** - Just select Unofficial Mode
2. **Choose processing mode** - Mode 3 recommended
3. **Paste TeraBox link** - Any public share link
4. **Download files** - Direct download or streaming

#### Features

- ✅ 3 different extraction modes
- ✅ User agent rotation
- ✅ Retry logic with exponential backoff
- ✅ Connection pooling
- ✅ Enhanced error handling
- ✅ Network diagnostics

#### Supported Links

```txt
https://www.terabox.com/s/1aBcDeFgHiJkL
https://1024terabox.com/s/1MnOpQrStUvWx
https://freeterabox.com/s/1YzAbCdEfGhIj
https://nephobox.com/s/1KlMnOpQrStUv
https://terasharelink.com/s/1WxYzAbCdEfGh
```

### 🍪 Cookie Mode

**Perfect for: Regular users, reliable downloads, personal projects:**

#### How it Works 1

- Uses your TeraBox session cookie
- Authenticated access to TeraBox APIs
- Direct download link generation
- Progress tracking with callbacks

#### Setup 1

1. **Login to TeraBox** - Use your browser
2. **Extract cookie** - Follow our detailed tutorial
3. **Configure TeraDL** - Paste cookie in Cookie Mode page
4. **Validate cookie** - Test authentication
5. **Start downloading** - Access any file you can see

#### Cookie Extraction Tutorial

**Chrome:**

```txt
1. Open TeraBox.com and login
2. Press F12 (Developer Tools)
3. Go to Application tab
4. Expand Cookies → https://www.terabox.com
5. Copy cookie values: ndus, BDUSS, STOKEN
6. Format: ndus=value1; BDUSS=value2; STOKEN=value3;
```

**Firefox:**

```txt
1. Open TeraBox.com and login
2. Press F12 (Developer Tools)  
3. Go to Storage tab
4. Expand Cookies → https://www.terabox.com
5. Copy important cookie values
6. Format as name1=value1; name2=value2;
```

**Alternative Method:**

```
1. Open Network tab in Developer Tools
2. Refresh TeraBox page
3. Click any request to terabox.com
4. Copy entire "Cookie" header value
```

#### Features

- ✅ Direct download links
- ✅ File metadata (name, size, thumbnail)
- ✅ Progress tracking with callbacks
- ✅ Multiple file processing
- ✅ Download capability testing
- ✅ Cookie validation
- ✅ Error handling and retries

#### Example Usage

```python
from terabox_cookie_api import TeraBoxCookieAPI

# Initialize with cookie
cookie = "ndus=your_value; BDUSS=another_value; STOKEN=token_value"
api = TeraBoxCookieAPI(cookie)

# Get file info
file_info = api.get_file_info("https://terabox.com/s/your_link")

# Download with progress
def progress_callback(downloaded, total, percentage):
    print(f"Progress: {percentage:.1f}%")

result = api.download(file_info, save_path="download/", callback=progress_callback)
```

### 🏢 Official API Mode

**Perfect for: Business applications, enterprise use, full-featured apps**

#### How it Works

- Official TeraBox Open Platform APIs
- OAuth 2.0 authentication (Authorization Code + Device Code flows)
- Complete REST API implementation
- Enterprise-grade security and reliability

#### Setup

1. **Apply for API access** - Contact TeraBox business team
2. **Get credentials** - Receive Client ID, Client Secret, Private Secret
3. **Configure TeraDL** - Enter credentials in API Mode page
4. **Authenticate** - Complete OAuth flow
5. **Full access** - Use all TeraBox features

#### API Credentials Application

```
Contact: TeraBox Business Team
Required Info:
- Application name
- Product logo  
- URL schemes (for mobile)
- Use case description
- Business contact information

You'll receive:
- Client ID (AppKey)
- Client Secret (SecretKey)
- Private Secret (for signatures)
```

#### Authentication Flows

**Authorization Code Flow:**

```
1. Redirect user to TeraBox authorization page
2. User logs in and grants permission
3. TeraBox redirects back with authorization code
4. Exchange code for access token
5. Use token for API calls
```

**Device Code Flow (QR Code):**

```
1. Generate device code and QR code
2. User scans QR with TeraBox mobile app
3. Poll for authorization status
4. Receive access token when authorized
5. Use token for API calls
```

#### Features

- ✅ Complete user account integration
- ✅ File management (upload, download, list, search)
- ✅ Share management (create, manage external links)
- ✅ Video streaming (M3U8 with multiple qualities)
- ✅ Storage quota monitoring
- ✅ Bulk file operations
- ✅ Token refresh automation
- ✅ Enterprise security

#### API Endpoints Used

```
Authentication:
- POST /oauth/gettoken
- POST /oauth/tokeninfo  
- POST /oauth/refreshtoken
- GET  /oauth/devicecode

User Management:
- GET /openapi/uinfo
- GET /openapi/api/quota
- GET /openapi/active

File Management:
- GET /openapi/api/list
- GET /openapi/api/filemetas
- GET /openapi/api/search
- GET /openapi/api/download
- GET /openapi/api/streaming

Share Management:
- POST /openapi/share/verify
- GET  /openapi/api/shorturlinfo
- GET  /openapi/share/list
- GET  /openapi/share/download
```

## 🔄 Mode Comparison

| Feature | 🎪 Unofficial | 🍪 Cookie | 🏢 Official API |
|---------|--------------|-----------|----------------|
| **Setup** | None | Cookie extraction | API registration |
| **Authentication** | None | Session cookie | OAuth 2.0 |
| **File Access** | Share links only | Account files | Complete access |
| **Reliability** | Variable | Good | Excellent |
| **Features** | Basic | Moderate | Complete |
| **Business Use** | Limited | Good | Excellent |
| **Cost** | Free | Free | May have costs |
| **Support** | Community | Community + docs | Official |

## 🛠️ Advanced Configuration

### Environment Variables

```bash
# General Settings
TERADL_API_MODE=cookie              # unofficial, cookie, official
TERADL_MAX_FILE_SIZE=1000           # MB
TERADL_ENABLE_STREAMING=true        # true/false
TERADL_ENABLE_DEBUG=false           # true/false

# Unofficial Mode
TERADL_DEFAULT_MODE=3               # 1, 2, or 3
TERADL_MAX_RETRIES=3                # retry attempts
TERADL_TIMEOUT=30                   # seconds

# Cookie Mode  
TERABOX_COOKIE="ndus=...; BDUSS=..." # your cookie string

# Official API
TERABOX_CLIENT_ID=your_client_id
TERABOX_CLIENT_SECRET=your_secret
TERABOX_PRIVATE_SECRET=your_private_secret
```

### Configuration File

```json
{
  "app": {
    "api_mode": "cookie",
    "max_file_size_mb": 1000,
    "enable_streaming": true
  },
  "unofficial": {
    "default_mode": 3,
    "max_retries": 3,
    "retry_delay": 1.0
  },
  "cookie": {
    "validate_on_startup": true,
    "auto_retry": true
  },
  "official": {
    "api_domain": "www.terabox.com",
    "default_stream_quality": "M3U8_AUTO_720"
  }
}
```

## 📱 User Interface Guide

### Main Application

- **Mode indicator** - Shows current active mode
- **Quick mode switching** - Easy mode changes
- **File extraction** - Unified interface for all modes
- **Download/streaming** - Consistent across modes
- **Progress tracking** - Real-time status updates

### Page Navigation

- **🏠 Home** - Main file extraction interface
- **🔑 API Mode** - Configure Official API and mode selection
- **🍪 Cookie Mode** - Cookie extraction and management
- **📁 File Manager** - Official API file management (when authenticated)
- **⚙️ Settings** - Application configuration
- **🔧 Network Diagnostics** - Connection testing and debugging
- **📊 Mode Comparison** - Detailed mode comparison
- **ℹ️ About** - Application information

### Features by Page

**Main App (🏠):**

- TeraBox URL input
- Mode-specific processing
- File listing with thumbnails
- Download buttons
- Video streaming
- Progress indicators

**Cookie Mode (🍪):**

- Cookie extraction tutorial
- Cookie validation
- Single/multiple file processing
- Download with progress
- Debug and testing tools

**File Manager (📁):**

- Directory browsing
- File search
- User account info
- Storage quota display
- Bulk operations
- Download link generation

**Settings (⚙️):**

- Mode-specific configurations
- Credential management
- Export/import settings
- Environment variable support
- Advanced options

## 🔧 Development Guide

### Project Structure

```
teradl/
├── app.py                          # Main Streamlit application
├── terabox_core.py                 # Unofficial scraping methods
├── terabox_official_api.py         # Official API integration
├── terabox_cookie_api.py           # Cookie-based access
├── terabox_config.py               # Configuration management
├── config.py                       # Base configuration and utilities
├── requirements.txt                # Python dependencies
├── pages/
│   ├── 🔑_API_Mode.py             # API mode selection
│   ├── 🍪_Cookie_Mode.py          # Cookie management
│   ├── 📁_File_Manager.py         # File management interface
│   ├── ⚙️_Settings.py             # Application settings
│   ├── 🔧_Network_Diagnostics.py  # Network testing
│   ├── 📊_Mode_Comparison.py      # Mode comparison
│   ├── 🧪_Demo.py                 # Demo and testing
│   └── ℹ️_About.py                # About page
└── docs/
    ├── README_OFFICIAL_API.md      # Official API guide
    ├── README_STREAMLIT.md         # Streamlit version guide
    └── README_COMPLETE_GUIDE.md    # This complete guide
```

### Key Classes

```python
# Unofficial scraping
TeraboxCore(mode=3)
- extract_files(url)
- generate_download_links(...)

# Cookie-based access  
TeraBoxCookieAPI(cookie)
- get_file_info(url)
- download(file_info, save_path, callback)

# Official API
TeraBoxOfficialAPI(client_id, client_secret, private_secret)
- exchange_code_for_token(code)
- list_files(directory)
- get_download_links(file_ids)
```

### Adding New Features

1. **Choose the right mode** - Consider which modes should support the feature
2. **Update core classes** - Add methods to appropriate API classes
3. **Update UI** - Add interface elements in relevant pages
4. **Add configuration** - Update settings if needed
5. **Update documentation** - Keep docs current
6. **Test all modes** - Ensure compatibility

## 🐛 Troubleshooting

### Common Issues

#### Unofficial Mode

```
Problem: "Connection reset" errors
Solution: 
- Switch to Mode 3
- Check Network Diagnostics page
- Try different user agents
- Wait and retry later

Problem: "No files found"
Solution:
- Verify TeraBox URL is valid
- Check if link is public
- Try different processing modes
- Check link expiration
```

#### Cookie Mode

```
Problem: "Invalid cookie" error
Solution:
- Get fresh cookie from browser
- Ensure you're logged into TeraBox
- Include all important cookies (ndus, BDUSS, STOKEN)
- Check cookie format

Problem: "Download failed"
Solution:
- Validate cookie first
- Check if you have access to the file
- Verify internet connection
- Try different file
```

#### Official API

```
Problem: "Authentication failed"
Solution:
- Verify API credentials are correct
- Check if credentials expired
- Ensure proper signature generation
- Try refreshing tokens

Problem: "Rate limit exceeded"
Solution:
- Wait before retrying
- Check API usage limits
- Contact TeraBox for limit increases
- Implement proper backoff
```

### Debug Mode

Enable debug mode in Settings to see:

- Detailed request/response logs
- API call traces
- Error stack traces
- Configuration details
- Session state information

### Network Diagnostics

Use the Network Diagnostics page to:

- Test DNS resolution
- Check HTTP connectivity
- Compare different connection methods
- Test TeraBox extraction
- View system information

## 📊 Performance Tips

### Unofficial Mode

- Use Mode 3 for best reliability
- Enable user agent rotation
- Set appropriate retry delays
- Monitor connection health

### Cookie Mode  

- Keep cookies fresh
- Use progress callbacks for large files
- Implement proper error handling
- Test cookie validity regularly

### Official API

- Cache token information
- Batch file operations
- Use appropriate page sizes
- Monitor API quotas

## 🔐 Security Considerations

### Cookie Mode Security

- Keep cookies private and secure
- Don't share cookies with others
- Cookies expire with browser sessions
- Use HTTPS for all requests

### Official API Security

- Store credentials securely
- Use environment variables
- Implement proper token refresh
- Follow OAuth 2.0 best practices

### General Security

- Don't log sensitive data
- Use secure connections
- Validate all inputs
- Handle errors gracefully

## 📞 Support & Community

### Getting Help

1. **Check documentation** - Comprehensive guides available
2. **Use diagnostics** - Built-in debugging tools
3. **Try different modes** - Switch if one isn't working
4. **Check GitHub issues** - Community support
5. **Contact maintainers** - For persistent issues

### Contributing

- Report bugs and issues
- Suggest new features
- Improve documentation
- Submit pull requests
- Help other users

### License

MIT License - Free for personal and commercial use

---

## 🎉 Conclusion

TeraDL provides three powerful ways to access TeraBox content:

- **🎪 Unofficial Mode** - Perfect for quick, simple downloads
- **🍪 Cookie Mode** - Best balance of reliability and ease of use  
- **🏢 Official API** - Enterprise-grade features and support

Choose the mode that fits your needs, and enjoy reliable TeraBox downloads! 🚀

**Made with ❤️ using Streamlit**

*Based on analysis of terabox-downloader PyPI package and TeraBox Open Platform documentation*

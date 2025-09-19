# TeraDL - The Ultimate TeraBox Integration

**Four complete methods to access TeraBox content - from simple scraping to enterprise-grade APIs!**

![TeraDL](https://img.shields.io/badge/TeraDL-4%20Modes-blue?style=for-the-badge) ![Python](https://img.shields.io/badge/Python-3.8+-green?style=for-the-badge) ![Streamlit](https://img.shields.io/badge/Streamlit-Latest-red?style=for-the-badge)

## 🌟 Four Powerful Access Methods

### 🎯 Unofficial Mode - Quick & Free
**Perfect for: Personal use, testing, maximum privacy**
- ✅ No setup required - works immediately
- ✅ No account needed - maximum privacy  
- ✅ Free forever - no costs or subscriptions
- ✅ Share links only - simple and focused
- ⚠️ Variable reliability - may face anti-bot measures

### 🍪 Cookie Mode - Reliable & Simple
**Perfect for: Regular users, reliable downloads, personal projects**
- ✅ Session-based - uses your TeraBox login
- ✅ Direct downloads - guaranteed working links
- ✅ Easy setup - just copy browser cookie
- ✅ Progress tracking - advanced download features
- ⚠️ Requires TeraBox account and cookie extraction

### 🏢 Official API - Enterprise Grade
**Perfect for: Business applications, enterprise use, full features**
- ✅ OAuth 2.0 - official authentication standard
- ✅ Full features - complete file management
- ✅ Enterprise support - official backing
- ✅ Long-term stability - guaranteed compatibility
- ⚠️ Complex setup - requires API approval process

### 💳 RapidAPI - Commercial Service
**Perfect for: Commercial apps, SaaS, guaranteed reliability**
- ✅ Commercial reliability - professional uptime SLA
- ✅ Simple integration - just API key needed
- ✅ Professional support - commercial backing
- ✅ Guaranteed results - no anti-bot issues
- ⚠️ Paid service - requires RapidAPI subscription

## 🚀 Quick Start Guide

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Run TeraDL
streamlit run app.py

# Open browser to http://localhost:8501
```

### Choose Your Adventure

#### 🎯 For Quick Downloads (Unofficial Mode)
```
1. Open TeraDL
2. Paste TeraBox share link
3. Click "Extract Files"
4. Download immediately
✅ Works instantly, no setup needed!
```

#### 🍪 For Reliable Downloads (Cookie Mode)
```
1. Login to TeraBox in browser
2. Extract cookie (F12 → Application → Cookies)
3. Configure in Cookie Mode page
4. Access any file in your account
✅ More reliable than scraping!
```

#### 💳 For Commercial Use (RapidAPI Mode)
```
1. Sign up for RapidAPI account
2. Subscribe to TeraBox service
3. Get your API key
4. Configure in RapidAPI Mode page
✅ Professional reliability guaranteed!
```

#### 🏢 For Enterprise (Official API)
```
1. Apply for TeraBox API credentials
2. Complete OAuth setup
3. Authenticate your application
4. Access full TeraBox features
✅ Enterprise-grade integration!
```

## 📊 Detailed Comparison

| Feature | 🎯 Unofficial | 🍪 Cookie | 🏢 Official | 💳 RapidAPI |
|---------|--------------|-----------|-------------|-------------|
| **Setup** | None | Cookie | API approval | API key |
| **Cost** | Free | Free | Free* | Paid |
| **Reliability** | Variable | Good | Excellent | Excellent |
| **File Access** | Share links | Account files | Complete | Share links |
| **Download Speed** | Medium | Fast | Fast | Fast |
| **Business Use** | Limited | Good | Excellent | Excellent |
| **Support** | Community | Community | Official | Commercial |
| **Rate Limits** | May hit blocks | Account limits | API limits | Plan-based |

## 🔧 Technical Implementation

### Architecture Overview
```
TeraDL Streamlit App
├── 🎯 Unofficial Mode (terabox_core.py)
│   ├── Mode 1: Dynamic cookies
│   ├── Mode 2: Static cookies  
│   └── Mode 3: External service
├── 🍪 Cookie Mode (terabox_cookie_api.py)
│   ├── Session authentication
│   ├── Direct download links
│   └── Progress tracking
├── 🏢 Official API (terabox_official_api.py)
│   ├── OAuth 2.0 flows
│   ├── Complete REST API
│   └── Enterprise features
└── 💳 RapidAPI (terabox_rapidapi.py)
    ├── Commercial service
    ├── API key authentication
    └── Guaranteed reliability
```

### Key Files
```
Core Files:
- app.py                    # Main Streamlit application
- terabox_core.py          # Unofficial scraping methods  
- terabox_cookie_api.py    # Cookie-based integration
- terabox_official_api.py  # Official API client
- terabox_rapidapi.py      # RapidAPI integration
- config.py                # Configuration and utilities

UI Pages:
- pages/🔑_API_Mode.py     # Official API configuration
- pages/🍪_Cookie_Mode.py  # Cookie management
- pages/💳_RapidAPI_Mode.py # RapidAPI configuration  
- pages/📊_Mode_Comparison.py # Compare all modes
- pages/📁_File_Manager.py # File management (Official API)
- pages/⚙️_Settings.py     # Application settings
- pages/🔧_Network_Diagnostics.py # Network testing
```

## 📋 Setup Instructions

### 🎯 Unofficial Mode Setup
**No setup required!** Just run the app and start using.

### 🍪 Cookie Mode Setup

#### Step 1: Get Your Cookie
```
Chrome:
1. Open terabox.com and login
2. Press F12 → Application tab
3. Cookies → https://www.terabox.com
4. Copy: ndus, BDUSS, STOKEN
5. Format: ndus=value1; BDUSS=value2; STOKEN=value3;

Firefox:
1. Open terabox.com and login
2. Press F12 → Storage tab
3. Cookies → https://www.terabox.com
4. Copy important cookie values
5. Format as name1=value1; name2=value2;
```

#### Step 2: Configure TeraDL
```
1. Go to Cookie Mode page
2. Paste your cookie string
3. Click "Validate Cookie"
4. Start downloading!
```

### 💳 RapidAPI Mode Setup

#### Step 1: Get RapidAPI Access
```
1. Sign up at rapidapi.com
2. Search for "terabox-downloader-direct-download-link-generator2"
3. Choose subscription plan:
   - Basic: Limited requests
   - Pro: Higher limits
   - Ultra: Unlimited requests
4. Subscribe to your chosen plan
```

#### Step 2: Configure TeraDL
```
1. Copy your X-RapidAPI-Key from dashboard
2. Go to RapidAPI Mode page
3. Enter your API key
4. Click "Validate API Key"
5. Start using commercial service!
```

### 🏢 Official API Setup

#### Step 1: Apply for API Credentials
```
Contact TeraBox Business Team:
- Provide application details
- Describe use case
- Submit business information

Receive:
- Client ID (AppKey)
- Client Secret (SecretKey)
- Private Secret (for signatures)
```

#### Step 2: Configure Authentication
```
1. Go to API Mode page
2. Enter your credentials
3. Choose authentication method:
   - Authorization Code Flow (web)
   - Device Code Flow (QR code)
4. Complete OAuth process
5. Access full API features!
```

## 🎯 Usage Examples

### Example 1: Quick Download (Unofficial)
```python
# Just paste a TeraBox link and download
# No setup, no authentication, works immediately
```

### Example 2: Reliable Download (Cookie)
```python
from terabox_cookie_api import TeraBoxCookieAPI

# Your browser cookie
cookie = "ndus=your_value; BDUSS=another_value; STOKEN=token"

# Initialize client
api = TeraBoxCookieAPI(cookie)

# Get file info
file_info = api.get_file_info("https://terabox.com/s/your_link")

# Download with progress
def progress_callback(downloaded, total, percentage):
    print(f"Progress: {percentage:.1f}%")

result = api.download(file_info, save_path="download/", callback=progress_callback)
```

### Example 3: Commercial Service (RapidAPI)
```python
from terabox_rapidapi import TeraBoxRapidAPI

# Your RapidAPI key
api_key = "your_rapidapi_key_here"

# Initialize client
api = TeraBoxRapidAPI(api_key)

# Get file info
file_info = api.get_file_info("https://terabox.com/s/your_link")

# Download file
result = api.download_file(file_info, save_path="download/")
```

### Example 4: Enterprise Integration (Official API)
```python
from terabox_official_api import TeraBoxOfficialAPI

# Your API credentials
api = TeraBoxOfficialAPI(client_id, client_secret, private_secret)

# Authenticate
auth_url = api.get_authorization_url()
# ... complete OAuth flow ...

# List user files
files = api.list_files(directory="/")

# Search files
search_results = api.search_files(keyword="video")

# Get download links
download_links = api.get_download_links(["file_id_1", "file_id_2"])
```

## 🔄 Mode Selection Guide

### When to Use Each Mode

#### 🎯 Unofficial Mode
```
✅ Use when:
- Quick one-time downloads
- Testing TeraBox links
- Maximum privacy needed
- No setup time available
- Free solution required

❌ Don't use when:
- Need guaranteed reliability
- Building commercial apps
- Regular heavy usage
- Need file management
```

#### 🍪 Cookie Mode  
```
✅ Use when:
- Have TeraBox account
- Need reliable downloads
- Want direct download links
- Regular personal usage
- Can extract browser cookies

❌ Don't use when:
- Don't have TeraBox account
- Can't extract cookies
- Need file management
- Building for others
```

#### 🏢 Official API
```
✅ Use when:
- Building business applications
- Need full file management
- Want official support
- Enterprise requirements
- Long-term projects

❌ Don't use when:
- Simple personal downloads
- Can't get API approval
- Quick prototyping
- Don't need full features
```

#### 💳 RapidAPI
```
✅ Use when:
- Building commercial apps
- Need guaranteed reliability
- Want professional support
- Can afford subscription
- Need SLA guarantees

❌ Don't use when:
- Personal use only
- Budget constraints
- Don't need guarantees
- Simple requirements
```

## 🛠️ Advanced Features

### Multi-Mode Support
- **Seamless switching** between all four modes
- **Unified interface** - same UI for all methods
- **Session persistence** - settings saved per mode
- **Fallback mechanisms** - try different modes if one fails

### Enhanced Download Features
- **Progress tracking** - real-time download progress
- **Bulk operations** - process multiple files
- **Error recovery** - automatic retry mechanisms
- **File validation** - verify downloads

### Professional Features
- **Configuration management** - save/load settings
- **Logging system** - detailed operation logs
- **Network diagnostics** - connection testing
- **Performance monitoring** - track success rates

## 📈 Performance Optimization

### Best Practices by Mode

#### 🎯 Unofficial Mode
```python
# Use Mode 3 for best results
terabox = TeraboxCore(mode=3)

# Enable retry logic
config.max_retries = 3
config.retry_delay = 1.0

# Monitor network health
# Use Network Diagnostics page
```

#### 🍪 Cookie Mode
```python
# Keep cookies fresh
# Validate before use
api.validate_cookie()

# Use progress callbacks
def progress(downloaded, total, percentage):
    # Update UI or log progress
    pass

# Implement error handling
try:
    result = api.download(file_info, callback=progress)
except Exception as e:
    # Handle errors gracefully
    pass
```

#### 🏢 Official API
```python
# Cache token info
token_info = api.get_token_info()

# Batch operations
file_ids = ["id1", "id2", "id3"]
download_links = api.get_download_links(file_ids)

# Monitor quotas
quota = api.get_quota_info()
```

#### 💳 RapidAPI
```python
# Respect rate limits
import time

for url in urls:
    result = api.get_file_info(url)
    time.sleep(1)  # Rate limiting

# Monitor usage
# Check RapidAPI dashboard regularly
```

## 🔐 Security Considerations

### Data Privacy
- **Unofficial Mode**: Maximum privacy, no account data
- **Cookie Mode**: Uses personal account, secure cookie handling
- **Official API**: OAuth 2.0 standard, encrypted tokens
- **RapidAPI**: Commercial service, secure API keys

### Best Practices
```python
# Store credentials securely
import os
api_key = os.getenv('RAPIDAPI_KEY')

# Use environment variables
export TERABOX_COOKIE="your_cookie_here"
export RAPIDAPI_KEY="your_key_here"

# Validate inputs
def validate_url(url):
    # Implement URL validation
    pass

# Handle errors gracefully
try:
    result = api.get_file_info(url)
except Exception as e:
    log_error(e)
    return error_response(e)
```

## 📞 Support & Troubleshooting

### Common Issues

#### Connection Problems
```
Problem: ConnectionResetError
Solution:
- Try different modes
- Use Network Diagnostics
- Check internet connection
- Switch user agents
```

#### Authentication Issues
```
Cookie Mode: Get fresh cookie
Official API: Refresh tokens
RapidAPI: Check subscription status
Unofficial: No auth needed
```

#### Rate Limiting
```
Unofficial: Switch modes, wait
Cookie: Respect account limits
Official: Monitor API quotas
RapidAPI: Check plan limits
```

### Getting Help
1. **Built-in Diagnostics** - Use Network Diagnostics page
2. **Mode Comparison** - Compare features and choose best fit
3. **Documentation** - Comprehensive guides available
4. **Community Support** - GitHub issues and discussions
5. **Commercial Support** - Available for Official API and RapidAPI modes

## 🎉 Conclusion

TeraDL is now the **most comprehensive TeraBox integration** available, offering:

- **🎯 Unofficial Mode** - For quick, free downloads
- **🍪 Cookie Mode** - For reliable, authenticated access
- **🏢 Official API** - For enterprise applications
- **💳 RapidAPI** - For commercial reliability

**Choose the mode that fits your needs, and enjoy the best TeraBox experience possible!**

### 🌟 What Makes TeraDL Special

1. **Four Complete Methods** - More options than any other solution
2. **Unified Interface** - Same beautiful UI for all methods
3. **Easy Mode Switching** - Change methods anytime
4. **Comprehensive Documentation** - Detailed guides for everything
5. **Professional Features** - From simple downloads to enterprise integration
6. **Open Source** - MIT license, free to use and modify
7. **Active Development** - Continuously improved and updated

### 🚀 Perfect for Everyone

- **👤 Individual Users** - Unofficial or Cookie modes
- **👥 Teams** - Cookie or Official API modes
- **🏢 Businesses** - Official API or RapidAPI modes
- **🔧 Developers** - All modes with full API access
- **🎓 Students** - Free modes for learning
- **💼 Enterprises** - Official API with OAuth 2.0

---

**Made with ❤️ using Streamlit**

*Integrating the best of terabox-downloader PyPI package, TeraBox Open Platform APIs, and custom scraping methods*

**Start downloading today - choose your mode and get started in minutes!** 🎉

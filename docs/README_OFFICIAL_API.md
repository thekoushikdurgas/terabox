# TeraDL - Official TeraBox API Integration

This document explains the official TeraBox API integration features added to TeraDL Streamlit application.

## 🎯 Overview

TeraDL now supports both unofficial scraping methods and official TeraBox Open Platform APIs, giving users flexibility in how they access TeraBox content.

### 🔄 Two Operation Modes

1. **🎯 Unofficial Mode** - Original scraping-based approach
2. **🏢 Official API Mode** - New TeraBox Open Platform integration

## 🏢 Official API Mode Features

### 🔑 Authentication Methods

#### Authorization Code Flow
- Web-based OAuth 2.0 flow
- Redirects to TeraBox login page
- Returns authorization code for token exchange
- Best for web applications

#### Device Code Flow (QR Code)
- QR code-based authentication
- Users scan QR with TeraBox mobile app
- Polling mechanism to check authorization status
- Best for desktop/server applications

### 👤 User Management

#### User Information
- Get user profile details
- Check VIP/Premium status
- View account type (new/existing)
- Access user ID and avatar

#### Storage Quota
- View total storage capacity
- Check used storage space
- Calculate available space
- Monitor usage percentage

#### Account Features
- Activate external link sharing capability
- Manage premium features
- Access user-specific settings

### 📁 File Management

#### File Operations
- **List Files**: Browse directories and files
- **Search Files**: Search across entire storage
- **File Details**: Get comprehensive file metadata
- **Download Links**: Generate direct download URLs
- **File Info**: Access file properties and thumbnails

#### Directory Navigation
- Navigate through folder structures
- Support for nested directories
- Breadcrumb navigation
- Home directory access

#### File Filtering & Sorting
- Filter by file type (video, image, document, etc.)
- Sort by name, size, date modified
- Bulk selection capabilities
- Multi-file operations

### 🎥 Streaming & Media

#### Video Streaming
- Generate M3U8 streaming URLs
- Multiple quality options (480p, 720p, 1080p)
- Direct browser playback support
- HLS (HTTP Live Streaming) format

#### Audio Streaming
- M3U8 audio streaming
- Multiple bitrate options
- Direct audio playback

### 🔗 Share Management

#### External Link Processing
- Verify share passwords
- Extract share information
- List shared files
- Get shared file details

#### Share File Operations
- Generate download links for shared files
- Stream shared videos
- Copy shared files to personal storage
- Bulk operations on shared content

### 📊 Advanced Features

#### API Integration
- Full REST API implementation
- Proper error handling and retry logic
- Rate limiting compliance
- Token refresh automation

#### Security
- OAuth 2.0 standard compliance
- Secure token storage
- Signature-based authentication
- Encrypted communication

## 🚀 Getting Started with Official API

### Step 1: API Credentials

To use the official API, you need credentials from TeraBox:

1. **Apply for API Access**
   - Contact TeraBox business team
   - Provide application details
   - Describe your use case

2. **Receive Credentials**
   - Client ID (AppKey)
   - Client Secret (SecretKey)
   - Private Secret (for signatures)

### Step 2: Configure TeraDL

1. **Switch to Official API Mode**
   ```
   - Open TeraDL application
   - Go to "🔑 API Mode" page
   - Click "🏢 Use Official API Mode"
   ```

2. **Enter Credentials**
   ```
   - Input Client ID
   - Input Client Secret
   - Input Private Secret
   - Click "💾 Save Credentials"
   ```

3. **Authenticate**
   - Choose authentication method
   - Complete OAuth flow
   - Verify authentication status

### Step 3: Use Official Features

1. **File Management**
   - Go to "📁 File Manager" page
   - Browse your TeraBox files
   - Search, download, and stream content

2. **Enhanced Main App**
   - Use TeraBox URLs as usual
   - Enjoy improved reliability
   - Access additional features

## 🔧 Configuration Options

### Environment Variables

Set these environment variables for enhanced functionality:

```bash
# TeraBox API Configuration
TERABOX_CLIENT_ID=your_client_id
TERABOX_CLIENT_SECRET=your_client_secret
TERABOX_PRIVATE_SECRET=your_private_secret

# Application Settings
TERADL_API_MODE=official  # or 'unofficial'
TERADL_DEFAULT_QUALITY=720p
TERADL_MAX_FILE_SIZE=1000  # MB
```

### Session Storage

The application stores session data for:
- Authentication tokens
- User preferences
- API mode selection
- File browser state

## 🔄 Mode Comparison

| Feature | Unofficial Mode | Official API Mode |
|---------|----------------|-------------------|
| **Setup** | ✅ No setup required | ❌ Requires API credentials |
| **Reliability** | ⚠️ May face blocks | ✅ Stable and supported |
| **File Access** | ✅ Share links only | ✅ Full account access |
| **File Management** | ❌ Limited | ✅ Complete |
| **Upload Files** | ❌ No | ✅ Yes |
| **Search Files** | ❌ No | ✅ Yes |
| **User Account** | ❌ No access | ✅ Full integration |
| **Streaming** | ⚠️ Basic | ✅ Advanced |
| **Rate Limits** | ⚠️ May hit blocks | ✅ Official limits |
| **Support** | ❌ Community only | ✅ Official support |

## 🛠️ API Endpoints Used

### Authentication Endpoints
```
POST /oauth/gettoken          - Exchange code for token
POST /oauth/tokeninfo         - Get token information  
POST /oauth/refreshtoken      - Refresh expired token
GET  /oauth/devicecode        - Get device code & QR
```

### User Management Endpoints
```
GET /openapi/uinfo           - User information
GET /openapi/api/quota       - Storage quota
GET /openapi/active          - Activate features
```

### File Management Endpoints
```
GET /openapi/api/list        - List files
GET /openapi/api/filemetas   - File metadata
GET /openapi/api/search      - Search files
GET /openapi/api/download    - Download links
GET /openapi/api/streaming   - Streaming URLs
```

### Share Management Endpoints
```
POST /openapi/share/verify    - Verify share password
GET  /openapi/api/shorturlinfo - Share information
GET  /openapi/share/list      - Share file list
GET  /openapi/share/download  - Share download links
GET  /openapi/share/streaming - Share streaming URLs
```

## 🔐 Security Considerations

### Token Security
- Tokens are stored in session state only
- Automatic token refresh
- Secure signature generation
- No persistent storage of credentials

### API Security
- HTTPS-only communication
- Request signing with private key
- Rate limiting compliance
- Error handling for security events

### Best Practices
- Use environment variables for credentials
- Implement proper error handling
- Monitor API usage and limits
- Regular token refresh
- Secure credential storage

## 🐛 Troubleshooting

### Common Issues

#### Authentication Failures
```
Problem: "Authentication failed" error
Solution: 
- Verify API credentials are correct
- Check if credentials have expired
- Ensure proper signature generation
- Try refreshing tokens
```

#### API Rate Limits
```
Problem: "Rate limit exceeded" error
Solution:
- Wait before retrying requests
- Implement exponential backoff
- Monitor API usage
- Contact TeraBox for limit increases
```

#### Network Errors
```
Problem: Connection timeouts or failures
Solution:
- Check internet connectivity
- Verify API endpoints are accessible
- Try different request methods
- Check firewall/proxy settings
```

#### File Access Issues
```
Problem: "File not found" or access denied
Solution:
- Verify file exists in account
- Check file permissions
- Ensure proper authentication
- Try refreshing file list
```

## 📈 Performance Optimization

### Caching Strategies
- Cache user information
- Store file lists temporarily
- Reuse authentication tokens
- Cache API domain information

### Request Optimization
- Batch file operations
- Use appropriate page sizes
- Implement request queuing
- Monitor response times

### Error Recovery
- Automatic retry mechanisms
- Graceful degradation
- Fallback to unofficial mode
- User-friendly error messages

## 🔄 Migration Guide

### From Unofficial to Official

1. **Preparation**
   - Obtain API credentials
   - Test credentials in development
   - Backup existing configurations

2. **Migration Steps**
   - Switch to Official API mode
   - Configure credentials
   - Complete authentication
   - Test functionality

3. **Verification**
   - Test file extraction
   - Verify download functionality
   - Check streaming capabilities
   - Validate error handling

### Rollback Plan
- Keep unofficial mode available
- Easy mode switching
- Session state preservation
- No data loss during switch

## 📝 Development Notes

### Code Structure
```
terabox_official_api.py     - Main API client
pages/🔑_API_Mode.py        - Mode selection & config
pages/📁_File_Manager.py    - File management UI
app.py                      - Enhanced main application
```

### Key Classes
- `TeraBoxOfficialAPI` - Complete API client
- `TeraboxCore` - Original scraping methods
- Session state management
- Error handling utilities

### Testing
- Unit tests for API methods
- Integration tests for workflows
- Error scenario testing
- Performance testing

## 📞 Support

### Official API Support
- Contact TeraBox business team
- API documentation reference
- Developer community forums
- Technical support tickets

### TeraDL Support
- GitHub issues for bugs
- Feature requests welcome
- Community contributions
- Documentation improvements

---

**Note:** This integration provides legitimate access to TeraBox services through official channels. Always respect TeraBox's terms of service and usage policies.

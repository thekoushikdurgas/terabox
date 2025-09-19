# TeraDL Configuration System

## Overview

TeraDL uses a comprehensive, hierarchical configuration system that provides flexibility, security, and ease of use. The system supports multiple configuration sources with a clear priority order.

## Configuration Architecture

### Configuration Files

1. **Base Configuration**: `utils/config.json`
   - Contains default settings for all modules
   - Version controlled and shared across deployments
   - Provides sensible defaults for all configuration options

2. **User Configuration**: `teradl_config.json` (created automatically)
   - User-specific overrides and customizations
   - Sensitive data is encrypted (API keys, credentials)
   - Not version controlled for security

### Configuration Hierarchy (Priority Order)

1. **Environment Variables** (Highest Priority)
2. **User Configuration** (`teradl_config.json`)
3. **Base Configuration** (`utils/config.json`)
4. **Code Defaults** (Lowest Priority)

## Configuration Sections

### App Configuration
Global application settings:

```json
{
  "app": {
    "api_mode": "unofficial",           // unofficial, rapidapi, cookie, official
    "theme": "light",                   // light, dark
    "language": "en",                   // en, es, fr, de, zh
    "max_file_size_mb": 1000,          // Maximum file size for downloads
    "enable_streaming": true,           // Enable video streaming
    "enable_debug": false,              // Debug mode
    "cache_duration_minutes": 30,       // UI cache duration
    "default_download_dir": "output/download"  // Default download directory
  }
}
```

### RapidAPI Configuration
Commercial API service settings:

```json
{
  "rapidapi": {
    "api_key": "your_api_key_here",     // Encrypted in user config
    "base_url": "https://...",          // RapidAPI service URL
    "host": "service.p.rapidapi.com",   // Host header
    "timeout": 30,                      // Request timeout
    "max_retries": 3,                   // Retry attempts
    "retry_delay": 2.0,                 // Delay between retries
    "enable_cache": true,               // Enable response caching
    "cache_ttl_hours": 24              // Cache time-to-live
  }
}
```

### Unofficial Mode Configuration
Scraping mode settings:

```json
{
  "unofficial": {
    "default_mode": 3,                  // 1, 2, or 3
    "max_retries": 3,                   // Retry attempts
    "retry_delay": 1.0,                 // Delay between retries
    "timeout_seconds": 30,              // Request timeout
    "user_agents_rotation": true,       // Rotate user agents
    "enable_logging": true,             // Enable request logging
    "external_service_url": "https://terabox.hnn.workers.dev"
  }
}
```

### Official API Configuration
TeraBox Official API settings:

```json
{
  "official": {
    "client_id": null,                  // Encrypted in user config
    "client_secret": null,              // Encrypted in user config
    "private_secret": null,             // Encrypted in user config
    "api_domain": "www.terabox.com",    // API domain
    "upload_domain": null,              // Upload domain (optional)
    "default_stream_quality": "M3U8_AUTO_720",  // Stream quality
    "enable_token_refresh": true,       // Auto token refresh
    "token_refresh_threshold": 3600,    // Refresh threshold (seconds)
    "timeout": 30,                      // Request timeout
    "max_retries": 3                    // Retry attempts
  }
}
```

### Cookie Mode Configuration
Cookie-based authentication settings:

```json
{
  "cookie": {
    "validate_on_startup": true,        // Validate cookies on startup
    "auto_retry": true,                 // Auto retry on failure
    "timeout": 30,                      // Request timeout
    "max_retries": 3,                   // Retry attempts
    "retry_delay": 1.5                  // Delay between retries
  }
}
```

### Browser Configuration
Browser integration settings:

```json
{
  "browser": {
    "default_browser": "chrome",        // Default browser
    "supported_browsers": ["chrome", "firefox", "edge", "safari", "opera"],
    "open_in_new_tab": true,           // Open in new tab
    "enable_browser_selection": true   // Enable browser selection UI
  }
}
```

### Cache Configuration
Global caching settings:

```json
{
  "cache": {
    "enable_global_cache": true,        // Enable caching globally
    "cache_directory": "output/sessions", // Cache directory
    "default_ttl_hours": 24,           // Default TTL
    "max_cache_size_mb": 100,          // Max cache size
    "auto_cleanup": true,              // Auto cleanup old cache
    "cleanup_interval_hours": 6        // Cleanup interval
  }
}
```

### Network Configuration
Network and HTTP settings:

```json
{
  "network": {
    "default_timeout": 30,             // Default timeout
    "max_retries": 3,                  // Max retries
    "retry_delay": 1.0,                // Retry delay
    "connection_pool_size": 10,        // Connection pool size
    "enable_ssl_verify": true,         // SSL verification
    "user_agent": "TeraDL-Client/1.0"  // User agent string
  }
}
```

### Logging Configuration
Logging system settings:

```json
{
  "logging": {
    "level": "INFO",                   // Log level
    "file": "output/logs/teradl.log",  // Log file path
    "max_file_size_mb": 10,           // Max log file size
    "backup_count": 5,                 // Number of backup files
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  }
}
```

### Security Configuration
Security and encryption settings:

```json
{
  "security": {
    "enable_encryption": true,          // Enable data encryption
    "keyring_service": "TeraDL",       // Keyring service name
    "session_timeout_minutes": 60      // Session timeout
  }
}
```

## Environment Variables

All configuration values can be overridden using environment variables:

### App Configuration
```bash
export TERADL_API_MODE=rapidapi
export TERADL_THEME=dark
export TERADL_LANGUAGE=en
export TERADL_MAX_FILE_SIZE=1000
export TERADL_ENABLE_STREAMING=true
export TERADL_ENABLE_DEBUG=false
export TERADL_DOWNLOAD_DIR=downloads
```

### RapidAPI Configuration
```bash
export RAPIDAPI_KEY=your_api_key
export RAPIDAPI_BASE_URL=https://...
export RAPIDAPI_HOST=service.p.rapidapi.com
export RAPIDAPI_TIMEOUT=30
export RAPIDAPI_MAX_RETRIES=3
export RAPIDAPI_ENABLE_CACHE=true
export RAPIDAPI_CACHE_TTL=24
```

### Unofficial Mode Configuration
```bash
export TERADL_DEFAULT_MODE=3
export TERADL_MAX_RETRIES=3
export TERADL_RETRY_DELAY=1.0
export TERADL_TIMEOUT=30
export TERADL_EXTERNAL_SERVICE_URL=https://terabox.hnn.workers.dev
```

### Official API Configuration
```bash
export TERABOX_CLIENT_ID=your_client_id
export TERABOX_CLIENT_SECRET=your_client_secret
export TERABOX_PRIVATE_SECRET=your_private_secret
export TERABOX_API_DOMAIN=www.terabox.com
export TERABOX_STREAM_QUALITY=M3U8_AUTO_720
export TERABOX_TIMEOUT=30
export TERABOX_MAX_RETRIES=3
```

### Cache Configuration
```bash
export TERADL_ENABLE_CACHE=true
export TERADL_CACHE_DIR=cache
export TERADL_CACHE_TTL=24
export TERADL_CACHE_MAX_SIZE=100
```

### Network Configuration
```bash
export TERADL_NETWORK_TIMEOUT=30
export TERADL_NETWORK_RETRIES=3
export TERADL_USER_AGENT="Custom-Agent/1.0"
```

### Logging Configuration
```bash
export TERADL_LOG_LEVEL=DEBUG
export TERADL_LOG_FILE=app.log
export TERADL_LOG_MAX_SIZE=20
```

## Configuration Management

### Accessing Configuration

```python
from utils.terabox_config import get_config_manager

# Get configuration manager
config_mgr = get_config_manager()

# Access specific configurations
app_config = config_mgr.get_app_config()
rapidapi_config = config_mgr.get_rapidapi_config()
unofficial_config = config_mgr.get_unofficial_config()
```

### Updating Configuration

```python
# Update app configuration
config_mgr.update_app_config(
    theme='dark',
    enable_debug=True
)

# Update RapidAPI configuration
config_mgr.update_rapidapi_config(
    api_key='new_key',
    timeout=45
)

# Save changes
config_mgr.save_config()
```

### Configuration Export/Import

```python
# Export configuration (without sensitive data)
config_data = config_mgr.export_config()

# Import configuration
config_mgr.import_config(config_data)

# Reset to defaults
config_mgr.reset_to_defaults()
```

## Security Features

### Data Encryption
- Sensitive data (API keys, credentials) is automatically encrypted
- Uses Fernet symmetric encryption
- Keys are stored securely in system keyring when available
- Fallback to session-based keys for environments without keyring

### Safe Configuration Export
- Export functionality excludes sensitive data
- API keys and credentials are not included in exports
- Configuration status is included instead of actual values

## Configuration UI

The TeraDL Settings page provides a comprehensive interface for managing all configuration options:

1. **🎯 General**: Basic app settings
2. **🌐 Browser**: Browser integration settings  
3. **💳 RapidAPI**: Commercial API configuration
4. **🎪 Unofficial Mode**: Scraping mode settings
5. **🏢 Official API**: Official API credentials
6. **🔧 Advanced**: Export/import and advanced options
7. **📊 Status**: Configuration overview and system status
8. **💾 Cache**: Cache management and cleanup

## Migration from Legacy Configuration

The new system automatically loads settings from the existing `utils/config.json` file and migrates them to the new structure. No manual migration is required.

## Best Practices

1. **Use Environment Variables**: For production deployments and sensitive data
2. **Keep Base Config Updated**: Update `utils/config.json` for new defaults
3. **Regular Backups**: Export configuration regularly for backup
4. **Security**: Never commit user configuration files with sensitive data
5. **Testing**: Use different configurations for development and production

## Troubleshooting

### Configuration Not Loading
1. Check file permissions for `utils/config.json`
2. Verify JSON syntax in configuration files
3. Check environment variable names and values
4. Review application logs for configuration errors

### Encryption Issues
1. Ensure system keyring is available
2. Check if encryption key is accessible
3. Try resetting encryption key in advanced settings
4. Verify sufficient permissions for keyring access

### Performance Issues
1. Adjust cache settings for better performance
2. Optimize timeout values for your network
3. Configure appropriate retry settings
4. Monitor cache usage and cleanup frequency

## API Reference

See `utils/terabox_config.py` for complete API documentation and available methods.

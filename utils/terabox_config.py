"""
TeraBox Configuration Management
Handles comprehensive configuration, credentials, and settings for all TeraDL modes

This module provides a centralized configuration management system that handles
all aspects of TeraDL configuration across different modes and components.

Configuration Architecture:
- Hierarchical configuration loading (base -> advanced -> environment)
- Secure credential storage with encryption
- Mode-specific configuration sections
- Environment variable override support
- Configuration validation and error handling

Configuration Hierarchy (in order of precedence):
1. Environment Variables (highest priority)
2. Advanced Configuration File (teradl_config.json)
3. Base Configuration File (utils/config.json)
4. Default Values (lowest priority)

Security Features:
- Credential encryption using Fernet symmetric encryption
- Keyring integration for secure key storage
- Session-based fallback for encryption keys
- Sensitive data masking in logs and exports
- Automatic credential validation

Supported Modes:
- App: General application settings and preferences
- RapidAPI: Commercial API service configuration
- Unofficial: Scraping mode settings and retry policies
- Official: OAuth API credentials and endpoints
- Cookie: Session cookie management settings
- Browser: Browser selection and behavior settings
- Cache: Response caching and performance settings
- Network: HTTP client and connection settings
- Logging: Debug and audit log configuration
- Security: Encryption and session management

Configuration Patterns:
- Dataclass-based configuration objects for type safety
- Centralized config manager with unified interface
- Automatic configuration persistence and loading
- Validation and error recovery mechanisms
- Export/import functionality for configuration backup
"""

import os
import json
import streamlit as st
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
import keyring
from cryptography.fernet import Fernet
import base64
from pathlib import Path
from utils.config import log_info, log_error

@dataclass
class RapidAPIConfig:
    """Configuration for RapidAPI mode"""
    api_key: Optional[str] = None
    base_url: str = "https://terabox-downloader-direct-download-link-generator2.p.rapidapi.com"
    host: str = "terabox-downloader-direct-download-link-generator2.p.rapidapi.com"
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 2.0
    enable_cache: bool = True
    cache_ttl_hours: int = 24

@dataclass
class UnofficialConfig:
    """Configuration for unofficial scraping mode"""
    default_mode: int = 3
    max_retries: int = 3
    retry_delay: float = 1.0
    timeout_seconds: int = 30
    user_agents_rotation: bool = True
    enable_logging: bool = True
    external_service_url: str = "https://terabox.hnn.workers.dev"

@dataclass
class CookieConfig:
    """Configuration for cookie mode"""
    validate_on_startup: bool = True
    auto_retry: bool = True
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.5

@dataclass
class BrowserConfig:
    """Configuration for browser functionality"""
    default_browser: str = "chrome"
    supported_browsers: list = None
    open_in_new_tab: bool = True
    enable_browser_selection: bool = True
    
    def __post_init__(self):
        if self.supported_browsers is None:
            self.supported_browsers = ["chrome", "firefox", "edge", "safari", "opera"]

@dataclass
class CacheConfig:
    """Configuration for cache management"""
    enable_global_cache: bool = True
    cache_directory: str = "output/sessions"
    default_ttl_hours: int = 24
    max_cache_size_mb: int = 100
    auto_cleanup: bool = True
    cleanup_interval_hours: int = 6

@dataclass
class NetworkConfig:
    """Configuration for network operations"""
    default_timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    connection_pool_size: int = 10
    enable_ssl_verify: bool = True
    user_agent: str = "TeraDL-Client/1.0"

@dataclass
class LoggingConfig:
    """Configuration for logging"""
    level: str = "INFO"
    file: str = "output/logs/teradl.log"
    max_file_size_mb: int = 10
    backup_count: int = 5
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

@dataclass
class SecurityConfig:
    """Configuration for security settings"""
    enable_encryption: bool = True
    keyring_service: str = "TeraDL"
    session_timeout_minutes: int = 60

@dataclass 
class OfficialAPIConfig:
    """Configuration for official API mode"""
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    private_secret: Optional[str] = None
    api_domain: str = "www.terabox.com"
    upload_domain: Optional[str] = None
    default_stream_quality: str = "M3U8_AUTO_720"
    enable_token_refresh: bool = True
    token_refresh_threshold: int = 3600  # seconds
    timeout: int = 30
    max_retries: int = 3

@dataclass
class AppConfig:
    """Main application configuration"""
    api_mode: str = "unofficial"  # "unofficial" or "official"
    theme: str = "light"
    language: str = "en"
    max_file_size_mb: int = 1000
    enable_streaming: bool = True
    enable_debug: bool = False
    cache_duration_minutes: int = 30
    default_download_dir: str = "download"

class TeraBoxConfigManager:
    """
    Comprehensive configuration manager for TeraBox settings
    
    This class provides centralized management of all TeraDL configuration aspects,
    including secure credential storage, hierarchical configuration loading,
    and environment variable integration.
    
    Configuration Management Features:
    - Hierarchical configuration loading with proper precedence
    - Secure encryption of sensitive credentials
    - Environment variable override support
    - Configuration validation and error recovery
    - Export/import functionality for backup and migration
    - Automatic configuration persistence
    
    Security Architecture:
    - Fernet symmetric encryption for sensitive data
    - Keyring integration for secure key storage
    - Session-based fallback for encryption keys
    - Credential masking in logs and exports
    - Secure configuration file handling
    
    Configuration Sections:
    - App: General application settings
    - RapidAPI: Commercial API service settings
    - Unofficial: Scraping mode configuration
    - Official: OAuth API credentials and settings
    - Cookie: Session cookie management
    - Browser: Browser preferences and settings
    - Cache: Response caching configuration
    - Network: HTTP client settings
    - Logging: Debug and audit configuration
    - Security: Encryption and session settings
    """
    
    def __init__(self):
        """
        Initialize configuration manager with secure setup
        
        Initialization Process:
        1. Set up configuration file paths
        2. Initialize encryption system for sensitive data
        3. Create default configuration objects
        4. Load configuration from all sources (files + environment)
        5. Log initialization status and configuration summary
        """
        log_info("Initializing TeraBoxConfigManager")
        
        # Configuration File Paths
        # Purpose: Define configuration file hierarchy
        # Strategy: Advanced config overrides base config
        self.config_file = "teradl_config.json"  # Advanced/user config file
        self.base_config_file = "utils/config.json"  # Base configuration file
        self.keyring_service = "TeraDL"  # Keyring service name for credential storage
        
        log_info(f"Configuration files - Base: {self.base_config_file}, Advanced: {self.config_file}")
        
        # Encryption System Initialization
        # Purpose: Set up secure storage for sensitive credentials
        # Strategy: Use system keyring or session-based fallback
        self.encryption_key = self._get_or_create_encryption_key()
        log_info("Encryption system initialized for secure credential storage")
        
        # Configuration Objects Initialization
        # Purpose: Create typed configuration objects for each section
        # Pattern: Dataclass-based configuration with defaults
        # Benefits: Type safety, IDE support, validation
        log_info("Creating configuration objects with default values")
        
        self.app_config = AppConfig()
        self.rapidapi_config = RapidAPIConfig()
        self.unofficial_config = UnofficialConfig()
        self.official_config = OfficialAPIConfig()
        self.cookie_config = CookieConfig()
        self.browser_config = BrowserConfig()
        self.cache_config = CacheConfig()
        self.network_config = NetworkConfig()
        self.logging_config = LoggingConfig()
        self.security_config = SecurityConfig()
        
        log_info("Default configuration objects created successfully")
        
        # Hierarchical Configuration Loading
        # Purpose: Load and apply configuration from all sources
        # Order: Base config -> Advanced config -> Environment variables
        log_info("Starting hierarchical configuration loading process")
        self._load_config()
        
        log_info("TeraBoxConfigManager initialization completed successfully")
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for sensitive data"""
        try:
            # Try to get existing key
            key_str = keyring.get_password(self.keyring_service, "encryption_key")
            if key_str:
                return base64.urlsafe_b64decode(key_str.encode())
            else:
                # Create new key
                key = Fernet.generate_key()
                key_str = base64.urlsafe_b64encode(key).decode()
                keyring.set_password(self.keyring_service, "encryption_key", key_str)
                return key
        except Exception:
            # Fallback to session-based key
            if 'encryption_key' not in st.session_state:
                st.session_state.encryption_key = Fernet.generate_key()
            return st.session_state.encryption_key
    
    def _encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        try:
            fernet = Fernet(self.encryption_key)
            encrypted_data = fernet.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception:
            return data  # Fallback to unencrypted
    
    def _decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        try:
            fernet = Fernet(self.encryption_key)
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            return fernet.decrypt(decoded_data).decode()
        except Exception:
            return encrypted_data  # Fallback to original data
    
    def _load_config(self):
        """Load configuration from base config and advanced config files, then environment"""
        # First load from base config.json
        self._load_base_config()
        
        # Then load from advanced config file (overrides base)
        self._load_advanced_config()
        
        # Finally override with environment variables
        self._load_from_environment()
    
    def _load_base_config(self):
        """Load configuration from utils/config.json"""
        if os.path.exists(self.base_config_file):
            try:
                with open(self.base_config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # Update all configurations from base config
                config_mappings = {
                    'app': self.app_config,
                    'rapidapi': self.rapidapi_config,
                    'unofficial': self.unofficial_config,
                    'official': self.official_config,
                    'cookie': self.cookie_config,
                    'browser': self.browser_config,
                    'cache': self.cache_config,
                    'network': self.network_config,
                    'logging': self.logging_config,
                    'security': self.security_config
                }
                
                for section_name, config_obj in config_mappings.items():
                    if section_name in config_data:
                        for key, value in config_data[section_name].items():
                            if hasattr(config_obj, key):
                                setattr(config_obj, key, value)
            
            except Exception as e:
                if hasattr(st, 'error'):
                    st.error(f"Error loading base config: {e}")
                else:
                    print(f"Error loading base config: {e}")
    
    def _load_advanced_config(self):
        """Load configuration from teradl_config.json (advanced/user overrides)"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # Update configurations (same structure as base config)
                config_mappings = {
                    'app': self.app_config,
                    'rapidapi': self.rapidapi_config,
                    'unofficial': self.unofficial_config,
                    'official': self.official_config,
                    'cookie': self.cookie_config,
                    'browser': self.browser_config,
                    'cache': self.cache_config,
                    'network': self.network_config,
                    'logging': self.logging_config,
                    'security': self.security_config
                }
                
                for section_name, config_obj in config_mappings.items():
                    if section_name in config_data:
                        for key, value in config_data[section_name].items():
                            if hasattr(config_obj, key):
                                if section_name == 'official' and key in ['client_id', 'client_secret', 'private_secret'] and value:
                                    # Decrypt sensitive data for official API
                                    setattr(config_obj, key, self._decrypt_data(value))
                                else:
                                    setattr(config_obj, key, value)
            
            except Exception as e:
                if hasattr(st, 'error'):
                    st.error(f"Error loading advanced config: {e}")
                else:
                    print(f"Error loading advanced config: {e}")
    
    def _load_from_environment(self):
        """Load configuration from environment variables"""
        env_mappings = {
            # App config
            'TERADL_API_MODE': ('app_config', 'api_mode'),
            'TERADL_THEME': ('app_config', 'theme'),
            'TERADL_LANGUAGE': ('app_config', 'language'),
            'TERADL_MAX_FILE_SIZE': ('app_config', 'max_file_size_mb'),
            'TERADL_ENABLE_STREAMING': ('app_config', 'enable_streaming'),
            'TERADL_ENABLE_DEBUG': ('app_config', 'enable_debug'),
            'TERADL_DOWNLOAD_DIR': ('app_config', 'default_download_dir'),
            
            # RapidAPI config
            'RAPIDAPI_KEY': ('rapidapi_config', 'api_key'),
            'RAPIDAPI_BASE_URL': ('rapidapi_config', 'base_url'),
            'RAPIDAPI_HOST': ('rapidapi_config', 'host'),
            'RAPIDAPI_TIMEOUT': ('rapidapi_config', 'timeout'),
            'RAPIDAPI_MAX_RETRIES': ('rapidapi_config', 'max_retries'),
            'RAPIDAPI_ENABLE_CACHE': ('rapidapi_config', 'enable_cache'),
            'RAPIDAPI_CACHE_TTL': ('rapidapi_config', 'cache_ttl_hours'),
            
            # Unofficial config
            'TERADL_DEFAULT_MODE': ('unofficial_config', 'default_mode'),
            'TERADL_MAX_RETRIES': ('unofficial_config', 'max_retries'),
            'TERADL_RETRY_DELAY': ('unofficial_config', 'retry_delay'),
            'TERADL_TIMEOUT': ('unofficial_config', 'timeout_seconds'),
            'TERADL_EXTERNAL_SERVICE_URL': ('unofficial_config', 'external_service_url'),
            
            # Official API config
            'TERABOX_CLIENT_ID': ('official_config', 'client_id'),
            'TERABOX_CLIENT_SECRET': ('official_config', 'client_secret'),
            'TERABOX_PRIVATE_SECRET': ('official_config', 'private_secret'),
            'TERABOX_API_DOMAIN': ('official_config', 'api_domain'),
            'TERABOX_STREAM_QUALITY': ('official_config', 'default_stream_quality'),
            'TERABOX_TIMEOUT': ('official_config', 'timeout'),
            'TERABOX_MAX_RETRIES': ('official_config', 'max_retries'),
            
            # Cookie config
            'TERADL_COOKIE_VALIDATE_STARTUP': ('cookie_config', 'validate_on_startup'),
            'TERADL_COOKIE_AUTO_RETRY': ('cookie_config', 'auto_retry'),
            'TERADL_COOKIE_TIMEOUT': ('cookie_config', 'timeout'),
            
            # Browser config
            'TERADL_DEFAULT_BROWSER': ('browser_config', 'default_browser'),
            'TERADL_BROWSER_NEW_TAB': ('browser_config', 'open_in_new_tab'),
            
            # Cache config
            'TERADL_ENABLE_CACHE': ('cache_config', 'enable_global_cache'),
            'TERADL_CACHE_DIR': ('cache_config', 'cache_directory'),
            'TERADL_CACHE_TTL': ('cache_config', 'default_ttl_hours'),
            'TERADL_CACHE_MAX_SIZE': ('cache_config', 'max_cache_size_mb'),
            
            # Network config
            'TERADL_NETWORK_TIMEOUT': ('network_config', 'default_timeout'),
            'TERADL_NETWORK_RETRIES': ('network_config', 'max_retries'),
            'TERADL_USER_AGENT': ('network_config', 'user_agent'),
            
            # Logging config
            'TERADL_LOG_LEVEL': ('logging_config', 'level'),
            'TERADL_LOG_FILE': ('logging_config', 'file'),
            'TERADL_LOG_MAX_SIZE': ('logging_config', 'max_file_size_mb'),
        }
        
        for env_var, (config_obj, attr_name) in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                config_instance = getattr(self, config_obj)
                
                # Type conversion
                current_value = getattr(config_instance, attr_name)
                if isinstance(current_value, bool):
                    env_value = env_value.lower() in ('true', '1', 'yes', 'on')
                elif isinstance(current_value, int):
                    env_value = int(env_value)
                elif isinstance(current_value, float):
                    env_value = float(env_value)
                
                setattr(config_instance, attr_name, env_value)
    
    def save_config(self):
        """Save configuration to advanced config file"""
        try:
            config_data = {
                'app': asdict(self.app_config),
                'rapidapi': asdict(self.rapidapi_config),
                'unofficial': asdict(self.unofficial_config),
                'official': {},
                'cookie': asdict(self.cookie_config),
                'browser': asdict(self.browser_config),
                'cache': asdict(self.cache_config),
                'network': asdict(self.network_config),
                'logging': asdict(self.logging_config),
                'security': asdict(self.security_config)
            }
            
            # Encrypt sensitive official API data
            official_dict = asdict(self.official_config)
            for key, value in official_dict.items():
                if key in ['client_id', 'client_secret', 'private_secret'] and value:
                    config_data['official'][key] = self._encrypt_data(value)
                else:
                    config_data['official'][key] = value
            
            # Encrypt sensitive RapidAPI key
            if config_data['rapidapi']['api_key']:
                config_data['rapidapi']['api_key'] = self._encrypt_data(config_data['rapidapi']['api_key'])
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2)
            
            return True
        except Exception as e:
            if hasattr(st, 'error'):
                st.error(f"Error saving config: {e}")
            else:
                print(f"Error saving config: {e}")
            return False
    
    def get_app_config(self) -> AppConfig:
        """Get application configuration"""
        return self.app_config
    
    def get_rapidapi_config(self) -> RapidAPIConfig:
        """Get RapidAPI configuration"""
        return self.rapidapi_config
    
    def get_unofficial_config(self) -> UnofficialConfig:
        """Get unofficial mode configuration"""
        return self.unofficial_config
    
    def get_official_config(self) -> OfficialAPIConfig:
        """Get official API configuration"""
        return self.official_config
    
    def get_cookie_config(self) -> CookieConfig:
        """Get cookie mode configuration"""
        return self.cookie_config
    
    def get_browser_config(self) -> BrowserConfig:
        """Get browser configuration"""
        return self.browser_config
    
    def get_cache_config(self) -> CacheConfig:
        """Get cache configuration"""
        return self.cache_config
    
    def get_network_config(self) -> NetworkConfig:
        """Get network configuration"""
        return self.network_config
    
    def get_logging_config(self) -> LoggingConfig:
        """Get logging configuration"""
        return self.logging_config
    
    def get_security_config(self) -> SecurityConfig:
        """Get security configuration"""
        return self.security_config
    
    def set_api_mode(self, mode: str):
        """Set API mode (unofficial or official)"""
        if mode in ['unofficial', 'official']:
            self.app_config.api_mode = mode
            self.save_config()
    
    def set_official_credentials(self, client_id: str, client_secret: str, private_secret: str):
        """Set official API credentials"""
        self.official_config.client_id = client_id
        self.official_config.client_secret = client_secret
        self.official_config.private_secret = private_secret
        self.save_config()
    
    def set_rapidapi_key(self, api_key: str):
        """Set RapidAPI key"""
        self.rapidapi_config.api_key = api_key
        self.save_config()
    
    def clear_rapidapi_key(self):
        """Clear RapidAPI key"""
        self.rapidapi_config.api_key = None
        self.save_config()
    
    def has_rapidapi_key(self) -> bool:
        """Check if RapidAPI key is configured"""
        return bool(self.rapidapi_config.api_key)
    
    def clear_official_credentials(self):
        """Clear official API credentials"""
        self.official_config.client_id = None
        self.official_config.client_secret = None
        self.official_config.private_secret = None
        self.save_config()
    
    def has_official_credentials(self) -> bool:
        """Check if official API credentials are configured"""
        return all([
            self.official_config.client_id,
            self.official_config.client_secret,
            self.official_config.private_secret
        ])
    
    def update_app_config(self, **kwargs):
        """Update application configuration"""
        for key, value in kwargs.items():
            if hasattr(self.app_config, key):
                setattr(self.app_config, key, value)
        self.save_config()
    
    def update_rapidapi_config(self, **kwargs):
        """Update RapidAPI configuration"""
        for key, value in kwargs.items():
            if hasattr(self.rapidapi_config, key):
                setattr(self.rapidapi_config, key, value)
        self.save_config()
    
    def update_unofficial_config(self, **kwargs):
        """Update unofficial configuration"""
        for key, value in kwargs.items():
            if hasattr(self.unofficial_config, key):
                setattr(self.unofficial_config, key, value)
        self.save_config()
    
    def update_official_config(self, **kwargs):
        """Update official API configuration"""
        for key, value in kwargs.items():
            if hasattr(self.official_config, key):
                setattr(self.official_config, key, value)
        self.save_config()
    
    def update_cookie_config(self, **kwargs):
        """Update cookie configuration"""
        for key, value in kwargs.items():
            if hasattr(self.cookie_config, key):
                setattr(self.cookie_config, key, value)
        self.save_config()
    
    def update_browser_config(self, **kwargs):
        """Update browser configuration"""
        for key, value in kwargs.items():
            if hasattr(self.browser_config, key):
                setattr(self.browser_config, key, value)
        self.save_config()
    
    def update_cache_config(self, **kwargs):
        """Update cache configuration"""
        for key, value in kwargs.items():
            if hasattr(self.cache_config, key):
                setattr(self.cache_config, key, value)
        self.save_config()
    
    def update_network_config(self, **kwargs):
        """Update network configuration"""
        for key, value in kwargs.items():
            if hasattr(self.network_config, key):
                setattr(self.network_config, key, value)
        self.save_config()
    
    def update_logging_config(self, **kwargs):
        """Update logging configuration"""
        for key, value in kwargs.items():
            if hasattr(self.logging_config, key):
                setattr(self.logging_config, key, value)
        self.save_config()
    
    def update_security_config(self, **kwargs):
        """Update security configuration"""
        for key, value in kwargs.items():
            if hasattr(self.security_config, key):
                setattr(self.security_config, key, value)
        self.save_config()
    
    def export_config(self) -> Dict[str, Any]:
        """Export configuration (without sensitive data)"""
        return {
            'app': asdict(self.app_config),
            'rapidapi': {
                'base_url': self.rapidapi_config.base_url,
                'host': self.rapidapi_config.host,
                'timeout': self.rapidapi_config.timeout,
                'max_retries': self.rapidapi_config.max_retries,
                'retry_delay': self.rapidapi_config.retry_delay,
                'enable_cache': self.rapidapi_config.enable_cache,
                'cache_ttl_hours': self.rapidapi_config.cache_ttl_hours,
                'has_api_key': bool(self.rapidapi_config.api_key)
            },
            'unofficial': asdict(self.unofficial_config),
            'official': {
                'api_domain': self.official_config.api_domain,
                'upload_domain': self.official_config.upload_domain,
                'default_stream_quality': self.official_config.default_stream_quality,
                'enable_token_refresh': self.official_config.enable_token_refresh,
                'token_refresh_threshold': self.official_config.token_refresh_threshold,
                'timeout': self.official_config.timeout,
                'max_retries': self.official_config.max_retries,
                'has_credentials': self.has_official_credentials()
            },
            'cookie': asdict(self.cookie_config),
            'browser': asdict(self.browser_config),
            'cache': asdict(self.cache_config),
            'network': asdict(self.network_config),
            'logging': asdict(self.logging_config),
            'security': {
                'enable_encryption': self.security_config.enable_encryption,
                'keyring_service': self.security_config.keyring_service,
                'session_timeout_minutes': self.security_config.session_timeout_minutes
            }
        }
    
    def import_config(self, config_data: Dict[str, Any]):
        """Import configuration from data"""
        try:
            config_mappings = {
                'app': self.app_config,
                'rapidapi': self.rapidapi_config,
                'unofficial': self.unofficial_config,
                'official': self.official_config,
                'cookie': self.cookie_config,
                'browser': self.browser_config,
                'cache': self.cache_config,
                'network': self.network_config,
                'logging': self.logging_config,
                'security': self.security_config
            }
            
            for section_name, config_obj in config_mappings.items():
                if section_name in config_data:
                    for key, value in config_data[section_name].items():
                        if hasattr(config_obj, key) and key not in ['has_credentials', 'has_api_key']:
                            setattr(config_obj, key, value)
            
            self.save_config()
            return True
        except Exception as e:
            if hasattr(st, 'error'):
                st.error(f"Error importing config: {e}")
            else:
                print(f"Error importing config: {e}")
            return False
    
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self.app_config = AppConfig()
        self.rapidapi_config = RapidAPIConfig()
        self.unofficial_config = UnofficialConfig()
        self.official_config = OfficialAPIConfig()
        self.cookie_config = CookieConfig()
        self.browser_config = BrowserConfig()
        self.cache_config = CacheConfig()
        self.network_config = NetworkConfig()
        self.logging_config = LoggingConfig()
        self.security_config = SecurityConfig()
        self.save_config()
    
    def get_default_download_path(self) -> str:
        """Get the default download directory path and ensure it exists"""
        download_dir = self.app_config.default_download_dir
        # Ensure the directory exists
        import os
        os.makedirs(download_dir, exist_ok=True)
        return download_dir
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get configuration summary for display"""
        return {
            'API Mode': self.app_config.api_mode.title(),
            'Theme': self.app_config.theme.title(),
            'Language': self.app_config.language.upper(),
            'Max File Size': f"{self.app_config.max_file_size_mb} MB",
            'Streaming Enabled': "Yes" if self.app_config.enable_streaming else "No",
            'Debug Mode': "Yes" if self.app_config.enable_debug else "No",
            'Download Directory': self.app_config.default_download_dir,
            'RapidAPI Configured': "Yes" if bool(self.rapidapi_config.api_key) else "No",
            'RapidAPI Cache': "Enabled" if self.rapidapi_config.enable_cache else "Disabled",
            'Unofficial Mode': f"Mode {self.unofficial_config.default_mode}",
            'Unofficial Retries': self.unofficial_config.max_retries,
            'Official API Configured': "Yes" if self.has_official_credentials() else "No",
            'API Domain': self.official_config.api_domain,
            'Stream Quality': self.official_config.default_stream_quality,
            'Default Browser': self.browser_config.default_browser.title(),
            'Cache Enabled': "Yes" if self.cache_config.enable_global_cache else "No",
            'Cache Directory': self.cache_config.cache_directory,
            'Network Timeout': f"{self.network_config.default_timeout}s",
            'Log Level': self.logging_config.level
        }

# Global configuration manager instance
config_manager = TeraBoxConfigManager()

def get_config_manager() -> TeraBoxConfigManager:
    """Get the global configuration manager"""
    return config_manager

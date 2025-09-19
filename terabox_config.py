"""
TeraBox Configuration Management
Handles configuration, credentials, and settings for both unofficial and official modes
"""

import os
import json
import streamlit as st
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
import keyring
from cryptography.fernet import Fernet
import base64

@dataclass
class UnofficialConfig:
    """Configuration for unofficial scraping mode"""
    default_mode: int = 3
    max_retries: int = 3
    retry_delay: float = 1.0
    timeout_seconds: int = 30
    user_agents_rotation: bool = True
    enable_logging: bool = True

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

class TeraBoxConfigManager:
    """Configuration manager for TeraBox settings"""
    
    def __init__(self):
        self.config_file = "teradl_config.json"
        self.keyring_service = "TeraDL"
        self.encryption_key = self._get_or_create_encryption_key()
        
        # Load configurations
        self.app_config = AppConfig()
        self.unofficial_config = UnofficialConfig()
        self.official_config = OfficialAPIConfig()
        
        self._load_config()
    
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
        """Load configuration from file and environment"""
        # Load from file
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                
                # Update configurations
                if 'app' in config_data:
                    for key, value in config_data['app'].items():
                        if hasattr(self.app_config, key):
                            setattr(self.app_config, key, value)
                
                if 'unofficial' in config_data:
                    for key, value in config_data['unofficial'].items():
                        if hasattr(self.unofficial_config, key):
                            setattr(self.unofficial_config, key, value)
                
                if 'official' in config_data:
                    for key, value in config_data['official'].items():
                        if hasattr(self.official_config, key):
                            if key in ['client_id', 'client_secret', 'private_secret'] and value:
                                # Decrypt sensitive data
                                setattr(self.official_config, key, self._decrypt_data(value))
                            else:
                                setattr(self.official_config, key, value)
            
            except Exception as e:
                st.error(f"Error loading config: {e}")
        
        # Override with environment variables
        self._load_from_environment()
    
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
            
            # Unofficial config
            'TERADL_DEFAULT_MODE': ('unofficial_config', 'default_mode'),
            'TERADL_MAX_RETRIES': ('unofficial_config', 'max_retries'),
            'TERADL_RETRY_DELAY': ('unofficial_config', 'retry_delay'),
            'TERADL_TIMEOUT': ('unofficial_config', 'timeout_seconds'),
            
            # Official API config
            'TERABOX_CLIENT_ID': ('official_config', 'client_id'),
            'TERABOX_CLIENT_SECRET': ('official_config', 'client_secret'),
            'TERABOX_PRIVATE_SECRET': ('official_config', 'private_secret'),
            'TERABOX_API_DOMAIN': ('official_config', 'api_domain'),
            'TERABOX_STREAM_QUALITY': ('official_config', 'default_stream_quality'),
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
        """Save configuration to file"""
        try:
            config_data = {
                'app': asdict(self.app_config),
                'unofficial': asdict(self.unofficial_config),
                'official': {}
            }
            
            # Encrypt sensitive official API data
            official_dict = asdict(self.official_config)
            for key, value in official_dict.items():
                if key in ['client_id', 'client_secret', 'private_secret'] and value:
                    config_data['official'][key] = self._encrypt_data(value)
                else:
                    config_data['official'][key] = value
            
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            return True
        except Exception as e:
            st.error(f"Error saving config: {e}")
            return False
    
    def get_app_config(self) -> AppConfig:
        """Get application configuration"""
        return self.app_config
    
    def get_unofficial_config(self) -> UnofficialConfig:
        """Get unofficial mode configuration"""
        return self.unofficial_config
    
    def get_official_config(self) -> OfficialAPIConfig:
        """Get official API configuration"""
        return self.official_config
    
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
    
    def update_app_config(self, **kwargs):
        """Update application configuration"""
        for key, value in kwargs.items():
            if hasattr(self.app_config, key):
                setattr(self.app_config, key, value)
        self.save_config()
    
    def export_config(self) -> Dict[str, Any]:
        """Export configuration (without sensitive data)"""
        return {
            'app': asdict(self.app_config),
            'unofficial': asdict(self.unofficial_config),
            'official': {
                'api_domain': self.official_config.api_domain,
                'upload_domain': self.official_config.upload_domain,
                'default_stream_quality': self.official_config.default_stream_quality,
                'enable_token_refresh': self.official_config.enable_token_refresh,
                'token_refresh_threshold': self.official_config.token_refresh_threshold,
                'has_credentials': self.has_official_credentials()
            }
        }
    
    def import_config(self, config_data: Dict[str, Any]):
        """Import configuration from data"""
        try:
            if 'app' in config_data:
                for key, value in config_data['app'].items():
                    if hasattr(self.app_config, key):
                        setattr(self.app_config, key, value)
            
            if 'unofficial' in config_data:
                for key, value in config_data['unofficial'].items():
                    if hasattr(self.unofficial_config, key):
                        setattr(self.unofficial_config, key, value)
            
            if 'official' in config_data:
                for key, value in config_data['official'].items():
                    if hasattr(self.official_config, key) and key != 'has_credentials':
                        setattr(self.official_config, key, value)
            
            self.save_config()
            return True
        except Exception as e:
            st.error(f"Error importing config: {e}")
            return False
    
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self.app_config = AppConfig()
        self.unofficial_config = UnofficialConfig()
        self.official_config = OfficialAPIConfig()
        self.save_config()
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get configuration summary for display"""
        return {
            'API Mode': self.app_config.api_mode.title(),
            'Theme': self.app_config.theme.title(),
            'Max File Size': f"{self.app_config.max_file_size_mb} MB",
            'Streaming Enabled': "Yes" if self.app_config.enable_streaming else "No",
            'Debug Mode': "Yes" if self.app_config.enable_debug else "No",
            'Unofficial Mode': f"Mode {self.unofficial_config.default_mode}",
            'Max Retries': self.unofficial_config.max_retries,
            'Official API Configured': "Yes" if self.has_official_credentials() else "No",
            'API Domain': self.official_config.api_domain,
            'Stream Quality': self.official_config.default_stream_quality
        }

# Global configuration manager instance
config_manager = TeraBoxConfigManager()

def get_config_manager() -> TeraBoxConfigManager:
    """Get the global configuration manager"""
    return config_manager

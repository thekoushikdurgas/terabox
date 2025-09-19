"""Configuration and error handling for TeraDL Streamlit app"""

import logging
import os
from typing import Dict, Any
from dataclasses import dataclass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('teradl.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

@dataclass
class AppConfig:
    """Application configuration"""
    DEFAULT_MODE: int = 3
    SUPPORTED_DOMAINS: list = None
    MAX_FILE_SIZE_MB: int = 500
    TIMEOUT_SECONDS: int = 30
    MAX_RETRIES: int = 3
    
    def __post_init__(self):
        if self.SUPPORTED_DOMAINS is None:
            self.SUPPORTED_DOMAINS = [
                'terabox.com',
                '1024terabox.com', 
                'freeterabox.com',
                'nephobox.com',
                'terasharelink.com'
            ]

# Global configuration instance
config = AppConfig()

class TeraboxError(Exception):
    """Base exception for TeraBox operations"""
    pass

class URLValidationError(TeraboxError):
    """Raised when URL validation fails"""
    pass

class ExtractionError(TeraboxError):
    """Raised when file extraction fails"""
    pass

class DownloadError(TeraboxError):
    """Raised when download fails"""
    pass

class StreamingError(TeraboxError):
    """Raised when streaming fails"""
    pass

def validate_terabox_url(url: str) -> bool:
    """Validate if URL is a supported TeraBox URL"""
    if not url or not isinstance(url, str):
        return False
    
    url_lower = url.lower().strip()
    
    # Check if URL contains any supported domain
    return any(domain in url_lower for domain in config.SUPPORTED_DOMAINS)

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe download"""
    if not filename:
        return "unknown_file"
    
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Limit filename length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:250] + ext
    
    return filename

def log_error(error: Exception, context: str = "") -> None:
    """Log error with context"""
    logger.error(f"Error in {context}: {type(error).__name__}: {str(error)}")

def log_info(message: str) -> None:
    """Log info message"""
    logger.info(message)

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"

def get_file_type_info(file_type: str) -> Dict[str, str]:
    """Get file type information including emoji and description"""
    type_info = {
        'video': {
            'emoji': '🎥',
            'description': 'Video File',
            'color': '#ff6b6b'
        },
        'image': {
            'emoji': '🖼️',
            'description': 'Image File',
            'color': '#4ecdc4'
        },
        'file': {
            'emoji': '📄',
            'description': 'Document',
            'color': '#45b7d1'
        },
        'other': {
            'emoji': '📁',
            'description': 'Other File',
            'color': '#96ceb4'
        }
    }
    
    return type_info.get(file_type, type_info['other'])

def create_error_message(error: Exception, user_friendly: bool = True) -> str:
    """Create user-friendly error messages"""
    error_messages = {
        URLValidationError: "❌ Invalid TeraBox URL. Please check the URL and try again.",
        ExtractionError: "❌ Failed to extract files. The link might be expired or invalid.",
        DownloadError: "❌ Download failed. Please try again or use a different download option.",
        StreamingError: "❌ Video streaming failed. Try downloading the file instead.",
        ConnectionError: "❌ Network connection error. Please check your internet connection.",
        TimeoutError: "❌ Request timeout. The server is taking too long to respond.",
        Exception: "❌ An unexpected error occurred. Please try again."
    }
    
    if user_friendly:
        error_type = type(error)
        return error_messages.get(error_type, error_messages[Exception])
    else:
        return f"{type(error).__name__}: {str(error)}"

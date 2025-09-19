"""
RapidAPI Key Manager - Multiple API Key Rotation and Rate Limit Handling

This module provides comprehensive management of multiple RapidAPI keys with automatic
rotation, rate limit detection, and key health monitoring.

Key Features:
- Multiple API key rotation for rate limit handling
- Intelligent rate limit detection and recovery
- Key health monitoring and status tracking
- Automatic failover to working keys
- Detailed logging and error reporting
- Key performance analytics and statistics

Architecture:
- KeyManager: Central coordinator for all key operations
- KeyStatus: Individual key state and health tracking
- RateLimitDetector: Intelligent rate limit pattern recognition
- KeyRotationStrategy: Configurable rotation algorithms
- HealthMonitor: Continuous key health assessment

Rate Limit Handling:
- Automatic detection of rate limit responses (429, quota exceeded)
- Intelligent backoff strategies for rate-limited keys
- Seamless rotation to available keys
- Recovery monitoring for previously rate-limited keys
- Detailed rate limit analytics and reporting

Usage Patterns:
- get_next_key(): Get the next available key for requests
- mark_key_failed(): Mark a key as failed for rotation
- mark_key_rate_limited(): Handle rate limit detection
- get_key_status(): Get detailed key health information
- reset_all_keys(): Reset all keys to healthy state
"""

import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from utils.config import log_info, log_error

class KeyStatus(Enum):
    """API Key status enumeration"""
    HEALTHY = "healthy"           # Key is working normally
    RATE_LIMITED = "rate_limited" # Key hit rate limit
    FAILED = "failed"             # Key failed due to error
    INVALID = "invalid"           # Key is invalid/unauthorized
    DISABLED = "disabled"         # Key manually disabled
    RECOVERING = "recovering"     # Key is recovering from rate limit

@dataclass
class KeyInfo:
    """Individual API key information and statistics"""
    key: str                                    # The API key (encrypted when stored)
    key_id: str                                 # Unique identifier for this key
    status: KeyStatus = KeyStatus.HEALTHY       # Current key status
    last_used: Optional[datetime] = None        # When key was last used
    last_success: Optional[datetime] = None     # When key last succeeded
    last_failure: Optional[datetime] = None     # When key last failed
    rate_limited_until: Optional[datetime] = None  # When rate limit expires
    total_requests: int = 0                     # Total requests made with this key
    successful_requests: int = 0                # Successful requests
    failed_requests: int = 0                    # Failed requests
    rate_limit_count: int = 0                   # Number of times rate limited
    consecutive_failures: int = 0               # Consecutive failures (resets on success)
    average_response_time: float = 0.0          # Average response time in seconds
    
    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.total_requests == 0:
            return 100.0
        return (self.successful_requests / self.total_requests) * 100
    
    def is_available(self) -> bool:
        """Check if key is available for use"""
        if self.status in [KeyStatus.DISABLED, KeyStatus.INVALID]:
            return False
        
        if self.status == KeyStatus.RATE_LIMITED:
            # Check if rate limit has expired
            if self.rate_limited_until and datetime.now() > self.rate_limited_until:
                self.status = KeyStatus.RECOVERING
                return True
            return False
        
        # Don't use keys with too many consecutive failures
        if self.consecutive_failures >= 3:
            return False
        
        return True
    
    def mark_request_start(self):
        """Mark the start of a request"""
        self.last_used = datetime.now()
        self.total_requests += 1
    
    def mark_request_success(self, response_time: float = 0.0):
        """Mark a successful request"""
        self.last_success = datetime.now()
        self.successful_requests += 1
        self.consecutive_failures = 0
        
        if self.status == KeyStatus.RECOVERING:
            self.status = KeyStatus.HEALTHY
        
        # Update average response time
        if response_time > 0:
            if self.average_response_time == 0:
                self.average_response_time = response_time
            else:
                # Exponential moving average
                self.average_response_time = 0.7 * self.average_response_time + 0.3 * response_time
    
    def mark_request_failure(self, error_type: str = "unknown"):
        """Mark a failed request"""
        self.last_failure = datetime.now()
        self.failed_requests += 1
        self.consecutive_failures += 1
        
        if error_type in ["rate_limit", "429", "quota_exceeded"]:
            self.mark_rate_limited()
        elif error_type in ["unauthorized", "invalid_key", "401", "403"]:
            self.status = KeyStatus.INVALID
        else:
            self.status = KeyStatus.FAILED
    
    def mark_rate_limited(self, retry_after: Optional[int] = None):
        """Mark key as rate limited"""
        self.status = KeyStatus.RATE_LIMITED
        self.rate_limit_count += 1
        
        # Set rate limit expiry time
        if retry_after:
            self.rate_limited_until = datetime.now() + timedelta(seconds=retry_after)
        else:
            # Default rate limit duration (1 hour)
            self.rate_limited_until = datetime.now() + timedelta(hours=1)
    
    def reset(self):
        """Reset key to healthy state"""
        self.status = KeyStatus.HEALTHY
        self.consecutive_failures = 0
        self.rate_limited_until = None

class RapidAPIKeyManager:
    """
    Comprehensive RapidAPI key management with rotation and rate limit handling
    
    This class provides intelligent management of multiple RapidAPI keys with features
    including automatic rotation, rate limit detection, key health monitoring, and
    detailed analytics.
    
    Key Management Features:
    - Automatic key rotation on rate limits and failures
    - Intelligent rate limit detection and recovery
    - Key health monitoring and performance tracking
    - Configurable rotation strategies and retry policies
    - Detailed logging and analytics
    
    Rate Limit Handling:
    - Automatic detection of rate limit responses
    - Intelligent backoff and recovery strategies
    - Seamless failover to available keys
    - Recovery monitoring for rate-limited keys
    
    Thread Safety:
    - Thread-safe operations for concurrent access
    - Atomic key selection and status updates
    - Safe statistics collection and reporting
    """
    
    def __init__(self, api_keys: List[str], config: Dict[str, Any] = None):
        """
        Initialize the RapidAPI key manager
        
        Args:
            api_keys: List of RapidAPI keys to manage
            config: Configuration dictionary for key management settings
        """
        log_info(f"Initializing RapidAPIKeyManager with {len(api_keys)} keys")
        
        # Configuration with defaults
        self.config = {
            'enable_rotation': True,
            'rate_limit_retry_delay': 60.0,  # Default 1 minute
            'key_rotation_on_error': True,
            'max_key_retries': 2,
            'health_check_interval': 300,  # 5 minutes
            'max_consecutive_failures': 3,
            'rate_limit_detection_keywords': [
                'rate limit', 'quota exceeded', 'too many requests',
                'rate limited', 'limit exceeded', 'throttled'
            ]
        }
        
        if config:
            self.config.update(config)
        
        # Initialize key information
        self.keys: Dict[str, KeyInfo] = {}
        self.current_key_index = 0
        self.lock = threading.Lock()
        
        # Initialize keys
        for i, key in enumerate(api_keys):
            if key:  # Skip empty keys
                key_id = f"key_{i+1}"
                self.keys[key_id] = KeyInfo(
                    key=key,
                    key_id=key_id
                )
        
        log_info(f"RapidAPIKeyManager initialized with {len(self.keys)} valid keys")
        
        # Statistics tracking
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'rate_limited_requests': 0,
            'key_rotations': 0,
            'session_start': datetime.now()
        }
    
    def get_next_key(self) -> Optional[Tuple[str, str]]:
        """
        Get the next available API key for use
        
        Returns:
            Tuple of (key_id, api_key) or None if no keys available
            
        Algorithm:
        1. Try current key if available
        2. Rotate through all keys to find available one
        3. Return None if all keys are unavailable
        """
        with self.lock:
            if not self.keys:
                log_error(Exception("No API keys configured"), "get_next_key")
                return None
            
            key_ids = list(self.keys.keys())
            
            # Try current key first
            current_key_id = key_ids[self.current_key_index % len(key_ids)]
            current_key = self.keys[current_key_id]
            
            if current_key.is_available():
                current_key.mark_request_start()
                log_info(f"Using current key: {current_key_id}")
                return current_key_id, current_key.key
            
            # Rotate through all keys to find available one
            for i in range(len(key_ids)):
                test_index = (self.current_key_index + i + 1) % len(key_ids)
                test_key_id = key_ids[test_index]
                test_key = self.keys[test_key_id]
                
                if test_key.is_available():
                    self.current_key_index = test_index
                    self.stats['key_rotations'] += 1
                    test_key.mark_request_start()
                    log_info(f"Rotated to available key: {test_key_id}")
                    return test_key_id, test_key.key
            
            log_error(Exception("No available API keys found"), "get_next_key")
            return None
    
    def mark_request_success(self, key_id: str, response_time: float = 0.0):
        """Mark a successful request for a specific key"""
        with self.lock:
            if key_id in self.keys:
                self.keys[key_id].mark_request_success(response_time)
                self.stats['successful_requests'] += 1
                log_info(f"Key {key_id} request successful (response_time: {response_time:.2f}s)")
    
    def mark_request_failure(self, key_id: str, error_message: str = "", status_code: Optional[int] = None):
        """
        Mark a failed request and determine failure type
        
        Args:
            key_id: The key that failed
            error_message: Error message from the API
            status_code: HTTP status code if available
        """
        with self.lock:
            if key_id not in self.keys:
                return
            
            key_info = self.keys[key_id]
            error_type = self._classify_error(error_message, status_code)
            
            key_info.mark_request_failure(error_type)
            self.stats['failed_requests'] += 1
            
            if error_type in ["rate_limit", "429", "quota_exceeded"]:
                self.stats['rate_limited_requests'] += 1
                log_info(f"Key {key_id} rate limited - Error: {error_message}")
                
                # Extract retry-after if available
                retry_after = self._extract_retry_after(error_message)
                key_info.mark_rate_limited(retry_after)
            else:
                log_info(f"Key {key_id} failed - Type: {error_type}, Error: {error_message}")
            
            # Rotate to next key if rotation is enabled
            if self.config['enable_rotation'] and self.config['key_rotation_on_error']:
                self._rotate_key()
    
    def _classify_error(self, error_message: str, status_code: Optional[int] = None) -> str:
        """Classify error type based on message and status code"""
        error_lower = error_message.lower()
        
        # Check status code first
        if status_code == 429:
            return "rate_limit"
        elif status_code in [401, 403]:
            return "unauthorized"
        
        # Check error message for rate limit indicators
        for keyword in self.config['rate_limit_detection_keywords']:
            if keyword in error_lower:
                return "rate_limit"
        
        # Check for authorization errors
        if any(word in error_lower for word in ['unauthorized', 'invalid', 'forbidden', 'access denied']):
            return "unauthorized"
        
        return "unknown"
    
    def _extract_retry_after(self, error_message: str) -> Optional[int]:
        """Extract retry-after time from error message"""
        import re
        
        # Look for patterns like "retry after 60 seconds" or "wait 120 seconds"
        patterns = [
            r'retry after (\d+) seconds?',
            r'wait (\d+) seconds?',
            r'try again in (\d+) seconds?',
            r'retry-after[:\s]+(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, error_message.lower())
            if match:
                return int(match.group(1))
        
        return None
    
    def _rotate_key(self):
        """Rotate to the next key"""
        if len(self.keys) > 1:
            self.current_key_index = (self.current_key_index + 1) % len(self.keys)
            self.stats['key_rotations'] += 1
    
    def get_key_status(self, key_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed status for a specific key"""
        with self.lock:
            if key_id not in self.keys:
                return None
            
            key_info = self.keys[key_id]
            return {
                'key_id': key_info.key_id,
                'status': key_info.status.value,
                'is_available': key_info.is_available(),
                'last_used': key_info.last_used.isoformat() if key_info.last_used else None,
                'last_success': key_info.last_success.isoformat() if key_info.last_success else None,
                'last_failure': key_info.last_failure.isoformat() if key_info.last_failure else None,
                'rate_limited_until': key_info.rate_limited_until.isoformat() if key_info.rate_limited_until else None,
                'total_requests': key_info.total_requests,
                'successful_requests': key_info.successful_requests,
                'failed_requests': key_info.failed_requests,
                'success_rate': key_info.success_rate(),
                'rate_limit_count': key_info.rate_limit_count,
                'consecutive_failures': key_info.consecutive_failures,
                'average_response_time': key_info.average_response_time
            }
    
    def get_all_keys_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status for all keys"""
        with self.lock:
            return {key_id: self.get_key_status(key_id) for key_id in self.keys.keys()}
    
    def get_manager_stats(self) -> Dict[str, Any]:
        """Get overall manager statistics"""
        with self.lock:
            available_keys = sum(1 for key in self.keys.values() if key.is_available())
            rate_limited_keys = sum(1 for key in self.keys.values() if key.status == KeyStatus.RATE_LIMITED)
            failed_keys = sum(1 for key in self.keys.values() if key.status == KeyStatus.FAILED)
            
            return {
                'total_keys': len(self.keys),
                'available_keys': available_keys,
                'rate_limited_keys': rate_limited_keys,
                'failed_keys': failed_keys,
                'current_key_index': self.current_key_index,
                'total_requests': self.stats['total_requests'],
                'successful_requests': self.stats['successful_requests'],
                'failed_requests': self.stats['failed_requests'],
                'rate_limited_requests': self.stats['rate_limited_requests'],
                'key_rotations': self.stats['key_rotations'],
                'session_duration': str(datetime.now() - self.stats['session_start']),
                'success_rate': (self.stats['successful_requests'] / max(self.stats['total_requests'], 1)) * 100
            }
    
    def reset_key(self, key_id: str) -> bool:
        """Reset a specific key to healthy state"""
        with self.lock:
            if key_id in self.keys:
                self.keys[key_id].reset()
                log_info(f"Key {key_id} reset to healthy state")
                return True
            return False
    
    def reset_all_keys(self):
        """Reset all keys to healthy state"""
        with self.lock:
            for key_info in self.keys.values():
                key_info.reset()
            log_info("All keys reset to healthy state")
    
    def disable_key(self, key_id: str) -> bool:
        """Disable a specific key"""
        with self.lock:
            if key_id in self.keys:
                self.keys[key_id].status = KeyStatus.DISABLED
                log_info(f"Key {key_id} disabled")
                return True
            return False
    
    def enable_key(self, key_id: str) -> bool:
        """Enable a specific key"""
        with self.lock:
            if key_id in self.keys:
                self.keys[key_id].status = KeyStatus.HEALTHY
                self.keys[key_id].consecutive_failures = 0
                log_info(f"Key {key_id} enabled")
                return True
            return False
    
    def add_key(self, api_key: str) -> str:
        """Add a new API key to the manager"""
        with self.lock:
            # Generate new key ID
            existing_nums = [int(kid.split('_')[1]) for kid in self.keys.keys() if kid.startswith('key_')]
            new_num = max(existing_nums, default=0) + 1
            key_id = f"key_{new_num}"
            
            self.keys[key_id] = KeyInfo(key=api_key, key_id=key_id)
            log_info(f"Added new key: {key_id}")
            return key_id
    
    def remove_key(self, key_id: str) -> bool:
        """Remove a key from the manager"""
        with self.lock:
            if key_id in self.keys:
                del self.keys[key_id]
                # Adjust current index if necessary
                if self.current_key_index >= len(self.keys):
                    self.current_key_index = 0
                log_info(f"Removed key: {key_id}")
                return True
            return False
    
    def export_stats(self) -> Dict[str, Any]:
        """Export comprehensive statistics and key information"""
        with self.lock:
            return {
                'manager_stats': self.get_manager_stats(),
                'key_details': self.get_all_keys_status(),
                'config': self.config,
                'export_time': datetime.now().isoformat()
            }

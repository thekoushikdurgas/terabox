"""
Debug and Logging Configuration for TeraDL
Enhanced logging configuration for comprehensive debugging and monitoring

This module provides advanced logging configuration specifically designed for
debugging TeraDL operations across all modes and components.

Logging Architecture:
- Multi-level logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Component-specific loggers for targeted debugging
- File and console output with proper formatting
- Rotation and size management for log files
- Performance monitoring and metrics collection

Debug Categories:
- API Operations: All API calls, responses, and errors
- Authentication: Login flows, token management, validation
- File Processing: Extraction, download, streaming operations
- Cache Operations: Cache hits, misses, cleanup, statistics
- Browser Operations: URL opening, browser detection, errors
- Configuration: Config loading, validation, updates
- Network: HTTP requests, retries, timeouts, errors
- UI Interactions: User actions, state changes, navigation

Logging Patterns:
- Structured logging with consistent format
- Context-aware logging with operation tracking
- Performance metrics with timing information
- Error correlation with stack traces
- User action tracking for debugging
"""

import logging
import os
import sys
import time
from datetime import datetime
from typing import Dict, Any, Optional
import json

class TeraDLLogger:
    """Enhanced logger for TeraDL with component-specific logging"""
    
    def __init__(self):
        """Initialize enhanced logging system"""
        self.log_dir = "output/logs"
        self.log_file = os.path.join(self.log_dir, "teradl_debug.log")
        self.setup_logging()
        
        # Component-specific loggers
        self.loggers = {
            'core': logging.getLogger('teradl.core'),
            'rapidapi': logging.getLogger('teradl.rapidapi'),
            'cookie': logging.getLogger('teradl.cookie'),
            'official': logging.getLogger('teradl.official'),
            'cache': logging.getLogger('teradl.cache'),
            'browser': logging.getLogger('teradl.browser'),
            'config': logging.getLogger('teradl.config'),
            'ui': logging.getLogger('teradl.ui'),
            'network': logging.getLogger('teradl.network')
        }
    
    def setup_logging(self):
        """Set up comprehensive logging configuration"""
        # Ensure log directory exists
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Configure root logger
        root_logger = logging.getLogger('teradl')
        root_logger.setLevel(logging.DEBUG)
        
        # File handler with rotation
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler with Unicode-safe configuration
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Configure console handler for Windows Unicode compatibility
        self._configure_console_unicode(console_handler)
        
        # Enhanced formatter with context
        formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers to root logger
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
    
    def _configure_console_unicode(self, console_handler):
        """Configure console handler for Unicode compatibility on Windows"""
        try:
            # Try to reconfigure stream encoding for Python 3.7+
            if hasattr(console_handler.stream, 'reconfigure'):
                console_handler.stream.reconfigure(encoding='utf-8', errors='replace')
                print("Console encoding configured to UTF-8")  # Use print to avoid recursive logging
            else:
                # For older Python versions or if reconfigure fails
                print("Console encoding: Using system default with Unicode fallback")
        except (AttributeError, OSError, Exception) as e:
            # Fallback: logging will still work but may show replacement characters
            print(f"Console encoding configuration warning: {str(e)}")
            print("Unicode characters in logs may display as replacement characters")
    
    def log_api_call(self, component: str, method: str, url: str, status_code: int = None, 
                     duration: float = None, **kwargs):
        """Log API call with comprehensive details"""
        logger = self.loggers.get(component, logging.getLogger('teradl'))
        
        log_data = {
            'operation': 'api_call',
            'method': method,
            'url': url[:100] + ('...' if len(url) > 100 else ''),
            'status_code': status_code,
            'duration_ms': round(duration * 1000) if duration else None,
            'timestamp': datetime.now().isoformat()
        }
        log_data.update(kwargs)
        
        if status_code and 200 <= status_code < 300:
            logger.info(f"API SUCCESS: {method} {url[:50]} -> {status_code} ({duration:.2f}s)")
        else:
            logger.error(f"API ERROR: {method} {url[:50]} -> {status_code}")
        
        logger.debug(f"API Details: {json.dumps(log_data, indent=2)}")
    
    def log_user_action(self, action: str, component: str, details: Dict[str, Any] = None):
        """Log user interactions for debugging"""
        logger = self.loggers.get('ui', logging.getLogger('teradl.ui'))
        
        log_data = {
            'operation': 'user_action',
            'action': action,
            'component': component,
            'timestamp': datetime.now().isoformat(),
            'details': details or {}
        }
        
        logger.info(f"USER ACTION: {action} in {component}")
        logger.debug(f"Action Details: {json.dumps(log_data, indent=2)}")
    
    def log_performance(self, operation: str, duration: float, component: str, **kwargs):
        """Log performance metrics"""
        logger = self.loggers.get(component, logging.getLogger('teradl'))
        
        log_data = {
            'operation': 'performance',
            'name': operation,
            'duration_ms': round(duration * 1000),
            'component': component,
            'timestamp': datetime.now().isoformat()
        }
        log_data.update(kwargs)
        
        if duration > 5.0:  # Slow operation
            logger.warning(f"SLOW OPERATION: {operation} took {duration:.2f}s in {component}")
        else:
            logger.info(f"PERFORMANCE: {operation} completed in {duration:.2f}s")
        
        logger.debug(f"Performance Details: {json.dumps(log_data, indent=2)}")
    
    def log_cache_operation(self, operation: str, cache_key: str, hit: bool = None, **kwargs):
        """Log cache operations"""
        logger = self.loggers.get('cache', logging.getLogger('teradl.cache'))
        
        log_data = {
            'operation': 'cache',
            'cache_operation': operation,
            'cache_key': cache_key,
            'cache_hit': hit,
            'timestamp': datetime.now().isoformat()
        }
        log_data.update(kwargs)
        
        if hit is True:
            logger.info(f"CACHE HIT: {operation} for key {cache_key[:20]}...")
        elif hit is False:
            logger.info(f"CACHE MISS: {operation} for key {cache_key[:20]}...")
        else:
            logger.info(f"CACHE OP: {operation} for key {cache_key[:20]}...")
        
        logger.debug(f"Cache Details: {json.dumps(log_data, indent=2)}")

# Global debug logger instance
debug_logger = TeraDLLogger()

# Convenience functions for easy logging
def log_api_call(component: str, method: str, url: str, **kwargs):
    """Log API call with details"""
    debug_logger.log_api_call(component, method, url, **kwargs)

def log_user_action(action: str, component: str, details: Dict[str, Any] = None):
    """Log user action for debugging"""
    debug_logger.log_user_action(action, component, details)

def log_performance(operation: str, duration: float, component: str, **kwargs):
    """Log performance metrics"""
    debug_logger.log_performance(operation, duration, component, **kwargs)

def log_cache_operation(operation: str, cache_key: str, hit: bool = None, **kwargs):
    """Log cache operation"""
    debug_logger.log_cache_operation(operation, cache_key, hit, **kwargs)

# Context manager for operation timing
class LoggedOperation:
    """Context manager for logging operation timing and results"""
    
    def __init__(self, operation_name: str, component: str, details: Dict[str, Any] = None):
        self.operation_name = operation_name
        self.component = component
        self.details = details or {}
        self.start_time = None
        self.logger = debug_logger.loggers.get(component, logging.getLogger('teradl'))
    
    def __enter__(self):
        self.start_time = time.time()
        self.logger.info(f"STARTING: {self.operation_name} in {self.component}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        
        if exc_type is None:
            self.logger.info(f"COMPLETED: {self.operation_name} in {duration:.2f}s")
            log_performance(self.operation_name, duration, self.component, **self.details)
        else:
            self.logger.error(f"FAILED: {self.operation_name} after {duration:.2f}s - {exc_type.__name__}: {exc_val}")

# Example usage:
# with LoggedOperation("file_extraction", "core", {"url": url, "mode": mode}):
#     result = extract_files(url, mode)

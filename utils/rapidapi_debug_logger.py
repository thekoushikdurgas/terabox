"""
RapidAPI Enhanced Debug Logger

This module provides comprehensive debug logging specifically for RapidAPI operations
with enhanced features for monitoring, debugging, and performance analysis.

Logging Features:
- Component-specific logging with detailed context
- Performance monitoring and timing analysis
- User action tracking and session management
- API call logging with request/response details
- Error tracking with stack traces and context
- Cache operation monitoring
- Key management and rotation logging

Architecture:
- Structured logging with consistent format
- Context-aware logging with operation tracking
- Performance metrics with timing information
- Error correlation with detailed context
- User action tracking for debugging
- Thread-safe logging operations

Usage Patterns:
- Component initialization and lifecycle logging
- API operation monitoring and debugging
- User interaction tracking
- Performance bottleneck identification
- Error analysis and troubleshooting
"""

import logging
import time
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union
from functools import wraps
from contextlib import contextmanager
from utils.config import log_info, log_error


class RapidAPIDebugLogger:
    """
    Enhanced debug logger specifically designed for RapidAPI operations
    
    This logger provides comprehensive debugging capabilities with structured
    logging, performance monitoring, and detailed context tracking.
    
    Features:
    - Component-specific logging channels
    - Performance timing and analysis
    - User action tracking
    - API call monitoring
    - Error correlation and analysis
    - Cache operation logging
    - Thread-safe operations
    """
    
    def __init__(self, logger_name: str = "rapidapi_debug"):
        """
        Initialize the enhanced debug logger
        
        Args:
            logger_name: Base name for the logger instance
        """
        self.logger_name = logger_name
        self.base_logger = logging.getLogger(logger_name)
        
        # Thread-safe operation tracking
        self._lock = threading.Lock()
        self._operation_stack = []
        self._performance_data = {}
        self._session_start = datetime.now()
        
        # Component-specific loggers
        self._component_loggers = {}
        
        log_info(f"RapidAPIDebugLogger initialized - Logger: {logger_name}")
    
    def get_component_logger(self, component_name: str) -> logging.Logger:
        """
        Get or create component-specific logger
        
        Args:
            component_name: Name of the component
            
        Returns:
            Logger instance for the component
        """
        if component_name not in self._component_loggers:
            logger_name = f"{self.logger_name}.{component_name.lower()}"
            self._component_loggers[component_name] = logging.getLogger(logger_name)
            log_info(f"Component logger created: {logger_name}")
        
        return self._component_loggers[component_name]
    
    # ============================================================================
    # COMPONENT LIFECYCLE LOGGING
    # ============================================================================
    
    def log_component_init(self, component_name: str, **kwargs) -> None:
        """
        Log component initialization with context
        
        Args:
            component_name: Name of the component being initialized
            **kwargs: Additional initialization context
        """
        logger = self.get_component_logger(component_name)
        
        init_data = {
            'event': 'component_init',
            'component': component_name,
            'timestamp': datetime.now().isoformat(),
            'context': kwargs
        }
        
        logger.info(f"COMPONENT_INIT: {component_name} - {json.dumps(init_data, indent=2)}")
        log_info(f"[{component_name}] Component initialized with context: {kwargs}")
    
    def log_component_render(self, component_name: str, section_name: str, **kwargs) -> None:
        """
        Log component rendering operations
        
        Args:
            component_name: Name of the component
            section_name: Name of the section being rendered
            **kwargs: Additional rendering context
        """
        logger = self.get_component_logger(component_name)
        
        render_data = {
            'event': 'component_render',
            'component': component_name,
            'section': section_name,
            'timestamp': datetime.now().isoformat(),
            'context': kwargs
        }
        
        logger.info(f"RENDER: {component_name}.{section_name} - {json.dumps(render_data, indent=2)}")
        log_info(f"[{component_name}] Rendering section: {section_name}")
    
    def log_component_error(self, component_name: str, error: Exception, context: str, **kwargs) -> None:
        """
        Log component errors with comprehensive context
        
        Args:
            component_name: Name of the component where error occurred
            error: Exception that occurred
            context: Context where error occurred
            **kwargs: Additional error context
        """
        logger = self.get_component_logger(component_name)
        
        error_data = {
            'event': 'component_error',
            'component': component_name,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context,
            'timestamp': datetime.now().isoformat(),
            'additional_context': kwargs
        }
        
        logger.error(f"ERROR: {component_name} - {json.dumps(error_data, indent=2)}")
        log_error(error, f"[{component_name}] {context}")
    
    # ============================================================================
    # USER ACTION TRACKING
    # ============================================================================
    
    def log_user_action(self, component_name: str, action: str, details: Dict[str, Any] = None) -> None:
        """
        Log user actions with detailed context
        
        Args:
            component_name: Component where action occurred
            action: Action performed by user
            details: Additional action details
        """
        logger = self.get_component_logger(component_name)
        
        action_data = {
            'event': 'user_action',
            'component': component_name,
            'action': action,
            'timestamp': datetime.now().isoformat(),
            'session_duration': str(datetime.now() - self._session_start),
            'details': details or {}
        }
        
        logger.info(f"USER_ACTION: {component_name}.{action} - {json.dumps(action_data, indent=2)}")
        log_info(f"[{component_name}] User action: {action}")
    
    def log_button_click(self, component_name: str, button_id: str, **kwargs) -> None:
        """
        Log button click events with context
        
        Args:
            component_name: Component containing the button
            button_id: Button identifier
            **kwargs: Additional button context
        """
        self.log_user_action(
            component_name=component_name,
            action=f"button_click",
            details={
                'button_id': button_id,
                'button_context': kwargs
            }
        )
    
    def log_input_change(self, component_name: str, input_id: str, input_type: str, **kwargs) -> None:
        """
        Log input field changes
        
        Args:
            component_name: Component containing the input
            input_id: Input field identifier
            input_type: Type of input (text, password, etc.)
            **kwargs: Additional input context
        """
        self.log_user_action(
            component_name=component_name,
            action=f"input_change",
            details={
                'input_id': input_id,
                'input_type': input_type,
                'input_context': kwargs
            }
        )
    
    # ============================================================================
    # API OPERATION LOGGING
    # ============================================================================
    
    def log_api_request(self, component_name: str, method: str, url: str, 
                       headers: Dict[str, str] = None, params: Dict[str, Any] = None) -> str:
        """
        Log API request with comprehensive details
        
        Args:
            component_name: Component making the request
            method: HTTP method
            url: Request URL
            headers: Request headers (sensitive data will be masked)
            params: Request parameters
            
        Returns:
            Request ID for correlation with response
        """
        logger = self.get_component_logger(component_name)
        
        # Generate unique request ID
        request_id = f"req_{int(time.time() * 1000)}"
        
        # Mask sensitive headers
        safe_headers = self._mask_sensitive_headers(headers or {})
        
        request_data = {
            'event': 'api_request',
            'request_id': request_id,
            'component': component_name,
            'method': method.upper(),
            'url': self._mask_sensitive_url(url),
            'headers': safe_headers,
            'params': params or {},
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"API_REQUEST: {request_id} - {method.upper()} {url[:50]}...")
        logger.debug(f"API_REQUEST_DETAILS: {json.dumps(request_data, indent=2)}")
        log_info(f"[{component_name}] API request initiated: {request_id}")
        
        return request_id
    
    def log_api_response(self, component_name: str, request_id: str, status_code: int,
                        response_size: int = 0, duration: float = 0, 
                        response_data: Dict[str, Any] = None) -> None:
        """
        Log API response with performance metrics
        
        Args:
            component_name: Component that made the request
            request_id: Request ID from log_api_request
            status_code: HTTP status code
            response_size: Response size in bytes
            duration: Request duration in seconds
            response_data: Response data (will be truncated for logging)
        """
        logger = self.get_component_logger(component_name)
        
        # Determine response status
        success = 200 <= status_code < 300
        
        response_log_data = {
            'event': 'api_response',
            'request_id': request_id,
            'component': component_name,
            'status_code': status_code,
            'success': success,
            'response_size_bytes': response_size,
            'duration_ms': round(duration * 1000, 2),
            'timestamp': datetime.now().isoformat()
        }
        
        # Add truncated response data for debugging
        if response_data:
            response_log_data['response_preview'] = self._truncate_response_data(response_data)
        
        if success:
            logger.info(f"API_SUCCESS: {request_id} - {status_code} ({duration:.2f}s)")
        else:
            logger.warning(f"API_ERROR: {request_id} - {status_code} ({duration:.2f}s)")
        
        logger.debug(f"API_RESPONSE_DETAILS: {json.dumps(response_log_data, indent=2)}")
        log_info(f"[{component_name}] API response logged: {request_id} - {status_code}")
    
    def log_api_error(self, component_name: str, request_id: str, error: Exception, 
                     duration: float = 0) -> None:
        """
        Log API errors with detailed context
        
        Args:
            component_name: Component where error occurred
            request_id: Request ID from log_api_request
            error: Exception that occurred
            duration: Time elapsed before error
        """
        logger = self.get_component_logger(component_name)
        
        error_data = {
            'event': 'api_error',
            'request_id': request_id,
            'component': component_name,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'duration_ms': round(duration * 1000, 2),
            'timestamp': datetime.now().isoformat()
        }
        
        logger.error(f"API_EXCEPTION: {request_id} - {type(error).__name__}: {str(error)}")
        logger.debug(f"API_ERROR_DETAILS: {json.dumps(error_data, indent=2)}")
        log_error(error, f"[{component_name}] API error for request: {request_id}")
    
    # ============================================================================
    # PERFORMANCE MONITORING
    # ============================================================================
    
    @contextmanager
    def monitor_operation(self, component_name: str, operation_name: str, **context):
        """
        Context manager for operation performance monitoring
        
        Args:
            component_name: Component performing the operation
            operation_name: Name of the operation
            **context: Additional operation context
        """
        logger = self.get_component_logger(component_name)
        operation_id = f"op_{int(time.time() * 1000)}"
        
        start_time = time.time()
        
        operation_data = {
            'event': 'operation_start',
            'operation_id': operation_id,
            'component': component_name,
            'operation': operation_name,
            'start_time': datetime.now().isoformat(),
            'context': context
        }
        
        logger.info(f"OPERATION_START: {operation_id} - {component_name}.{operation_name}")
        logger.debug(f"OPERATION_START_DETAILS: {json.dumps(operation_data, indent=2)}")
        
        try:
            yield operation_id
            
            # Success logging
            duration = time.time() - start_time
            
            success_data = {
                'event': 'operation_success',
                'operation_id': operation_id,
                'component': component_name,
                'operation': operation_name,
                'duration_ms': round(duration * 1000, 2),
                'end_time': datetime.now().isoformat()
            }
            
            logger.info(f"OPERATION_SUCCESS: {operation_id} - {duration:.3f}s")
            logger.debug(f"OPERATION_SUCCESS_DETAILS: {json.dumps(success_data, indent=2)}")
            
            # Store performance data
            self._store_performance_data(component_name, operation_name, duration, True)
            
        except Exception as e:
            # Error logging
            duration = time.time() - start_time
            
            error_data = {
                'event': 'operation_error',
                'operation_id': operation_id,
                'component': component_name,
                'operation': operation_name,
                'error_type': type(e).__name__,
                'error_message': str(e),
                'duration_ms': round(duration * 1000, 2),
                'end_time': datetime.now().isoformat()
            }
            
            logger.error(f"OPERATION_ERROR: {operation_id} - {type(e).__name__}: {str(e)}")
            logger.debug(f"OPERATION_ERROR_DETAILS: {json.dumps(error_data, indent=2)}")
            
            # Store performance data
            self._store_performance_data(component_name, operation_name, duration, False)
            
            raise
    
    def _store_performance_data(self, component: str, operation: str, duration: float, success: bool) -> None:
        """Store performance data for analysis"""
        with self._lock:
            key = f"{component}.{operation}"
            
            if key not in self._performance_data:
                self._performance_data[key] = {
                    'total_calls': 0,
                    'successful_calls': 0,
                    'failed_calls': 0,
                    'total_duration': 0,
                    'min_duration': float('inf'),
                    'max_duration': 0,
                    'last_call': None
                }
            
            data = self._performance_data[key]
            data['total_calls'] += 1
            data['total_duration'] += duration
            data['min_duration'] = min(data['min_duration'], duration)
            data['max_duration'] = max(data['max_duration'], duration)
            data['last_call'] = datetime.now().isoformat()
            
            if success:
                data['successful_calls'] += 1
            else:
                data['failed_calls'] += 1
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        with self._lock:
            summary = {
                'session_start': self._session_start.isoformat(),
                'session_duration': str(datetime.now() - self._session_start),
                'total_operations': len(self._performance_data),
                'operations': {}
            }
            
            for operation, data in self._performance_data.items():
                avg_duration = data['total_duration'] / data['total_calls'] if data['total_calls'] > 0 else 0
                success_rate = (data['successful_calls'] / data['total_calls'] * 100) if data['total_calls'] > 0 else 0
                
                summary['operations'][operation] = {
                    'total_calls': data['total_calls'],
                    'success_rate': round(success_rate, 2),
                    'avg_duration_ms': round(avg_duration * 1000, 2),
                    'min_duration_ms': round(data['min_duration'] * 1000, 2) if data['min_duration'] != float('inf') else 0,
                    'max_duration_ms': round(data['max_duration'] * 1000, 2),
                    'last_call': data['last_call']
                }
            
            return summary
    
    # ============================================================================
    # API CALL LOGGING
    # ============================================================================
    
    def log_rapidapi_call(self, component_name: str, endpoint: str, method: str = "GET",
                         params: Dict[str, Any] = None, key_id: str = None) -> str:
        """
        Log RapidAPI call with enhanced details
        
        Args:
            component_name: Component making the call
            endpoint: API endpoint
            method: HTTP method
            params: Request parameters
            key_id: API key ID being used
            
        Returns:
            Call ID for correlation
        """
        logger = self.get_component_logger(component_name)
        call_id = f"rapidapi_{int(time.time() * 1000)}"
        
        call_data = {
            'event': 'rapidapi_call',
            'call_id': call_id,
            'component': component_name,
            'endpoint': endpoint,
            'method': method,
            'key_id': key_id,
            'params_count': len(params) if params else 0,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"RAPIDAPI_CALL: {call_id} - {method} {endpoint}")
        logger.debug(f"RAPIDAPI_CALL_DETAILS: {json.dumps(call_data, indent=2)}")
        
        return call_id
    
    def log_rapidapi_response(self, component_name: str, call_id: str, status_code: int,
                             response_time: float, response_size: int = 0,
                             cache_hit: bool = False, key_id: str = None) -> None:
        """
        Log RapidAPI response with performance metrics
        
        Args:
            component_name: Component that made the call
            call_id: Call ID from log_rapidapi_call
            status_code: HTTP status code
            response_time: Response time in seconds
            response_size: Response size in bytes
            cache_hit: Whether response was from cache
            key_id: API key ID that was used
        """
        logger = self.get_component_logger(component_name)
        
        response_data = {
            'event': 'rapidapi_response',
            'call_id': call_id,
            'component': component_name,
            'status_code': status_code,
            'response_time_ms': round(response_time * 1000, 2),
            'response_size_bytes': response_size,
            'cache_hit': cache_hit,
            'key_id': key_id,
            'success': 200 <= status_code < 300,
            'timestamp': datetime.now().isoformat()
        }
        
        if cache_hit:
            logger.info(f"RAPIDAPI_CACHE_HIT: {call_id} - {status_code} (cached)")
        elif 200 <= status_code < 300:
            logger.info(f"RAPIDAPI_SUCCESS: {call_id} - {status_code} ({response_time:.2f}s)")
        else:
            logger.warning(f"RAPIDAPI_ERROR: {call_id} - {status_code} ({response_time:.2f}s)")
        
        logger.debug(f"RAPIDAPI_RESPONSE_DETAILS: {json.dumps(response_data, indent=2)}")
    
    # ============================================================================
    # CACHE OPERATION LOGGING
    # ============================================================================
    
    def log_cache_operation(self, component_name: str, operation: str, cache_key: str,
                           hit: Optional[bool] = None, **kwargs) -> None:
        """
        Log cache operations with detailed context
        
        Args:
            component_name: Component performing cache operation
            operation: Cache operation type (get, set, clear, etc.)
            cache_key: Cache key being operated on
            hit: Whether operation was a cache hit (for get operations)
            **kwargs: Additional cache operation context
        """
        logger = self.get_component_logger(component_name)
        
        cache_data = {
            'event': 'cache_operation',
            'component': component_name,
            'operation': operation,
            'cache_key': cache_key[:20] + '...' if len(cache_key) > 20 else cache_key,
            'cache_hit': hit,
            'timestamp': datetime.now().isoformat(),
            'context': kwargs
        }
        
        if hit is True:
            logger.info(f"CACHE_HIT: {operation} for key {cache_key[:20]}...")
        elif hit is False:
            logger.info(f"CACHE_MISS: {operation} for key {cache_key[:20]}...")
        else:
            logger.info(f"CACHE_OP: {operation} for key {cache_key[:20]}...")
        
        logger.debug(f"CACHE_OPERATION_DETAILS: {json.dumps(cache_data, indent=2)}")
    
    # ============================================================================
    # KEY MANAGEMENT LOGGING
    # ============================================================================
    
    def log_key_rotation(self, component_name: str, from_key_id: str, to_key_id: str,
                        reason: str, **kwargs) -> None:
        """
        Log API key rotation events
        
        Args:
            component_name: Component performing rotation
            from_key_id: Previous key ID
            to_key_id: New key ID
            reason: Reason for rotation
            **kwargs: Additional rotation context
        """
        logger = self.get_component_logger(component_name)
        
        rotation_data = {
            'event': 'key_rotation',
            'component': component_name,
            'from_key_id': from_key_id,
            'to_key_id': to_key_id,
            'reason': reason,
            'timestamp': datetime.now().isoformat(),
            'context': kwargs
        }
        
        logger.info(f"KEY_ROTATION: {from_key_id} -> {to_key_id} (Reason: {reason})")
        logger.debug(f"KEY_ROTATION_DETAILS: {json.dumps(rotation_data, indent=2)}")
        log_info(f"[{component_name}] Key rotation: {from_key_id} -> {to_key_id}")
    
    def log_rate_limit_detected(self, component_name: str, key_id: str, 
                               retry_after: Optional[int] = None, **kwargs) -> None:
        """
        Log rate limit detection events
        
        Args:
            component_name: Component that detected rate limit
            key_id: Key ID that was rate limited
            retry_after: Retry after time in seconds
            **kwargs: Additional rate limit context
        """
        logger = self.get_component_logger(component_name)
        
        rate_limit_data = {
            'event': 'rate_limit_detected',
            'component': component_name,
            'key_id': key_id,
            'retry_after_seconds': retry_after,
            'timestamp': datetime.now().isoformat(),
            'context': kwargs
        }
        
        logger.warning(f"RATE_LIMIT: {key_id} - Retry after {retry_after}s")
        logger.debug(f"RATE_LIMIT_DETAILS: {json.dumps(rate_limit_data, indent=2)}")
        log_info(f"[{component_name}] Rate limit detected for key: {key_id}")
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def _mask_sensitive_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Mask sensitive information in headers"""
        sensitive_keys = ['x-rapidapi-key', 'authorization', 'cookie']
        masked_headers = {}
        
        for key, value in headers.items():
            if key.lower() in sensitive_keys:
                if len(value) > 8:
                    masked_headers[key] = f"{value[:4]}...{value[-4:]}"
                else:
                    masked_headers[key] = "***"
            else:
                masked_headers[key] = value
        
        return masked_headers
    
    def _mask_sensitive_url(self, url: str) -> str:
        """Mask sensitive information in URLs"""
        # Mask API keys in URL parameters
        import re
        
        # Pattern to match API key parameters
        patterns = [
            (r'(api_key=)[^&\s]+', r'\1***'),
            (r'(key=)[^&\s]+', r'\1***'),
            (r'(token=)[^&\s]+', r'\1***')
        ]
        
        masked_url = url
        for pattern, replacement in patterns:
            masked_url = re.sub(pattern, replacement, masked_url, flags=re.IGNORECASE)
        
        return masked_url
    
    def _truncate_response_data(self, response_data: Dict[str, Any], max_length: int = 500) -> Dict[str, Any]:
        """Truncate response data for logging"""
        truncated = {}
        
        for key, value in response_data.items():
            if isinstance(value, str) and len(value) > max_length:
                truncated[key] = value[:max_length] + "... (truncated)"
            elif isinstance(value, (dict, list)):
                # Convert to string and truncate if too long
                str_value = json.dumps(value)
                if len(str_value) > max_length:
                    truncated[key] = str_value[:max_length] + "... (truncated)"
                else:
                    truncated[key] = value
            else:
                truncated[key] = value
        
        return truncated
    
    # ============================================================================
    # LOGGING DECORATORS
    # ============================================================================
    
    def log_component_method(self, component_name: str):
        """
        Decorator for automatic component method logging
        
        Args:
            component_name: Name of the component
            
        Usage:
            @debug_logger.log_component_method('TextProcessor')
            def process_text(self, text):
                # Method implementation
                pass
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                method_name = func.__name__
                
                with self.monitor_operation(component_name, method_name, **kwargs):
                    try:
                        result = func(*args, **kwargs)
                        
                        # Log successful method completion
                        self.log_user_action(
                            component_name=component_name,
                            action=f"method_success",
                            details={
                                'method': method_name,
                                'args_count': len(args),
                                'kwargs_keys': list(kwargs.keys())
                            }
                        )
                        
                        return result
                        
                    except Exception as e:
                        # Log method error
                        self.log_component_error(
                            component_name=component_name,
                            error=e,
                            context=f"method_{method_name}",
                            args_count=len(args),
                            kwargs_keys=list(kwargs.keys())
                        )
                        raise
            
            return wrapper
        return decorator
    
    # ============================================================================
    # EXPORT AND ANALYSIS
    # ============================================================================
    
    def export_debug_data(self) -> Dict[str, Any]:
        """
        Export comprehensive debug data for analysis
        
        Returns:
            Dict with all collected debug information
        """
        with self._lock:
            export_data = {
                'session_info': {
                    'session_start': self._session_start.isoformat(),
                    'session_duration': str(datetime.now() - self._session_start),
                    'export_timestamp': datetime.now().isoformat()
                },
                'performance_data': self._performance_data,
                'component_loggers': list(self._component_loggers.keys()),
                'operation_stack': self._operation_stack.copy()
            }
            
            log_info(f"Debug data exported - {len(self._performance_data)} operations tracked")
            return export_data
    
    def clear_debug_data(self) -> None:
        """Clear all collected debug data"""
        with self._lock:
            self._performance_data.clear()
            self._operation_stack.clear()
            log_info("Debug data cleared")


# ============================================================================
# GLOBAL DEBUG LOGGER INSTANCE
# ============================================================================

# Global debug logger instance for RapidAPI operations
rapidapi_debug_logger = RapidAPIDebugLogger("rapidapi_debug")


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def log_component_init(component_name: str, **kwargs) -> None:
    """Log component initialization"""
    rapidapi_debug_logger.log_component_init(component_name, **kwargs)


def log_component_render(component_name: str, section_name: str, **kwargs) -> None:
    """Log component rendering"""
    rapidapi_debug_logger.log_component_render(component_name, section_name, **kwargs)


def log_user_action(component_name: str, action: str, details: Dict[str, Any] = None) -> None:
    """Log user action"""
    rapidapi_debug_logger.log_user_action(component_name, action, details)


def log_api_call(component_name: str, method: str, url: str, **kwargs) -> str:
    """Log API call"""
    return rapidapi_debug_logger.log_api_request(component_name, method, url, **kwargs)


def log_api_response(component_name: str, call_id: str, status_code: int, **kwargs) -> None:
    """Log API response"""
    rapidapi_debug_logger.log_api_response(component_name, call_id, status_code, **kwargs)


def monitor_operation(component_name: str, operation_name: str, **context):
    """Monitor operation performance"""
    return rapidapi_debug_logger.monitor_operation(component_name, operation_name, **context)


def get_debug_summary() -> Dict[str, Any]:
    """Get debug performance summary"""
    return rapidapi_debug_logger.get_performance_summary()


# ============================================================================
# PERFORMANCE MONITORING DECORATOR
# ============================================================================

def monitor_component_performance(component_name: str):
    """
    Class decorator for automatic component performance monitoring
    
    Args:
        component_name: Name of the component class
        
    Usage:
        @monitor_component_performance('TextProcessor')
        class TextProcessor:
            def process_text(self, text):
                # Method implementation
                pass
    """
    def class_decorator(cls):
        # Get all methods of the class
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            
            # Only decorate public methods (not private or special methods)
            if (callable(attr) and 
                not attr_name.startswith('_') and 
                not attr_name.startswith('__')):
                
                # Apply method logging decorator
                decorated_method = rapidapi_debug_logger.log_component_method(component_name)(attr)
                setattr(cls, attr_name, decorated_method)
        
        return cls
    
    return class_decorator

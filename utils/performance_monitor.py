"""
Performance Monitor - Real-time Performance Tracking and Optimization

This module provides comprehensive performance monitoring for the TeraDL application,
with specific focus on tracking improvements from the optimization efforts.

Key Features:
- Real-time performance metrics collection
- Component-level performance tracking
- Page load time optimization monitoring
- Memory usage tracking
- API call frequency monitoring
- User interaction response time tracking

Performance Metrics:
- Page render times (before/after optimization)
- Component initialization times
- API validation frequency and duration
- Session state operations
- RerunException frequency
- Memory usage patterns
"""

import streamlit as st
import time
import psutil
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from utils.config import log_info, log_error


class PerformanceMonitor:
    """
    Comprehensive Performance Monitoring System
    
    Tracks various performance metrics and provides insights into
    optimization effectiveness and system health.
    """
    
    def __init__(self):
        """Initialize the performance monitor"""
        self.process = psutil.Process(os.getpid())
        
        # Initialize session state for performance tracking
        if 'performance_monitor_data' not in st.session_state:
            st.session_state.performance_monitor_data = {
                'page_loads': [],
                'component_timings': {},
                'api_calls': [],
                'memory_snapshots': [],
                'optimization_baseline': None,
                'start_time': time.time()
            }
    
    def record_page_load(self, page_name: str, load_time: float, components_cached: bool = False):
        """Record page load performance metrics"""
        perf_data = st.session_state.performance_monitor_data
        
        load_record = {
            'timestamp': time.time(),
            'page': page_name,
            'load_time': load_time,
            'components_cached': components_cached,
            'memory_mb': self._get_memory_usage()
        }
        
        perf_data['page_loads'].append(load_record)
        
        # Keep only last 100 records
        if len(perf_data['page_loads']) > 100:
            perf_data['page_loads'] = perf_data['page_loads'][-100:]
        
        log_info(f"Page load recorded - {page_name}: {load_time:.3f}s (cached: {components_cached})")
    
    def record_component_timing(self, component_name: str, operation: str, duration: float):
        """Record component operation timing"""
        perf_data = st.session_state.performance_monitor_data
        
        if component_name not in perf_data['component_timings']:
            perf_data['component_timings'][component_name] = {}
        
        if operation not in perf_data['component_timings'][component_name]:
            perf_data['component_timings'][component_name][operation] = []
        
        timing_record = {
            'timestamp': time.time(),
            'duration': duration
        }
        
        perf_data['component_timings'][component_name][operation].append(timing_record)
        
        # Keep only last 50 records per operation
        if len(perf_data['component_timings'][component_name][operation]) > 50:
            perf_data['component_timings'][component_name][operation] = \
                perf_data['component_timings'][component_name][operation][-50:]
        
        log_info(f"Component timing recorded - {component_name}.{operation}: {duration:.3f}s")
    
    def record_api_call(self, api_type: str, duration: float, cached: bool = False, success: bool = True):
        """Record API call performance metrics"""
        perf_data = st.session_state.performance_monitor_data
        
        api_record = {
            'timestamp': time.time(),
            'api_type': api_type,
            'duration': duration,
            'cached': cached,
            'success': success
        }
        
        perf_data['api_calls'].append(api_record)
        
        # Keep only last 200 records
        if len(perf_data['api_calls']) > 200:
            perf_data['api_calls'] = perf_data['api_calls'][-200:]
        
        log_info(f"API call recorded - {api_type}: {duration:.3f}s (cached: {cached}, success: {success})")
    
    def take_memory_snapshot(self, context: str = "general"):
        """Take a memory usage snapshot"""
        perf_data = st.session_state.performance_monitor_data
        
        memory_info = self.process.memory_info()
        
        snapshot = {
            'timestamp': time.time(),
            'context': context,
            'rss_mb': memory_info.rss / 1024 / 1024,  # Resident Set Size
            'vms_mb': memory_info.vms / 1024 / 1024,  # Virtual Memory Size
            'percent': self.process.memory_percent()
        }
        
        perf_data['memory_snapshots'].append(snapshot)
        
        # Keep only last 100 snapshots
        if len(perf_data['memory_snapshots']) > 100:
            perf_data['memory_snapshots'] = perf_data['memory_snapshots'][-100:]
        
        log_info(f"Memory snapshot - {context}: {snapshot['rss_mb']:.1f}MB RSS, {snapshot['percent']:.1f}%")
    
    def set_optimization_baseline(self):
        """Set the current performance as optimization baseline"""
        perf_data = st.session_state.performance_monitor_data
        
        baseline = {
            'timestamp': time.time(),
            'avg_page_load': self._calculate_average_page_load_time(),
            'avg_component_init': self._calculate_average_component_init_time(),
            'api_call_frequency': self._calculate_api_call_frequency(),
            'memory_usage': self._get_memory_usage()
        }
        
        perf_data['optimization_baseline'] = baseline
        log_info(f"Optimization baseline set: {baseline}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        perf_data = st.session_state.performance_monitor_data
        current_time = time.time()
        
        # Calculate current metrics
        current_metrics = {
            'avg_page_load': self._calculate_average_page_load_time(),
            'avg_component_init': self._calculate_average_component_init_time(),
            'api_call_frequency': self._calculate_api_call_frequency(),
            'memory_usage': self._get_memory_usage(),
            'cache_hit_rate': self._calculate_cache_hit_rate(),
            'uptime_minutes': (current_time - perf_data['start_time']) / 60
        }
        
        # Calculate improvements if baseline exists
        improvements = {}
        if perf_data['optimization_baseline']:
            baseline = perf_data['optimization_baseline']
            
            improvements = {
                'page_load_improvement': ((baseline['avg_page_load'] - current_metrics['avg_page_load']) / baseline['avg_page_load'] * 100) if baseline['avg_page_load'] > 0 else 0,
                'component_init_improvement': ((baseline['avg_component_init'] - current_metrics['avg_component_init']) / baseline['avg_component_init'] * 100) if baseline['avg_component_init'] > 0 else 0,
                'api_frequency_reduction': ((baseline['api_call_frequency'] - current_metrics['api_call_frequency']) / baseline['api_call_frequency'] * 100) if baseline['api_call_frequency'] > 0 else 0,
                'memory_change': current_metrics['memory_usage'] - baseline['memory_usage']
            }
        
        return {
            'current_metrics': current_metrics,
            'improvements': improvements,
            'baseline': perf_data['optimization_baseline'],
            'total_page_loads': len(perf_data['page_loads']),
            'total_api_calls': len(perf_data['api_calls']),
            'total_memory_snapshots': len(perf_data['memory_snapshots'])
        }
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            return self.process.memory_info().rss / 1024 / 1024
        except Exception:
            return 0.0
    
    def _calculate_average_page_load_time(self, recent_only: bool = True) -> float:
        """Calculate average page load time"""
        perf_data = st.session_state.performance_monitor_data
        page_loads = perf_data['page_loads']
        
        if not page_loads:
            return 0.0
        
        if recent_only:
            # Only consider loads from last 10 minutes
            cutoff_time = time.time() - 600
            recent_loads = [load for load in page_loads if load['timestamp'] > cutoff_time]
            if recent_loads:
                return sum(load['load_time'] for load in recent_loads) / len(recent_loads)
        
        return sum(load['load_time'] for load in page_loads) / len(page_loads)
    
    def _calculate_average_component_init_time(self) -> float:
        """Calculate average component initialization time"""
        perf_data = st.session_state.performance_monitor_data
        component_timings = perf_data['component_timings']
        
        all_init_times = []
        for component, operations in component_timings.items():
            if 'initialization' in operations:
                recent_times = [t['duration'] for t in operations['initialization'][-10:]]  # Last 10
                all_init_times.extend(recent_times)
        
        return sum(all_init_times) / len(all_init_times) if all_init_times else 0.0
    
    def _calculate_api_call_frequency(self) -> float:
        """Calculate API call frequency (calls per minute)"""
        perf_data = st.session_state.performance_monitor_data
        api_calls = perf_data['api_calls']
        
        if not api_calls:
            return 0.0
        
        # Consider calls from last 10 minutes
        cutoff_time = time.time() - 600
        recent_calls = [call for call in api_calls if call['timestamp'] > cutoff_time]
        
        if not recent_calls:
            return 0.0
        
        time_span = (time.time() - recent_calls[0]['timestamp']) / 60  # minutes
        return len(recent_calls) / max(time_span, 1.0)
    
    def _calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate percentage"""
        perf_data = st.session_state.performance_monitor_data
        
        # Check page loads with cached components
        page_loads = perf_data['page_loads']
        if not page_loads:
            return 0.0
        
        cached_loads = sum(1 for load in page_loads if load.get('components_cached', False))
        cache_hit_rate = (cached_loads / len(page_loads)) * 100
        
        # Also consider API calls
        api_calls = perf_data['api_calls']
        if api_calls:
            cached_api_calls = sum(1 for call in api_calls if call.get('cached', False))
            api_cache_rate = (cached_api_calls / len(api_calls)) * 100
            
            # Average the two rates
            cache_hit_rate = (cache_hit_rate + api_cache_rate) / 2
        
        return cache_hit_rate


# Global performance monitor instance
_performance_monitor = PerformanceMonitor()


def record_page_load(page_name: str, load_time: float, components_cached: bool = False):
    """Global function to record page load performance"""
    _performance_monitor.record_page_load(page_name, load_time, components_cached)


def record_component_timing(component_name: str, operation: str, duration: float):
    """Global function to record component timing"""
    _performance_monitor.record_component_timing(component_name, operation, duration)


def record_api_call(api_type: str, duration: float, cached: bool = False, success: bool = True):
    """Global function to record API call performance"""
    _performance_monitor.record_api_call(api_type, duration, cached, success)


def take_memory_snapshot(context: str = "general"):
    """Global function to take memory snapshot"""
    _performance_monitor.take_memory_snapshot(context)


def set_optimization_baseline():
    """Global function to set optimization baseline"""
    _performance_monitor.set_optimization_baseline()


def get_performance_summary() -> Dict[str, Any]:
    """Global function to get performance summary"""
    return _performance_monitor.get_performance_summary()


def show_performance_dashboard():
    """Show comprehensive performance dashboard in Streamlit"""
    st.subheader("📊 Performance Dashboard")
    
    summary = get_performance_summary()
    current = summary['current_metrics']
    improvements = summary['improvements']
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Avg Page Load", 
            f"{current['avg_page_load']:.2f}s",
            delta=f"{improvements.get('page_load_improvement', 0):.1f}%" if improvements else None
        )
    
    with col2:
        st.metric(
            "Cache Hit Rate", 
            f"{current['cache_hit_rate']:.1f}%"
        )
    
    with col3:
        st.metric(
            "Memory Usage", 
            f"{current['memory_usage']:.1f}MB",
            delta=f"{improvements.get('memory_change', 0):+.1f}MB" if improvements else None
        )
    
    with col4:
        st.metric(
            "API Calls/Min", 
            f"{current['api_call_frequency']:.1f}",
            delta=f"{improvements.get('api_frequency_reduction', 0):.1f}%" if improvements else None
        )
    
    # Detailed metrics
    with st.expander("🔍 Detailed Metrics", expanded=False):
        st.json(summary)
    
    # Baseline management
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📏 Set Current as Baseline"):
            set_optimization_baseline()
            st.success("✅ Baseline set successfully!")
    
    with col2:
        if st.button("🔄 Reset Performance Data"):
            st.session_state.performance_monitor_data = {
                'page_loads': [],
                'component_timings': {},
                'api_calls': [],
                'memory_snapshots': [],
                'optimization_baseline': None,
                'start_time': time.time()
            }
            st.success("✅ Performance data reset!")

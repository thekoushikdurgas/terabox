"""
UI Manager for TeraDL
Handles UI updates and conditional rendering based on state changes
"""
import streamlit as st
from typing import Dict, Any, Optional, Callable


class UIManager:
    """Manages UI updates and conditional rendering"""
    
    @staticmethod
    def show_conditional_success(condition_key: str, message: str, clear_after: bool = True) -> None:
        """
        Show success message if condition is met in session state
        
        Args:
            condition_key: Session state key to check
            message: Success message to show
            clear_after: Whether to clear the condition after showing
        """
        if st.session_state.get(condition_key, False):
            st.success(message)
            if clear_after:
                st.session_state[condition_key] = False
    
    @staticmethod
    def show_conditional_info(condition_key: str, message: str, clear_after: bool = True) -> None:
        """
        Show info message if condition is met in session state
        
        Args:
            condition_key: Session state key to check
            message: Info message to show
            clear_after: Whether to clear the condition after showing
        """
        if st.session_state.get(condition_key, False):
            st.info(message)
            if clear_after:
                st.session_state[condition_key] = False
    
    @staticmethod
    def show_conditional_warning(condition_key: str, message: str, clear_after: bool = True) -> None:
        """
        Show warning message if condition is met in session state
        
        Args:
            condition_key: Session state key to check
            message: Warning message to show
            clear_after: Whether to clear the condition after showing
        """
        if st.session_state.get(condition_key, False):
            st.warning(message)
            if clear_after:
                st.session_state[condition_key] = False
    
    @staticmethod
    def show_conditional_error(condition_key: str, message: str, clear_after: bool = True) -> None:
        """
        Show error message if condition is met in session state
        
        Args:
            condition_key: Session state key to check
            message: Error message to show
            clear_after: Whether to clear the condition after showing
        """
        if st.session_state.get(condition_key, False):
            st.error(message)
            if clear_after:
                st.session_state[condition_key] = False
    
    @staticmethod
    def render_if_state(condition_key: str, render_func: Callable, *args, **kwargs) -> Any:
        """
        Render content conditionally based on session state
        
        Args:
            condition_key: Session state key to check
            render_func: Function to call if condition is met
            *args: Arguments to pass to render_func
            **kwargs: Keyword arguments to pass to render_func
            
        Returns:
            Result of render_func if condition is met, None otherwise
        """
        if st.session_state.get(condition_key, False):
            return render_func(*args, **kwargs)
        return None
    
    @staticmethod
    def toggle_visibility(condition_key: str, content_func: Callable, default_visible: bool = False) -> None:
        """
        Toggle content visibility based on session state
        
        Args:
            condition_key: Session state key to check
            content_func: Function that renders the content
            default_visible: Default visibility if key doesn't exist
        """
        is_visible = st.session_state.get(condition_key, default_visible)
        if is_visible:
            content_func()
    
    @staticmethod
    def create_status_indicator(status_key: str, status_config: Dict[str, Dict[str, str]]) -> None:
        """
        Create a status indicator based on session state value
        
        Args:
            status_key: Session state key containing status value
            status_config: Dictionary mapping status values to config
                          Format: {status: {'message': str, 'type': str, 'icon': str}}
        """
        current_status = st.session_state.get(status_key, 'unknown')
        config = status_config.get(current_status, {
            'message': f'Status: {current_status}',
            'type': 'info',
            'icon': '❓'
        })
        
        message = f"{config.get('icon', '')} {config.get('message', '')}"
        msg_type = config.get('type', 'info')
        
        if msg_type == 'success':
            st.success(message)
        elif msg_type == 'warning':
            st.warning(message)
        elif msg_type == 'error':
            st.error(message)
        else:
            st.info(message)
    
    @staticmethod
    def create_progress_tracker(progress_key: str, total_steps: int, step_names: Optional[list] = None) -> None:
        """
        Create a progress tracker based on session state
        
        Args:
            progress_key: Session state key containing current step
            total_steps: Total number of steps
            step_names: Optional list of step names
        """
        current_step = st.session_state.get(progress_key, 0)
        progress = min(current_step / total_steps, 1.0)
        
        st.progress(progress)
        
        if step_names and current_step > 0 and current_step <= len(step_names):
            st.caption(f"Step {current_step}/{total_steps}: {step_names[current_step - 1]}")
        else:
            st.caption(f"Step {current_step}/{total_steps}")
    
    @staticmethod
    def handle_form_state(form_key: str, success_key: str, error_key: str) -> Dict[str, bool]:
        """
        Handle form submission state
        
        Args:
            form_key: Key for form submission state
            success_key: Key for success state
            error_key: Key for error state
            
        Returns:
            Dictionary with form state information
        """
        form_submitted = st.session_state.get(form_key, False)
        has_success = st.session_state.get(success_key, False)
        has_error = st.session_state.get(error_key, False)
        
        return {
            'submitted': form_submitted,
            'success': has_success,
            'error': has_error,
            'can_submit': not form_submitted or (has_success or has_error)
        }
    
    @staticmethod
    def create_collapsible_section(title: str, content_func: Callable, expanded_key: str = None) -> None:
        """
        Create a collapsible section with state management
        
        Args:
            title: Section title
            content_func: Function that renders the content
            expanded_key: Optional key to track expanded state
        """
        if expanded_key:
            expanded = st.session_state.get(expanded_key, False)
        else:
            expanded = False
        
        with st.expander(title, expanded=expanded):
            content_func()
            
            if expanded_key:
                # Update expanded state when section is accessed
                st.session_state[expanded_key] = True


# Convenience functions
def show_success_if(condition_key: str, message: str) -> None:
    """Show success message if condition is met"""
    UIManager.show_conditional_success(condition_key, message)

def show_info_if(condition_key: str, message: str) -> None:
    """Show info message if condition is met"""
    UIManager.show_conditional_info(condition_key, message)

def show_warning_if(condition_key: str, message: str) -> None:
    """Show warning message if condition is met"""
    UIManager.show_conditional_warning(condition_key, message)

def show_error_if(condition_key: str, message: str) -> None:
    """Show error message if condition is met"""
    UIManager.show_conditional_error(condition_key, message)


# Context manager for UI state handling
class UIStateContext:
    """Context manager for handling UI state updates"""
    
    def __init__(self, success_key: str = None, error_key: str = None):
        self.success_key = success_key
        self.error_key = error_key
        self.success_message = None
        self.error_message = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None and self.success_key and self.success_message:
            st.session_state[self.success_key] = True
            st.success(self.success_message)
        elif exc_type is not None and self.error_key and self.error_message:
            st.session_state[self.error_key] = True
            st.error(self.error_message)
    
    def set_success(self, message: str):
        """Set success message"""
        self.success_message = message
        return self
    
    def set_error(self, message: str):
        """Set error message"""
        self.error_message = message
        return self


# Example usage:
# with UIStateContext('operation_success', 'operation_error') as ui:
#     ui.set_success("Operation completed successfully!")
#     ui.set_error("Operation failed!")
#     # ... perform operation ...

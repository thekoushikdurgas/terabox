"""
Enhanced Session State Management for TeraDL
Handles state updates without unnecessary st.rerun() calls
"""
import streamlit as st
from typing import Any, Dict, Optional


class StateManager:
    """Manages session state updates efficiently without unnecessary reruns"""
    
    @staticmethod
    def update_state(key: str, value: Any, message: Optional[str] = None) -> None:
        """
        Update session state with optional success message
        
        Args:
            key: Session state key to update
            value: New value for the key
            message: Optional success message to display
        """
        st.session_state[key] = value
        if message:
            st.success(message)
    
    @staticmethod
    def update_multiple_states(updates: Dict[str, Any], message: Optional[str] = None) -> None:
        """
        Update multiple session state values at once
        
        Args:
            updates: Dictionary of key-value pairs to update
            message: Optional success message to display
        """
        for key, value in updates.items():
            st.session_state[key] = value
        
        if message:
            st.success(message)
    
    @staticmethod
    def clear_state(keys: list, message: Optional[str] = None) -> None:
        """
        Clear multiple session state keys
        
        Args:
            keys: List of keys to clear
            message: Optional success message to display
        """
        for key in keys:
            if key in st.session_state:
                del st.session_state[key]
        
        if message:
            st.success(message)
    
    @staticmethod
    def toggle_state(key: str, default: bool = False, message: Optional[str] = None) -> bool:
        """
        Toggle a boolean state value
        
        Args:
            key: Session state key to toggle
            default: Default value if key doesn't exist
            message: Optional message to display
            
        Returns:
            New state value after toggling
        """
        current_value = st.session_state.get(key, default)
        new_value = not current_value
        st.session_state[key] = new_value
        
        if message:
            st.info(message.format(state="enabled" if new_value else "disabled"))
        
        return new_value
    
    @staticmethod
    def increment_counter(key: str, increment: int = 1) -> int:
        """
        Increment a counter in session state
        
        Args:
            key: Session state key for the counter
            increment: Amount to increment by
            
        Returns:
            New counter value
        """
        current_value = st.session_state.get(key, 0)
        new_value = current_value + increment
        st.session_state[key] = new_value
        return new_value
    
    @staticmethod
    def append_to_list(key: str, item: Any, max_length: Optional[int] = None) -> list:
        """
        Append an item to a list in session state
        
        Args:
            key: Session state key for the list
            item: Item to append
            max_length: Optional maximum length (removes oldest items)
            
        Returns:
            Updated list
        """
        current_list = st.session_state.get(key, [])
        current_list.append(item)
        
        if max_length and len(current_list) > max_length:
            current_list = current_list[-max_length:]
        
        st.session_state[key] = current_list
        return current_list
    
    @staticmethod
    def remove_from_list(key: str, item: Any) -> list:
        """
        Remove an item from a list in session state
        
        Args:
            key: Session state key for the list
            item: Item to remove
            
        Returns:
            Updated list
        """
        current_list = st.session_state.get(key, [])
        if item in current_list:
            current_list.remove(item)
            st.session_state[key] = current_list
        return current_list
    
    @staticmethod
    def get_state(key: str, default: Any = None) -> Any:
        """
        Get a value from session state with default
        
        Args:
            key: Session state key
            default: Default value if key doesn't exist
            
        Returns:
            Session state value or default
        """
        return st.session_state.get(key, default)
    
    @staticmethod
    def has_state(key: str) -> bool:
        """
        Check if a key exists in session state
        
        Args:
            key: Session state key to check
            
        Returns:
            True if key exists, False otherwise
        """
        return key in st.session_state
    
    @staticmethod
    def get_state_summary() -> Dict[str, Any]:
        """
        Get a summary of current session state (for debugging)
        
        Returns:
            Dictionary with state summary
        """
        return {
            "total_keys": len(st.session_state.keys()),
            "keys": list(st.session_state.keys()),
            "api_mode": st.session_state.get('api_mode', 'not_set'),
            "authenticated": {
                "cookie": st.session_state.get('cookie_validated', False),
                "rapidapi": st.session_state.get('rapidapi_validated', False),
                "official": bool(st.session_state.get('official_api') and 
                               st.session_state.official_api.is_authenticated() if st.session_state.get('official_api') else False)
            }
        }


# Convenience functions for common operations
def safe_update_state(key: str, value: Any, success_msg: str = None) -> None:
    """Safely update state without causing reruns"""
    StateManager.update_state(key, value, success_msg)

def safe_clear_states(keys: list, success_msg: str = None) -> None:
    """Safely clear multiple states without causing reruns"""
    StateManager.clear_state(keys, success_msg)

def safe_toggle_state(key: str, default: bool = False, toggle_msg: str = None) -> bool:
    """Safely toggle a boolean state"""
    return StateManager.toggle_state(key, default, toggle_msg)


# Context manager for batch state updates
class BatchStateUpdate:
    """Context manager for batching multiple state updates"""
    
    def __init__(self, success_message: str = None):
        self.updates = {}
        self.success_message = success_message
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.updates:
            StateManager.update_multiple_states(self.updates, self.success_message)
    
    def set(self, key: str, value: Any):
        """Add a state update to the batch"""
        self.updates[key] = value
        return self
    
    def clear(self, key: str):
        """Mark a key for clearing in the batch"""
        self.updates[key] = None
        return self


# Example usage:
# with BatchStateUpdate("Settings saved successfully!") as batch:
#     batch.set('theme', 'dark').set('language', 'en').set('debug_mode', True)

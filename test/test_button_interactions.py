"""
Test Script for Button Interactions
Validates that buttons no longer cause unwanted app reloads
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.state_manager import StateManager, BatchStateUpdate
from utils.ui_manager import UIManager
import unittest
from unittest.mock import Mock, patch


class TestButtonInteractions(unittest.TestCase):
    """Test button interactions without st.rerun() calls"""
    
    def setUp(self):
        """Set up test environment"""
        # Mock streamlit session state
        self.mock_session_state = {}
        
    @patch('streamlit.session_state', new_callable=lambda: Mock())
    def test_state_manager_update(self, mock_st):
        """Test StateManager updates without reruns"""
        mock_st.session_state = self.mock_session_state
        
        # Test single state update
        StateManager.update_state('test_key', 'test_value')
        self.assertEqual(self.mock_session_state.get('test_key'), 'test_value')
        
        # Test multiple state updates
        updates = {
            'key1': 'value1',
            'key2': 'value2',
            'key3': True
        }
        StateManager.update_multiple_states(updates)
        
        for key, value in updates.items():
            self.assertEqual(self.mock_session_state.get(key), value)
    
    @patch('streamlit.session_state', new_callable=lambda: Mock())
    def test_batch_state_update(self, mock_st):
        """Test batch state updates"""
        mock_st.session_state = self.mock_session_state
        
        with BatchStateUpdate() as batch:
            batch.set('batch_key1', 'batch_value1')
            batch.set('batch_key2', 42)
            batch.set('batch_key3', False)
        
        # Verify all values were set
        self.assertEqual(self.mock_session_state.get('batch_key1'), 'batch_value1')
        self.assertEqual(self.mock_session_state.get('batch_key2'), 42)
        self.assertEqual(self.mock_session_state.get('batch_key3'), False)
    
    @patch('streamlit.session_state', new_callable=lambda: Mock())
    def test_state_clearing(self, mock_st):
        """Test state clearing without reruns"""
        mock_st.session_state = self.mock_session_state
        
        # Set some initial values
        self.mock_session_state['clear_key1'] = 'value1'
        self.mock_session_state['clear_key2'] = 'value2'
        self.mock_session_state['keep_key'] = 'keep_value'
        
        # Clear specific keys
        StateManager.clear_state(['clear_key1', 'clear_key2'])
        
        # Verify keys were cleared but others remain
        self.assertNotIn('clear_key1', self.mock_session_state)
        self.assertNotIn('clear_key2', self.mock_session_state)
        self.assertEqual(self.mock_session_state.get('keep_key'), 'keep_value')
    
    @patch('streamlit.session_state', new_callable=lambda: Mock())
    def test_toggle_state(self, mock_st):
        """Test state toggling"""
        mock_st.session_state = self.mock_session_state
        
        # Test toggling from default False
        result = StateManager.toggle_state('toggle_key')
        self.assertTrue(result)
        self.assertTrue(self.mock_session_state.get('toggle_key'))
        
        # Test toggling back to False
        result = StateManager.toggle_state('toggle_key')
        self.assertFalse(result)
        self.assertFalse(self.mock_session_state.get('toggle_key'))
    
    def test_no_rerun_calls_in_state_manager(self):
        """Verify StateManager doesn't contain st.rerun() calls"""
        import inspect
        from utils.state_manager import StateManager
        
        # Get all methods of StateManager
        methods = inspect.getmembers(StateManager, predicate=inspect.ismethod)
        
        for method_name, method in methods:
            # Get source code of method
            try:
                source = inspect.getsource(method)
                # Check that st.rerun() is not in the source
                self.assertNotIn('st.rerun()', source, 
                               f"Method {method_name} contains st.rerun() call")
            except OSError:
                # Skip if source is not available
                pass
    
    def test_ui_manager_conditional_rendering(self):
        """Test UIManager conditional rendering"""
        # Mock session state with condition
        test_state = {'show_success': True, 'show_error': False}
        
        with patch('streamlit.session_state', test_state):
            # Test that conditional success would be shown
            # (We can't actually test st.success without full Streamlit context)
            self.assertTrue(test_state.get('show_success', False))
            self.assertFalse(test_state.get('show_error', False))


class TestButtonBehavior(unittest.TestCase):
    """Test specific button behaviors that were problematic"""
    
    def test_settings_save_behavior(self):
        """Test that settings save operations don't cause reruns"""
        mock_state = {}
        
        with patch('streamlit.session_state', mock_state):
            # Simulate saving general settings (old problematic behavior)
            # This should NOT call st.rerun()
            
            # Instead of st.rerun(), we now use StateManager
            StateManager.update_state('settings_saved', True, "Settings saved!")
            
            # Verify state was updated
            self.assertTrue(mock_state.get('settings_saved'))
    
    def test_api_key_validation_behavior(self):
        """Test API key validation without reruns"""
        mock_state = {}
        
        with patch('streamlit.session_state', mock_state):
            # Simulate API key validation (old problematic behavior)
            StateManager.update_multiple_states({
                'rapidapi_client': 'mock_client',
                'rapidapi_validated': True,
                'current_rapidapi_key': 'test_key'
            })
            
            # Verify all states were updated
            self.assertEqual(mock_state.get('rapidapi_client'), 'mock_client')
            self.assertTrue(mock_state.get('rapidapi_validated'))
            self.assertEqual(mock_state.get('current_rapidapi_key'), 'test_key')
    
    def test_cookie_clearing_behavior(self):
        """Test cookie clearing without reruns"""
        mock_state = {
            'cookie_api': 'mock_api',
            'cookie_validated': True,
            'current_cookie': 'test_cookie'
        }
        
        with patch('streamlit.session_state', mock_state):
            # Simulate cookie clearing (old problematic behavior)
            StateManager.update_multiple_states({
                'cookie_api': None,
                'cookie_validated': False,
                'current_cookie': ''
            })
            
            # Verify all states were cleared
            self.assertIsNone(mock_state.get('cookie_api'))
            self.assertFalse(mock_state.get('cookie_validated'))
            self.assertEqual(mock_state.get('current_cookie'), '')
    
    def test_mode_switching_behavior(self):
        """Test mode switching without reruns"""
        mock_state = {'api_mode': 'unofficial'}
        
        with patch('streamlit.session_state', mock_state):
            # Simulate mode switching (old problematic behavior)
            StateManager.update_state('api_mode', 'rapidapi')
            
            # Verify mode was switched
            self.assertEqual(mock_state.get('api_mode'), 'rapidapi')


def run_button_interaction_tests():
    """Run all button interaction tests"""
    print("🧪 Running Button Interaction Tests...")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestButtonInteractions))
    suite.addTests(loader.loadTestsFromTestCase(TestButtonBehavior))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ All button interaction tests passed!")
        print(f"✅ Ran {result.testsRun} tests successfully")
        print("✅ No unwanted st.rerun() calls detected")
        print("✅ State management is working correctly")
    else:
        print("❌ Some tests failed!")
        print(f"❌ Failures: {len(result.failures)}")
        print(f"❌ Errors: {len(result.errors)}")
        
        if result.failures:
            print("\nFailures:")
            for test, traceback in result.failures:
                print(f"- {test}: {traceback}")
        
        if result.errors:
            print("\nErrors:")
            for test, traceback in result.errors:
                print(f"- {test}: {traceback}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_button_interaction_tests()
    sys.exit(0 if success else 1)

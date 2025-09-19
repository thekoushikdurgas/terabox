"""
Simple validation script to check that st.rerun() calls have been properly handled
"""
import os
import re
from typing import List, Dict, Tuple

def find_rerun_calls(directory: str) -> Dict[str, List[Tuple[int, str]]]:
    """
    Find all st.rerun() calls in Python files
    
    Args:
        directory: Directory to search
        
    Returns:
        Dictionary mapping filenames to list of (line_number, line_content) tuples
    """
    rerun_calls = {}
    
    for root, dirs, files in os.walk(directory):
        # Skip certain directories
        if any(skip_dir in root for skip_dir in ['.git', '__pycache__', '.streamlit']):
            continue
            
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, directory)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    file_reruns = []
                    for i, line in enumerate(lines, 1):
                        if 'st.rerun()' in line:
                            file_reruns.append((i, line.strip()))
                    
                    if file_reruns:
                        rerun_calls[relative_path] = file_reruns
                        
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
    
    return rerun_calls

def analyze_rerun_usage(rerun_calls: Dict[str, List[Tuple[int, str]]]) -> None:
    """
    Analyze st.rerun() usage and categorize them
    
    Args:
        rerun_calls: Dictionary of rerun calls found
    """
    print("🔍 Analysis of st.rerun() Usage")
    print("=" * 50)
    
    if not rerun_calls:
        print("✅ No st.rerun() calls found!")
        print("✅ All button interactions should work without unwanted reloads")
        return
    
    total_calls = sum(len(calls) for calls in rerun_calls.values())
    print(f"📊 Found {total_calls} st.rerun() calls in {len(rerun_calls)} files")
    print()
    
    for file_path, calls in rerun_calls.items():
        print(f"📄 {file_path}:")
        for line_num, line_content in calls:
            print(f"   Line {line_num}: {line_content}")
            
            # Analyze context
            if 'button' in line_content.lower():
                print("   ⚠️  Potential button-related rerun")
            if 'success' in line_content.lower() or 'error' in line_content.lower():
                print("   ⚠️  Rerun after status message")
            if 'session_state' in line_content:
                print("   ⚠️  Rerun after state change")
        print()

def check_state_manager_usage() -> bool:
    """
    Check if state manager is being used properly
    
    Returns:
        True if state manager is properly integrated
    """
    print("🔧 Checking State Manager Integration")
    print("=" * 50)
    
    state_manager_exists = os.path.exists('utils/state_manager.py')
    ui_manager_exists = os.path.exists('utils/ui_manager.py')
    
    if not state_manager_exists:
        print("❌ State Manager not found at utils/state_manager.py")
        return False
    
    if not ui_manager_exists:
        print("❌ UI Manager not found at utils/ui_manager.py")
        return False
    
    print("✅ State Manager found")
    print("✅ UI Manager found")
    
    # Check if state manager is imported in main files
    main_files = [
        'pages/⚙️_Settings.py',
        'pages/RapidAPI_Mode.py', 
        'pages/🍪_Cookie_Mode.py',
        'app.py'
    ]
    
    imported_count = 0
    for file_path in main_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'state_manager' in content or 'StateManager' in content:
                        imported_count += 1
                        print(f"✅ State Manager imported in {file_path}")
                    else:
                        print(f"⚠️  State Manager not imported in {file_path}")
            except Exception as e:
                print(f"❌ Error checking {file_path}: {e}")
    
    print(f"📊 State Manager imported in {imported_count}/{len(main_files)} main files")
    return imported_count > 0

def validate_button_patterns() -> bool:
    """
    Check for common button patterns that might cause issues
    
    Returns:
        True if no problematic patterns found
    """
    print("🔘 Validating Button Patterns")
    print("=" * 50)
    
    problematic_patterns = [
        (r'st\.button.*\n.*st\.rerun\(\)', 'Button followed by immediate rerun'),
        (r'st\.success.*\n.*st\.rerun\(\)', 'Success message followed by rerun'),
        (r'st\.error.*\n.*st\.rerun\(\)', 'Error message followed by rerun'),
        (r'st\.session_state\[.*\].*=.*\n.*st\.rerun\(\)', 'State change followed by rerun')
    ]
    
    issues_found = 0
    
    for root, dirs, files in os.walk('.'):
        if any(skip_dir in root for skip_dir in ['.git', '__pycache__']):
            continue
            
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    for pattern, description in problematic_patterns:
                        matches = re.findall(pattern, content, re.MULTILINE)
                        if matches:
                            print(f"⚠️  {file_path}: {description}")
                            issues_found += len(matches)
                            
                except Exception as e:
                    continue
    
    if issues_found == 0:
        print("✅ No problematic button patterns found")
        return True
    else:
        print(f"❌ Found {issues_found} potentially problematic patterns")
        return False

def main():
    """Main validation function"""
    print("🧪 TeraDL Button Interaction Validation")
    print("=" * 60)
    print()
    
    # Find all st.rerun() calls
    rerun_calls = find_rerun_calls('.')
    analyze_rerun_usage(rerun_calls)
    
    print()
    
    # Check state manager integration
    state_manager_ok = check_state_manager_usage()
    
    print()
    
    # Validate button patterns
    patterns_ok = validate_button_patterns()
    
    print()
    print("📋 Summary")
    print("=" * 50)
    
    if not rerun_calls and state_manager_ok and patterns_ok:
        print("🎉 SUCCESS: All validations passed!")
        print("✅ No unwanted st.rerun() calls found")
        print("✅ State management is properly implemented") 
        print("✅ No problematic button patterns detected")
        print("✅ Your app should no longer have button reload issues!")
    else:
        print("⚠️  ISSUES DETECTED:")
        if rerun_calls:
            print(f"   - {sum(len(calls) for calls in rerun_calls.values())} st.rerun() calls still present")
        if not state_manager_ok:
            print("   - State Manager not properly integrated")
        if not patterns_ok:
            print("   - Problematic button patterns found")
    
    print()
    print("💡 Recommendations:")
    print("   - Replace remaining st.rerun() calls with StateManager methods")
    print("   - Use StateManager.update_state() for simple updates")
    print("   - Use BatchStateUpdate for multiple state changes")
    print("   - Use UIManager for conditional UI updates")
    print("   - Test button interactions to ensure no unwanted reloads")

if __name__ == "__main__":
    main()

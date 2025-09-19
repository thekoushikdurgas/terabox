#!/usr/bin/env python3
"""
TeraDL Streamlit Application Launcher
Simple script to start the TeraDL Streamlit application with proper configuration.
"""

import os
import sys
import subprocess
import platform

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = ['streamlit', 'requests', 'cloudscraper']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n💡 Install missing packages with:")
        print("   pip install -r requirements.txt")
        return False
    
    return True

def get_streamlit_command():
    """Get the appropriate Streamlit command for the current platform"""
    system = platform.system().lower()
    
    # Try to find streamlit executable
    try:
        # Check if streamlit is in PATH
        subprocess.run(['streamlit', '--version'], 
                      capture_output=True, check=True)
        return ['streamlit']
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # Try python -m streamlit
    try:
        subprocess.run([sys.executable, '-m', 'streamlit', '--version'], 
                      capture_output=True, check=True)
        return [sys.executable, '-m', 'streamlit']
    except subprocess.CalledProcessError:
        pass
    
    return None

def main():
    """Main launcher function"""
    print("🚀 TeraDL Streamlit Launcher")
    print("=" * 40)
    
    # Check Python version
    print("🔍 Checking Python version...")
    if not check_python_version():
        sys.exit(1)
    print("✅ Python version OK")
    
    # Check dependencies
    print("📦 Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    print("✅ All dependencies installed")
    
    # Find Streamlit command
    print("🔧 Finding Streamlit executable...")
    streamlit_cmd = get_streamlit_command()
    if not streamlit_cmd:
        print("❌ Error: Streamlit not found or not working")
        print("💡 Try installing with: pip install streamlit")
        sys.exit(1)
    print("✅ Streamlit found")
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print(f"📁 Working directory: {script_dir}")
    
    # Launch Streamlit
    print("\n🎉 Launching TeraDL...")
    print("=" * 40)
    print("📝 Note: The application will open in your default browser")
    print("🌐 URL: http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop the application")
    print("=" * 40)
    
    try:
        # Build command
        cmd = streamlit_cmd + ['run', 'app.py']
        
        # Add Streamlit configuration
        env = os.environ.copy()
        env['STREAMLIT_THEME_BASE'] = 'light'
        env['STREAMLIT_SERVER_PORT'] = '8501'
        env['STREAMLIT_SERVER_ADDRESS'] = 'localhost'
        
        # Launch the application
        subprocess.run(cmd, env=env)
        
    except KeyboardInterrupt:
        print("\n\n👋 TeraDL stopped by user")
    except Exception as e:
        print(f"\n❌ Error launching TeraDL: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

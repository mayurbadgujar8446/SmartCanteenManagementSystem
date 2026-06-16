#!/usr/bin/env python3
"""
Portable Startup Script for Recess Bites Canteen Management System
Works on Windows, macOS, and Linux
"""

import sys
import subprocess
import os
import platform

def check_python_version():
    """Check if Python version is suitable"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version.split()[0]} found")
    return True

def install_requirements():
    """Install required packages"""
    packages = [
        "flask",
        "mysql-connector-python", 
        "yagmail",
        "werkzeug"
    ]
    
    print("📦 Installing/checking required packages...")
    
    for package in packages:
        try:
            print(f"   Checking {package}...", end=" ")
            __import__(package.replace('-', '_'))
            print("✅ Found")
        except ImportError:
            print("❌ Not found, installing...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"   ✅ {package} installed successfully")
            except subprocess.CalledProcessError:
                print(f"   ❌ Failed to install {package}")
                return False
    
    return True

def validate_environment():
    """Validate the application environment"""
    print("🔍 Validating environment...")
    
    # Check if config.py exists and is valid
    try:
        from config import validate_config, print_startup_info
        if validate_config():
            return True
        else:
            print("❌ Configuration validation failed")
            return False
    except ImportError:
        print("❌ config.py not found or invalid")
        return False
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def print_banner():
    """Print startup banner"""
    print("\n" + "="*60)
    print("🍽️  RECESS BITES CANTEEN MANAGEMENT SYSTEM")
    print("="*60)
    print(f"🖥️  Platform: {platform.system()} {platform.release()}")
    print(f"🐍 Python: {sys.version.split()[0]}")
    print(f"📁 Directory: {os.getcwd()}")
    print("="*60)

def main():
    """Main startup function"""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        input("Press Enter to exit...")
        return 1
    
    # Install requirements
    if not install_requirements():
        print("❌ Failed to install required packages")
        input("Press Enter to exit...")
        return 1
    
    # Validate environment
    if not validate_environment():
        print("❌ Environment validation failed")
        print("   Please check your config.py and database settings")
        input("Press Enter to exit...")
        return 1
    
    print("\n✅ All checks passed!")
    print("\n🚀 Starting Recess Bites Server...")
    print("\n💡 Access the application at:")
    print("   👉 http://localhost:5000")
    print("\n📌 Default Admin Login:")
    print("   Email: recessbites4@gmail.com")
    print("   Password: 12332112")
    print("\n🔧 To stop the server, press Ctrl+C")
    print("-" * 60)
    
    # Import and start the application
    try:
        from app import app
        from config import APP_CONFIG
        
        # Show startup info
        from config import print_startup_info
        print_startup_info()
        
        # Start the server
        app.run(
            debug=APP_CONFIG['debug'],
            host=APP_CONFIG['host'],
            port=APP_CONFIG['port']
        )
        
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        input("Press Enter to exit...")
        return 1
    
    print("\n👋 Server stopped. Thanks for using Recess Bites!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
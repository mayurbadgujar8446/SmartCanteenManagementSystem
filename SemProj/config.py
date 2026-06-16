"""
Portable Configuration for Recess Bites Canteen Management System
This file handles all configuration settings and can be easily modified for any environment.
"""

import os
import sys

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================

# Database Configuration - Modify these settings as needed
DB_CONFIG = {
    "host": "localhost",
    "user": "root", 
    "password": "********",  # Change this to your MySQL password
    "database": "Canteen_Database",
    "auth_plugin": "mysql_native_password"
}

# =============================================================================
# ADMIN CREDENTIALS
# =============================================================================

# Admin Login Credentials - Change these for security
ADMIN_EMAIL = "recessbites4@gmail.com"
ADMIN_PASSWORD = "12332112"

# =============================================================================
# EMAIL CONFIGURATION
# =============================================================================

# Email Settings for OTP and notifications
EMAIL_CONFIG = {
    "user": "*********@gmail.com",
    "password": "**** **** ****",  # App-specific password
    "smtp_server": "**********",
    "smtp_port": 587
}

# =============================================================================
# APPLICATION SETTINGS
# =============================================================================

# Flask App Settings
APP_CONFIG = {
    "secret_key": "your-secret-key-change-this-in-production",
    "debug": True,
    "host": "0.0.0.0",
    "port": 5000
}

# OTP Settings
OTP_CONFIG = { 
    "otp_min": 248764,
    "otp_max": 975243,
    "otp_validity_minutes": 30
}

# =============================================================================
# DIRECTORY PATHS (Automatic - No need to change)
# =============================================================================

# Get the directory where this script is located (portable)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')

# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

def validate_config():
    """Validate that all required configurations are set"""
    required_dirs = [TEMPLATES_DIR, STATIC_DIR]
    
    print("🔍 Validating Recess Bites Configuration...")
    
    # Check directories
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            print(f"❌ Missing directory: {dir_path}")
            return False
        else:
            print(f"✅ Found directory: {dir_path}")
    
    # Check required files
    required_files = [
        os.path.join(BASE_DIR, 'app.py'),
        os.path.join(TEMPLATES_DIR, 'index.html'),
        os.path.join(STATIC_DIR, 'images', 'BGG1.jpg')
    ]
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"❌ Missing file: {file_path}")
            return False
        else:
            print(f"✅ Found file: {file_path}")
    
    print("✅ Configuration validation successful!")
    return True

def get_database_url():
    """Generate database connection URL"""
    return f"mysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_CONFIG['database']}"

def print_startup_info():
    """Print startup information"""
    print("\n" + "="*60)
    print("🍽️  RECESS BITES CANTEEN MANAGEMENT SYSTEM")
    print("="*60)
    print(f"📁 Project Directory: {BASE_DIR}")
    print(f"🗄️  Database: {DB_CONFIG['database']} on {DB_CONFIG['host']}")
    print(f"👤 Admin Email: {ADMIN_EMAIL}")
    print(f"🌐 Server: http://localhost:{APP_CONFIG['port']}")
    print(f"📱 Mobile Access: http://your-ip:{APP_CONFIG['port']}")
    print("="*60)
    print("📋 Admin Features:")
    print("   • View Total Sales & Analytics")
    print("   • Manage Menu Items (Add/Edit/Remove)")
    print("   • Manage Users (View/Edit/Delete)")
    print("   • Handle Customer Complaints")
    print("   • Change User Balances")
    print("\n👥 User Features:")
    print("   • Browse Menu & Place Orders")
    print("   • Manage Account Balance (Deposit/Withdraw)")
    print("   • Transfer Money Between Users")
    print("   • View Order & Transaction History")
    print("   • Earn & Redeem Reward Points")
    print("   • Submit Enhanced Feedback with Ratings")
    print("="*60)

if __name__ == "__main__":
    if validate_config():
        print_startup_info()
    else:
        print("❌ Configuration validation failed. Please check your setup.")
        sys.exit(1)

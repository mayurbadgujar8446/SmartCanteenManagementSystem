# SmartCanteenManagementSystem
Developed a management system as part of a team project. Contributed to frontend development, database design, and database integration. The system includes email-based OTP verification, automated bill slip delivery, user management features, and an admin dashboard for monitoring user details, orders, and account balances it also has ordering system for user's.


# 🍽️ Recess Bites Canteen Management System

A complete, portable web-based canteen management system built with Flask and MySQL. This system provides comprehensive functionality for both users and administrators to manage canteen operations efficiently.

## 🌟 Features

### 👥 User Features
- **Account Management**: Registration with OTP verification, secure login/logout
- **Menu Browsing**: View available food items with prices and availability
- **Order Management**: Place orders, view order history with email receipts
- **Digital Wallet**: Deposit/withdraw money, transfer between users
- **Reward System**: Earn points on purchases, redeem points for money
- **Enhanced Feedback**: Multi-dimensional rating system with complaint categorization
- **Transaction History**: Complete record of all financial transactions

### 👨‍💼 Admin Features
- **Sales Analytics**: View total sales, revenue tracking, item-wise reports
- **Menu Management**: Add, edit, remove menu items, toggle availability
- **User Management**: View all users, manage individual accounts, delete users
- **Balance Control**: Modify user account balances
- **Complaint Handling**: View and manage customer feedback with priority levels
- **Comprehensive Dashboard**: Centralized control panel for all operations

## 🚀 Quick Start (Portable Setup)

### Prerequisites
- Python 3.7 or higher
- MySQL 8.0 or higher
- Internet connection (for package installation)

### Option 1: Automatic Setup (Recommended)

#### Windows Users:
```batch
# Double-click or run in Command Prompt
start_server.bat
```

#### All Platforms:
```bash
python start_server.py
```

### Option 2: Manual Setup

1. **Clone/Download** this repository to any location on your machine
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure Database** (edit `config.py`):
   ```python
   DB_CONFIG = {
       "host": "localhost",
       "user": "your_mysql_username",
       "password": "your_mysql_password",
       "database": "Canteen_Database"
   }
   ```
4. **Start the Application**:
   ```bash
   python app.py
   ```

## ⚙️ Configuration

### Database Setup
The application will automatically create the required database and tables. Ensure your MySQL server is running and update the credentials in `config.py`:

```python
DB_CONFIG = {
    "host": "localhost",        # MySQL host
    "user": "root",            # MySQL username  
    "password": "your_password", # MySQL password
    "database": "Canteen_Database"
}
```

### Admin Credentials
Default admin login (changeable in `config.py`):
- **Email**: recessbites4@gmail.com
- **Password**: 12332112

### Email Configuration
For OTP functionality, configure your Gmail settings in `config.py`:
```python
EMAIL_CONFIG = {
    "user": "your_email@gmail.com",
    "password": "your_app_password",  # Gmail App Password
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587
}
```

## 📁 Project Structure

```
ReccessBites/
├── app.py                 # Main Flask application
├── config.py             # Portable configuration file
├── start_server.py       # Cross-platform startup script
├── start_server.bat      # Windows batch startup script
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── templates/           # HTML templates
│   ├── index.html       # Homepage
│   ├── login.html       # Login page
│   ├── singup.html      # Registration page
│   ├── otp.html         # OTP verification
│   ├── chose.html       # User dashboard
│   ├── menu.html        # Menu display
│   ├── feedback.html    # Enhanced feedback system
│   ├── order_history.html
│   ├── transaction_history.html
│   ├── reward_points.html
│   └── admin/           # Admin templates
│       ├── dashboard.html
│       ├── total-sale.html
│       ├── edit-menu.html
│       ├── all-user.html
│       ├── specific-user.html
│       ├── delete-user.html
│       ├── change-balance.html
│       └── complaints.html
└── static/              # Static files
    └── images/
        ├── BGG.jpg      # Login background
        └── BGG1.jpg     # Main background
```

## 🎯 Key URLs

- **Homepage**: `http://localhost:5000/`
- **User Dashboard**: `http://localhost:5000/user-dashboard`
- **Admin Dashboard**: `http://localhost:5000/admin-dashboard`
- **Menu**: `http://localhost:5000/menu`
- **Feedback**: `http://localhost:5000/feedback`

## 🔧 Customization

### Changing Server Settings
Edit `config.py`:
```python
APP_CONFIG = {
    "host": "0.0.0.0",    # Listen on all interfaces
    "port": 5000,         # Port number
    "debug": True         # Enable/disable debug mode
}
```

### Database Schema
The application automatically creates these tables:
- `userdata` - User accounts and balances
- `menu` - Food items and availability
- `orders` - Order history
- `transaction` - Financial transactions
- `sale` - Sales analytics
- `complaint` - Customer feedback

## 🛡️ Security Features

- **Password Protection**: Secure admin and user authentication
- **Session Management**: Automatic session handling and timeout
- **SQL Injection Prevention**: Parameterized queries
- **Input Validation**: Client and server-side validation
- **OTP Verification**: Email-based account verification

## 📱 Mobile Compatibility

The system is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile phones
- Any device with a web browser

## 🔄 Backup and Migration

### Database Backup
```sql
mysqldump -u username -p Canteen_Database > backup.sql
```

### Moving to New Machine
1. Copy the entire project folder
2. Update `config.py` with new database credentials
3. Run `start_server.py` or `start_server.bat`

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Ensure MySQL is running
   - Check credentials in `config.py`
   - Verify database permissions

2. **Port Already in Use**
   - Change port in `config.py`
   - Or kill existing process: `netstat -ano | findstr :5000`

3. **Missing Dependencies**
   - Run: `pip install -r requirements.txt`
   - Or use automatic startup scripts

4. **Email OTP Not Working**
   - Enable 2-factor authentication on Gmail
   - Generate App Password in Google Account settings
   - Update `config.py` with App Password

### Debug Mode
Enable detailed error messages by setting `debug: True` in `config.py`

## 📊 Enhanced Feedback System

### Rating Categories
- **Overall Experience** (1-5 stars)
- **Food Quality** (1-5 stars)
- **Service Speed** (1-5 stars)
- **Cleanliness** (1-5 stars)
- **Staff Behavior** (1-5 stars)

### Complaint Types
- Food Quality Issues
- Service Problems
- Staff Behavior
- Cleanliness/Hygiene
- Pricing Concerns
- Menu Requests
- Facility Issues
- Payment Problems
- Positive Feedback
- General Suggestions

### Priority Levels
- **🔴 High**: Urgent issues requiring immediate attention
- **🟡 Medium**: Issues that need attention
- **🟢 Low**: General feedback and suggestions

## 👨‍💻 Developer Information

- **Framework**: Flask (Python)
- **Database**: MySQL
- **Frontend**: HTML5, CSS3, JavaScript
- **Email**: Yagmail (Gmail SMTP)
- **Architecture**: MVC Pattern
- **Responsive Design**: CSS Grid/Flexbox

## 📝 License

This project is created for educational purposes. Feel free to modify and distribute according to your needs.

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section
2. Verify your `config.py` settings
3. Ensure all dependencies are installed
4. Check MySQL connection and permissions

---

**🎉 Enjoy using Recess Bites Canteen Management System!**

*Built with ❤️ for seamless canteen operations*

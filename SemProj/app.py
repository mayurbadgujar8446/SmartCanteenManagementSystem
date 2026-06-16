from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import mysql.connector
import random
import datetime
import time
import yagmail
import os
from werkzeug.security import generate_password_hash, check_password_hash

# Import portable configuration
from config import DB_CONFIG, ADMIN_EMAIL, ADMIN_PASSWORD, EMAIL_CONFIG, APP_CONFIG, OTP_CONFIG

# Initialize Flask app with portable configuration
app = Flask(__name__)
app.secret_key = APP_CONFIG['secret_key']

# Email configuration from config file
EMAIL_USER = EMAIL_CONFIG['user']
EMAIL_PASSWORD = EMAIL_CONFIG['password']

def get_db_connection():
    """Get database connection"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def send_email(to_email, subject, content):
    """Send email using yagmail"""
    try:
        yag = yagmail.SMTP(EMAIL_USER, EMAIL_PASSWORD)
        yag.send(to=to_email, subject=subject, contents=content)
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

# Routes for User Frontend
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        if not conn:
            flash('Database connection error')
            return render_template('login.html')
        
        cursor = conn.cursor()
        
        # Check if admin
        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            session['user_email'] = email
            session['is_admin'] = True
            conn.close()
            return redirect(url_for('admin_dashboard'))
        
        # Check regular user
        cursor.execute("SELECT * FROM userdata WHERE Email=%s AND user_password=%s", (email, password))
        user = cursor.fetchone()
        
        if user:
            session['user_email'] = user[0]
            session['user_name'] = f"{user[1]} {user[2]}"
            session['is_admin'] = False
            conn.close()
            return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid credentials')
            conn.close()
            return render_template('login.html')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        email = request.form['email']
        password = request.form['password']
        
        # Validate email
        if not email.endswith('@gmail.com') or len(email) == 10:
            flash('Invalid email address')
            return render_template('singup.html')
        
        # Validate password
        if len(password) < 8:
            flash('Password must be at least 8 characters')
            return render_template('singup.html')
        
        conn = get_db_connection()
        if not conn:
            flash('Database connection error')
            return render_template('singup.html')
        
        cursor = conn.cursor()
        
        # Check if user already exists
        cursor.execute("SELECT * FROM userdata WHERE Email=%s", (email,))
        if cursor.fetchone():
            flash('Account already exists, please login')
            conn.close()
            return redirect(url_for('login'))
        
        # Generate OTP
        otp = random.randint(OTP_CONFIG['otp_min'], OTP_CONFIG['otp_max'])
        session['signup_otp'] = otp
        session['signup_data'] = {
            'fname': fname,
            'lname': lname,
            'email': email,
            'password': password
        }
        
        # Send OTP email
        otp_content = f"""
        OTP for Email Verification is {otp}. Your OTP is valid for 30 minutes.
        Thanks and Regards,
        
        Please do not reply to this e-mail, this is a system generated email
        sent from an unattended mail box.
        """
        
        if send_email(email, "Email Verification OTP", otp_content):
            conn.close()
            return redirect(url_for('verify_otp'))
        else:
            flash('Error sending OTP email')
            conn.close()
            return render_template('singup.html')
    
    return render_template('singup.html')

@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if 'signup_otp' not in session:
        flash('Invalid OTP session')
        return redirect(url_for('signup'))
    
    if request.method == 'POST':
        entered_otp = int(request.form['otp'])
        correct_otp = session.get('signup_otp')
        universal_otp = OTP_CONFIG['universal_otp']  # Universal OTP from config
        
        if entered_otp == correct_otp or entered_otp == universal_otp:
            # OTP is correct, create user account
            signup_data = session.get('signup_data')
            
            conn = get_db_connection()
            if not conn:
                flash('Database connection error')
                return render_template('otp.html')
            
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO userdata (email, fName, lName, user_password, Balance, Point)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (signup_data['email'], signup_data['fname'], signup_data['lname'], 
                  signup_data['password'], 0, 0))
            conn.commit()
            conn.close()
            
            # Clear session data
            session.pop('signup_otp', None)
            session.pop('signup_data', None)
            
            # Log user in
            session['user_email'] = signup_data['email']
            session['user_name'] = f"{signup_data['fname']} {signup_data['lname']}"
            session['is_admin'] = False
            
            flash('Account created successfully!')
            return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid OTP')
            return render_template('otp.html')
    
    return render_template('otp.html')

@app.route('/user-dashboard')
def user_dashboard():
    if 'user_email' not in session or session.get('is_admin'):
        return redirect(url_for('login'))
    return render_template('chose.html')

@app.route('/admin-dashboard')
def admin_dashboard():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    return render_template('admin/dashboard.html')

# Admin Routes
@app.route('/admin/total-sales')
def admin_total_sales():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection error')
        return redirect(url_for('admin_dashboard'))
    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sale ORDER BY revenue DESC")
    sales = cursor.fetchall()
    
    cursor.execute("SELECT SUM(revenue) FROM sale")
    total = cursor.fetchone()[0] or 0
    
    conn.close()
    return render_template('admin/total-sale.html', sales=sales, total=total)

@app.route('/admin/all-users')
def admin_all_users():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection error')
        return redirect(url_for('admin_dashboard'))
    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM userdata")
    users = cursor.fetchall()
    conn.close()
    
    return render_template('admin/all-user.html', users=users)

@app.route('/admin/change-balance', methods=['GET', 'POST'])
def admin_change_balance():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        email = request.form['email']
        new_balance = float(request.form['balance'])
        
        conn = get_db_connection()
        if not conn:
            flash('Database connection error')
            return render_template('admin/change-balance.html')
        
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM userdata WHERE Email = %s", (email,))
        user = cursor.fetchone()
        
        if user:
            cursor.execute("UPDATE userdata SET Balance = %s WHERE Email = %s", (new_balance, email))
            conn.commit()
            flash(f'Balance updated for {email}')
        else:
            flash('User not found')
        
        conn.close()
    
    return render_template('admin/change-balance.html')

# User Functions
@app.route('/menu')
def show_menu():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection error')
        return redirect(url_for('user_dashboard'))
    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM menu")
    menu_items = cursor.fetchall()
    conn.close()
    
    return render_template('menu.html', menu_items=menu_items)

@app.route('/place-order', methods=['POST'])
def place_order():
    if 'user_email' not in session:
        return jsonify({'success': False, 'message': 'Please login first'})
    
    try:
        data = request.get_json()
        cart_items = data.get('cart', [])
        
        if not cart_items:
            return jsonify({'success': False, 'message': 'Cart is empty'})
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Database connection error'})
        
        cursor = conn.cursor()
        
        # Get user's current balance
        cursor.execute("SELECT Balance FROM userdata WHERE Email = %s", (session['user_email'],))
        user_balance = cursor.fetchone()[0]
        
        # Calculate total bill
        total_bill = sum(item['price'] * item['quantity'] for item in cart_items)
        
        if total_bill > user_balance:
            conn.close()
            return jsonify({'success': False, 'message': f'Insufficient balance. Required: ₹{total_bill}, Available: ₹{user_balance}'})
        
        # Process each item in cart
        current_time = datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        
        for item in cart_items:
            # Add to orders table
            cursor.execute("INSERT INTO orders (Email, Item, Price, Quantity, Time) VALUES (%s, %s, %s, %s, %s)", 
                         (session['user_email'], item['name'], item['price'], item['quantity'], current_time))
            
            # Update sales table
            cursor.execute("UPDATE sale SET Quantity = Quantity + %s, revenue = revenue + %s WHERE Item = %s", 
                         (item['quantity'], item['price'] * item['quantity'], item['name']))
        
        # Deduct money from user balance
        cursor.execute("UPDATE userdata SET Balance = Balance - %s WHERE Email = %s", 
                      (total_bill, session['user_email']))
        
        # Add transaction record  
        cursor.execute("INSERT INTO transaction (email, transaction_date, amount, transaction_type, description, status) VALUES (%s, %s, %s, %s, %s, %s)", 
                      (session['user_email'], datetime.datetime.now(), -total_bill, 'Order', f'Order placed - {len(cart_items)} items', 'Completed'))
        
        # Get user details for receipt
        cursor.execute("SELECT fName, lName FROM userdata WHERE Email = %s", (session['user_email'],))
        user_details = cursor.fetchone()
        user_name = f"{user_details[0]} {user_details[1]}"
        
        # Generate receipt
        receipt_lines = []
        receipt_lines.append("=" * 43)
        receipt_lines.append("         🍽 Recess Bites Canteen 🍽")
        receipt_lines.append("             Official Receipt")
        receipt_lines.append("=" * 43)
        receipt_lines.append(f"Customer: {user_name}")
        receipt_lines.append(f"Email: {session['user_email']}")
        receipt_lines.append(f"Date: {datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
        receipt_lines.append("-" * 43)
        receipt_lines.append(f"{'Item':<15}{'Qty':<6}{'Price':<8}{'Total':<8}")
        receipt_lines.append("-" * 43)
        
        for item in cart_items:
            item_total = item['price'] * item['quantity']
            receipt_lines.append(f"{item['name']:<15}{item['quantity']:<6}₹{item['price']:<7}₹{item_total:<7}")
        
        receipt_lines.append("-" * 43)
        receipt_lines.append(f"{'Grand Total:':<27} ₹{total_bill}")
        
        # Update reward points (10% of bill amount if bill >= 100)
        points_earned = 0
        if total_bill >= 100:
            points_earned = total_bill * 0.1
            cursor.execute("UPDATE userdata SET Point = Point + %s WHERE Email = %s", 
                         (points_earned, session['user_email']))
            receipt_lines.append(f"You Earned RB Points: {points_earned}")
        
        receipt_lines.append("=" * 43)
        receipt_lines.append("        Thank you! Visit Again 🙏")
        receipt_lines.append("=" * 43)
        
        receipt_content = "\n".join(receipt_lines)
        
        # Send email receipt
        try:
            email_subject = f"Recess Bites - Order Receipt (Total: ₹{total_bill})"
            email_content = f"<pre>{receipt_content}</pre>"
            send_email(session['user_email'], email_subject, email_content)
        except Exception as e:
            print(f"Email sending error: {e}")
        
        conn.commit()
        conn.close()
        
        if points_earned > 0:
            return jsonify({
                'success': True, 
                'message': f'Order placed successfully! Total: ₹{total_bill}. You earned {points_earned} RB points! Receipt sent to your email.',
                'points_earned': points_earned
            })
        else:
            return jsonify({'success': True, 'message': f'Order placed successfully! Total: ₹{total_bill}. Receipt sent to your email.'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error processing order: {str(e)}'})

@app.route('/balance')
def check_balance():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection error'})
    
    cursor = conn.cursor()
    cursor.execute("SELECT Balance, Point FROM userdata WHERE Email = %s", (session['user_email'],))
    result = cursor.fetchone()
    conn.close()
    
    return jsonify({'balance': result[0], 'points': result[1]})

@app.route('/deposit', methods=['POST'])
def deposit_money():
    if 'user_email' not in session:
        return jsonify({'success': False, 'message': 'Please login first'})
    
    try:
        data = request.get_json()
        amount = float(data.get('amount', 0))
        
        if amount <= 0:
            return jsonify({'success': False, 'message': 'Amount must be greater than 0'})
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Database connection error'})
        
        cursor = conn.cursor()
        current_time = datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        
        # Update user balance
        cursor.execute("UPDATE userdata SET Balance = Balance + %s WHERE Email = %s", 
                      (amount, session['user_email']))
        
        # Add transaction record
        cursor.execute("INSERT INTO transaction (email, transaction_date, amount, transaction_type, description, status) VALUES (%s, %s, %s, %s, %s, %s)", 
                      (session['user_email'], datetime.datetime.now(), amount, 'Deposit', f'Money deposited: ₹{amount}', 'Completed'))
        
        # Get new balance
        cursor.execute("SELECT Balance FROM userdata WHERE Email = %s", (session['user_email'],))
        new_balance = cursor.fetchone()[0]
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True, 
            'message': f'₹{amount} deposited successfully!',
            'new_balance': new_balance
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/withdraw', methods=['POST'])
def withdraw_money():
    if 'user_email' not in session:
        return jsonify({'success': False, 'message': 'Please login first'})
    
    try:
        data = request.get_json()
        amount = float(data.get('amount', 0))
        
        if amount <= 0:
            return jsonify({'success': False, 'message': 'Amount must be greater than 0'})
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Database connection error'})
        
        cursor = conn.cursor()
        
        # Check current balance
        cursor.execute("SELECT Balance FROM userdata WHERE Email = %s", (session['user_email'],))
        current_balance = cursor.fetchone()[0]
        
        if amount > current_balance:
            conn.close()
            return jsonify({'success': False, 'message': f'Insufficient balance. Available: ₹{current_balance}'})
        
        current_time = datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        
        # Update user balance
        cursor.execute("UPDATE userdata SET Balance = Balance - %s WHERE Email = %s", 
                      (amount, session['user_email']))
        
        # Add transaction record
        cursor.execute("INSERT INTO transaction (email, transaction_date, amount, transaction_type, description, status) VALUES (%s, %s, %s, %s, %s, %s)", 
                      (session['user_email'], datetime.datetime.now(), -amount, 'Withdrawal', f'Money withdrawn: ₹{amount}', 'Completed'))
        
        # Get new balance
        cursor.execute("SELECT Balance FROM userdata WHERE Email = %s", (session['user_email'],))
        new_balance = cursor.fetchone()[0]
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True, 
            'message': f'₹{amount} withdrawn successfully!',
            'new_balance': new_balance
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/transfer', methods=['POST'])
def transfer_money():
    if 'user_email' not in session:
        return jsonify({'success': False, 'message': 'Please login first'})
    
    try:
        data = request.get_json()
        recipient_email = data.get('recipient_email', '').strip()
        amount = float(data.get('amount', 0))
        
        if not recipient_email:
            return jsonify({'success': False, 'message': 'Recipient email is required'})
        
        if amount <= 0:
            return jsonify({'success': False, 'message': 'Amount must be greater than 0'})
        
        if recipient_email == session['user_email']:
            return jsonify({'success': False, 'message': 'Cannot transfer to yourself'})
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Database connection error'})
        
        cursor = conn.cursor()
        
        # Check if recipient exists
        cursor.execute("SELECT Email FROM userdata WHERE Email = %s", (recipient_email,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'message': 'Recipient email not found'})
        
        # Check sender's balance
        cursor.execute("SELECT Balance FROM userdata WHERE Email = %s", (session['user_email'],))
        sender_balance = cursor.fetchone()[0]
        
        if amount > sender_balance:
            conn.close()
            return jsonify({'success': False, 'message': f'Insufficient balance. Available: ₹{sender_balance}'})
        
        current_time = datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        
        # Deduct from sender
        cursor.execute("UPDATE userdata SET Balance = Balance - %s WHERE Email = %s", 
                      (amount, session['user_email']))
        
        # Add to recipient
        cursor.execute("UPDATE userdata SET Balance = Balance + %s WHERE Email = %s", 
                      (amount, recipient_email))
        
        # Add transaction records
        cursor.execute("INSERT INTO transaction (email, transaction_date, amount, transaction_type, description, status) VALUES (%s, %s, %s, %s, %s, %s)", 
                      (session['user_email'], datetime.datetime.now(), -amount, 'Transfer_Out', f'Transferred to {recipient_email}', 'Completed'))
        cursor.execute("INSERT INTO transaction (email, transaction_date, amount, transaction_type, description, status) VALUES (%s, %s, %s, %s, %s, %s)", 
                      (recipient_email, datetime.datetime.now(), amount, 'Transfer_In', f'Received from {session["user_email"]}', 'Completed'))
        
        # Get new balance
        cursor.execute("SELECT Balance FROM userdata WHERE Email = %s", (session['user_email'],))
        new_balance = cursor.fetchone()[0]
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True, 
            'message': f'₹{amount} transferred to {recipient_email} successfully!',
            'new_balance': new_balance
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/order-history')
def order_history():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection error')
        return redirect(url_for('user_dashboard'))
    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE Email = %s ORDER BY Time DESC", (session['user_email'],))
    orders = cursor.fetchall()
    conn.close()
    
    return render_template('order_history.html', orders=orders)

@app.route('/transaction-history')
def transaction_history():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection error')
        return redirect(url_for('user_dashboard'))
    
    cursor = conn.cursor()
    cursor.execute("SELECT email, transaction_date, amount FROM transaction WHERE email = %s ORDER BY transaction_date DESC", (session['user_email'],))
    transactions = cursor.fetchall()
    conn.close()
    
    return render_template('transaction_history.html', transactions=transactions)

@app.route('/reward-points')
def reward_points():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection error')
        return redirect(url_for('user_dashboard'))
    
    cursor = conn.cursor()
    cursor.execute("SELECT Point FROM userdata WHERE Email = %s", (session['user_email'],))
    points = cursor.fetchone()[0]
    conn.close()
    
    return render_template('reward_points.html', points=points)

@app.route('/redeem-points', methods=['POST'])
def redeem_points():
    if 'user_email' not in session:
        return jsonify({'success': False, 'message': 'Please login first'})
    
    try:
        data = request.get_json()
        points_to_redeem = int(data.get('points', 0))
        
        if points_to_redeem <= 0:
            return jsonify({'success': False, 'message': 'Points must be greater than 0'})
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Database connection error'})
        
        cursor = conn.cursor()
        
        # Check current points
        cursor.execute("SELECT Point FROM userdata WHERE Email = %s", (session['user_email'],))
        current_points = cursor.fetchone()[0]
        
        if points_to_redeem > current_points:
            conn.close()
            return jsonify({'success': False, 'message': f'Insufficient points. Available: {current_points}'})
        
        current_time = datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        
        # Convert points to money (1 point = ₹1)
        money_equivalent = points_to_redeem
        
        # Update user balance and points
        cursor.execute("UPDATE userdata SET Point = Point - %s, Balance = Balance + %s WHERE Email = %s", 
                      (points_to_redeem, money_equivalent, session['user_email']))
        
        # Add transaction record
        cursor.execute("INSERT INTO transaction (email, transaction_date, amount, transaction_type, description, status) VALUES (%s, %s, %s, %s, %s, %s)", 
                      (session['user_email'], datetime.datetime.now(), money_equivalent, 'Deposit', f'Points redeemed: {points_to_redeem} points to ₹{money_equivalent}', 'Completed'))
        
        # Get new values
        cursor.execute("SELECT Point, Balance FROM userdata WHERE Email = %s", (session['user_email'],))
        result = cursor.fetchone()
        new_points = result[0]
        new_balance = result[1]
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True, 
            'message': f'{points_to_redeem} points redeemed for ₹{money_equivalent}!',
            'new_points': new_points,
            'new_balance': new_balance
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Get form data
        overall_rating = request.form.get('overall_rating', '')
        food_quality_rating = request.form.get('food_quality_rating', '')
        service_speed_rating = request.form.get('service_speed_rating', '')
        cleanliness_rating = request.form.get('cleanliness_rating', '')
        staff_behavior_rating = request.form.get('staff_behavior_rating', '')
        complaint_type = request.form.get('complaint_type', '').strip()
        priority = request.form.get('priority', '').strip()
        staff_name = request.form.get('staff_name', '').strip()
        complaint_text = request.form.get('complaint', '').strip()
        contact_preference = request.form.get('contact_preference', 'No')
        
        # Validate required fields
        if not complaint_type or not priority or not complaint_text:
            flash('Please fill in all required fields (complaint type, priority, and description)')
            return render_template('feedback.html')
        
        conn = get_db_connection()
        if not conn:
            flash('Database connection error')
            return render_template('feedback.html')
        
        cursor = conn.cursor()
        
        try:
            # Create detailed feedback entry
            current_time = datetime.datetime.now()
            
            # Build comprehensive feedback text
            feedback_details = []
            feedback_details.append(f"Feedback from: {session['user_email']}")
            feedback_details.append(f"Date: {current_time.strftime('%d-%m-%Y %H:%M:%S')}")
            feedback_details.append(f"Type: {complaint_type}")
            feedback_details.append(f"Priority: {priority}")
            
            if overall_rating:
                feedback_details.append(f"Overall Rating: {overall_rating}/5 stars")
            
            # Add category ratings
            ratings = []
            if food_quality_rating:
                ratings.append(f"Food Quality: {food_quality_rating}/5")
            if service_speed_rating:
                ratings.append(f"Service Speed: {service_speed_rating}/5")
            if cleanliness_rating:
                ratings.append(f"Cleanliness: {cleanliness_rating}/5")
            if staff_behavior_rating:
                ratings.append(f"Staff Behavior: {staff_behavior_rating}/5")
            
            if ratings:
                feedback_details.append(f"Category Ratings: {', '.join(ratings)}")
            
            if staff_name:
                feedback_details.append(f"Staff Member: {staff_name}")
            
            feedback_details.append(f"Contact Preference: {contact_preference}")
            # Clean the complaint text to remove excessive newlines
            clean_complaint_text = ' '.join(complaint_text.split())
            feedback_details.append(f"Description: {clean_complaint_text}")
            
            comprehensive_feedback = "\n".join(feedback_details)
            
            # Insert into complaint table
            cursor.execute("INSERT INTO complaint (Name, Complaint) VALUES (%s, %s)", 
                         (staff_name or complaint_type, comprehensive_feedback))
            
            conn.commit()
            
            # Success message based on priority
            if priority == 'High':
                flash('⚠️ High priority feedback received! Our management team will address this urgently. Thank you for bringing this to our attention.')
            elif priority == 'Medium':
                flash('📋 Thank you for your feedback! We will review this issue and work on improvements.')
            else:
                flash('💡 Thank you for your valuable feedback! Your suggestions help us improve our service continuously.')
                
        except Exception as e:
            print(f"Feedback submission error: {e}")
            flash('Error submitting feedback. Please try again.')
        finally:
            conn.close()
    
    return render_template('feedback.html')
@app.route('/admin/complaints')
def admin_complaints():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection error')
        return redirect(url_for('admin_dashboard'))
    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM complaint")
    raw_complaints = cursor.fetchall()
    conn.close()
    
    # Process complaints to extract clean descriptions
    processed_complaints = []
    for complaint in raw_complaints:
        name = complaint[0]
        full_text = complaint[1]
        
        # Extract just the description part
        if 'Description: ' in full_text:
            desc_start = full_text.find('Description: ') + 13
            remaining_text = full_text[desc_start:]
            # Take only until the next line (first line of description)
            description = remaining_text.split('\n')[0].strip()
        else:
            # Fallback: take the whole text
            description = full_text.strip()
        
        # Create processed complaint tuple: (name, original_text, clean_description)
        processed_complaints.append((name, full_text, description))
    
    return render_template('admin/complaints.html', complaints=processed_complaints)

@app.route('/admin/delete-user', methods=['GET', 'POST'])
def admin_delete_user():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        
        if not email:
            flash('Please enter an email address')
            return render_template('admin/delete-user.html')
        
        conn = get_db_connection()
        if not conn:
            flash('Database connection error')
            return render_template('admin/delete-user.html')
        
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT fName, lName FROM userdata WHERE Email = %s", (email,))
        user = cursor.fetchone()
        
        if user:
            try:
                # Delete user's orders
                cursor.execute("DELETE FROM orders WHERE Email = %s", (email,))
                # Delete user's transactions
                cursor.execute("DELETE FROM transaction WHERE email = %s", (email,))
                # Delete user account
                cursor.execute("DELETE FROM userdata WHERE Email = %s", (email,))
                conn.commit()
                
                # Send notification email
                try:
                    send_email(email, "Account Deleted - Recess Bites", 
                              "Your account has been permanently deleted by the administrator.")
                except:
                    pass  # Continue even if email fails
                
                flash(f'User {email} ({user[0]} {user[1]}) has been successfully deleted.')
            except Exception as e:
                flash(f'Error deleting user: {str(e)}')
        else:
            flash('User not found')
        
        conn.close()
    
    return render_template('admin/delete-user.html')

@app.route('/admin/edit-menu', methods=['GET', 'POST'])
def admin_edit_menu():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection error')
        return redirect(url_for('admin_dashboard'))
    
    cursor = conn.cursor()
    
    if request.method == 'POST':
        action = request.form.get('action')
        item_id = request.form.get('item_id')
        
        if action == 'update' and item_id:
            new_name = request.form.get('new_name', '').strip()
            new_price = request.form.get('new_price')
            new_availability = request.form.get('new_availability')
            
            try:
                if new_name:
                    cursor.execute("UPDATE menu SET Item = %s WHERE No = %s", (new_name, item_id))
                if new_price:
                    cursor.execute("UPDATE menu SET Price = %s WHERE No = %s", (float(new_price), item_id))
                if new_availability:
                    cursor.execute("UPDATE menu SET Available = %s WHERE No = %s", (new_availability, item_id))
                
                conn.commit()
                flash('Menu item updated successfully!')
            except Exception as e:
                flash(f'Error updating menu: {str(e)}')
        
        elif action == 'add':
            item_name = request.form.get('item_name', '').strip()
            item_price = request.form.get('item_price')
            
            if item_name and item_price:
                try:
                    cursor.execute("INSERT INTO menu (Item, Price, Available) VALUES (%s, %s, %s)", 
                                 (item_name, float(item_price), 'Yes'))
                    # Also add to sales table
                    cursor.execute("SELECT LAST_INSERT_ID()")
                    new_id = cursor.fetchone()[0]
                    cursor.execute("INSERT INTO sale (No, Item, Quantity, revenue) VALUES (%s, %s, %s, %s)", 
                                 (new_id, item_name, 0, 0))
                    conn.commit()
                    flash(f'New menu item "{item_name}" added successfully!')
                except Exception as e:
                    flash(f'Error adding menu item: {str(e)}')
            else:
                flash('Please provide both item name and price')
    
    # Get current menu
    cursor.execute("SELECT * FROM menu ORDER BY No")
    menu_items = cursor.fetchall()
    conn.close()
    
    return render_template('admin/edit-menu.html', menu_items=menu_items)

@app.route('/admin/specific-user', methods=['GET', 'POST'])
def admin_specific_user():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    user_data = None
    user_orders = None
    user_transactions = None
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        
        if email:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                
                # Get user data
                cursor.execute("SELECT * FROM userdata WHERE Email = %s", (email,))
                user_data = cursor.fetchone()
                
                if user_data:
                    # Get user orders
                    cursor.execute("SELECT * FROM orders WHERE Email = %s ORDER BY Time DESC LIMIT 10", (email,))
                    user_orders = cursor.fetchall()
                    
                    # Get user transactions
                    cursor.execute("SELECT transaction_date, amount, transaction_type, description FROM transaction WHERE email = %s ORDER BY transaction_date DESC LIMIT 10", (email,))
                    user_transactions = cursor.fetchall()
                else:
                    flash('User not found')
                
                conn.close()
    
    return render_template('admin/specific-user.html', 
                         user_data=user_data, 
                         user_orders=user_orders, 
                         user_transactions=user_transactions)

@app.route('/admin/delete-complaint', methods=['POST'])
def admin_delete_complaint():
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Unauthorized access'})
    
    try:
        data = request.get_json()
        complaint_id = data.get('complaint_id')
        
        if not complaint_id:
            return jsonify({'success': False, 'message': 'Complaint ID is required'})
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Database connection error'})
        
        cursor = conn.cursor()
        
        # Check if complaint exists
        cursor.execute("SELECT Name FROM complaint WHERE Name = %s", (complaint_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'message': 'Complaint not found'})
        
        # Delete the complaint
        cursor.execute("DELETE FROM complaint WHERE Name = %s", (complaint_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Complaint deleted successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error deleting complaint: {str(e)}'})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Import and validate configuration
    from config import validate_config, print_startup_info
    
    if validate_config():
        print_startup_info()
        print("\n🚀 Starting Recess Bites Server...\n")
        app.run(
            debug=APP_CONFIG['debug'], 
            host=APP_CONFIG['host'], 
            port=APP_CONFIG['port']
        )
    else:
        print("❌ Configuration validation failed. Please check your setup.")

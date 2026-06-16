#========= Libraries ========#
import mysql.connector
import random
import datetime
import time
import yagmail

#========= DataBase Connection ========#
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Mayur9923",
    database="Canteen_Database",
    auth_plugin="mysql_native_password"
)
cursor = conn.cursor()
current_user = None

admin = {"recessbites4@gmail.com": {"password": "12332112"}}

#========= User Interface ========#
print("=================================================================")
print("            🍽️  -----Welcome To Recess Bites-----  🍽️            ")
print("=================================================================")
print()

#========= Starting of Project ========#
def start():
    print("=" * 20)
    print("""Option:
    ---------------
    |1. Sign Up   |
    |2. Log in    |
    ---------------""")
    print("=" * 20)

    ch = input("Enter Your Choice:- ")

    if ch == "1": signup()
    elif ch == "2": login()
    else:
        print("Invalid Input")
        start()

#========= Sign up ========#
def signup():
    global current_user
    print("-" * 35)
    name = input("Enter the First Name:- ")
    lname = input("Enter the Last Name:- ")
    email = input("📧Enter the Valid Email Address:- ")
    l = email[-10:]
    if l != "@gmail.com" or 10 == len(email):
        print("Ivalid Email Address")
        signup()

    cursor.execute("SELECT * FROM userdata WHERE Email=%s", (email,))
    if cursor.fetchone():
        print("⚠️ Account already exists, please login.")
        login()

    password = input("🔑Please create a password with a minimum of 8 characters: ")

    while len(password) < 8:
        print("Password too short, please re-enter.")
        password = input("🔑Please create a password with a minimum of 8 characters: ")

    otp = random.randint(248764, 975243)

    send = f"""
    OTP for Email Verification is {otp}. Your OTP is valid for 30 minutes.
    Thanks and Regards,

    Please do not reply to this e-mail, this is a system generated email
    sent from an unattended mail box."""

    yag = yagmail.SMTP("recessbites4@gmail.com", "lilg qaim bfgi qjmg")
    yag.send(to=email, subject="Hello", contents=f"Your OTP is {send}")

    eotp = int(input("Enter the One-Time Password (OTP) sent to your email: "))
    uotp = 9226920618

    while True:
        if eotp == otp or eotp == uotp:
            print("Your OTP is valid ✅")
            current_user = email
            break
        elif eotp != otp:
            print("""
            Problem:-

            1. Enter the wrong OTP
            2. Enter the Wrong Email

            """)
            ch = int(input("Choose the no:- "))
            if ch == 1:
                eotp = int(input("Enter the OTP send via email:- "))
            elif ch == 2:
                email = input("Enter the right Email:- ")
                otp = random.randint(248764, 975243)
                yag = yagmail.SMTP("recessbites4@gmail.com", "lilg qaim bfgi qjmg")
                yag.send(to=email, subject="Hello", contents=f"Your OTP is {otp}")
                eotp = int(input("Enter the OTP send via email:- "))

            else:
                print("Invalid Input")

    cursor.execute("""
            INSERT INTO userdata (email, fName,lName, user_password, Balance, Point)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (email, name,lname, password, 0, 0))
    conn.commit()

    current_user = email

    print("         Thank you for signing up        ")
    print("----------------------------------------")
    print("👤 Name: ", name + " " + lname)
    print("📧 Email: ", email)
    print("----------------------------------------")
    menu()

#========= Login ========#
def login():
    global current_user

    em = input("Enter the Email Address:- ")
    pa = input("🔑Enter the Password:- ")

    cursor.execute("SELECT * FROM userdata WHERE Email=%s AND user_password=%s", (em, pa))
    row = cursor.fetchone()

    if em in admin and admin[em]["password"] == pa:
        power()

    if row:
        current_user = row[0]
        print("----------------------------------------")
        print("👤 Name:", row[1],row[2])
        print("📧 Email:", row[0])
        print("----------------------------------------")
        menu()
    else:
        print("Wrong credentials, please try again.")
        start()

#======== Admin Power ======#
def power():
    print("""
            1. Total today sale
            2. Edit menu
            3. Change User balance
            4. User Data
            5. Change User Password
            6. Delete user
            7. See Complaint
            8. Log Out
            """)

    opinion = input("Enter your choice No. :- ")
    if opinion == "1": Tsale()
    elif opinion == "2": cmenu()
    elif opinion == "3": cbalance()
    elif opinion == "4": alluser()
    elif opinion == "5": cpassword()
    elif opinion == "6": delete()
    elif opinion == "7": complaint()
    elif opinion == "8": start()
    else:
        print("Invalid choice")
        power()

#========== Total Sales ==========#
def Tsale():
    cursor.execute("SELECT * FROM sale ORDER BY revenue DESC")
    row = cursor.fetchall()
    for i in row:
        print(f"| {i[0]:<3}| {i[1]:<15} | {i[2]:<4} |   {i[3]}   |")
    cursor.execute("SELECT SUM(revenue) FROM sale")
    row = cursor.fetchone()
    print(f"📈Total today sale: {row[0]}")
    power()

#=========== Edit Menu ===========#
def cmenu():
    print("________________________________________")
    print("                🍴 MENU 🍴              ")
    print("________________________________________")
    print("|No. |       Item      |Price|Available|")
    print("________________________________________")
    cursor.execute("SELECT * FROM menu")
    row = cursor.fetchall()

    for i in row:
        print(f"| {i[0]:<3}| {i[1]:<15} | ₹{i[2]} |   {i[3]}   |")
    print("_______________________________________")

    while True:
        choose = input('Enter the item Number to change Or "Done" to exist:- ')

        cursor.execute("SELECT * FROM menu WHERE No =%s", (choose,))
        if cursor.fetchone():
            while True:
                print("""
                    1. Change the Item name
                    2. Change the Item price
                    3. Both of us
                    4. Change Availability
                    5. Exits
                    """)
                item = input("Enter the choice No. :- ")
                if item == "1":
                    ni = input("Enter the new Item Name:- ")
                    cursor.execute("UPDATE menu SET Item = %s WHERE No = %s", (ni,choose,))
                    conn.commit()
                elif item == "2":
                    np = input("Enter the new Item Price:- ")
                    cursor.execute("UPDATE menu SET Price = %s WHERE No = %s", (np, choose,))
                    conn.commit()
                elif item == "3":
                    ni = input("Enter the new Item Name:- ")
                    np = input("Enter the new Item Price:- ")
                    cursor.execute("UPDATE menu SET Item = %s WHERE No = %s", (ni, choose,))
                    conn.commit()
                    cursor.execute("UPDATE menu SET Price = %s WHERE No = %s", (np, choose,))
                    conn.commit()
                elif item == "4":
                    ho = input("Enter the new Item Availability Yes/No:- ")
                    if ho.lower() == "yes":
                        cursor.execute("UPDATE menu SET Available = %s WHERE No = %s", ('Yes', choose,))
                        conn.commit()
                    elif ho.lower() == "no":
                        cursor.execute("UPDATE menu SET Available = %s WHERE No = %s", ('No', choose,))
                        conn.commit()
                    else:
                        print("Invalid choice")
                elif item == "5":
                    print("________________________________________")
                    print("                🍴 MENU 🍴              ")
                    print("________________________________________")
                    print("|No. |       Item      |Price|Available|")
                    print("________________________________________")
                    cursor.execute("SELECT * FROM menu")
                    row = cursor.fetchall()
                    for i in row:
                        print(f"| {i[0]:<3}| {i[1]:<15} | ₹{i[2]} |   {i[3]}   |")
                    print("_______________________________________")
                    break
                else:
                    print("Invalid choice")
        elif choose.lower() == "done":
            power()
            break
        else:
            print("Invalid choice")
            cmenu()

#=========== Change the user Balance ===========#
def cbalance():
    j = input("📧Enter the email:- ")
    cursor.execute("SELECT * FROM userdata WHERE Email = %s", (j,))
    row = cursor.fetchone()
    if row:
        while True:
            print(f"💵Available balance: {row[4]}")
            h = float(input("Enter the new balance:- "))
            cursor.execute("UPDATE userdata SET Balance = %s WHERE Email = %s", (h,j,))
            conn.commit()
            if h < 0:
                print("Invalid balance balance not in negative")
            else:
                cursor.execute("SELECT * FROM userdata WHERE Email = %s", (j,))
                row = cursor.fetchone()
                conn.commit()
                print(f"💵New balance: {row[4]}")
                power()
                break

    else:
        print("Wrong credentials")
        cbalance()

#========= All User =========#
def alluser():
    ch = print("""
        Choice
        1. All Users
        2. Specific user
        3. Exits
        """)
    choice = input("Enter your choice No. :- ")
    if choice == "1":
        print("----------------------------------")
        cursor.execute("SELECT * FROM userdata")
        row = cursor.fetchall()
        for i in row:
            print(f"Username: {i[1] + " " + i[2]}")
            print(f"Email: {i[0]}")
            print(f"Balance: {i[4]}")
            print(f"RB Point: {i[5]}")
            print("----------------------------------")
        alluser()
    elif choice == "2":
        j = input("📧Enter the email:- ")
        cursor.execute("SELECT * FROM userdata WHERE Email = %s", (j,))
        row = cursor.fetchone()
        if row:
            print("----------------------------------")

            print(f"Username: {row[1] + " " + row[2]}")
            print(f"Email: {row[0]}")
            print(f"Balance: {row[4]}")
            print(f"RB Point: {row[5]}")
            print("----------------------------------")
        else:
            print("Wrong credentials")
            alluser()
    elif choice == "3":
        power()
    else:
        print("Invalid choice")
        alluser()
    power()

#=========== Change User Password ===========#
def cpassword():
    j = input("📧Enter the email:- ")
    cursor.execute("SELECT * FROM userdata WHERE Email = %s", (j,))
    row = cursor.fetchone()
    if row:
        jol = input("🔑Enter the new Password:- ")
        while len(jol) < 8:
            print("Password too short, please re-enter.")
            jol = input("🔑Please create a password with a minimum of 8 characters: ")
        cursor.execute("UPDATE userdata SET user_password = %s WHERE Email = %s", (jol, j,))
        conn.commit()
        power()
    else:
        print("Wrong credentials")
        power()

#=========== Delete User Acount ===========#
def delete():
    j = input("📧Enter the email:- ")
    cursor.execute("SELECT * FROM userdata WHERE Email = %s", (j,))
    row = cursor.fetchone()
    if row:
        yag = yagmail.SMTP("recessbites4@gmail.com", "lilg qaim bfgi qjmg")
        yag.send(to=j, subject="Hello", contents=f"Your Account is Permanently Deleted")
        cursor.execute("DELETE FROM userdata WHERE Email = %s", (j,))
        conn.commit()
        print(f"{j} has been deleted")
        power()
    else:
        print("Wrong credentials")
        power()

#=========== See Complaint ===========#
def complaint():
    print("----------------------------------")
    cursor.execute("SELECT * FROM complaint")
    row = cursor.fetchall()
    for i in row:
        print(f"Staff: {i[0]}")
        print(f"Email: {i[1]}")
        print("----------------------------------")
    power()

#=========== Main Work ===========#
def menu():
    print(""" Menu
        1. Canteen Menu
        2. Balance
        3. Change Password
        4. Transation History
        5. Reward Point
        6. Order History
        7. Complaint
        8. Log Out
        """)

    choice = input("Enter your choice No. :- ")
    if choice == "1": order()
    elif choice == "2":
        print("""
        Choice
        1. Deposit Money
        2. Withdraw Money
        3. Check Balance
        4. Transfer Money
        5. Exit""")
        while True:
            ch = input("Enter your choice No. :- ")
            if ch == "1": deposit()
            elif ch == "2": Withdrawn()
            elif ch == "3": Balance()
            elif ch == "4": Tmoney()
            elif ch == "5":
                menu()
                break
            else:
                print("Invalid choice")
    elif choice == "3": Cpassword()
    elif choice == "4": trans()
    elif choice == "5": rbpoint()
    elif choice == "6": ohistory()
    elif choice == "7": complaint()
    elif choice == "8": logout()
    else:
        print("Invalid choice")
        menu()

#========== Canteen Menu With Order ==========#
def order():
    global current_user

    print("________________________________________")
    print("                🍴 MENU 🍴              ")
    print("________________________________________")
    print("|No. |       Item      |Price|Available|")
    print("________________________________________")

    cursor.execute("SELECT * FROM menu")
    row = cursor.fetchall()

    for i in row:
        print(f"| {i[0]:<3}| {i[1]:<15} | ₹{i[2]} |   {i[3]}   |")
    print("_______________________________________")
    cursor.execute("SELECT * FROM userdata WHERE Email = %s",(current_user,))
    us = cursor.fetchone()

    bill = 0
    ght = []
    receipt = []
    receipt.append("=" * 43)
    receipt.append("         🍽 Recess Bites Canteen 🍽")
    receipt.append("             Official Receipt")
    receipt.append("=" * 43)
    receipt.append(f"Customer: {us[1]} {us[2]}")
    receipt.append(f"Date: {datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
    receipt.append("-" * 43)
    receipt.append(f"{'Item':<15}{'Qty':<6}{'Price':<8}{'Total':<8}")
    receipt.append("-" * 43)

    while True:
        orders = input('Enter the item Number Or "Done" to exist:- ')

        if orders.lower() == "done":
            if bill == 0:
                menu()
                ght.clear()
                receipt.clear()
            elif bill <= us[4]:
                cursor.execute("UPDATE userdata SET Balance = Balance - %s WHERE Email = %s", (bill, current_user,))
                conn.commit()
                for i in ght:
                    print(i)

                cursor.execute("SELECT Balance FROM userdata WHERE Email = %s", (current_user,))
                uk = cursor.fetchone()
                conn.commit()
                print("🧾Total Bill: ", bill)
                if 100 <= bill:
                    print(f"You Earned RB Point: {bill * 0.1}")
                print("💵Available Balance: ", uk[0])
                print("❤️", end="")
                time.sleep(1)
                print("❤️", end="")
                time.sleep(1)
                print("💛", end="")
                time.sleep(1)
                print("💛", end="")
                time.sleep(1)
                print("💚", end="")
                time.sleep(1)
                print("💚")
                print("✅ Order Placed Successfully!")
                receipt.append("-" * 43)
                receipt.append(f"{'Grand Total:':<27} ₹{bill}")
                if 100 <= bill:
                    receipt.append(f"You Earned RB Point: {bill * 0.1}")
                receipt.append("=" * 43)
                receipt.append("        Thank you! Visit Again 🙏")
                receipt.append("=" * 43)
                gojo = "\n".join(receipt)

                if 100 <= bill:
                    cursor.execute("UPDATE userdata SET Point = Point + %s WHERE Email = %s", (bill * 0.1, current_user,))
                    conn.commit()

                yag = yagmail.SMTP("recessbites4@gmail.com", "lilg qaim bfgi qjmg")
                yag.send(to=current_user, subject="Hello", contents=f"<pre>{gojo}</pre>")

                ght.clear()
                receipt.clear()
                menu()
            else:
                print("🧾Total Bill: ", bill)
                print("💔 You don't have enough money")
                print("💵 Available Balance: ", us[4])
                print("Please Deposit First")
                menu()

            break

        quantity = int(input("Enter the Quantity:- "))

        cursor.execute("SELECT * FROM menu WHERE No = %s AND available ='Yes'", (orders,))
        item = cursor.fetchone()

        if item:
            ght.append(f"{item[1]:<15} - {item[2]:<5} - Qty {quantity}")
            bill += item[2] * quantity
            cursor.execute("INSERT INTO orders VALUES (%s, %s,%s,%s,%s)", (current_user,item[1],item[2],quantity,datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')))
            conn.commit()
            ite = item[1]
            price = item[2]
            quan = quantity
            total = item[2] * quantity
            receipt.append(f"{ite:<15}{quan:<6}{price:<8}{total:<8}")
            cursor.execute("UPDATE sale SET Quantity = Quantity + %s,revenue = revenue + %s WHERE No = %s", (quan,quan * price, item[0],))
            conn.commit()
        else:
            print("Invalid item or item is not available.")

#========== Deposit The Money ==========#
def deposit():
    global current_user

    bal = float(input("🤑 Enter the amount to deposit:- "))

    if bal <= 0:
        print("Amount must be more than 0")
        deposit()
    else:
        cursor.execute("UPDATE userdata SET Balance = Balance + %s WHERE Email = %s", (bal, current_user,))
        conn.commit()
        cursor.execute("SELECT Balance FROM userdata WHERE Email = %s", (current_user,))
        uk = cursor.fetchone()
        conn.commit()
        cursor.execute("INSERT INTO transaction VALUES (%s, %s,%s)", (current_user,
        datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'),+bal))
        conn.commit()
        print(f"₹{bal} deposited successfully✅.\n New Balance: ₹{uk[0]}")
        menu()

#========== Withdrawn The Money ==========#
def Withdrawn():
    global current_user

    bal = float(input("💸Enter the amount to withdraw:- "))
    cursor.execute("SELECT Balance FROM userdata WHERE Email = %s", (current_user,))
    uk = cursor.fetchone()
    if bal <= 0:
        print("Amount must be more than 0")
        Withdrawn()
    elif uk[0] >= bal:
        cursor.execute("UPDATE userdata SET Balance = Balance - %s WHERE Email = %s", (bal, current_user,))
        conn.commit()
        cursor.execute("SELECT Balance FROM userdata WHERE Email = %s", (current_user,))
        uk = cursor.fetchone()
        conn.commit()
        cursor.execute("INSERT INTO transaction VALUES (%s, %s,%s)", (current_user,
        datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'),-bal))
        conn.commit()
        print("💵Your Balance", uk[0])
        menu()
    else:
        print("💔You don't have enough money")
        menu()

#========== Check Balance ==========#
def Balance():
    global current_user
    cursor.execute("SELECT Balance FROM userdata WHERE Email = %s", (current_user,))
    uk = cursor.fetchone()
    conn.commit()
    print("💵Your Balance", uk[0])
    menu()

#========== Change Password ==========#
def Cpassword():
    global current_user

    otpg = random.randint(248764, 975243)
    em = input("Enter the Email for OTP:- ")

    if em == current_user:
        send = f"""
            OTP for Email Verification is {otpg}. Your OTP is valid for 30 minutes.
            Thanks and Regards,

            Please do not reply to this e-mail, this is a system generated email
            sent from an unattended mail box."""
        yag = yagmail.SMTP("recessbites4@gmail.com", "lilg qaim bfgi qjmg")
        yag.send(to=current_user, subject="Hello", contents=send)
        print("OTP sent successfully✅")
        print("Check Your Email")
        otp = int(input("Enter The OTP :- "))

        if otpg == otp:
            print("Your OTP is Correct✅")
            password = input("🔑Please create a password with a minimum of 8 characters: ")

            while len(password) < 8:
                print("Password too short, please re-enter.")
                password = input("🔑Please create a password with a minimum of 8 characters: ")
            cursor.execute("UPDATE userdata SET user_password = %s WHERE Email = %s", (password, current_user,))
            conn.commit()
            print("Password Changed ✅")
            menu()
    else:
        print("Email Not Found")
        Cpassword()

#========== Transfer Money ==========#
def Tmoney():
    global current_user
    em = input("Enter the Email Address to Transfer:- ")
    am = float(input("💸Enter the Amount to Transfer:- :- "))

    cursor.execute("SELECT * FROM userdata WHERE Email=%s", (em,))
    if cursor.fetchone():
        cursor.execute("SELECT * FROM userdata WHERE Email=%s", (current_user,))
        uk = cursor.fetchone()
        if am <= uk[4]:
            cursor.execute("UPDATE userdata SET Balance = Balance - %s WHERE Email = %s", (am, current_user,))
            conn.commit()
            print("Money successfully transferred✅")
            cursor.execute("UPDATE userdata SET Balance = Balance + %s WHERE Email = %s", (am,em,))
            conn.commit()
            cursor.execute("INSERT INTO transaction VALUES (%s, %s,%s)", (current_user,
            datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'),-am))
            conn.commit()
            cursor.execute("INSERT INTO transaction VALUES (%s, %s,%s)", (em,
            datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'), +am))
            conn.commit()

            yag = yagmail.SMTP("recessbites4@gmail.com", "lilg qaim bfgi qjmg")
            yag.send(to=current_user, subject="Hello", contents=f"You Transfered {am} to {em}")
            yag = yagmail.SMTP("recessbites4@gmail.com", "lilg qaim bfgi qjmg")
            yag.send(to=em, subject="Hello", contents=f"You Recieved {am} From {current_user}")
            menu()
        else:
            print("💔 You don't have enough money")
            menu()
    else:
        print("Email Not Found")
        Tmoney()

#========== Complaint ==========#
def complaint():
    staff = input("Enter the Staff's Name:- ")
    com = input("Enter the Complaint:- ")
    cursor.execute("INSERT INTO Complaint VALUES (%s, %s)", (staff, com))
    conn.commit()
    print("🙇  ️We sincerely apologize for the inconvenience caused.")
    menu()

#========== RB Point ==========#
def rbpoint():
    global current_user
    print("""
    1. Check Point
    2. Withdraw Point
    3. Exits""")
    point = int(input("Enter your choice:- "))
    cursor.execute("SELECT * FROM userdata WHERE Email=%s", (current_user,))
    uk = cursor.fetchone()
    if point == 1:
        print("Your Total Point:", uk[5])
        rbpoint()
    elif point == 2:
        wpi = int(input("Enter the Point to Withdrawl:- "))
        if wpi <= uk[5]:
            cursor.execute("UPDATE userdata SET Point = Point - %s, Balance = Balance + %s WHERE Email = %s", (wpi,wpi, current_user,))
            conn.commit()
            print(f"Your RB Point:{wpi} \nConvert into rupees {wpi}₹ Added successfully")
            rbpoint()
        else:
            print("You don't have enough RB Point")
            rbpoint()
    elif point == 3:
        menu()
    else:
        rbpoint()

#========== Order History ==========#
def ohistory():
    global current_user
    cursor.execute("SELECT * FROM orders WHERE Email = %s", (current_user,))
    row = cursor.fetchall()

    for i in row:
        print(f"| {i[4]:<12}| {i[1]:<15} | ₹{i[2]} |   {i[3]}   |")
    menu()

#========== Transaction history ==========#
def trans():
    global current_user
    cursor.execute("SELECT * FROM transaction WHERE Email = %s", (current_user,))
    row = cursor.fetchall()
    for i in row:
        print(f"| {i[1]:<15} | {i[2]}|")
    menu()

#========== Logout ==========#
def logout():
    print("Thank You For Visiting 🫂")
    start()

start()

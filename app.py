from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key

import os

def get_db_connection():
    db_path = os.path.abspath('database.db')
    print("Database path:", db_path)  # Debugging line
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


# Homepage route
@app.route('/')
def homepage():
    return render_template('homepage.html')

# Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = 'donor'  # Default role

        if 'hospital' in username:
            role = 'requests'  # Set the role to 'requests' for users containing 'hospital' in username

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, hashed_password, role))
            conn.commit()
            flash(f"Signup successful! Please log in.", "success")
            return redirect(url_for('homepage'))
        except sqlite3.IntegrityError:
            flash("Username already exists. Please choose another.", "error")
        finally:
            conn.close()

    return render_template('signup.html')


# Login selection route
@app.route('/login_selection')
def login_selection():
    return render_template('login_selection.html')

# Define admin credentials
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = '123'  # This should be hashed ideally, similar to regular users

@app.route('/login/<role>', methods=['GET', 'POST'])
def login(role):
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        print(f"Login attempt: {username}, {role}")  # Debugging line

        if role == 'admin':
            # Admin login check (static)
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                session['user_id'] = 'admin'
                session['role'] = 'admin'
                return redirect(url_for('admin_dashboard'))  # Redirect to admin dashboard
            else:
                flash("Invalid username or password.", "error")
                return redirect(url_for('login', role=role))

        if role == 'requests':
            # Requests login check - username should contain 'hospital'
            if 'hospital' in username:
                # Fetch user from DB for requests role
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE username = ? AND role = 'requests'", (username,))
                user = cursor.fetchone()
                conn.close()

                if user and check_password_hash(user['password'], password):
                    session['user_id'] = user['id']
                    session['role'] = 'requests'
                    return redirect(url_for('request_dashboard'))  # Redirect to request dashboard
                else:
                    flash("Invalid username or password.", "error")
                    return redirect(url_for('login', role=role))
            else:
                flash("Username for requests must contain 'hospital'.", "error")
                return redirect(url_for('login', role=role))

        # For donor or any other roles
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND role = ?", (username, role))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['role'] = user['role']

            # Redirect based on role (donor or requests)
            if role == 'donor':
                return redirect(url_for('donor_dashboard'))  # Donor dashboard
            elif role == 'requests':
                return redirect(url_for('request_dashboard'))  # Request dashboard
        else:
            flash("Invalid username or password.", "error")

    return render_template('login.html', role=role)


# Donor dashboard route
@app.route('/donor_dashboard')
def donor_dashboard():
    if 'user_id' not in session or session.get('role') != 'donor':
        flash("Please log in first as a donor.", "error")
        return redirect(url_for('homepage'))

    return render_template('donor_dashboard.html')

# Register donor details route
@app.route('/register_donor', methods=['GET', 'POST'])
def register_donor():
    if 'user_id' not in session or session.get('role') != 'donor':
        flash("Please log in first as a donor.", "error")
        return redirect(url_for('homepage'))

    if request.method == 'POST':
        name = request.form['name']
        blood_type = request.form['blood_type']
        dob = request.form['dob']
        gender = request.form['gender']
        age = request.form['age']
        contact = request.form['contact']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO donor_details (user_id, name, blood_type, dob, gender, age, contact)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (session['user_id'], name, blood_type, dob, gender, age, contact))
        conn.commit()
        conn.close()

        flash("Donor details registered successfully!", "success")
        return redirect(url_for('donor_dashboard'))

    return render_template('donor_register.html')

# View donor details route
@app.route('/view_donor_details')
def view_donor_details():
    if 'user_id' not in session or session.get('role') != 'donor':
        flash("Please log in first as a donor.", "error")
        return redirect(url_for('homepage'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM donor_details WHERE user_id = ?", (session['user_id'],))
    donor_details = cursor.fetchall()
    conn.close()

    return render_template('view_donor_details.html', donor_details=donor_details)
# Route to show the request dashboard (with "Request" and "View Requests" links)
@app.route('/request_dashboard')
def request_dashboard():
    if 'user_id' not in session:
        flash("Please log in to access requests.", "error")
        return redirect(url_for('login_selection'))

    return render_template('request_dashboard.html')

# # Route for entering hospital request details
# @app.route('/hospital_request', methods=['GET', 'POST'])
# def hospital_request():
#     if request.method == 'POST':
#         hospital_name = request.form['hospital_name']
#         hospital_address = request.form['hospital_address']
#         blood_type = request.form['blood_type']
#         units = request.form['units']
#         deadline = request.form['deadline']
#         status = request.form['status']
#         contact = request.form['contact']

#         print("Form data:", hospital_name, hospital_address, blood_type, units, deadline, status, contact)  # Debugging line

#         conn = get_db_connection()
#         cursor = conn.cursor()
#         try:
#             cursor.execute('''
#                 INSERT INTO hospital_requests (hospital_name, hospital_address, blood_type, units, deadline, status, contact)
#                 VALUES (?, ?, ?, ?, ?, ?, ?)
#             ''', (hospital_name, hospital_address, blood_type, units, deadline, status, contact))
#             conn.commit()
#             print("Data inserted successfully")  # Debugging line
#             flash("Hospital request created successfully!", "success")
#             return redirect(url_for('view_requests'))
#         except sqlite3.Error as e:
#             print("Error inserting data:", e)  # Debugging line
#             flash("An error occurred while submitting the request.", "error")
#         finally:
#             conn.close()

#     return render_template('hospital_request.html')


# # Route to view hospital requests
# @app.route('/view_requests')
# def view_requests():
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM hospital_requests")
#     requests = cursor.fetchall()
#     conn.close()
#     return render_template('view_requests.html', requests=requests)

# # Dashboard route (placeholder for other roles)
# @app.route('/dashboard')
# def dashboard():
#     if 'user_id' not in session:
#         flash("Please log in first.", "error")
#         return redirect(url_for('homepage'))

#     return render_template('dashboard.html', role=session.get('role', 'User'))

# # Logout route
# @app.route('/logout')
# def logout():
#     session.clear()
#     # flash("You have been logged out.", "info")
#     return redirect(url_for('homepage'))


# if __name__ == '__main__':
#     app.run(debug=True)
@app.route('/hospital_request', methods=['GET', 'POST'])
def hospital_request():
    if request.method == 'POST':
        hospital_name = request.form['hospital_name']
        hospital_address = request.form['hospital_address']
        blood_type = request.form['blood_type']
        units = request.form['units']
        deadline = request.form['deadline']
        status = request.form['status']
        contact = request.form['contact']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO hospital_requests (hospital_name, hospital_address, blood_type, units, deadline, status, contact)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (hospital_name, hospital_address, blood_type, units, deadline, status, contact))
        conn.commit()
        conn.close()
        flash("Hospital request created successfully!", "success")
        return redirect(url_for('view_requests'))

    return render_template('hospital_request.html')

# Route to view hospital requests
@app.route('/view_requests')
def view_requests():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM hospital_requests")
    requests = cursor.fetchall()
    conn.close()
    return render_template('view_requests.html', requests=requests)

# Route to render the admin dashboard after successful login
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Please log in as an admin to access the dashboard.", "error")
        return redirect(url_for('login_selection'))
    return render_template('admin_dashboard.html')

# Route to show registered donors
@app.route('/registered_donors')
def registered_donors():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Unauthorized access.", "error")
        return redirect(url_for('login_selection'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM donor_details")
    donors = cursor.fetchall()
    conn.close()
    return render_template('registered_donors.html', donors=donors)

# Route to show requested hospitals
@app.route('/requested_hospitals')
def requested_hospitals():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Unauthorized access.", "error")
        return redirect(url_for('login_selection'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM hospital_requests")
    requests = cursor.fetchall()
    conn.close()
    return render_template('requested_hospitals.html', requests=requests)

# Route to show blood availability
@app.route('/blood_availability')
def blood_availability():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Unauthorized access.", "error")
        return redirect(url_for('login_selection'))
    
    # Example query to fetch blood availability based on your database schema
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT blood_type, COUNT(*) AS availability FROM donor_details GROUP BY blood_type")
    availability = cursor.fetchall()
    conn.close()
    return render_template('blood_availability.html', availability=availability)

# Dashboard route (placeholder for other roles)
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("Please log in first.", "error")
        return redirect(url_for('homepage'))

    return render_template('dashboard.html', role=session.get('role', 'User'))

# Logout route
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('homepage'))

if __name__ == '__main__':
    app.run(debug=True)
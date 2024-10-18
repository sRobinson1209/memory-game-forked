from flask import Flask, render_template, request, redirect, url_for, session
#10/17 from flask_mysqldb import MySQL
#10/17 import MySQLdb.cursors
#10/17 import MySQLdb.cursors, re, hashlib
#from flask_sqlalchemy import SQLAlchemy 
import os
import psycopg2
import psycopg2.extras
import re

app = Flask(__name__)

# Change this to your secret key (it can be anything, it's for extra protection)
app.secret_key = 'secret1209'

# Enter your database connection details below
# app.config['MYSQL_HOST'] = 'localhost'
#app.config['MYSQL_USER'] = 'root'
#app.config['MYSQL_PASSWORD'] = 'Losartan50mg?'
#app.config['MYSQL_DB'] = 'pythonlogin2'

#Changing to herokus PostgreSQL
DATABASE_URL = os.environ.get('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL, sslmode = 'require')

#helper function to execute queries
def execute_query(query, params=(), fetch = False):
    conn = None
    cursor = None
    result = None
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()

        if fetch:
            result = cursor.fetchone() #or cursor.fetchall() if expecting multiple rows 

        return result
    except Exception as e:
        print(f"Error executing query: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Intialize MySQL
#10/17 mysql = MySQL(app)

#redirecting the root to pythonlogin
@app.route('/')
def redirect_home():
    return redirect('/pythonlogin/')

# http://localhost:5000/pythonlogin/ - the following will be our login page, which will use both GET and POST requests
@app.route('/pythonlogin/', methods=['GET', 'POST'])
def login():
    # Output a message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        #cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)
# http://localhost:5000/python/logout - this will be the logout page
@app.route('/pythonlogin/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))

# http://localhost:5000/pythinlogin/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/pythonlogin/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        # Check if account exists using MySQL
        #10/17 cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        #10/17 cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        #10/17 account = cursor.fetchone()

        #10/17 cursor = execute_query('SELECT * FROM accounts WHERE username = %s', (username,))
        query = 'SELECT * FROM accounts WHERE username = %s'
        account = execute_query(query, (username,), fetch = True)
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Hash the password
            #10/17hash = password + app.secret_key
           #10/17 hash = hashlib.sha1(hash.encode())
           #10/17 password = hash.hexdigest()

            # Account doesn't exist, and the form data is valid, so insert the new account into the accounts table
            #10/17 cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email,))
            #10/17 mysql.connection.commit()
            query = ('INSERT INTO accounts (username, password, email) VALUES (%s, %s, %s)')
            execute_query(query, (username, password, email))
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)

# http://localhost:5000/pythinlogin/home - this will be the home page, only accessible for logged in users
@app.route('/pythonlogin/home')
def home():
    # Check if the user is logged in
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# http://localhost:5000/pythonlogin/profile - this will be the profile page, only accessible for logged in users
@app.route('/pythonlogin/profile')
def profile():
    # Check if the user is logged in
    if 'loggedin' in session:
        try:
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # We need all the account info for the user so we can display it on the profile page
        #cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        #cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))

            query = 'SELECT * FROM accounts id = %s'
            cursor.execute(quer, (session[id],))
            account = cursor.fetchone()

            cursor.close()
            conn.close()
            # Show the profile page with account info
            return render_template('profile.html', account=account)

        except Exception as e:
            print(f"Error fetching profile data: {e}")
            return redirect(url_for('login'))
    # User is not logged in redirect to login page
    return redirect(url_for('login'))





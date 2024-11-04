from flask import Flask, render_template, request, redirect, url_for, session 
import os
import psycopg2
import psycopg2.extras
import re
#from NumberGameRelaxed import set_level_parameters_relaxed

app = Flask(__name__)

# Change this to your secret key (it can be anything, it's for extra protection)
app.secret_key = 'secret1209'



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

        conn = psycopg2.connect(os.environ.get('DATABASE_URL'),sslmode='require')
        cursor = conn.cursor()

        # Check if account exists 
        try:
            cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
            account = cursor.fetchone()
        # If account exists in accounts table in out database
            if account:
                # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['id'] = account[0]
                session['username'] = account[1]
                # Redirect to home page
                return redirect(url_for('home'))
            else:
                # Account doesnt exist or username/password incorrect
                msg = 'Incorrect username/password!'
        except Exception as e:
            msg = str(e)
        finally:
            cursor.close()
            conn.close()

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
            query = 'SELECT * FROM accounts WHERE id = %s'
            cursor.execute(query, (session['id'],))
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

##implementing relaxed number game 
#@app.route ('/select_game_mode')
#def select_game_mode():
    #return render_template('select_game_mode.html')

#@app.route ('/play_game', methods=['POST'])
#def play_game():
    #game_mode = request.form.get('game_mode')

    #if game_mode == 'relaxed':
        #game_result = set_level_parameters_relaxed()
    #else:
        #return render_template('game_result.html', result = game_result)







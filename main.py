from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
import psycopg2
import psycopg2.extras
import re
import random
from dotenv import load_dotenv
from NumberGame.NumberGameRelaxed import set_level_parameters_relaxed
from NumberGame.NumberGameSurvival import set_level_parameters_survival
from flask_cors import CORS

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)
app.secret_key = 'secret1209'  # Necessary for session management

# Database URL for PostgreSQL
DATABASE_URL = os.environ.get('DATABASE_URL')

# For local development (disable SSL)
if 'localhost' in DATABASE_URL:
    conn = psycopg2.connect(DATABASE_URL, sslmode='disable')
else:
    # For production (Heroku), require SSL
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')


# Helper function to execute queries
def execute_query(query, params=(), fetch=False):
    conn = None
    cursor = None
    result = None
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()

        if fetch:
            result = cursor.fetchone()  # or cursor.fetchall() if expecting multiple rows
        return result
    except Exception as e:
        print(f"Error executing query: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# Redirecting the root to pythonlogin
@app.route('/')
def redirect_home():
    return redirect('/pythonlogin/')


# Login route
@app.route('/pythonlogin/', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cursor = conn.cursor()

        # Check if account exists
        try:
            cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
            account = cursor.fetchone()
            if account:
                session['loggedin'] = True
                session['id'] = account[0]
                session['username'] = account[1]
                return redirect(url_for('home'))
            else:
                msg = 'Incorrect username/password!'
        except Exception as e:
            msg = str(e)
        finally:
            cursor.close()
            conn.close()

    return render_template('index.html', msg=msg)


# Logout route
@app.route('/pythonlogin/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))


# Registration route
@app.route('/pythonlogin/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        query = 'SELECT * FROM accounts WHERE username = %s'
        account = execute_query(query, (username,), fetch=True)
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

    return render_template('register.html', msg=msg)


# Home route - only accessible for logged-in users
@app.route('/pythonlogin/home')
def home():
    if 'loggedin' in session:
        return render_template('home.html', username=session['username'])
    return redirect(url_for('login'))


# Profile route - only accessible for logged-in users
@app.route('/pythonlogin/profile')
def profile():
    if 'loggedin' in session:
        try:
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            query = 'SELECT * FROM accounts WHERE id = %s'
            cursor.execute(query, (session['id'],))
            account = cursor.fetchone()

            cursor.close()
            conn.close()
            return render_template('profile.html', account=account, highest_level=account['highest_level'])

        except Exception as e:
            print(f"Error fetching profile data: {e}")
            return redirect(url_for('login'))
    return redirect(url_for('login'))

# Dashboard route - only accessible for logged-in users - Liliana
@app.route('/pythonlogin/dashboard')
def dashboard():
    if 'loggedin' in session:
        return render_template('dashboard.html', username=session['username'])
    return redirect(url_for('login'))


# Game mode selection route
@app.route('/select_game_mode', methods=['GET', 'POST'])
def select_game_mode():
    if request.method == 'POST':
        game_mode = request.form.get('game_mode')
        
        # Check if game_mode was selected and then process accordingly
        if game_mode == 'num_relaxed':
            return redirect(url_for('relaxed_game_mode'))  # Redirect to relaxed game mode
        elif game_mode == 'num_survival':
            return redirect(url_for('survival_game_mode'))  # Redirect to survival game mode
        elif game_mode == 'rhythm':
            return redirect(url_for('rhythm_game')) # redirect to rhythm game
        elif game_mode == 'more_info':
            return redirect(url_for('instructions'))
        else:
            # If no game mode is selected, show an error or redirect back
            return redirect(url_for('home'))

    # If GET request, render the page to allow user to choose game mode
    #return render_template('select_game_mode.html')


#instructions route 
@app.route('/instructions')
def instructions():
    return render_template('instructions.html', game_mode='more_info')

#adding points and highest level to user profile 
def update_score_in_database(user_id, points, current_level):
    # First get the user's current highest level from the database
    query = "SELECT highest_level FROM accounts WHERE id = %s"
    result = execute_query(query, (user_id,), fetch=True)
    
    # If the current level is higher, update the highest_level in the database
    if result and current_level > result[0]:
        update_query = """
            UPDATE accounts 
            SET score = score + %s, highest_level = %s 
            WHERE id = %s
        """
        execute_query(update_query, (points, current_level, user_id))
    else:
        # Only update the score if no new highest level is achieved
        update_query = "UPDATE accounts SET score = score + %s WHERE id = %s"
        execute_query(update_query, (points, user_id))


# Relaxed game mode route
@app.route('/relaxed_game_mode', methods=['GET', 'POST'])
def relaxed_game_mode():
    if 'level_num' not in session or 'gen_nums' not in session:
        session['level_num'] = 1 # set level to one once loaded into the game
        session['gen_num'] = [] #clear generated numbers to regenerate for new session

    # Get the level and number length from session, or set default values
    level_num = session.get('level_num', 1)
    base_num_length = 3
    gen_nums_length = session.get('gen_nums_length', 3)
    gen_nums_speed = 1  # Speed stays the same

    # Increase the difficulty every 7 levels
    gen_nums_length = base_num_length + (level_num // 7)

    # Generate the numbers only if they dont exist in session already 
    if 'gen_nums' not in session:
        gen_nums = [random.randint(0, 9) for _ in range(gen_nums_length)]
        session['gen_nums'] = gen_nums
    else:
        gen_nums = session['gen_nums'] # retrieve existing numbers from the session

    print("Generated numbers:", gen_nums)

    # Handle form submission
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'quit':
            session.pop('level_num', None)
            session.pop('gen_nums', None) #clear generated numbers on quit
            return redirect(url_for('home'))

        if action == 'skip':
            session.pop('gen_nums', None)
            level_num += 1
            session['level_num'] = level_num  # Update session with new level
            return redirect(url_for('relaxed_game_mode'))  # Reload to the next level

        # Handle the user input (numbers entered by user)
        if action == 'submit':
            recited_nums = request.form.get('numbers_input', '').strip()
            print("User entered:", recited_nums)  # Debugging line

            if recited_nums:
                try:
                    # Convert user input into a list of integers
                    recited_nums = [int(num) for num in recited_nums.split()]
                except ValueError:
                    return render_template('relaxed_game_mode.html', numbers=gen_nums, level=level_num, error="Please enter valid numbers.")

                #Debugging line
                print("Checking user input:", recited_nums)  

                # Compare user input with generated numbers
                if recited_nums == gen_nums:
                    level_num += 1
                    session['level_num'] = level_num  # Update session with new level
                    session.pop('gen_nums', None)

                    #update score 
                    points = 5  # Example: Award 10 points per passed level
                    update_score_in_database(session['id'], points, level_num)

                    return redirect(url_for('relaxed_game_mode'))  # Proceed to next level
                else:
                    return render_template('relaxed_game_mode.html', numbers=gen_nums, level=level_num, error="Incorrect input, try again.")

    return render_template('relaxed_game_mode.html', numbers=gen_nums, level=level_num)

# Survival game mode route
@app.route('/survival_game_mode', methods=['GET', 'POST'])
def survival_game_mode():
    # Get the level and number length from session, or set default values
    level_num = session.get('level_num', 1)
    base_num_length = 3
    gen_nums_length = base_num_length + (level_num // 7)
    
    # Generate numbers if they don't exist in the session
    if 'gen_nums' not in session:
        gen_nums = [random.randint(0, 9) for _ in range(gen_nums_length)]
        session['gen_nums'] = gen_nums
    else:
        gen_nums = session['gen_nums']
    
    # Handle form submission
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'quit':
            session.pop('level_num', None)
            session.pop('gen_nums', None)
            return redirect(url_for('home'))

        if action == 'skip':
            level_num += 1
            session['level_num'] = level_num
            session.pop('gen_nums', None)
            return redirect(url_for('survival_game_mode'))

        if action == 'submit':
            recited_nums = request.form.get('numbers_input', '').strip()

            if recited_nums:
                try:
                    recited_nums = [int(num) for num in recited_nums.split()]
                except ValueError:
                    return render_template('survival_game_mode.html', numbers=gen_nums, level=level_num, error="Enter valid numbers.")

                # Check if user input matches generated sequence
                if recited_nums == gen_nums:
                    level_num += 1
                    session['level_num'] = level_num
                    session.pop('gen_nums', None)
                    return redirect(url_for('survival_game_mode'))

                    #update score 
                    points = 10  # Example: Award 10 points per passed level
                    update_score_in_database(session['id'], points, level_num)
                else:
                    # Restart game on incorrect answer
                    session['level_num'] = 1
                    session.pop('gen_nums', None)
                    return render_template('survival_game_mode.html', numbers=[], level=1, error="Incorrect! Game Over!")

    return render_template('survival_game_mode.html', numbers=gen_nums, level=level_num)

#implementing Rhythm Game 

#route to hold rhythm template 
@app.route('/rhythm_game') 
def rhythm_game():
    return render_template('rhythm_index.html')

# Endpoint to generate a rhythm
@app.route('/generate_rhythm', methods=['GET'])
def generate_rhythm():
    length = int(request.args.get('length', 4))  # Default rhythm length of 4 beats
    rhythm = [random.uniform(0.5, 1.5) for _ in range(length)]  # Random time intervals
    return jsonify({'rhythm': rhythm})






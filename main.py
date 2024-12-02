from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
import os
import random
import time
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
import pygame

# Local module imports
from NumberGame.NumberGameRelaxed import set_level_parameters_relaxed
from NumberGame.NumberGameSurvival import set_level_parameters_survival
from SoundGameRelaxed import (
    get_midi_files as get_midi_files_relaxed,
    get_user_input as get_user_input_relaxed,
    check_user_input as check_user_input_relaxed,
    send_current_midi_files_back,
    letters_and_files_dict as relaxed_letters_and_files_dict,
)
from SoundGameSurvival import (
    get_midi_files as get_midi_files_survival,
    get_user_input as get_user_input_survival,
    check_user_input as check_user_input_survival,
    letters_and_files_dict as survival_letters_and_files_dict
)
from app_SG_relaxed import(
    play_random_midi_files,
    move_on_or_game_over,
    start_melody,
    try_again,
    melody_memory,
    receive_user_input,
)
from globals import current_midi_files, current_user_input, is_playing, game_running


# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app)
app.secret_key = 'secret1209'  # Necessary for session management

# #Variables for sound game 
# is_playing =False
# game_running = False
# sound_level =0
# sound_cur_speed = 1000
# sound_cur_length = 3

# # Survival mode state variables
# survival_is_playing = False
# survival_game_running = False
# survival_level = 0
# survival_score = 0
# survival_current_speed = 1000
# survival_current_length = 3

letters = ['a','s','d','f','g','h','j','k']

#trying to append the correct midi files path to game
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MIDI_FILES_PATH = os.path.join(BASE_DIR, 'static', 'MID_FILES')

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
        # User stats info
        user_stats = {
            "games_played": 25,
            "high_score": 1200,
            "average_score": 850,
        }
        return render_template('dashboard.html', username=session['username'], stats=user_stats)
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
        elif game_mode == 'sound_game_sur':
            return redirect(url_for('sound_game_sur'))
        elif game_mode == 'rhythm_relaxed':
            return redirect(url_for('rhythm_game_relaxed')) # redirect to rhythm game
        elif game_mode == 'rhythm_survival':
            return redirect(url_for('rhythm_game_survival'))
        elif game_mode == 'sound_game_rel':
            return redirect(url_for('sound_game_relaxed'))
        elif game_mode == 'more_info':
            return redirect(url_for('instructions'))
        else:
            # If no game mode is selected, show an error or redirect back
            return redirect(url_for('home'))



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

#number game relaxed 
@app.route('/relaxed_game_mode', methods=['GET', 'POST'])
def relaxed_game_mode():
    # Initialize session keys specific to the relaxed mode
    if 'relaxed_level_num' not in session or 'relaxed_gen_nums' not in session:
        session['relaxed_level_num'] = 1  # Start at level 1 for relaxed mode
        session['relaxed_gen_nums'] = []  # Clear generated numbers for a new session

    level_num = session.get('relaxed_level_num', 1)
    base_num_length = 3
    gen_nums_length = base_num_length + (level_num // 3)

    # Generate the numbers if not already generated
    if not session.get('relaxed_gen_nums'):
        gen_nums = [random.randint(0, 9) for _ in range(gen_nums_length)]
        session['relaxed_gen_nums'] = gen_nums
    else:
        gen_nums = session['relaxed_gen_nums']

    print(f"Relaxed Mode - Generated numbers: {gen_nums}, Level: {level_num}")

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'quit':
            # Reset the game level and numbers for relaxed mode
            #session['relaxed_level_num'] = 1
            level = 1
            session.pop('relaxed_gen_nums', None)
            return redirect(url_for('home'), numbers=[], level=1)

        if action == 'skip' or action == 'submit':
            if action == 'submit':
                recited_nums = request.form.get('numbers_input', '').strip()
                try:
                    recited_nums = [int(num) for num in recited_nums.split()]
                except ValueError:
                    return render_template('relaxed_game_mode.html', numbers=gen_nums, level=level_num, error="Invalid input.")

                if recited_nums != gen_nums:
                    return render_template('relaxed_game_mode.html', numbers=gen_nums, level=level_num, error="Incorrect input.")

            # Update level and regenerate numbers for relaxed mode
            level_num += 1
            session['relaxed_level_num'] = level_num
            session.pop('relaxed_gen_nums', None)
            gen_nums = [random.randint(0, 9) for _ in range(base_num_length + (level_num // 3))]
            session['relaxed_gen_nums'] = gen_nums

            points = 5
            update_score_in_database(session['id'], points, level_num)
            return redirect(url_for('relaxed_game_mode'))

    return render_template('relaxed_game_mode.html', numbers=gen_nums, level=level_num)

#survival game 
@app.route('/survival_game_mode', methods=['GET', 'POST'])
def survival_game_mode():
    # Initialize session keys specific to the survival mode
    if 'survival_level_num' not in session or 'survival_gen_nums' not in session:
        session['survival_level_num'] = 1  # Start at level 1 for survival mode
        session['survival_gen_nums'] = []  # Clear generated numbers for a new session

    level_num = session.get('survival_level_num', 1)
    base_num_length = 3
    gen_nums_length = base_num_length + (level_num // 3)

    # Generate the numbers if not already generated
    if not session.get('survival_gen_nums'):
        gen_nums = [random.randint(0, 9) for _ in range(gen_nums_length)]
        session['survival_gen_nums'] = gen_nums
    else:
        gen_nums = session['survival_gen_nums']

    print(f"Survival Mode - Generated numbers: {gen_nums}, Level: {level_num}")

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'quit':
            # Reset the game level and numbers for survival mode
            level = 1
            session.pop('survival_gen_nums', None)
            return redirect(url_for('home'))

        if action == 'skip' or action == 'submit':
            if action == 'submit':
                recited_nums = request.form.get('numbers_input', '').strip()
                try:
                    recited_nums = [int(num) for num in recited_nums.split()]
                except ValueError:
                    return render_template('survival_game_mode.html', numbers=gen_nums, level=level_num, error="Invalid input.")

                if recited_nums != gen_nums:
                    # Restart the survival mode game on incorrect input
                    session['survival_level_num'] = 1
                    session.pop('survival_gen_nums', None)
                    return render_template('survival_game_mode.html', numbers=[], level=1, error="Incorrect! Game Over!")

            # Update level and regenerate numbers for survival mode
            level_num += 1
            session['survival_level_num'] = level_num
            session.pop('survival_gen_nums', None)
            gen_nums = [random.randint(0, 9) for _ in range(base_num_length + (level_num // 3))]
            session['survival_gen_nums'] = gen_nums

            points = 10
            update_score_in_database(session['id'], points, level_num)
            return redirect(url_for('survival_game_mode'))

    return render_template('survival_game_mode.html', numbers=gen_nums, level=level_num)



#sound game routes 
@app.route('/sound_game_relaxed')
def sound_game_relaxed():
    return render_template('index_SG_relaxed.html')

@app.route('/start_melody', methods=['POST'])
def start_melody_route():
    return start_melody()

# @app.route('/user_input', methods=['POST'])
# def user_input_route():
#     user_input = request.json.get('userInput', [])
#     get_user_input(user_input)  # Update user input in the backend
#     return receive_user_input()

# @app.route('/try_melody_again', methods=['POST'])
# def try_melody_again_route():
#     return try_again()


# @app.route('/melody_memory_sur')
# def melody_memory_sur():
#     return melody_memory()

#SocketIO event to play specific MIDI file
@socketio.on('play_midi')
def handle_play_midi(data):
    midi_file = data['midiFile']
    pygame.mixer.init()
    pygame.mixer.music.load(midi_file)
    pygame.mixer.music.play()

# #Sound Game Survival 
@app.route('/sound_game_sur',methods=['GET','POST'])
def sound_game_sur():
    return render_template('index_SG_Survival.html')

def play_random_midi_files_survival():
    global survival_is_playing

    if survival_is_playing:
        return  # Prevent starting a new melody while one is playing

    survival_is_playing = True  # Set the flag to True when melody starts
    calculate_parameters_survival()  # Adjust parameters based on the level

    global survival_current_length, survival_current_speed, survival_letters_and_files_dict

    if survival_current_length > len(survival_letters_and_files_dict):
        raise ValueError("Length cannot exceed the number of available file paths.")

    midi_files = random.sample(list(survival_letters_and_files_dict.keys()), survival_current_length)
    get_midi_files_survival(midi_files)

    pygame.mixer.init()

    try:
        for midi_file in midi_files:
            letter = survival_letters_and_files_dict[midi_file]
            socketio.emit('highlight_square', {'letter': letter})

            pygame.mixer.music.load(os.path.join('static', 'MID_FILES', midi_file))
            pygame.mixer.music.play()
            pygame.time.wait(survival_current_speed)
            socketio.emit('reset_square', {'letter': letter})
            time.sleep(0.1)

        socketio.emit('melody_finished')
        print("Finished playing Survival Mode melody.")
    except pygame.error as e:
        print(f"Error playing MIDI file: {e}")
    finally:
        survival_is_playing = False

#function to check if the user input was correct and proceed accordingly
def move_on_or_game_over():
    print("Calling move_on_or_game_over function!")
    checked_user_input = check_user_input()

    global score
    global level

    print(f"User input has been checked: {checked_user_input}")

    if checked_user_input:
        
        score += 2
        level += 1
        print("User input was correct!")
        socketio.emit('next_round')  #notify frontend to proceed to the next round
        return play_random_midi_files()
    
    else:
        print("User input was incorrect!")
        global game_running
        game_running = False
        socketio.emit('game_over', {'level': level, 'score': score})  #notify frontend that the game is over
        return f"Game Over!\nLevel: {level}\nScore: {score}"

def calculate_parameters_survival():
    global survival_level, survival_current_speed, survival_current_length, survival_score

    if survival_level != 0 and survival_level % 2 == 0:
        survival_current_speed -= 300
        survival_score += 2

    if survival_level != 0 and survival_level % 3 == 0:
        if survival_current_length < 8:
            survival_current_length += 1
        survival_current_speed += 20
        survival_score += 3

    print(f"Survival Mode -> Level: {survival_level}, Score: {survival_score}, "
          f"Speed: {survival_current_speed}, Length: {survival_current_length}")

# @app.route('/user_input_survival', methods=['POST'])
# def receive_user_input_survival():
#     user_input = request.json.get('userInput', [])
#     get_user_input_survival(user_input)

#     if check_user_input_survival():
#         global survival_level, survival_score
#         survival_level += 1
#         survival_score += 2
#         print("Survival Mode: User input correct.")
#         socketio.emit('next_round')
#         play_random_midi_files_survival()
#         return jsonify({'message': 'Correct! Proceeding to next level.'})
#     else:
#         print("Survival Mode: User input incorrect.")
#         global survival_game_running
#         survival_game_running = False
#         socketio.emit('game_over', {
#             'level': survival_level,
#             'score': survival_score
#         })
#         return jsonify({'message': f"Game Over! Level: {survival_level}, Score: {survival_score}"})

@socketio.on('quit_game_survival')
def handle_quit_game_survival():
    global survival_is_playing, survival_game_running
    global survival_level, survival_current_length, survival_current_speed, survival_score

    survival_is_playing = False
    survival_game_running = False
    survival_level = 0
    survival_current_length = 3
    survival_current_speed = 1000
    survival_score = 0

    print("Survival Mode: Game quit by the user.")

#HTTP route to send list of available letters to frontend
@app.route('/get_letters', methods=['GET'])
def get_letters():
    return jsonify({'letters': letters})




@app.route('/rhythm_game_relaxed', methods=['GET', 'POST'])
def rhythm_game_relaxed():
    # Render the rhythm game with relaxed mode settings
    return render_template('rhythm_index.html', mode='Relaxed')

@app.route('/rhythm_game_survival', methods=['GET', 'POST'])
def rhythm_game_survival():
    # Render the rhythm game with survival mode settings
    return render_template('rhythm_index.html', mode='Survival')

@app.route('/generate_rhythm', methods=['GET'])
def generate_rhythm():
    length = int(request.args.get('length', 4))  # Default rhythm length of 4 beats
    rhythm = [random.uniform(0.5, 1.5) for _ in range(length)]  # Random time intervals
    return jsonify({'rhythm': rhythm})



if __name__ == '__main__':
    socketio.run(app, debug=True)







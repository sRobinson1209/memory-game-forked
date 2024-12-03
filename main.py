from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
from flask_cors import CORS
from flask_socketio import SocketIO
import os
import random
import time
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
import pygame
import re

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
    move_on_or_game_over as move_on_or_game_over_relaxed,
    start_melody,
    try_again,
    melody_memory,
    receive_user_input,
)
from app import(
    play_random_midi_files as play_random_midi_files_sur,
    move_on_or_game_over as move_on_or_game_over_survival
)
from globals import current_midi_files, current_user_input, is_playing, game_running


# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app)
app.secret_key = 'secret1209'  # Necessary for session management


letters = ['a','s','d','f','g','h','j','k']

#trying to append the correct midi files path to game
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# MIDI_FILES_PATH = os.path.join(BASE_DIR, 'static', 'MID_FILES')

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
            return redirect(url_for('melody_memory_sur'))
        elif game_mode == 'rhythm_relaxed':
            return redirect(url_for('rhythm_game_relaxed')) # redirect to rhythm game
        elif game_mode == 'rhythm_survival':
            return redirect(url_for('rhythm_game_survival'))
        elif game_mode == 'sound_game_rel':
            return redirect(url_for('melody_memory_relaxed'))
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

#Number survival game 
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

#Sound Game Relaxed 

#Game state variables
is_playing = False
game_running = False

level = 0

current_speed = 1000 
current_length = 3

letters = ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k']

#route to serve index_SG_relaxed.HTML file
@app.route('/melody_memory_relaxed')
def melody_memory_relaxed():
    return render_template('index_SG_relaxed.html')

#SocketIO event to play specific MIDI file
@socketio.on('play_midi')
def handle_play_midi(data):
    midi_file = data['midiFile']
    pygame.mixer.init()
    pygame.mixer.music.load(midi_file)
    pygame.mixer.music.play()

#HTTP route to start melody playback if the game isn't already running
@app.route('/start_melody', methods=['POST'])
def start_melody():
    global game_running
    if not game_running:
        game_running = True
        socketio.start_background_task(play_random_midi_files)  #start melody task
    return jsonify({'message': 'Melody started!'})

#listen for 'quit_game' event from frontend
@socketio.on('quit_game')
def handle_quit_game():
    global is_playing
    global game_running
    global level
    global current_speed
    global current_length

    is_playing = False  
    game_running = False

    level = 0 #reset level
    current_speed = 1000 #reset speed
    current_length = 3 #reset length

    print('Game has been quit by the user.')

#HTTP route to send list of available letters to frontend
@app.route('/get_letters', methods=['GET'])
def get_letters():
    return jsonify({'letters': letters})

#HTTP route to receive user input and check if it matches the melody
@app.route('/user_input', methods=['POST'])
def receive_user_input():
    user_input = request.json.get('userInput', [])
    get_user_input_relaxed(user_input)
    message = move_on_or_game_over_relaxed()
    return jsonify({'message': message})

#HTTP route to handle level progression after the user passes a level
@app.route('/pass_level', methods=['POST'])
def pass_level():
    global level

    level += 1  
    print("User passed the level!")
    
    socketio.emit('next_round') #emit event to frontend to inform about the next round
    socketio.start_background_task(play_random_midi_files) #start next melody sequence by calling the function
    return jsonify({'message': 'Moved to the next round!'})

#calculates the parameters based on the level the user is on
def calculate_parameters():
    print("Called calculate_parameters!")
    
    global level
    global current_speed
    global current_length

    #every 2nd level increase speed
    if level != 0 and level % 2 == 0:
        current_speed = current_speed - 300
    
    #every 3rd level inc length and dec speed by a little (so game isn't impossible)
    if level != 0 and level % 3 == 0:
        if current_length < 8: #make sure notes don't go out of octive range
            current_length = current_length + 1

        current_speed = current_speed + 20
    
    print(f"Current Level: {level}\nCurrent Speed: {current_speed}\nCurrent Length: {current_length}")

import os

MIDI_FILES_PATH = os.path.join('static', 'MID_FILES')  # Define the path to your MIDI files

def play_random_midi_files():
    global is_playing

    if is_playing:
        return  # Prevent starting a new melody while one is still playing

    is_playing = True  # Set the flag to True when melody starts

    calculate_parameters()

    global current_length
    global current_speed
    global relaxed_letters_and_files_dict

    # Check if the length is not greater than the available file paths
    if current_length > len(relaxed_letters_and_files_dict):
        raise ValueError("Length cannot be greater than the number of available file paths.")

    # Select random MIDI files
    midi_files = random.sample(list(relaxed_letters_and_files_dict.keys()), current_length)
    get_midi_files_relaxed(midi_files)  # Notify the frontend with the selected file names

    # Construct full paths for playback
    full_paths = [os.path.join(MIDI_FILES_PATH, file) for file in midi_files]
    print(f"Full paths for playback: {full_paths}")

    pygame.mixer.init()

    # Stop any currently playing sound and clear the queue
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()  # Unload the previous music to avoid overlap

    try:
        for file_name, full_path in zip(midi_files, full_paths):
            # Get the corresponding letter for the file
            letter = relaxed_letters_and_files_dict[file_name]
            socketio.emit('highlight_square', {'letter': letter})  # Notify frontend to highlight the square

            # Load and play the MIDI file
            pygame.mixer.music.load(full_path)
            pygame.mixer.music.play()
            pygame.time.wait(current_speed)  # Wait for the length of the sound

            # Reset the square on the frontend
            socketio.emit('reset_square', {'letter': letter})
            time.sleep(0.1)  # Delay between notes

        socketio.emit('melody_finished')
        print('Finished playing all selected MIDI files.')
    except pygame.error as e:
        print(f"Error playing MIDI file: {e}")
    finally:
        is_playing = False  # Reset the flag when done

    
#function to check if the user input was correct and proceed accordingly
def move_on_or_game_over():
    print("Calling move_on_or_game_over function!")
    checked_user_input = check_user_input_relaxed()

    global level

    print(f"User input has been checked: {checked_user_input}")

    if checked_user_input:
        
        #score += 2
        level += 1
        print("User input was correct!")
        socketio.emit('next_round')  #notify frontend to proceed to the next round
        return play_random_midi_files()
    
    else:
        print("User input was incorrect!")
        #emit event to frontend to show "Try Again" and "Pass" buttons
        socketio.emit('input_incorrect', {'level': level})  
        return f"Input was incorrect. Try again!"


@app.route('/try_melody_again', methods=['POST'])
def try_melody_again():
    socketio.start_background_task(try_again)  
    return jsonify({'message': 'Previous melody started!'})

#HTTP route to retry last melody after an incorrect input
def try_again():
    print("Trying again!")

    return_midi_files = send_current_midi_files_back()

    global is_playing

    print(f"Previous MIDI files: {return_midi_files}")

    if is_playing:
        return  #prevent starting a new melody while one is still playing
    
    is_playing = True  #set the flag to True when melody starts
    
    global current_length
    global current_speed
    global relaxed_letters_and_files_dict

    get_midi_files_relaxed(return_midi_files) #return previously played midi files to backend

    pygame.mixer.init()
    if pygame.mixer.music.get_busy(): #stop any currently playing sound and clear the queue
        pygame.mixer.music.stop()  
        pygame.mixer.music.unload()  #unload the previous music to avoid overlap

    for midi_file in return_midi_files:
        letter = relaxed_letters_and_files_dict[midi_file]
        
        socketio.emit('highlight_square', {'letter': letter}) #emit an event to the front end to turn the corresponding square blue
        pygame.mixer.music.load(midi_file)
        pygame.mixer.music.play()
        pygame.time.wait(current_speed) #wait for the length of the sound (simulate the time the note is playing)
        socketio.emit('reset_square', {'letter': letter}) #emit an event to the front end to turn the square back to grey
        time.sleep(0.1)  #delay between notes 

    socketio.emit('melody_finished')
    print('Finished playing all selected MIDI files.')
    is_playing = False  #reset the flag when done

#sound game survival 
#Game state variables
is_playing = False
game_running = False

level = 0
score = 0

current_speed = 1000 
current_length = 3

sur_letters = ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k']

#route to serve index.HTML file
@app.route('/melody_memory_sur')
def melody_memory_sur():
    return render_template('index_SG_Survival.html')

#SocketIO event to play specific MIDI file
@socketio.on('play_midi')
def handle_play_midi(data):
    midi_file = data['midiFile']
    pygame.mixer.init()
    pygame.mixer.music.load(midi_file)
    pygame.mixer.music.play()


#HTTP route to start melody playback if the game isn't already running
@app.route('/start_melody_sur', methods=['POST'])
def start_melody_sur():
    global game_running
    if not game_running:
        game_running = True
        socketio.start_background_task(play_random_midi_files)  # start the melody task
    return jsonify({'message': 'Melody started!'})


#listen for the 'quit_game' event from the frontend
@socketio.on('quit_game')
def handle_quit_game():
    global is_playing
    global game_running
    global current_length
    global current_speed
    global score
    global level

    is_playing = False  
    game_running = False 

    current_length = 3
    current_speed = 1000

    print('Game has been quit by the user.')

    score = 0
    level = 0

#HTTP route to send list of available letters to frontend
@app.route('/get_letters_sur', methods=['GET'])
def get_letters_sur():
    return jsonify({'letters': sur_letters})


#HTTP route to receive user input and check if it matches the melody
@app.route('/user_input_survival', methods=['POST'])
def receive_user_input_sur():
    user_input = request.json.get('userInput', [])
    get_user_input_survival(user_input)
    message = move_on_or_game_over_survival()
    return jsonify({'message': message})

#calculates the parameters based on the level the user is on
def calculate_parameters():
    print("Called calculate_parameters!")
    
    global level
    global current_speed
    global current_length
    global score

    #every 2nd level increase speed
    if level != 0 and level % 2 == 0:
        current_speed = current_speed - 300
        score +=  2
    
    #every 3rd level inc length and dec speed by a little (so game isn't impossible)
    if level != 0 and level % 3 == 0:

        if current_length < 8: #make sure notes don't go out of octive range
            current_length = current_length + 1

        current_speed = current_speed + 20
        score += 3
    
    print(f"Current Level: {level}\nCurrent Score: {score}\nCurrent Speed: {current_speed}\nCurrent Length: {current_length}")

#play random MIDI files for user to recite
def play_random_midi_files():
    global is_playing

    if is_playing:
        return  #prevent starting a new melody while one is still playing

    is_playing = True  #set the flag to True when melody starts

    calculate_parameters() #called from backend

    global current_length
    global current_speed
    global survival_letters_and_files_dict

    #check length is not greater than the available file paths
    if current_length > len(survival_letters_and_files_dict):
        raise ValueError("Length cannot be greater than the number of available file paths.")

    midi_files = random.sample(list(survival_letters_and_files_dict.keys()), current_length) #selects random MIDI files to play
    get_midi_files_survival(midi_files) #return random midi files to backend

    pygame.mixer.init()

    #stop any currently playing sound and clear the queue
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()  #stop any currently playing MIDI
        pygame.mixer.music.unload()  #unload the previous music to avoid overlap


    for midi_file in midi_files:
        letter = survival_letters_and_files_dict[midi_file]
        
        socketio.emit('highlight_square', {'letter': letter}) #emit an event to the front end to turn the corresponding square red
        pygame.mixer.music.load(midi_file)
        pygame.mixer.music.play()
        pygame.time.wait(current_speed) #wait for the length of the sound (simulate the time the note is playing)
        socketio.emit('reset_square', {'letter': letter}) #emit an event to the front end to turn the square back to grey
        time.sleep(0.1)  #delay between notes 

    socketio.emit('melody_finished')
    print('Finished playing all selected MIDI files.')
    is_playing = False  #reset the flag when done


#function to check if the user input was correct and proceed accordingly
def move_on_or_game_over_survival():
    print("Calling move_on_or_game_over function!")
    checked_user_input = check_user_input_survival()

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

if __name__ == '__main__':
    socketio.run(app, debug=True)







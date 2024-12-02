'''
========================
SURVIVAL MODE APP.PY FILE
========================
'''
from flask import Flask, send_file, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import random
import time
import pygame

from SoundGameSurvival import letters_and_files_dict, get_midi_files, get_user_input, check_user_input

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app)

#Game state variables
is_playing = False
game_running = False

level = 0
score = 0

current_speed = 1000 
current_length = 3

letters = ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k']

#route to serve index.HTML file
@app.route('/')
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
@app.route('/start_melody', methods=['POST'])
def start_melody():
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
@app.route('/get_letters', methods=['GET'])
def get_letters():
    return jsonify({'letters': letters})


#HTTP route to receive user input and check if it matches the melody
@app.route('/user_input', methods=['POST'])
def receive_user_input():
    user_input = request.json.get('userInput', [])
    get_user_input(user_input)
    message = move_on_or_game_over()
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
    global letters_and_files_dict

    #check length is not greater than the available file paths
    if current_length > len(letters_and_files_dict):
        raise ValueError("Length cannot be greater than the number of available file paths.")

    midi_files = random.sample(list(letters_and_files_dict.keys()), current_length) #selects random MIDI files to play
    get_midi_files(midi_files) #return random midi files to backend

    pygame.mixer.init()

    #stop any currently playing sound and clear the queue
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()  #stop any currently playing MIDI
        pygame.mixer.music.unload()  #unload the previous music to avoid overlap


    for midi_file in midi_files:
        letter = letters_and_files_dict[midi_file]
        
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


if __name__ == '__main__':
    socketio.run(app, debug=True)

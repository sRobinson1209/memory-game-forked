from flask import Flask, send_file, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import random
import time
import pygame

from SoundGameSurvival import level, score, current_length, current_speed, letters_and_files_dict, calculate_parameters, get_midi_files, get_user_input, check_user_input
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app)

letters = ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k']
is_playing = False

@app.route('/')
def melody_memory():
    return send_file('index.html')

@socketio.on('play_midi')
def handle_play_midi(data):
    midi_file = data['midiFile']
    pygame.mixer.init()
    pygame.mixer.music.load(midi_file)
    pygame.mixer.music.play()

@app.route('/start_melody', methods=['POST'])
def start_melody():
    socketio.start_background_task(play_random_midi_files)  # Run melody playback in a background task
    return jsonify({'message': 'Melody started!'})

@app.route('/get_letters', methods=['GET'])
def get_letters():
    return jsonify({'letters': letters})

@app.route('/user_input', methods=['POST'])
def receive_user_input():
    user_input = request.json.get('userInput', [])
    # Call the get_user_input function from SoundGameSurvival.py
    get_user_input(user_input)
    message = move_on_or_game_over()
    
    return jsonify({'message': message})

def play_random_midi_files():
    global is_playing

    if is_playing:
        return  # Prevent starting a new melody while one is still playing

    is_playing = True  # Set the flag to True when melody starts

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

    # Stop any currently playing sound and clear the queue
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()  # Stop any currently playing MIDI
        pygame.mixer.music.unload()  # Unload the previous music to avoid overlap


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
    is_playing = False  # Reset the flag when done
    
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
        socketio.emit('next_round')  # Notify frontend to proceed to the next round
        return play_random_midi_files()
    
    else:
        print("User input was incorrect!")
        socketio.emit('game_over', {'level': level, 'score': score})  # Notify frontend that the game is over
        
        return f"Game Over!\nLevel: {level}\nScore: {score}"


if __name__ == '__main__':
    socketio.run(app, debug=True)


'''
NEED TO MAKE SURE THE GLOBAL VARIABLES UPDATE!!!    
'''
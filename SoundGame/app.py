from flask import Flask, send_file, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import random
import time
import pygame

from SoundGameSurvival import current_length, current_speed, get_user_input
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app)

letters_and_files_dict = {
    'MID_FILES/c_note_one_sec.mid': 'a',
    'MID_FILES/d_note_one_sec.mid': 's',
    'MID_FILES/e_note_one_sec.mid': 'd',
    'MID_FILES/f_note_one_sec.mid': 'f',
    'MID_FILES/g_note_one_sec.mid': 'g',
    'MID_FILES/a_note_one_sec.mid': 'h',
    'MID_FILES/b_note_one_sec.mid': 'j',
    'MID_FILES/c_oct_note_one_sec.mid': 'k'
}

letters = ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k']

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
    result = get_user_input(user_input)
    return jsonify({'message': result})

def play_random_midi_files():

    global current_length
    global current_speed
    # Select random MIDI files to play (change this logic if needed)
    midi_files = random.sample(list(letters_and_files_dict.keys()), current_length)

    pygame.mixer.init()
    for midi_file in midi_files:
        letter = letters_and_files_dict[midi_file]
        
        # Emit an event to the front end to turn the corresponding square red
        socketio.emit('highlight_square', {'letter': letter})
        
        pygame.mixer.music.load(midi_file)
        pygame.mixer.music.play()

        # Wait for the length of the sound (simulate the time the note is playing)
        pygame.time.wait(current_speed)  

        # Emit an event to the front end to turn the square back to grey
        socketio.emit('reset_square', {'letter': letter})

        time.sleep(0.1)  # Delay between notes

    socketio.emit('melody_finished')  # Notify the front end that the melody has finished
    

if __name__ == '__main__':
    socketio.run(app, debug=True)

'''
Next Coding Sesh:
- add functionality to app.py so it does the same updating as SOundGameSurvival
- or modify app.py to use the same function from SOundGameSurvival'''

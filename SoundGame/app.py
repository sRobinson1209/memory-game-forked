'''
app.py handles setting up the Flask Backend

Flask is used to serve the game logic & handle communication between Python backend & thre frontend (js file)

Here there are API routes to handle the game logic (generating a melody and recieving the user's input)

Basically Separting backedn logic from frontent logic 
- front end interacts with UI
- back end is the python file that has the game in it
'''

from flask import Flask, jsonify, request
from flask_cors import CORS
import pretty_midi
import random
import pygame
import os
import time

app = Flask(__name__)
CORS(app)

# Globals and game state initialization
current_instrument = 'Acoustic Grand Piano'
current_key = 'c'
current_key_scale = [60, 62, 64, 65, 67, 69, 71, 72]
random_seq = []
current_speed = 1
current_length = 3
level = 0
score = 0
MIDI_FILE_PATH = 'generated_melody.mid'

#generates a new key
def generate_new_key():

    global current_key, current_key_scale
    key_dictionary = {
        "c": [60, 62, 64, 65, 67, 69, 71, 72],
        "d": [62, 64, 66, 67, 69, 71, 73, 74],
        "e": [64, 66, 68, 69, 71, 73, 75, 76],
        "f": [65, 67, 69, 70, 72, 74, 76, 77],
        "g": [55, 57, 59, 60, 62, 64, 66, 67],
        "a": [57, 59, 61, 62, 64, 66, 68, 69],
        "b": [59, 61, 63, 64, 66, 68, 70, 71]
    }
    
    #cycle through keys
    current_key_index = list(key_dictionary).index(current_key)

    try:
        current_key = list(key_dictionary)[current_key_index + 1]

    except IndexError:
        current_key = "c"  #reset to "c" if at end

    current_key_scale = key_dictionary[current_key]


#generates a new instrument
def generate_new_instrument():

    global current_instrument
    instruments = ['Acoustic Grand Piano', 'Rock Organ', 'Music Box', 'Flute', 'Choir Aahs', 'Violin', 'Trumpet', 'Bassoon', 'Cello']
    try:
        current_instrument = instruments[(instruments.index(current_instrument) + 1) % len(instruments)]
    except ValueError:
        current_instrument = 'Acoustic Grand Piano'


#calculates the parameters based on the level the user is on
def calculate_parameters():
    
    global level
    global current_speed
    global current_length
    global score

    #every 5th level increase speed
    if level != 0 and level % 5 == 0:
        current_speed = current_speed - 0.09
        score +=  2
    
    #every 10th level inc length and dec speed by a little (so game isn't impossible)
    if level != 0 and level % 10 == 0:

        if current_length < 8: #make sure notes don't go out of octive range
            current_length = current_length + 1

        current_speed = current_speed + 0.02
        score += 3

    #every 7th level change key
    if level != 0 and level % 7 == 0:
        generate_new_key()
        
        
    #every 15th level change instrument
    if level != 0 and level % 15 == 0:
        generate_new_instrument()


#generates the melody
@app.route('/generate_melody', methods=['GET'])
def generate_melody():
    global random_seq, current_key_scale, current_instrument, current_length, current_speed, score, level, MIDI_FILE_PATH
    calculate_parameters()

    if current_length > len(current_key_scale):
        return jsonify({'error': 'Length cannot be greater than the scale size'}), 400

    midi = pretty_midi.PrettyMIDI()
    sound_program = pretty_midi.instrument_name_to_program(current_instrument)
    instr = pretty_midi.Instrument(program=sound_program)

    random_seq = random.sample(current_key_scale[:current_length], current_length)

    for i, note_num in enumerate(random_seq):
        start_time = i * current_speed
        end_time = (i + 1) * current_speed
        note = pretty_midi.Note(velocity=100, pitch=note_num, start=start_time, end=end_time)
        instr.notes.append(note)

    midi.instruments.append(instr)
    midi.write(MIDI_FILE_PATH)

    level += 1
    score += 2

    return jsonify({
        'melody': random_seq,
        'level': level,
        'score': score,
        'instrument': current_instrument,
        'key': current_key,
        'speed': current_speed
    })

#endpoint to play the generated melody
@app.route('/play_melody', methods=['GET'])
def play_melody():
    if os.path.exists(MIDI_FILE_PATH):
        play_sound(MIDI_FILE_PATH)
        return jsonify({'status': 'playing'}), 200
    else:
        return jsonify({'error': 'No melody file found'}), 400


#plays a MIDI file
def play_sound(midi_file):
    pygame.mixer.init()
    pygame.mixer.music.load(midi_file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(1)


#run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
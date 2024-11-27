from flask import Flask, send_file, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import random
import time
import pygame

from SoundGameRelaxed import letters_and_files_dict, get_midi_files, get_user_input, check_user_input, send_current_midi_files_back
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app)

'''

EVERYTING SHOULD RESIT
FIX PASS TO PLAY MELODY

'''

letters = ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k']
is_playing = False
game_running = False
level = 0
current_speed = 1000 #default 1 second
current_length = 3

@app.route('/')
def melody_memory():
    return send_file('index_SG_relaxed.html')

@socketio.on('play_midi')
def handle_play_midi(data):
    midi_file = data['midiFile']
    pygame.mixer.init()
    pygame.mixer.music.load(midi_file)
    pygame.mixer.music.play()

@app.route('/start_melody', methods=['POST'])
def start_melody():
    global game_running
    if not game_running:
        game_running = True
        socketio.start_background_task(play_random_midi_files)  # start the melody task
    return jsonify({'message': 'Melody started!'})

# Listen for the 'quit_game' event from the frontend
@socketio.on('quit_game')
def handle_quit_game():
    global is_playing
    global game_running
    global level
    global current_speed
    global current_length
    is_playing = False  # stop any melody playing
    game_running = False  # mark the game as not running
    level = 0 #reset level
    current_speed = 1000 #reset speed
    current_length = 3 #reset length
    print('Game has been quit by the user.')

@app.route('/get_letters', methods=['GET'])
def get_letters():
    return jsonify({'letters': letters})

@app.route('/user_input', methods=['POST'])
def receive_user_input():
    user_input = request.json.get('userInput', [])
    get_user_input(user_input)
    message = move_on_or_game_over()
    
    return jsonify({'message': message})

@app.route('/pass_level', methods=['POST'])
def pass_level():
    global level
    level += 1  # Increase level as if the user passed the current level
    print("User passed the level!")
    
    # Emit event to frontend to inform about the next round
    socketio.emit('next_round')
    
    # Start the next melody sequence by calling the function
    socketio.start_background_task(play_random_midi_files)
    
    return jsonify({'message': 'Moved to the next round!'})

#calculates the parameters based on the level the user is on
def calculate_parameters():
    print("Called calculate_parameters!")
    
    global level
    global current_speed
    global current_length
    #global score

    #every 2nd level increase speed
    if level != 0 and level % 2 == 0:
        current_speed = current_speed - 300
        #score +=  2
    
    #every 3rd level inc length and dec speed by a little (so game isn't impossible)
    if level != 0 and level % 3 == 0:

        if current_length < 8: #make sure notes don't go out of octive range
            current_length = current_length + 1

        current_speed = current_speed + 20
        #score += 3
    
    print(f"Current Level: {level}\nCurrent Speed: {current_speed}\nCurrent Length: {current_length}")


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
        pygame.mixer.music.stop()  
        pygame.mixer.music.unload()  #unload the previous music to avoid overlap


    for midi_file in midi_files:
        letter = letters_and_files_dict[midi_file]
        
        socketio.emit('highlight_square', {'letter': letter}) #emit an event to the front end to turn the corresponding square blue
        pygame.mixer.music.load(midi_file)
        pygame.mixer.music.play()
        pygame.time.wait(current_speed) #wait for the length of the sound (simulate the time the note is playing)
        socketio.emit('reset_square', {'letter': letter}) #emit an event to the front end to turn the square back to grey
        time.sleep(0.1)  #delay between notes 

    socketio.emit('melody_finished')
    print('Finished playing all selected MIDI files.')
    is_playing = False  #reset the flag when done
    
def move_on_or_game_over():
    print("Calling move_on_or_game_over function!")
    checked_user_input = check_user_input()

   #global score
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
    global letters_and_files_dict

    get_midi_files(return_midi_files) #return previously played midi files to backend

    pygame.mixer.init()

    #stop any currently playing sound and clear the queue
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()  
        pygame.mixer.music.unload()  #unload the previous music to avoid overlap

    for midi_file in return_midi_files:
        letter = letters_and_files_dict[midi_file]
        
        socketio.emit('highlight_square', {'letter': letter}) #emit an event to the front end to turn the corresponding square blue
        pygame.mixer.music.load(midi_file)
        pygame.mixer.music.play()
        pygame.time.wait(current_speed) #wait for the length of the sound (simulate the time the note is playing)
        socketio.emit('reset_square', {'letter': letter}) #emit an event to the front end to turn the square back to grey
        time.sleep(0.1)  #delay between notes 

    socketio.emit('melody_finished')
    print('Finished playing all selected MIDI files.')
    is_playing = False  #reset the flag when done

    

if __name__ == '__main__':
    socketio.run(app, debug=True)
#Sound Game 
#@app.route('/sound_game_relaxed', methods=['GET', 'POST'])
#def sound_game_relaxed():
    #Game state variables
    is_playing = False
    game_running = False

    level = 0

    current_speed = 1000 
    current_length = 3

    letters = ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k']

#route to serve index_SG_relaxed.HTML file
@app.route('/sound_game_relaxed')
def melody_memory():
    #return send_file('index_SG_relaxed.html')
    return render_template('index_SG_relaxed.html')

BASE_DIR = os.path.join(os.getcwd(),'MID_FILES')
#SocketIO event to play specific MIDI file
@socketio.on('play_midi')
def handle_play_midi(data):
    midi_file = data['midiFile']
    midi_path = os.path.join(BASE_DIR, midi_file)
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(midi_path)
        pygame.mixer.music.play()
    except pygame.error as e:
        print(f"Error playing {midi_file}: {e}")
        socketio.emit('error', {'message': f"Error playing {midi_file}"})

game_running = False
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
    get_user_input(user_input)
    message = move_on_or_game_over()
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
    
    #global level
    #global current_speed
    #global current_length
    level = 0
    current_speed = 1000
    current_length = 3

    #every 2nd level increase speed
    if level != 0 and level % 2 == 0:
        current_speed = current_speed - 300
    
    #every 3rd level inc length and dec speed by a little (so game isn't impossible)
    if level != 0 and level % 3 == 0:
        if current_length < 8: #make sure notes don't go out of octive range
            current_length = current_length + 1

        current_speed = current_speed + 20
    
    print(f"Current Level: {level}\nCurrent Speed: {current_speed}\nCurrent Length: {current_length}")

is_playing = False
#play random MIDI files for user to recite
def play_random_midi_files():
    global is_playing

    if is_playing:
        return  #prevent starting a new melody while one is still playing

    is_playing = True  #set the flag to True when melody starts

    calculate_parameters()

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
    
#function to check if the user input was correct and proceed accordingly
def move_on_or_game_over():
    print("Calling move_on_or_game_over function!")
    checked_user_input = check_user_input()

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
    global letters_and_files_dict

    get_midi_files(return_midi_files) #return previously played midi files to backend

    pygame.mixer.init()
    if pygame.mixer.music.get_busy(): #stop any currently playing sound and clear the queue
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

    #return render_template('index_SG_relaxed.html')






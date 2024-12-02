'''
=======================
SOUND GAME RELAXED MODE
=======================
'''

current_midi_files = []
current_user_input = []

letters_and_files_dict = {
    'a_note_one_sec.mid': 'a',
    'b_note_one_sec.mid': 'b',
    'c_note_one_sec.mid': 'c',
    'd_note_one_sec.mid': 'd',
    'e_note_one_sec.mid': 'e',
    'f_note_one_sec.mid': 'f',
    'g_note_one_sec.mid': 'g',
    'c_oct_note_one_sec.mid': 'k',
}




#called from frontend to update global variable
def get_midi_files(midi_files):
    # Send only the file names
    print(f"Selected MIDI Files sent to frontend: {midi_files}")
    global current_midi_files
    current_midi_files = midi_files


#called from frontend to update global variable
def get_user_input(user_input):
    print(f"User input received: {user_input}")
    global current_user_input 
    current_user_input = user_input
    
#checkes the user input against the random midi file sequence
def check_user_input():
    print("Checking user input!")
    global letters_and_files_dict
    global current_midi_files
    global current_user_input
    
    if len(current_midi_files) != len(current_user_input):
        return False

    value_to_key_dict = {v: k for k, v in letters_and_files_dict.items()} #get value to key mapping by reversing dict

    for i in range(len(current_midi_files)):
        
        if current_user_input[i] in value_to_key_dict: #get key corresponding to user input
            corresponding_key = value_to_key_dict[current_user_input[i]]
        else:
            return False 

        if current_midi_files[i] != corresponding_key:
            return False

    return True


def send_current_midi_files_back():
    global current_midi_files
    return [os.path.basename(file) for file in current_midi_files]

    
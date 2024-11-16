import pretty_midi
import os
import pygame
import random

level = 0
current_speed = 1000 #default 1 second
current_length = 3
score = 0

letters_and_files_dict = {'MID_FILES/c_note_one_sec.mid' : 'a', 'MID_FILES/d_note_one_sec.mid' : 's', 'MID_FILES/e_note_one_sec.mid':'d',
                          'MID_FILES/f_note_one_sec.mid':'f', 'MID_FILES/g_note_one_sec.mid': 'g', 'MID_FILES/a_note_one_sec.mid': 'h',
                          'MID_FILES/b_note_one_sec.mid' : 'j', 'MID_FILES/c_oct_note_one_sec.mid':'k'}


#calculates the parameters based on the level the user is on
def calculate_parameters():
    
    global level
    global current_speed
    global current_length
    global score

    #every 5th level increase speed
    if level != 0 and level % 5 == 0:
        current_speed = current_speed - 100
        score +=  2
    
    #every 10th level inc length and dec speed by a little (so game isn't impossible)
    if level != 0 and level % 10 == 0:

        if current_length < 8: #make sure notes don't go out of octive range
            current_length = current_length + 1

        current_speed = current_speed + 20
        score += 3


def play_random_midi_files():

    calculate_parameters()

    global current_length
    global current_speed
    global score
    global level
    global letters_and_files_dict

    file_paths = [
    'MID_FILES/c_note_one_sec.mid',
    'MID_FILES/d_note_one_sec.mid',
    'MID_FILES/e_note_one_sec.mid',
    'MID_FILES/f_note_one_sec.mid',
    'MID_FILES/g_note_one_sec.mid',
    'MID_FILES/a_note_one_sec.mid',
    'MID_FILES/b_note_one_sec.mid',
    'MID_FILES/c_oct_note_one_sec.mid'
    ]
    # Ensure that the requested length is not greater than the available file paths
    if current_length > len(file_paths):
        raise ValueError("Length cannot be greater than the number of available file paths.")
    
    # Randomly shuffle and select 'length' number of file paths
    selected_files = random.sample(file_paths, current_length)
    print(f"Selected MID files: {selected_files}")

    pygame.mixer.init()
    for midi_file in selected_files:
        print(f"Playing: {midi_file}")
        pygame.mixer.music.load(midi_file)
        pygame.mixer.music.play()

        pygame.time.wait(current_speed) #500 is 1/2 a second

    print('Finished playing all selected MIDI files.')

    user_input = get_user_input()

    checked_user_input = check_user_input(selected_files, user_input, letters_and_files_dict)
    print(f"User input has been checked: {checked_user_input}")

    if checked_user_input:
        score += 2
        level += 1
        print("User input was correct!")
        return play_random_midi_files()
    
    else:
        print("User input was incorrect!")
        return f"Game Over!\nLevel: {level}\nScore: {score}"


def get_user_input(user_input):
    print(f"User input received: {user_input}")
    return f"User input was: {user_input}"


def check_user_input(selected_files, user_input, letters_and_files_dict):
    if len(selected_files) != len(user_input):
        return False

    # Reverse the dictionary to get a value-to-key mapping
    value_to_key_dict = {v: k for k, v in letters_and_files_dict.items()}

    for i in range(len(selected_files)):
        # Get the key corresponding to the user input (which is a value in the original dict)
        if user_input[i] in value_to_key_dict:
            corresponding_key = value_to_key_dict[user_input[i]]
        else:
            return False  # If the value doesn't exist in the dict, it's an invalid input

        # Compare the selected file with the corresponding key from user input
        if selected_files[i] != corresponding_key:
            return False

    return True



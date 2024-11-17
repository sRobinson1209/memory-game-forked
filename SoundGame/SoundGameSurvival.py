import pretty_midi
import os
import pygame
import random

level = 0
score = 0
current_speed = 1000 #default 1 second
current_length = 3
current_midi_files = []
current_user_input = []

letters_and_files_dict = {'MID_FILES/c_note_one_sec.mid' : 'a', 'MID_FILES/d_note_one_sec.mid' : 's', 'MID_FILES/e_note_one_sec.mid':'d',
                          'MID_FILES/f_note_one_sec.mid':'f', 'MID_FILES/g_note_one_sec.mid': 'g', 'MID_FILES/a_note_one_sec.mid': 'h',
                          'MID_FILES/b_note_one_sec.mid' : 'j', 'MID_FILES/c_oct_note_one_sec.mid':'k'}


#calculates the parameters based on the level the user is on
def calculate_parameters():
    print("Called calculate_parameters!")
    
    global level
    global current_speed
    global current_length
    global score

    #every 5th level increase speed
    if level != 0 and level % 5 == 0:
        current_speed = current_speed - 300
        score +=  2
    
    #every 10th level inc length and dec speed by a little (so game isn't impossible)
    if level != 0 and level % 3 == 0:

        if current_length < 8: #make sure notes don't go out of octive range
            current_length = current_length + 1

        current_speed = current_speed + 20
        score += 3
    
    print(f"Current Level: {level}\nCurrent Score: {score}\nCurrent Speed: {current_speed}\nCurrent Length: {current_length}")

#called from frontend to update global variable
def get_midi_files(midi_files):
    print(f"Selected MIDI Files recieved: {midi_files}")
    global current_midi_files
  
    current_midi_files = midi_files

#called from frontend to update global variable
def get_user_input(user_input):
    print(f"User input received: {user_input}")
    global current_user_input 
    
    current_user_input = user_input
    #return f"User input was: {user_input}"


def check_user_input():
    print("Checking user input!")
    global letters_and_files_dict
    global current_midi_files
    global current_user_input
    
    if len(current_midi_files) != len(current_user_input):
        return False

    # Reverse the dictionary to get a value-to-key mapping
    value_to_key_dict = {v: k for k, v in letters_and_files_dict.items()}

    for i in range(len(current_midi_files)):
        # Get the key corresponding to the user input (which is a value in the original dict)
        if current_user_input[i] in value_to_key_dict:
            corresponding_key = value_to_key_dict[current_user_input[i]]
        else:
            return False  # If the value doesn't exist in the dict, it's an invalid input

        # Compare the selected file with the corresponding key from user input
        if current_midi_files[i] != corresponding_key:
            return False

    return True


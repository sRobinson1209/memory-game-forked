'''
Program to Generate a Sequence of Sounds the User Needs to Mimic/Recite back
-----------------------

- generate sound sequence
    - can be random sounds
    - generated in a specific range of midi notes
    - length and speed must be able to inc
    - NO RHYTHM

- user input mimmicking sound
    - keys must correlate with sound 
    - check its in right order
    
'''
import pretty_midi
import random
import keyboard
import time

current_instrument = 'Acoustic Grand Piano' #default instrument
current_key = 'c' #default key
random_seq = [] #generated random sequence

current_speed = 1 #default speed
current_length = 3 #default sequence length

level = 0
points = 0


def generate_new_key():

    key_dictionary = {"c" : [60, 62, 64, 65, 67, 69, 71, 72], "d": [62, 64, 66, 67, 69, 71, 73, 74],
                            "e" : [64, 66, 68, 69, 71, 73, 75, 76], "f" : [65, 67, 69, 70, 72, 74, 76, 77], "g" : [55, 57, 59, 60, 62, 64, 66, 67],
                            "a" : [57, 59, 61, 62, 64, 66, 68, 69], "b" : [59, 61, 63, 64, 66, 68, 70, 71]}

    for i, key in enumerate(key_dictionary.keys()):
            if key == current_key:
                try:
                    current_key = key_dictionary[i+1]
                    current_key_scale = key_dictionary[current_key]
                except IndexError:
                    current_key = key_dictionary[0] #choose the 1st key if previous key was the last in the array
                    current_key_scale = key_dictionary[current_key]
    
    return current_key_scale


#check if a new instrument is required, if so move to the next instrument in the array
def generate_new_instrument():

    instruments = ['Acoustic Grand Piano', 'Electric Piano', 'Music Box', 'Rock Organ', 'Acoustic Guitar', 'Electric Bass', 'Violin', 'Choir Aahs']
    for i, instrument in enumerate(instruments):
            if instrument == current_instrument:
                try:
                    current_instrument = instruments[i+1]
                except IndexError:
                    current_instrument = instruments[0] #choose the 1st instrument if previous instrument was the last in the array


def calculate_parameters():
    
    global level
    global current_speed
    global current_length
    global current_instrument
    global current_key

    #every 5th level increase speed
    if level != 0 and level % 5 == 0:
        current_speed = current_speed - 0.05 #does this make it faster?????
    
    #every 10th level inc length and dec speed by a little (so game isn't impossible)
    if level != 0 and level % 10 == 0:

        if current_length != 8: #make sure notes don't go out of octive range
            current_length = current_length + 1

        current_speed = current_speed + 0.02

    #every 7th level change key
    if level != 0 and level % 7 == 0:
        current_key_scale = generate_new_key(current_key)
        
    #every 15th level change instrument
    if level != 0 and level % 15 == 0:
        current_instrument = generate_new_instrument(current_instrument)

    return current_key_scale


#creates a sequence of sounds given the range of notes and the length of the sequence
def create_sound(play_note = False, note_number = 0):

    current_key_scale = calculate_parameters() #retervies correct scale

    global current_instrument
    global current_length
    global current_speed
    global random_seq

    #create a PrettyMIDI object
    midi = pretty_midi.PrettyMIDI()
    sound_program = pretty_midi.instrument_name_to_program(current_instrument)
    instr = pretty_midi.Instrument(program=sound_program)

    #randomize the notes to create a sequence
    if current_length > len(current_key_scale): #check to make sure the length is not longer than list
        raise ValueError("The length cannot be greater than the size of the given list.")
    random_seq = random.sample(current_key_scale, current_length)

    if play_note:
        note = pretty_midi.Note(velocity = 100, pitch = note_number, start = 0, end = 1.0)
        instr.notes.append(note)

        #add the instrument to the PrettyMIDI object
        midi.instruments.append(instr)
    
        # Synthesize and play the MIDI note
        audio_data = midi.fluidsynth()
        pretty_midi.fluidsynth(audio_data)

        return None, None

    #add notes to instrument
    for i, note_num in enumerate(random_seq):
        start_time = i * current_speed
        end_time = (i + 1) * current_speed #shortens duration
        midi_note = pretty_midi.Note(velocity = 100, pitch = note_num, start = start_time, end = end_time)
        current_instrument.random_seq.append(midi_note)

    #add the instrument to the PrettyMIDI object
    midi.instruments.append(instr)

    #save the MIDI file
    midi.write('generated_melody.mid')
    MIDI_file = 'generated_melody.mid'

    return MIDI_file, random_seq


#make a method that deletes the generated file after it has been used so there isn't a ton of memory usage!!!

#plays midi file
    
'''
ORDER OF OPERATIONS:
1. start game
    - create_sound()
2. sound is played
    - play_MIDI_file()
3. play back melody
    - link keyboard keys to MIDI notes starting at A
    - take user input (maybe press enter to say done)
4. check if input is correct'''


def play_sound(MIDI_file, random_seq):
    print()
    #play the midi file

#accessor method to get the current_key_scale
def get_current_key_scale():
    global current_key
    key_dictionary = {"c" : [60, 62, 64, 65, 67, 69, 71, 72], "d": [62, 64, 66, 67, 69, 71, 73, 74],
                            "e" : [64, 66, 68, 69, 71, 73, 75, 76], "f" : [65, 67, 69, 70, 72, 74, 76, 77], "g" : [55, 57, 59, 60, 62, 64, 66, 67],
                            "a" : [57, 59, 61, 62, 64, 66, 68, 69], "b" : [59, 61, 63, 64, 66, 68, 70, 71]}
    
    current_key_scale = key_dictionary[current_key]
    return current_key_scale


def get_user_input():
    current_key_scale = get_current_key_scale()
    keyboard_letters = ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k']
    keyboard_note_dict = {}
    #create a dictionary to append values to dependent on the key
    for letter in keyboard_letters:
        for note in current_key_scale:
            keyboard_note_dict[letter] = note
            current_key_scale.remove(note)
            break
    
    print("Press keys a, s, d, f, g, h, j, k to play MIDI notes. Press 'q' to quit.")
    
    user_input = []
    while True:
        #wait for a key press
        letter_event = keyboard.read_event()
        
        if letter_event.event_type == keyboard.KEY_DOWN:
            letter = letter_event.name
            if letter in keyboard_note_dict:
                note = keyboard_note_dict[letter]

                create_sound(True, note) #<-------- modify the create sound function to handle this part
                user_input.append(note)

            elif letter == 'q':
                print("Exiting...")
                break

    return user_input
    
def check_user_input():

    global random_seq
    user_input = get_user_input()

    for i, s in enumerate(random_seq):

        if s != user_input[i]:
            return False
        
    return True


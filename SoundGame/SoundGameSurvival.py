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
import pygame

current_instrument = 'Acoustic Grand Piano' #default instrument
current_key = 'c' #default key
current_key_scale = [60, 62, 64, 65, 67, 69, 71, 72] #default scale
random_seq = [] #generated random sequence

current_speed = 1 #default speed
current_length = 3 #default sequence length

level = 0
points = 0
score = 0



#generates a new key
def generate_new_key():

    global current_key
    global current_key_scale

    key_dictionary = {"c" : [60, 62, 64, 65, 67, 69, 71, 72], "d": [62, 64, 66, 67, 69, 71, 73, 74],
                            "e" : [64, 66, 68, 69, 71, 73, 75, 76], "f" : [65, 67, 69, 70, 72, 74, 76, 77], "g" : [55, 57, 59, 60, 62, 64, 66, 67],
                            "a" : [57, 59, 61, 62, 64, 66, 68, 69], "b" : [59, 61, 63, 64, 66, 68, 70, 71]}

    for key in key_dictionary.keys():
            
            if key == current_key:
                try:
                
                    current_key_index = list(key_dictionary).index(current_key) #get the index of the current key
                    current_key = list(key_dictionary)[current_key_index+1] #replace the current_key as the next key
                    current_key_scale = key_dictionary[current_key] #replace the current_scale as the next scale
                    return
                    
                except IndexError:
                    current_key = "c" #choose the 1st key if previous key was the last in the array
                    current_key_scale = key_dictionary[current_key]
                    return


#generates a new instrument
def generate_new_instrument():

    global current_instrument

    instruments = ['Acoustic Grand Piano', 'Rock Organ', 'Music Box', 'Flute', 'Choir Aahs', 'Violin', 'Trumpet','Bassoon', 'Cello']
    for i, instrument in enumerate(instruments):
            if instrument == current_instrument:
                try:
                    current_instrument = instruments[i+1]
                    return
                except IndexError:
                    current_instrument = instruments[0] #choose the 1st instrument if previous instrument was the last in the array
                    return

#calculates the parameters based on the level the user is on
def calculate_parameters():
    
    global level
    global current_speed
    global current_length
    global current_instrument
    global current_key
    global current_key_scale

    #every 5th level increase speed
    if level != 0 and level % 5 == 0:
        current_speed = current_speed - 0.07 
    
    #every 10th level inc length and dec speed by a little (so game isn't impossible)
    if level != 0 and level % 10 == 0:

        if current_length != 8: #make sure notes don't go out of octive range
            current_length = current_length + 1

        current_speed = current_speed + 0.02

    #every 7th level change key
    if level != 0 and level % 7 == 0:
        generate_new_key()
        
        
    #every 15th level change instrument
    if level != 0 and level % 15 == 0:
        generate_new_instrument()
        
     #MAKE SURE YOU ADD TO THE SCORE!


#creates the sound the user must recite
def create_sound(play_note = False, note_number = 0):

    calculate_parameters() #retervies correct parameters

    global current_instrument
    global current_length
    global current_speed
    global random_seq
    global score
    global level

    #create a PrettyMIDI object
    midi = pretty_midi.PrettyMIDI()
    sound_program = pretty_midi.instrument_name_to_program(current_instrument)
    instr = pretty_midi.Instrument(program=sound_program)

    if play_note:
        note = pretty_midi.Note(velocity = 100, pitch = note_number, start = 0, end = 1.0)
        instr.notes.append(note)

        #add the instrument to the PrettyMIDI object
        midi.instruments.append(instr)
    
        # Synthesize and play the MIDI note
        audio_data = midi.fluidsynth()
        pretty_midi.fluidsynth(audio_data)

        return None, None
    
    #randomize the notes to create a sequence
    if current_length > len(current_key_scale): #check to make sure the length is not longer than list
        raise ValueError("The length cannot be greater than the size of the given list.")
    
    smaller_scale = current_key_scale[0:current_length]
    random_seq = random.sample(smaller_scale, current_length)

    #add notes to instrument
    for i, note_num in enumerate(random_seq):
        start_time = i * current_speed
        end_time = (i + 1) * current_speed #shortens duration
        midi_note = pretty_midi.Note(velocity = 100, pitch = note_num, start = start_time, end = end_time)
        #current_instrument.random_seq.append(midi_note)
        instr.notes.append(midi_note)

    #add the instrument to the PrettyMIDI object
    midi.instruments.append(instr)

    #save the MIDI file
    midi.write('generated_melody.mid')
    MIDI_file = 'generated_melody.mid'

    
    play_sound(MIDI_file)
    checked_input = check_user_input()
    if checked_input == False:
        print(f"Game Over! Level: {level} Score: {score}")

    if checked_input:
        level += 1
        score

    #return MIDI_file, random_seq



#plays midi file
def play_sound(MIDI_file):

    pygame.mixer.init()

    pygame.mixer.music.load(MIDI_file)

    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        time.sleep(1)


def get_user_input():
    global current_key_scale
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

#make a method that deletes the generated file after it has been used so there isn't a ton of memory usage!!!
create_sound()
'''
ORDER of OPS:
1. start game
	- create_sound
		- calculate_parameters
			- generate_new_key
			- generate_new_instrument
2. generated MIDI file is played for the user
	- play_sound
3. user recites the sound
	- get_user_input
		- get_current_key_scale
		- create_sound
4. check the user input
	- check_user_input

'''


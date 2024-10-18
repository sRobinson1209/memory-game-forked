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

current_instrument = '' #current instrument being used in the generated sequence
current_key = '' #current key being used in the generated sequence
current_speed = 1
current_length = 3
level = 0
points = 0


def generate_new_key():

    c_key = [60, 62, 64, 65, 67, 69, 71, 72]
    for i, key in keys:
            if key == current_key:
                try:
                    current_key = keys[i+1]
                except IndexError:
                    current_key = keys[0] #choose the 1st key if previous key was the last in the array

#check if a new instrument is required, if so move to the next instrument in the array
def generate_new_instrument():
    instruments = ['Acoustic Grand Piano', 'Electric Piano', 'Music Box', 'Rock Organ', 'Acoustic Guitar', 'Electric Bass', 'Violin', 'Choir Aahs']
    for i, instrument in instruments:
            if instrument == current_instrument:
                try:
                    current_instrument = instruments[i+1]
                except IndexError:
                    current_instrument = instruments[0] #choose the 1st instrument if previous instrument was the last in the array
    
    return new_inst


#calculates parameters to later generate a sequence of sound
def calculate_parametersOLD(new_instrument, new_key, sequence_length):

    global current_instrument
    global current_key
    
    if new_instrument:
        new_in = generate_new_instrument()
        

    #check if a new key is required, if so move to the next key in the array
    if new_key:
        new_k = generate_new_key()
        

    #generate a random sequence of notes depending on the sequence length
    #if sequence length is 3 then use first 3 notes
    #if sequence length is 5 use first 5 notes
    #if sequence length is 8 use all 8 notes
    if sequence_length == 3:
        notes = current_key[0:3]
    
    if sequence_length == 5:
        notes = current_key[0:5]
    
    if sequence_length == 8:
        notes = current_key[0:8]
    
    return notes, sequence_length

'''
every 5th level inc speed
every 7th level inc length dec speed by a little
every 10th level change key
every 15th level change instrument

'''
def calculate_parameters():
    
    global level
    global current_speed
    global current_length
    global current_instrument

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
        current_key = generate_new_key(current_key)
    
    #every 15th level change instrument
    if level != 0 and level % 15 == 0:
        current_instrument = generate_new_instrument(current_instrument)

    return current_speed, current_length, current_key, current_instrument #do you need to return a global variable?????





#creates a sequence of sounds given the range of notes and the length of the sequence
def create_sound(notes, sequence_length, speed):

    global current_instrument

    #create a PrettyMIDI object
    midi = pretty_midi.PrettyMIDI()
    sound_program = pretty_midi.instrument_name_to_program(current_instrument)
    instr = pretty_midi.Instrument(program=sound_program)

    #randomize the notes to create a sequence
    if sequence_length > len(notes): #check to make sure the length is not longer than list
        raise ValueError("The length cannot be greater than the size of the given list.")
    random_seq = random.sample(notes, sequence_length)

    #add notes to instrument
    for i, note_num in enumerate(random_seq):
        start_time = i * speed
        end_time = (i + 1) * speed #shortens duration
        midi_note = pretty_midi.Note(velocity = 100, pitch = note_num, start = start_time, end = end_time)
        current_instrument.random_seq.append(midi_note)

    #add the instrument to the PrettyMIDI object
    midi.instruments.append(instr)

    #save the MIDI file
    midi.write('generated_melody.mid')

    return 'generated_melody.mid'


    #maybe use the same notes???
    
    


'''
every 5th level inc speed
every 7th level inc length dec speed by a little
every 10th level change key
every 15th level change instrument

'''
                





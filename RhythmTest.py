import pygame
import time
import random

'''
Rhythm Game Notes:
------------------

Format/Setup:
- RhythmGameFunctionality.py file
    - all the general functinality that survival mode and relaxed mode calls from
- RhythemGameSurvival.py file
    - unquie files for the Survival mode to the rhythm game
- RhythemGameRelaxed.py file
    - unquie files for the Relaxed mode to the rhythm game
- Main.py file 
    - run and test without the user interface

    
Features of Rhythm Game:
- when space bar (or whatever key) is pressed have the sound play
- get rid of UI have it run from terminal
- find a variety of different WAV file beat sounds
- 

'''

# Initialize pygame and mixer for sound
pygame.init()
pygame.mixer.init()

# Load sound (replace with your own sound file paths)
beat_sounds = [
    pygame.mixer.Sound("C:\Users\ryanh\OneDrive\Desktop\Acoustic Bump_1.wav"),  # Replace with your own beat sounds
]

def main():
    try:
        rhythm_game()
    finally:
        pygame.quit()  # Ensure pygame quits even if the game errors out

# Rhythm generation function
def generate_rhythm(length):
    return [random.uniform(0.5, 1.5) for _ in range(length)]

# Function to play the rhythm
def play_rhythm(rhythm):
    for beat in rhythm:
        random.choice(beat_sounds).play()  # Play random beat sound
        time.sleep(beat)  # Wait for the duration of the beat
        pygame.mixer.stop()

# Rhythm game function
def rhythm_game():
    rhythm_length = 4  # Number of beats in the sequence
    rhythm = generate_rhythm(rhythm_length)
    
    print("Listen to the rhythm...")
    time.sleep(2)
    
    # Play the rhythm
    play_rhythm(rhythm)
    
    print("Repeat the rhythm by pressing SPACE at the right times.")
    time.sleep(1)
    
    # Capture user's timing
    user_timing = []
    start_time = time.time()
    index = 0
    
    while index < rhythm_length:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if index < rhythm_length:
                        user_timing.append(time.time() - start_time)
                        start_time = time.time()  # Reset time for next beat
                        index += 1
        
    # Compare user's rhythm with the actual rhythm
    correct_hits = 0
    for i in range(rhythm_length):
        difference = abs(user_timing[i] - rhythm[i])
        if difference < 0.3:  # Allow some leeway (0.3 seconds)
            correct_hits += 1

    # Display results
    if correct_hits == rhythm_length:
        print("Perfect!")
    else:
        print(f"{correct_hits}/{rhythm_length} correct!")
    
    time.sleep(3)  # Wait for 3 seconds before ending

# Run the rhythm game in terminal without UI
if __name__ == "__main__":
    rhythm_game()

# Quit pygame
pygame.quit()


from NumberGameSurvival import set_level_parameters_survival
from NumberGameRelaxed import set_level_parameters_relaxed

def main():
    print("")
    print("======================================")
    print("Select the Game Mode:")
    print("======================================")
    print("")
    print("Press 'r' for Relaxed Mode. Press 's' for Survival Mode. Press 'i' for more info.")
    print("-----------------------------------------------------------------------------------")
    print("")

    game_mode = input()


    survival_game_instructions = '''Survival Mode:\nPlayer is shown a sequence of numbers.\nPlayer must try to remember the numbers and enter them in the same order they were shown.\n
    If the player enters the numbers incorrectly, then the game will be over. Otherwise the player proceeds through the game.\n
    The game will go on infinitely with each sequence of numbers becoming longer and faster. As the player moves forward they are awarded points.'''

    relaxed_game_instructions = '''Relaxed Mode:\nPlayer is shown a sequence of numbers.\nPlayer must try to remember the numbers and enter them in the same order they were shown.\n
    If the player enters the numbers incorrectly, they will still have a chance to enter the numbers or skip. The game only ends if the player chooses to quit the game.\n
    The game will go on infinetly with each sequence of numbers becoming longer and faster. The player will not be rewarded any points.'''



    if game_mode == 'i' or game_mode == 'I':
        print(survival_game_instructions)
        print("")
        print("")
        print(relaxed_game_instructions)

        print("Press 'r' for Relaxed Mode. Press 's' for Survival Mode.")

        game_mode = input()

    if game_mode == 'r' or game_mode == 'R':
        r = set_level_parameters_relaxed()
        print(r)
        
    elif game_mode == 's' or game_mode == 'S':

        s = set_level_parameters_survival()
        print(s)

    else:
        print("Choose 'r', 's', or 'i'.")
    

if __name__ == "__main__":
    main()


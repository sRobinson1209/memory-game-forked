
"""
================
RELAXED MODE
================
"""
import random
import time

level_num = 0 #keep track of generate_numbers calls (aka levels)
gen_nums_length = 3 #default length player starts at


def generate_numbers(length, speed):
    """
    Generates a list of random numbers in the range 0-9 and prints them one by one with a delay.

    Args:
        length (int): The number of random numbers to generate.
        speed (float): The delay time in seconds between printing each number.

    Returns:
        list: A list of randomly generated integers between 0 and 9.
    """
    global level_num
    level_num += 1

    generated_numbers = [random.randint(0, 9) for _ in range(length)]
    
    for n in generated_numbers:
        print(n)
        time.sleep(speed)

    return generated_numbers


def number_input():
    """
    Prompts the user to input a sequence of numbers and handles special commands like quitting or skipping.

    Returns:
        list or str: 
            - If the user enters a valid number string, returns a list of integers.
            - If the user enters 'q' or 'Q', returns the string 'q' (indicating the user wants to quit).
            - If the user enters 's' or 'S', returns the string 's' (indicating the user wants to skip).

    Notes:
        - The function recursively calls itself if the user enters an invalid input (non-numeric).
    """
    print("Enter Numbers. Press 'q' to quit or 's' to skip.")
    recited_nums = input()

    if recited_nums == "q" or recited_nums == "Q" or recited_nums == "s" or recited_nums == "S": #check if user wants to quit or skip
        return recited_nums
    try:
        recited_nums = [int(r) for r in recited_nums] #checks for letters or non numbers
    except ValueError:
        print("Only enter numbers with no spaces. EX: 452")
        return number_input()

    return recited_nums



def check_input(generated_nums, recited_nums):
    """
    Compares a list of generated numbers to the user-inputted numbers to check for a match.

    Args:
        generated_nums (list): The list of numbers generated by the game.
        recited_nums (list): The list of numbers entered by the user.

    Returns:
        bool: 
            - Returns True if both lists are of the same length and all elements match in the same order.
            - Returns False if the lengths differ or if any number in the sequence doesn't match.
    """

    if len(generated_nums) !=len(recited_nums):
        return False
    
    for i in range(len(generated_nums)):
        if generated_nums[i] != recited_nums[i]:
            return False
        
    return True  


def set_level_parameters_relaxed():
    """
    Sets the parameters for the number generation and input handling based on the player's current level in relaxed mode.

    This function generates a sequence of random numbers for the player to recite back. 
    The player has multiple chances to get the input correct, with options to quit or skip. 
    After every 7 levels, the length of the generated number sequence increases.

    Global Variables:
        - level_num (int): Tracks the current level of the player and increments after each successful level.
        - gen_nums_length (int): The length of the number sequence to be generated, which increases every 7 levels.

    Returns:
        str or None: 
            - If the player quits, returns a message indicating the game has been quit.
            - If the input is correct, moves to the next level.

    Behavior:
        - Generates a sequence of random numbers based on the current level and fixed speed.
        - Prompts the user to recite the numbers.
        - If the input is incorrect, allows the player to retry until they get it right or choose to quit.
        - If the player enters "q" or "Q", the game is quit.
        - If the player enters "s" or "S", the current number sequence is skipped and a new one is generated.
    """
    global level_num
    global gen_nums_length

    gen_nums_speed = 1 #speed doesn't change since player is in relaxed mode

    if level_num % 7 == 0 and level_num != 0: #after every 7 levels inc length
        gen_nums_length += 1
        
    gen_num = generate_numbers(gen_nums_length, gen_nums_speed)
    recited_nums = number_input()

    if recited_nums == "q" or recited_nums == "Q": #quit game
        return f"You quit the game!"
    
    if recited_nums == "s" or recited_nums == "S": #skip question
        print("Skipping number sequence...")
        set_level_parameters_relaxed()

    checked_input = check_input(gen_num, recited_nums)

    #instead of ending the game the player gets multiple chances to enter correct input
    while checked_input is False:
        print("Incorrect input!\nPlease try again!") 

        recited_nums = number_input()
        if recited_nums == "q" or recited_nums == "Q": #quit game
            return f"You quit the game!"
        
        if recited_nums == "s" or recited_nums == "S": #skip question
            print("Skipping number sequence...")
            recited_nums = gen_num

        checked_input = check_input(gen_num, recited_nums)
    
    if checked_input: #move onto next level if input is correct(True)
        return set_level_parameters_relaxed()
    
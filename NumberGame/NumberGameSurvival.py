
import random
import time


level_num = 0 #keep track of generate_numbers calls (aka levels)
score = -1 #keeps track of points the player has after the game

#generates random number list (range 0-9)
def generate_numbers(length, speed):
    global level_num
    level_num += 1

    generated_numbers = [random.randint(0, 9) for _ in range(length)]
    
    for n in generated_numbers:
        print(n)
        time.sleep(speed)

    return generated_numbers

#takes in user input (recited number string)
def number_input():

    print("Enter Numbers. Press 'q' to quit.")
    recited_nums = input()

    if recited_nums == "q" or recited_nums == "Q": #check if user wants to quit 
        return recited_nums
    try:
        recited_nums = [int(r) for r in recited_nums] #CHECK FOR LETTERS OR NOT NUMBERS!
    except ValueError:
        print("Only enter numbers with no spaces. EX: 452")
        return number_input()

    return recited_nums


#checks the input (recited number string) from the user
def check_input(generated_nums, recited_nums):

    if len(generated_nums) !=len(recited_nums):
        return False
    
    for i in range(len(generated_nums)):
        if generated_nums[i] != recited_nums[i]:
            return False
        
    return True  


#determines the parameters for generate_numbers & speed function determined by "level" user is on
def set_level_parameters_survival():

    global score
    global level_num

    if level_num >= 0 and level_num <= 2:
        gen_nums_length = 3
        gen_nums_speed = 1 
        score += 1

    elif level_num > 2 and level_num <= 4:
        gen_nums_length = 5
        gen_nums_speed = .5 
        score += 2
    
    elif level_num > 4:
        gen_nums_length = 7
        gen_nums_speed = .3 
        score += 3
    
    gen_num = generate_numbers(gen_nums_length, gen_nums_speed)

    recited_nums = number_input()
    if recited_nums == "q" or recited_nums == "Q":
        return f"You quit the game!\nScore: {score} points"

    checked_input = check_input(gen_num, recited_nums)
    
    if checked_input:
        return set_level_parameters_survival()
    
    else: 
        return f"Game Over!\nScore: {score} points" #this is for survival mode





# def set_lev_mod():

#     global score
#     global level_num


        
#     gen_nums_speed = 1 
        

#     if level_num % 10 == 0 and level_num != 0: #after every 10 levels inc speed 
#         gen_nums_speed = gen_nums_speed - 0.05

#         if 



#     for i in range(50):

#         an = i % 10

        
#         print(f"10 % {i} = {an}")

# set_lev_mod()
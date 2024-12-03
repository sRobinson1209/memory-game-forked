# Memory Master

**Memory Master** is a web-based platform featuring a collection of minigames designed to challenge and improve your memory. Each game focuses on different memory skills, such as recalling sequences of numbers, rhythms, or sounds. The goal is to engage players in exercises that stimulate cognitive development and improve critical thinking abilities.

## Features

- **Variety of Minigames**: Choose from multiple memory games that test your ability to recall sequences across different senses—visual, auditory, and sensory.
- **User Accounts**: Players can create accounts using their email and password to track their progress as they advance through new levels in each game.
- **Cognitive Benefits**: Regularly playing these memory games can help improve problem-solving skills, pattern recognition, and overall cognitive development.
- **Game Modes**: Players can challenge themselves with number sequences, rhythm sequences, or sound sequences, offering a diverse range of memory exercises.
- **Progress Tracking**: As users progress in each game, their achievements and level advancements are stored in their accounts, helping them monitor improvement over time.

## Why Play?

Strengthening your memory through these games can have numerous benefits:
- **Improved Critical Thinking**: Exercising your brain in memory challenges helps with problem solving and decision-making.
- **Better Academic and Work Performance**: By enhancing cognitive function and pattern recognition, you'll be better equipped to tackle complex tasks in school or at work.
- **Balanced Memory Training**: Memory Master provides challenges that engage your memory visually, audibly, and sensorially, promoting a well-rounded mental workout.

## How It Works

1. **Choose a Minigame**: Select a memory game from the menu that interests you—whether it's about remembering number sequences, recalling rhythm patterns, or identifying sounds.
2. **Play and Recite**: Watch or listen carefully as the game provides a sequence. Then, try to replicate it from memory!
3. **Track Your Progress**: If you're signed in, your performance is saved, and you can continue to improve your scores and move up through the levels.

## Technologies Used

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Flask, Flask-SocketIO, Python
- **Database**: Postgre SQL
- **Other Libraries**: Pygame for sound playback in games

## File Groups 
- Main Game Site - will all implementation
    - main.app
    - Static Folder
    - Templates Folder
    - globals.py

- Sound Game
    - SoundGameRelaxed.py + app_SG_relaxed.py
    - SoundGameSurvival.py + app.py
- Number Game
    - NumberGamedRelaxed.py
    - NumberGageSurvival.py
- Rhythm game
    - Rhythm Final Folder
 ## To Run The Site 
 - Make sure you have the project folder downloaded and navigate to where the folder is. In the terminal, I first ran “     set FLASK_APP=main.py” so it knows what file to read from. Then run line: flask run  , and it should give you a         local host, and allow you to see all the site has to offer. 

 



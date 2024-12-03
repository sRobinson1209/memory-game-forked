# **Memory Master**

**Memory Master** is a web-based platform that offers a variety of memory-focused minigames designed to challenge and improve cognitive skills. Each game targets specific memory abilities, such as recalling number sequences, rhythms, or sounds. The platform aims to provide an engaging and fun way to enhance critical thinking and cognitive development.

---

## **Features**

- **Diverse Minigames**: Engage in different memory challenges, including visual, auditory, and rhythm-based exercises.
- **User Accounts**: Create accounts to track your progress and achievements as you advance through levels.
- **Cognitive Benefits**: Enhance problem-solving skills, pattern recognition, and overall mental acuity through consistent practice.
- **Game Modes**: Choose between relaxed or survival modes in various games:
  - Number sequences
  - Rhythm patterns
  - Sound sequences
- **Progress Tracking**: Track your performance and improvements over time, with achievements stored in your account.

---

## **Why Play?**

**Memory Master** helps you strengthen your memory while enjoying fun and challenging games. Benefits include:

- **Improved Critical Thinking**: Regular brain exercises improve problem-solving and decision-making.
- **Enhanced Academic and Professional Performance**: Boost cognitive function and pattern recognition for better performance in work or school.
- **Comprehensive Memory Training**: Train your brain through visual, auditory, and rhythm-based challenges, ensuring a balanced mental workout.

---

## **How It Works**

1. **Choose a Game**: Select a game from the menu, whether it's recalling numbers, rhythms, or sounds.
2. **Challenge Yourself**: Watch, listen, or interact as the game presents a sequence, then replicate it from memory.
3. **Track Your Progress**: If logged in, your progress is saved, allowing you to level up and monitor improvements.

---

## **Technologies Used**

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Flask, Flask-SocketIO, Python
- **Database**: PostgreSQL
- **Additional Libraries**: Pygame for sound-based games

---

## **File Structure**

### **Main Game Site**
Contains the primary implementation of the platform:
- `main.py`: The core application file
- `static/`: Contains static assets like JavaScript, CSS, and images
- `templates/`: HTML templates for the frontend
- `globals.py`: Shared variables and configurations

### **Sound Game**
- **Relaxed Mode**: `SoundGameRelaxed.py`, `app_SG_relaxed.py`
- **Survival Mode**: `SoundGameSurvival.py`, `app.py`

### **Number Game**
- **Relaxed Mode**: `NumberGameRelaxed.py`
- **Survival Mode**: `NumberGameSurvival.py`

### **Rhythm Game**
- Folder: `Rhythm Final Folder` (contains rhythm-based game files)

---

## **How to Run**

Follow these steps to set up and run the application:

1. **Clone the Repository**:
   -git clone <repository_url>
   -cd <repository_folder>
2. Make sure python is installed 3.11 no newer version 
3. To isolate project dependencies:
      - Create a virtual environment:
          - python -m venv venv
4. Activate the virtual environment
5. Install the dependencies 
    -Pip install -r requirements.txt
6. The .env file should have the necessary variables
     - Make sure python-dotnev is installed
7. Then set FLASK_APP=main.py and it should run


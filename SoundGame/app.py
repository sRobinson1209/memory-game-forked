'''
app.py handles setting up the Flask Backend

Flask is used to serve the game logic & handle communication between Python backend & thre frontend (js file)

Here there are API routes to handle the game logic (generating a melody and recieving the user's input)

Basically Separting backedn logic from frontent logic 
- front end interacts with UI
- back end is the python file that has the game in it
'''

from flask import Flask, send_file, jsonify
from flask_cors import CORS
import os
from SoundGameSurvival import current_length, generate_melody #, delete_melody_file


letters = ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k']

app = Flask(__name__)
CORS(app)
#CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins, make sure this is secure for production.



@app.route('/')
def melody_memory():
    
    return send_file('index.html')

@app.route('/start_melody', methods = ['POST'])
def start_melody():
    #delete_melody_file()
    generate_melody() #call generate_melody function from soundgame
    return jsonify({'message': 'Melody generated!'})

@app.route('/get_current_length', methods = ['GET'])
def get_current_length():
    global current_length
    return jsonify({'current_length': current_length})

# Endpoint to get keyboard letters
@app.route('/get_letters')
def get_letters():
    global letters
    
    return jsonify({'letters': letters})


#run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
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

current_length = 3
current_key_scale = [60, 62, 64, 65, 67, 69, 71, 72]  

app = Flask(__name__)
CORS(app)

@app.route('/')
def melody_memory():
    return send_file('index.html')

@app.route('/get_current_length')
def get_current_length():
    global current_length
    return jsonify({'current_length': current_length})

# Endpoint to get current key scale
@app.route('/get_current_key_scale')
def get_current_key_scale():
    global current_key_scale
    return jsonify({'current_key_scale': current_key_scale})


#run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
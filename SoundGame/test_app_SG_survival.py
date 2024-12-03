'''
==============================
SOUND GAME SURVIVAL MODE TESTS
==============================
'''


import unittest
from app import app, socketio
from SoundGameSurvival import check_user_input, get_midi_files, get_user_input
from flask_socketio import SocketIOTestClient

class SoundGameTestCase(unittest.TestCase):

    #set up test client & test SocketIO client
    def setUp(self):
        
        self.app = app.test_client()
        self.app.testing = True
        self.socketio_test_client = socketio.test_client(app)


    #disconnect socket client after tests
    def tearDown(self):
        self.socketio_test_client.disconnect()

    #test starting melody playback
    def test_start_melody(self):

        response = self.app.post('/start_melody')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'Melody started!')

    #test get letters route
    def test_get_letters(self):

        response = self.app.get('/get_letters')

        self.assertEqual(response.status_code, 200)
        self.assertIn('letters', response.json)
        self.assertEqual(response.json['letters'], ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k'])

    #test receiving user input that's correct in survival mode
    def test_receive_user_input_correct(self):

    
        get_midi_files(['MID_FILES/c_note_one_sec.mid', 'MID_FILES/d_note_one_sec.mid'])

        response = self.app.post('/user_input', json={'userInput': ['a', 's']})

        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json)


    #test receiving user input that's incorrect in suvival mode
    def test_receive_user_input_incorrect(self):
        
        get_midi_files(['MID_FILES/c_note_one_sec.mid', 'MID_FILES/d_note_one_sec.mid'])

        response = self.app.post('/user_input', json={'userInput': ['a', 'd']})

        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json)

    #test game quitting 
    def test_quit_game(self):
        
        self.socketio_test_client.emit('quit_game')
        self.assertTrue(self.socketio_test_client.is_connected())



    #test playing MIDI files
    def test_play_midi(self):
        midi_file = 'MID_FILES/c_note_one_sec.mid'
        self.socketio_test_client.emit('play_midi', {'midiFile': midi_file})
        
        self.assertTrue(self.socketio_test_client.is_connected()) #check socket client remains connected

    #tests game logic from SoundGameSurvival.py file
    def test_check_user_input_correct(self):
        
        #when user input is correct
        get_midi_files(['MID_FILES/c_note_one_sec.mid', 'MID_FILES/d_note_one_sec.mid'])
        get_user_input(['a', 's'])  

        self.assertTrue(check_user_input())  #should return True



    def test_check_user_input_incorrect(self):
        
        #when user input is incorrect
        get_midi_files(['MID_FILES/c_note_one_sec.mid', 'MID_FILES/d_note_one_sec.mid'])
        get_user_input(['a', 'd'])  
        self.assertFalse(check_user_input())  #should return False


if __name__ == '__main__':
    unittest.main()

'''
==============================
SOUND GAME RELAXED MODE TESTS
==============================
'''

import unittest
from app_SG_relaxed import app, socketio
from SoundGameRelaxed import check_user_input, get_midi_files, get_user_input, send_current_midi_files_back
from flask_socketio import SocketIOTestClient

class SoundGameRelaxedTestCase(unittest.TestCase):

    #setup test client & test SocketIO client
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

    #test the get letters route
    def test_get_letters(self):

        response = self.app.get('/get_letters')

        self.assertEqual(response.status_code, 200)
        self.assertIn('letters', response.json)

        self.assertEqual(response.json['letters'], ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k'])

    #test receiving correct user input
    def test_receive_user_input_correct(self):

        get_midi_files(['MID_FILES/c_note_one_sec.mid', 'MID_FILES/d_note_one_sec.mid'])

        response = self.app.post('/user_input', json={'userInput': ['a', 's']})
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json)

    #test receiving incorrect user input
    def test_receive_user_input_incorrect(self):

        get_midi_files(['MID_FILES/c_note_one_sec.mid', 'MID_FILES/d_note_one_sec.mid'])

        response = self.app.post('/user_input', json={'userInput': ['a', 'd']})
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json)

    #test quitting the game
    def test_quit_game(self):
        self.socketio_test_client.emit('quit_game')
        self.assertTrue(self.socketio_test_client.is_connected())



    #test playing the MIDI files
    def test_play_midi(self):
        midi_file = 'MID_FILES/c_note_one_sec.mid'
        self.socketio_test_client.emit('play_midi', {'midiFile': midi_file})
        self.assertTrue(self.socketio_test_client.is_connected())  #check that socket client remains connected


    #test checking correct user input in relaxed mode
    def test_check_user_input_correct(self):

        get_midi_files(['MID_FILES/c_note_one_sec.mid', 'MID_FILES/d_note_one_sec.mid'])
        get_user_input(['a', 's'])

        self.assertTrue(check_user_input())  #should return True


    #test checking incorrect user input in relaxed mode
    def test_check_user_input_incorrect(self):
        get_midi_files(['MID_FILES/c_note_one_sec.mid', 'MID_FILES/d_note_one_sec.mid'])
        get_user_input(['a', 'd'])

        self.assertFalse(check_user_input())  #should return False


    #test retrying the melody after incorrect input
    def test_try_melody_again(self):
        get_midi_files(['MID_FILES/c_note_one_sec.mid', 'MID_FILES/d_note_one_sec.mid'])
        
        response = self.app.post('/try_melody_again')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'Previous melody started!')



    #test passing a level in relaxed mode
    def test_pass_level(self):
        response = self.app.post('/pass_level')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'Moved to the next round!')

if __name__ == '__main__':
    unittest.main()
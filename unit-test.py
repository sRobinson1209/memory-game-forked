import unittest 
from main import app, execute_query

class TestRegister(unittest.TestCase):
    def setUp(self):
        #setting up test client
        self.app = app.test_client()
        self.app.testing = True

        execute_query("DELETE FROM accounts WHERE username = %s", ("testUser",))

    #making a fake user 
    def test_registration(self):
        response = self.app.post('/pythonlogin/register', data={
            'username': 'testUser',
            'password': 'testPass',
            'email': 'testUser@example.com'
        }, follow_redirects=True)

        print(response.data.decode('utf-8'))  
        self.assertEqual(response.status_code,200)
        self.assertIn(b'You have successfully registered!', response.data)

        #verifiying that the user was made and saved in the database
        account = execute_query("SELECT * FROM accounts WHERE username= %s",("testUser",),fetch=True)
        self.assertIsNotNone(account)
        self.assertEqual(account[1], 'testUser')
        self.assertEqual(account[2],'testPass')
        self.assertEqual(account[3], 'testUser@example.com')

    # This make sure the backend for the rhytym game generates a rhythm properly.
    def test_generate_rhythm(self):
        
        test_length = 10
        response = self.app.get(f'/generate_rhythm?length={test_length}')
        # Makes sure the endpoint works properly, online resources said this was best practice!
        self.assertEqual(response.status_code, 200)

        # Get the data
        data = response.get_json()
        self.assertIn('rhythm', data)
        rhythm = data['rhythm']

        # Makes sure it's the right length and in the right range.
        self.assertEqual(len(rhythm), test_length)

        for beat in rhythm:
            self.assertGreaterEqual(beat, 0.5)
            self.assertLessEqual(beat, 1.5)


if __name__ == '__main__':
    unittest.main()
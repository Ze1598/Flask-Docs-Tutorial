#Built-in modules
import os, unittest, tempfile
#The application module
import flaskr.flaskr

class FlaskrTestCase(unittest.TestCase):
    '''Inherits from the unittest.TestCase class.
    Creates a base class for the test with custom methods.'''

    def setUp(self):
        '''Create a new test client and set up the database 
        connection for the test.
        Called before each individual test function is run.'''
        #mkstemp() returns a tuple (low-level file handle, random file name)
        #The random name is used as the database name
        self.db_fd, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
        flaskr.app.testing = True
        self.app = flaskr.app.test_client()
        with flaskr.app.app_context():
            flaskr.flaskr.init_db()

    def tearDown(self):
        '''Tear down the database connection by closing the file and
        deleting it from the filesystem.'''
        os.close(self.db_fd)
        os.unlink(flaskr.app.config['DATABASE'])

    def test_empty_db(self):
        '''Access the root of the application and test if it contains a
        given string denoting it's empty.'''
        #Send an HTTP GET request to the application with the given path
        #Returns a 'response_class' object
        rv = self.app.get('/')
        #Then use the 'data' attribute to inspect the return value
        #Use the 'assert' keyword to guarantee the root of the\
        #application contains the string tested
        assert b'No entries here so far' in rv.data

    def login(self, username, password):
        '''Requests to the login page with the required form data
        (username and password).
        Follows the login page's redirects.'''
        return self.app.post('/login', 
        data = dict(username = username, password = password), 
        follow_redirects = True)
    
    def logout(self):
        '''Requests to the logout page. Follows the page's redirects'''
        return self.app.get('/logout', follow_redirects = True)
    
    def test_login_logout(self):
        '''Function responsible for the log in and log out tests.'''
        rv = self.login('admin', 'default')
        assert b'You were logged in' in rv.data
        rv = self.logout()
        assert b'You were logged out' in rv.data
        rv = self.login('adminx', 'default')
        assert b'Invalid username' in rv.data
        rv = self.login('admin', 'defaultx')
        assert b'Invalid password' in rv.data

    def test_messages(self):
        '''Check that HTML is allowed in the text but not in the title (i.e. the
        intended behavior).'''
        self.login('admin', 'default')
        rv = self.app.post('/add', 
        data = dict(title = '<Hello>', text = '<strong>HTML</strong> allowed here'),
        follow_redirects = True)
        assert b'No entries here so far' not in rv.data
        assert b'&lt;Hello&gt;' in rv.data
        assert b'<strong>HTML</strong> allowed here' in rv.data

if __name__ == '__main__':
    unittest.main()
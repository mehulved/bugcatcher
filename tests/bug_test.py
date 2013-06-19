import os
import tempfile
import unittest
import sys
import simplejson as json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import bug

class BugTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, bug.app.config['SQLALCHEMY_DATABASE_URI'] = tempfile.mkstemp()
        bug.app.config['TESTING'] = True
        self.app = bug.app.test_client()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(bug.app.config['SQLALCHEMY_DATABASE_URI'])

    def capture(self, description, action, happened, expected, security, email,
            browser, url, screen, console_log, image):
        return self.app.post('/capture')

    def test_get_capture(self):
        rv = self.app.get('/capture')
        assert "Method Not Allowed" in rv.data

    def test_empty_post(self):
        rv = self.app.post('/capture')
        bug.app.logger.info(rv.data)
        assert "Empty Response" in rv.data

    def test_post_data(self):
        return True

if __name__ == '__main__':
    unittest.main()


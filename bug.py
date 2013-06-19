from flask import Flask
from flask import request
import simplejson as json
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime

"""
Create a flask app, setup SQLAlchemy
"""
app = Flask(__name__)
app.config.from_pyfile('bugs.cfg')
db = SQLAlchemy(app)

"""
Bugs Class:
    Contains the model of bugs database table.
"""
class Bug(db.Model):
    __tablename__ = 'bugs'
    bug_id = db.Column('id', db.Integer, primary_key=True)
    description = db.Column(db.String(255))
    action = db.Column(db.Text)
    happened = db.Column(db.Text)
    expected = db.Column(db.Text)
    security = db.Column(db.Boolean)
    email = db.Column(db.String(50))
    browser = db.Column(db.String(150))
    url = db.Column(db.String(100))
    screen = db.Column(db.String(255))
    console_log = db.Column('console', db.Text)
    image = db.Column(db.LargeBinary)
    time = db.Column(db.DateTime)

    def __init__(self, description, action, happened, expected,
            security, email, browser, url, screen, console_log, image):
        self.description = description
        self.action = action
        self.happened = happened
        self.expected = expected
        self.security = security
        self.email = email
        self.browser = browser
        self.url = url
        self.screen = screen
        self.console_log = console_log
        self.image = image
        self.time = datetime.utcnow()

"""
Get the POST data sent by the Chrome extension and store it in
variables.  The POST data is received in JSON format so we need to use
simplejson to convert it into a dictionary.
Then pass the dictionary to SQLAlchemy Model to store it in the
database.
"""
@app.route('/capture', methods=["POST"])
def capture():
    if request.method == "POST":
        # Get JSON data and deserialize it to a dictionary
        data = json.loads(request.data)

        # Now let's start populating the received data
        description = data['entry']['label']
        action = data['entry']['whatdone']
        happened = data['entry']['whathad']
        expected = data['entry']['whatshould']
        security = bool(data['entry']['security'])
        email = data['entry']['usermail']
        browser = data['entry']['browser']
        url = data['entry']['url']
        screen = data['entry']['screen']
        console_log = data['entry']['console']
        image = data['entry']['screenshot']

        # Assign the data to Bug model
        bug = Bug(description, action, happened, expected,
                security, email, browser, url, screen, console_log,
                image)
        db.session.add(bug)

        # Write to database
        try:
            db.session.commit()
            response = True
        except Exception, e:
            print e
            response = False
        return json.dumps({'ok': response})

"""
Flask Main
"""
if __name__ == "__main__":
    app.run()

from flask import Flask, request, current_app
import simplejson as json
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime
import base64

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
        input = result = {}

        # Get JSON data and deserialize it to a dictionary
        data = json.loads(request.data)

        # Now let's start populating the received data
        input['description'] = data['entry']['label']
        input['action'] = data['entry']['whatdone']
        input['happened'] = data['entry']['whathad']
        input['expected'] = data['entry']['whatshould']
        input['security'] = bool(data['entry']['security'])
        input['email'] = data['entry']['usermail']
        input['browser'] = data['entry']['browser']
        input['url'] = data['entry']['url']
        input['screen'] = data['entry']['screen']
        input['console_log'] = data['entry']['console']
        input['image'] = data['entry']['screenshot']
        if current_app.config.get('USEDB'):
            response = store_to_db(input)
            result['db'] = response
        if current_app.config.get('BUGTRACKER'):
            response = send_to_bugtracker(current_app.config.get('BUGTRACKER'), input)
            result['bugtracker'] = response
        return json.dumps(result)

def store_to_db(data):
    # Assign the data to Bug model
    bug = Bug(data['description'], data['action'], data['happened'],
            data['expected'], data['security'], data['email'], data['browser'],
            data['url'], data['screen'], data['console_log'],
            data['image'])
    db.session.add(bug)

    # Write to database
    try:
        db.session.commit()
        response = True
    except Exception, e:
        print e
        response = False
    return response

def send_to_bugtracker(tracker, data):
    if tracker['service'] == 'PivotalTracker':
        from pyvotal import PTracker
        ptracker = PTracker(user=tracker['username'],
                password=tracker['password'])
        project = ptracker.projects.get(tracker['project_id'])
        app.logger.info(project.name)
        if project.name:
            story = ptracker.Story()
            story.story_type = "bug"
            story.name = data['description']
            story.description = "What was done: " + data['action'] + "\n"
            story.description += "What was expected: " + data['expected'] + "\n"
            story.description += "what happened: " + data['happened'] + "\n"
            if data['email']:
                story.description += "User Email: " + data['email'] + "\n"
            story.description += "Browser: " + data['browser'] + "\n"
            story.description += "URL: " + data['url'] + "\n"
            if data['security']:
                story.description += "Security Issue"
            story.description += "Screen: " + data['screen'] + "\n"
            if data['console_log']:
                story.description += "Console Log: " + data['console_log'] + "\n"
            # Image has been commented out till we can figure where to store
            # it.
            # story.description += "Image: " + data['image'] + "\n"
            bug_story = project.stories.add(story)
            if bug_story.id:
                story = project.stories.get(bug_story.id)
                story.add_attachment('screenshot.jpeg',
                        base64.b64decode(data['image']))
                return bug_story.id
        return False

"""
Flask Main
"""
if __name__ == "__main__":
    app.run()

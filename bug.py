from flask import Flask
from flask import request
import simplejson as json

app = Flask(__name__)

# Capture the bug data sent by the tool
@app.route('/capture', methods=["POST"])
def capture():
    error = None
    if request.method == "POST":
        data = json.loads(request.data)
        title = data['entry']['label']
        action = data['entry']['whatdone']
        happened = data['entry']['whathad']
        expected = data['entry']['whatshould']
        security = data['entry']['security']
        email = data['entry']['email']
        browser = data['entry']['browser']
        url = data['entry']['url']
        screensize = data['entry']['screen']
        scrollX = data['entry']['scrollX']
        scrollY = data['entry']['scrollY']
        console_log = data['entry']['console']
        image = data['entry']['screenshot']
    return render_template('success.html', error=error)

if __name__ == "__main__":
    app.run(debug=True)

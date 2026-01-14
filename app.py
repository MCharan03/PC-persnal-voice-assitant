from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html') # Use existing templates

# Socket events can be added here
# e.g., to receive updates from run_jarvis.py
# For now, it's a passive display as requested.

if __name__ == '__main__':
    socketio.run(app)

# Import necessary libraries
from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_cors import CORS, cross_origin
from refresh.website_n_xml_utils import start_my_function
import time

# Create Flask app and SocketIO instance
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Enable CORS for all routes
CORS(app)

# Define route for the main page
@app.route('/')
def index():
    return render_template('index.html')

# Define the function to be triggered when the button is clicked
@socketio.on('trigger_function')
def handle_trigger():
    def callback(output):
        socketio.emit('update_response', output)
    
    start_my_function(callback)


if __name__ == '__main__':
    # Run the app with Socket.IO support
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, ssl_context='adhoc')

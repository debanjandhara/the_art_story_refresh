# Import necessary libraries
from flask import Flask, render_template, request
from flask_socketio import SocketIO
from flask_cors import CORS, cross_origin
from refresh.website_n_xml_utils import start_my_function
from werkzeug.utils import secure_filename
import time

import os

# # Define the file path
# file_path = "database.csv"

# # Check if the file already exists
# if os.path.exists(file_path):
#     # If it exists, delete the file
#     os.remove(file_path)

# # Create a new file and write the header
# with open(file_path, 'w') as file:
#     file.write("Type,ID,last_checked,last_modified,last_vectorised,name\n")

# print("File created successfully:", file_path)

# import shutil

# # Specify the path of the folder to be deleted
# folder_path = "data"

# # Delete the folder and its contents
# if os.path.exists(folder_path):
#     shutil.rmtree(folder_path)

# print("Folder deleted successfully:", folder_path)


# Create Flask app and SocketIO instance
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
# socketio = SocketIO(app, cors_allowed_origins="*", path='/dd-refresh/socket.io')

# Enable CORS for all routes
CORS(app)
# CORS(app, resources={r"/dd-refresh/socket.io/*": {"origins": "*"}})

# Define route for the main page
@app.route('/')
def index():
    return render_template('index.html')

# --------------------- Make /upload_FAQ -----------
@app.route('/uploadFAQ', methods=['GET', 'POST'])
def upload_faq():
    if request.method == 'POST':
        # Create data folder if it does not exist
        if not os.path.exists('data'):
            os.makedirs('data')

        # Create faq folder if it does not exist
        if not os.path.exists('data/faq'):
            os.makedirs('data/faq')

        # Check if the faq file already exists
        if os.path.exists('data/faq/faq.txt'):
            os.remove('data/faq/faq.txt')
        
        
        # Get the file from the form
        file = request.files['file']

        # Save the file to data/faq folder with the name 'faq.txt'
        file.save(os.path.join('data/faq', 'faq.txt'))

        return 'File uploaded successfully', 200

    return render_template('uploadFAQ.html') 
# ---------------------------------------------------

# Define the function to be triggered when the button is clicked
@socketio.on('trigger_function')
def handle_trigger():
    def callback(output):
        socketio.emit('update_response', output)
    
    start_my_function(callback)


if __name__ == '__main__':
    # Run the app with Socket.IO support
    # socketio.run(app, debug=True, host='0.0.0.0', port=5000, ssl_context='adhoc', allow_unsafe_werkzeug=True)
    socketio.run(app, host='0.0.0.0', port=5000, ssl_context=('cert.pem', 'key.pem'), allow_unsafe_werkzeug=True)

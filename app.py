# Import necessary libraries
from flask import Flask, render_template, request, send_file, redirect, url_for
from flask_socketio import SocketIO
from flask_cors import CORS
import logging
import sys
import os
from datetime import datetime
from refresh.website_n_xml_utils import start_my_function
from werkzeug.utils import secure_filename

import time

import os

# --------------- CODE FOR HANDLING FRESH DATA GENERATION ------------------

# # Define the file path
# file_path = "database.csv"

# # Check if the file already exists
# if os.path.exists(file_path):
#     # If it exists, delete the file
#     os.remove(file_path)

# # # Create a new file and write the header
# # with open(file_path, 'w') as file:
# #     file.write("Type,ID,last_checked,last_modified,last_vectorised,name\n")

# print("File created successfully:", file_path)

# # -----> For Deleting : Data Folder

# import shutil

# # Specify the path of the folder to be deleted
# folder_path = "data"

# # Delete the folder and its contents
# if os.path.exists(folder_path):
#     shutil.rmtree(folder_path)

# print("Folder deleted successfully:", folder_path)

# ----------------------------------------------------------------------------------


# -------------------------- Log File Mgmt -------------------------------
log_file_path = "data/log.txt"

if not os.path.exists("data"):
    os.makedirs("data")

if not os.path.exists("data/log.txt"):
        with open("data/log.txt", "w") as log_file:
            log_file.write("")

logging.basicConfig(
    level=logging.INFO,
    format='\n%(asctime)s\n - %(levelname)s - %(message)s\n',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Handlers for logging to file and console
file_handler = logging.FileHandler(log_file_path)
console_handler = logging.StreamHandler()

# Adding handlers to the logger
logging.getLogger().addHandler(file_handler)
logging.getLogger().addHandler(console_handler)

# Custom class to redirect stdout and stderr to a logger
class LoggerWriter:
    def __init__(self, level):
        self.level = level

    def write(self, message):
        if message.strip():
            # This will add a log entry with newlines before and after the timestamp
            logging.log(self.level, f"{message.strip()}")

    def flush(self):
        pass  # Required for compatibility with sys.stdout and sys.stderr

sys.stdout = LoggerWriter(logging.INFO)  # Redirect print statements
sys.stderr = LoggerWriter(logging.ERROR)  # Redirect error messages

# Custom uncaught exception handler to log exceptions with newlines and timestamps
def custom_exception_handler(exctype, value, traceback):
    logging.error("Uncaught exception occurred", exc_info=(exctype, value, traceback))

# Set the custom exception handler
sys.excepthook = custom_exception_handler

print("Logging setup complete.")


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

# View the log file
@app.route('/view-log', methods=['GET'])
def view_log():
    if os.path.exists(log_file_path):
        # Return the log file to the client for viewing
        return send_file(log_file_path, as_attachment=False, download_name='log.txt')
    else:
        return "Log file does not exist.", 404

# Clean the logs
@app.route('/clean-log', methods=['GET', 'POST'])
def clean_log():
    log_file_path = 'data/log.txt'
    if os.path.exists(log_file_path):
        # Clear the contents of the log file
        with open(log_file_path, 'w') as log_file:
            log_file.write('')  # Writing an empty string to the file

        return "Log file has been cleaned.", 200
    else:
        return "Log file does not exist.", 404

# Upload FAQ
@app.route('/uploadFAQ', methods=['GET', 'POST'])
def upload_faq():
    if request.method == 'POST':
        # Create the necessary directories
        if not os.path.exists('data/faq'):
            os.makedirs('data/faq')
        
        # Remove existing file if it exists
        faq_path = 'data/faq/faq.txt'
        if os.path.exists(faq_path):
            os.remove(faq_path)

        # Save the uploaded file
        file = request.files['file']
        file.save(faq_path)

        # Redirect to the same page with a success flag
        return redirect(url_for('upload_faq') + '?uploadSuccess=true')
    
    return render_template('uploadFAQ.html')


# Define the function to be triggered when the button is clicked
@socketio.on('trigger_function')
def handle_trigger():
    def callback(output):
        # Log the callback output with a timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} - {output}"
        logging.info(log_entry)
        
        # Emit the response back to clients
        socketio.emit('update_response', output)

    # Attempt to start the function and check if it was successful
    if not start_my_function(callback):
        # If the function was not started because it was already running, notify the client
        socketio.emit('update_response', 'Function is already running.')


if __name__ == '__main__':
    # --> 👇 For Dev Mode Testing
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, ssl_context='adhoc', allow_unsafe_werkzeug=True)
    # --> 👇 For Prod/Deployment Mode 
    # socketio.run(app, host='0.0.0.0', port=5000, ssl_context=('cert.pem', 'key.pem'), allow_unsafe_werkzeug=True)

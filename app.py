# from flask import Flask, request, render_template, Response, redirect, url_for, session, jsonify
# from flask_mysqldb import MySQL
# from pydub import AudioSegment
# from werkzeug.utils import secure_filename
# from datetime import datetime
# import MySQLdb.cursors
# import logging
# import cv2
# import mediapipe as mp
# import numpy as np
# import pygame
# import os
# import threading
# import keyboard

# logging.basicConfig(level=logging.DEBUG)

# app = Flask(__name__)
# app.config['UPLOAD_FOLDER'] = 'path/to/save/uploads'  # Set this to the directory where you want to save uploads
# app.secret_key = 'vms'
# app.config['UPLOAD_FOLDER']='uploads'
# app.config['MAX_CONTENT_LENGTH']=16*1024*1024
# mysql = MySQL(app)
# app.config.from_object('config.Config')

# # Initialize MediaPipe Hand module
# mp_hands = mp.solutions.hands
# hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
# mp_draw = mp.solutions.drawing_utils

# # Initialize Pygame and Mixer
# pygame.init()
# mixer = pygame.mixer
# mixer.init()
# current_instrument = 'piano'

# # Define paths for personal sound files
# sound_dir_gui = 'C:/Users/ramch/OneDrive/Desktop/HandGestureVMI/static/guitarSounds'
# sound_dir_pia = 'C:/Users/ramch/OneDrive/Desktop/HandGestureVMI/static/pianoSounds'
# sound_dir_drum = 'C:/Users/ramch/OneDrive/Desktop/HandGestureVMI/static/drumsSounds'

# # Update with paths to your downloaded sounds
# instruments = {
#     'piano': {note: os.path.join(sound_dir_pia, f"{note}.mp3") for note in 'CDEFGAB'},
#     'guitar': {note: os.path.join(sound_dir_gui, f"{note}.mp3") for note in 'CDEFGAB'},
#     'drums': {note: os.path.join(sound_dir_drum, f"{note}.mp3") for note in 'CDEFGAB'}
# }

# # Define note regions on the screen
# note_regions = {
#     'C': ((50, 150), (50, 150)),
#     'D': ((150, 250), (50, 150)),
#     'E': ((250, 350), (50, 150)),
#     'F': ((350, 450), (50, 150)),
#     'G': ((450, 550), (50, 150)),
#     'A': ((550, 650), (50, 150)),
#     'B': ((650, 750), (50, 150))
# }

# # Create a dictionary to keep track of sound channels
# sound_channels = {note: mixer.Channel(i) for i, note in enumerate(instruments[current_instrument].keys())}

# # Initialize webcam
# cap = cv2.VideoCapture(0)

# # Define colors for visual feedback
# ACTIVE_COLOR = (0, 255, 0)
# INACTIVE_COLOR = (255, 0, 0)

# # Define function to draw note regions on frame
# def draw_note_regions(frame, active_note=None):
#     for note, ((x1, x2), (y1, y2)) in note_regions.items():
#         color = ACTIVE_COLOR if note == active_note else INACTIVE_COLOR
#         cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
#         cv2.putText(frame, note, (x1 + 10, y1 + 40), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)

# # Define function to calculate volume based on distance between thumb and index finger
# def calculate_volume(hand_landmarks):
#     thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
#     index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
#     distance = np.sqrt((thumb_tip.x - index_tip.x) ** 2 + (thumb_tip.y - index_tip.y) ** 2)
#     return min(max(0.1, 1.0 - distance * 2), 1.0)

# # Define function to handle sound playback and recording
# def play_sound(note, volume):
#     if note not in sound_channels:
#         print(f"Sound channel for {note} not found.")
#         return

#     print(f"Setting volume {volume} for note {note}.")
#     sound_channels[note].set_volume(volume)
#     if not sound_channels[note].get_busy():
#         print(f"Playing sound for note {note}.")
#         sound_channels[note].play(notes[note])
#     else:
#         print(f"Note {note} is already playing.")

# # Define function to switch instruments
# def switch_instrument(text):
#     global current_instrument, notes, sound_channels, cap

#     print(f"Switching to instrument: {text}")

#     if text not in instruments:
#         print(f"Instrument {text} not found.")
#         return

#     # Release and clean up current camera if open
#     if cap.isOpened():
#         print("Releasing current camera...")
#         cap.release()
#         cv2.destroyAllWindows()

#     # Switch instrument
#     current_instrument = text
#     notes = {note: mixer.Sound(instruments[current_instrument][note]) for note in 'CDEFGAB'}
#     sound_channels = {note: mixer.Channel(i) for i, note in enumerate(notes.keys())}

#     # Reinitialize the camera
#     print("Initializing new camera...")
#     try:
#         cap = cv2.VideoCapture(0)
#         print("Cam opened")
#     except:
#         print("Error in opening")
#     if not cap.isOpened():
#         print("Failed to open camera.")
#     else:
#         print("Camera initialized successfully.")

# # Load initial sounds
#     notes = {note: mixer.Sound(instruments[current_instrument][note]) for note in 'CDEFGAB'}

# # Thread function to monitor keyboard events
# def keyboard_monitor():
#     while True:
#         if keyboard.is_pressed('ctrl+q'):
#             print("Ctrl+Q pressed. Exiting...")
#             cap.release()  # Release the camera
#             cv2.destroyAllWindows()  # Close OpenCV windows
#             break

# # Start the keyboard monitoring thread
# keyboard_thread = threading.Thread(target=keyboard_monitor)
# keyboard_thread.start()

# def gen_frames():
#     while cap.isOpened():
#         success, frame = cap.read()
#         if not success:
#             print("Failed to capture frame from camera.")
#             break

#         frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         result = hands.process(frame_rgb)

#         active_note = None
#         if result.multi_hand_landmarks:
#             for hand_landmarks in result.multi_hand_landmarks:
#                 mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
#                 index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
#                 x = int(index_tip.x * frame.shape[1])
#                 y = int(index_tip.y * frame.shape[0])
#                 volume = calculate_volume(hand_landmarks)
#                 for note, ((x1, x2), (y1, y2)) in note_regions.items():
#                     if x1 < x < x2 and y1 < y < y2:
#                         play_sound(note, volume)
#                         active_note = note

#         draw_note_regions(frame, active_note)
#         ret, buffer = cv2.imencode('.jpg', frame)
#         frame = buffer.tobytes()
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        
# @app.route('/')
# def homepage():
#     return render_template('homepage.html')

# @app.route('/')
# def home():
#     return render_template('home.html')

# @app.route('/login/index', methods=['GET', 'POST'])
# def index():
#     if request.method == 'POST':
#         username = request.form.get('username')
#         password = request.form.get('password')

#         # Add your user authentication logic here
#         if username == 'user' and password == 'userpassword':  # Example credentials
#             session['user'] = username
#             return redirect(url_for('user_dashboard'))  # Redirect to user dashboard after successful login
#         else:
#             return "Invalid credentials", 401  # Return an error if credentials are invalid

#     return render_template('index.html')

# @app.route('/login/index')
# def index():
#     return render_template('index.html')

# @app.route('/login/admin', methods=['GET', 'POST'])
# def adminlogin():
#     if request.method == 'POST':
#         username = request.form.get('username')
#         password = request.form.get('password')

#         # Add your user authentication logic here
#         if username == 'user' and password == 'userpassword':  # Example credentials
#             session['user'] = username
#             return redirect(url_for('admin_dashboard'))  # Redirect to user dashboard after successful login
#         else:
#             return "Invalid credentials", 401  # Return an error if credentials are invalid\
#     return render_template('adminlogin.html')


# @app.route('/login/admin')
# def admin_login():
#     return render_template('adminlogin.html')

# @app.route('/playPiano')
# def playPiano():
#     switch_instrument('piano')
#     return render_template('play_instrument.html', current_instrument='piano')

# @app.route('/playGuitar')
# def playGuitar():
#     switch_instrument('guitar')
#     return render_template('play_instrument.html', current_instrument='guitar')

# @app.route('/playDrums')
# def playDrums():
#     switch_instrument('drums')
#     return render_template('play_instrument.html', current_instrument='drums')

# @app.route('/signup.html')
# def signup():
#     return render_template('signup.html')

# @app.route('/logindone', methods=['POST'])
# def logindone():
#     email = request.form['email']
#     name = request.form['name']
#     phno = request.form['phno']
#     password = request.form['pass']
#     copass = request.form['copass']
#     file = request.files['profile_image']

#     logging.debug('Received signup data: email=%s, password=%s, copass=%s', email, password, copass)

#     if password == copass:
#         try:
#             if file and file.filename:
#                 filename = secure_filename(file.filename)
#                 image_data = file.read()
#                 cursor = mysql.connection.cursor()
#                 cursor.execute('INSERT INTO users (name,email,phno, password,img,filename) VALUES (%s, %s, %s, %s, %s, %s)', (name, email, phno, password, image_data, filename))
#                 mysql.connection.commit()
                
#                 # Get the user ID
#                 cursor.execute('SELECT id FROM users WHERE email = %s', (email,))
#                 user = cursor.fetchone()
#                 session['user_id'] = user['id']  # Store user ID in session
                
#                 cursor.close()
#                 logging.debug('User %s successfully registered.', email)
#                 return render_template('loginDone.html')
#         except MySQLdb.Error as e:
#             logging.error('MySQL error: %s', str(e))
#             return render_template('signup.html', error=str(e))
#         except Exception as e:
#             logging.error('General error: %s', str(e))
#             return render_template('signup.html', error=str(e))
#     else:
#         logging.warning('Passwords do not match for user %s.', email)
#         error_message = "Password doesn't match for the user", email
#         return render_template('signup.html', error=error_message)

# @app.route('/dashboard', methods=['POST', 'GET'])
# def user_dashboard():
#     if 'user' in session:
#         return f"Welcome to the user dashboard, {session['user']}!"
#     else:
#         return redirect(url_for('index'))
    
# def admin_dashboard():
#     if 'admin' in session:
#         return f"Welcome to the admin dashboard, {session['admin']}!"
#     else:
#         return redirect(url_for('admin_login'))
    
# def dashboard():
#     email = request.form['email']
#     password = request.form['pass']
    
#     cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#     cursor.execute('SELECT * FROM users WHERE email = %s AND password = %s', (email, password))
#     account = cursor.fetchone()

#     if account:
#         session['user_id'] = account['id']  # Store user ID in session
#         return render_template('dashboard.html')
#     else:
#         logging.warning('Passwords do not match for user %s.', email)
#         return render_template('index.html', error="Incorrect email/password")
#     return render_template('dashboard.html')


# @app.route('/video_feed')
# def video_feed():
#     return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# @app.route('/switch_instrument/<instrument>', methods=['POST'])
# def switch_instrument_route(instrument):
#     if instrument in instruments:
#         try: 
#             switch_instrument(instrument)
#             print("instrument done")
#         except:
#             print("error")
#         return f"Switched to {instrument}", 200
#     return f"Instrument {instrument} not found", 404

# @app.route('/saved_recordings')
# def saved_recordings():
#     user_id = session.get('user_id')
#     cursor = mysql.connection.cursor()
#     cursor.execute('SELECT id, filename FROM mp3_files WHERE userId=%s', (user_id,))
#     recordings = cursor.fetchall()
#     cursor.close()
#     return render_template('saved_recordings.html', recordings=recordings)


# @app.route('/start_instrument')
# def start_instrument():
#     return render_template('play_instrument.html')

# @app.route('/profile', methods=['GET', 'POST'])
# def profile():
#     user_id = session.get('user_id')
#     print(user_id)  # Ensure user_id is retrieved from session or other secure method
#     # Fetch user data from the database (replace user_id with the actual user's ID)
#     cursor = mysql.connection.cursor()
#     cursor.execute('SELECT name, email,phno,img FROM users WHERE id=%s', (user_id,))
#     user = cursor.fetchone()
#     cursor.close()

#     if user:
#         # If there is binary image data, create a URL for the image
#         if user['img']:
#             user['image_url'] = url_for('serve_image', user_id=user_id)
#         else:
#             user['image_url'] = url_for('static', filename='default.jpg')
    
#     return render_template('profile.html', user=user)

# @app.route('/serve_image/<int:user_id>')
# def serve_image(user_id):
#     cursor = mysql.connection.cursor()
#     cursor.execute('SELECT img FROM users WHERE id=%s', (user_id,))
#     user = cursor.fetchone()
#     cursor.close()
    
#     if user and user['img']:
#         return Response(user['img'], mimetype='image/jpeg')  # Adjust mimetype if needed
#     else:
#         return Response("Image not found", mimetype='text/plain')

# @app.route('/quit', methods=['POST'])
# def quit():
#     global cap
#     if cap.isOpened():
#         cap.release()
#     cv2.destroyAllWindows()
#     return 'Camera and session ended', 200

# @app.route('/save_activity', methods=['POST'])
# def save_activity():
#     data = request.get_json()
#     activity = data.get('activity')
#     try:
#         cursor = mysql.connection.cursor()
#         cursor.execute('INSERT INTO activities (activity) VALUES (%s)', (activity,))
#         mysql.connection.commit()
#         cursor.close()
#         return jsonify({'status': 'success'}), 200
#     except Exception as e:
#         logging.error('Error saving activity: %s', str(e))
#         return jsonify({'error': 'Failed to save activity'}), 500
    
# @app.route('/gobacktodashboard')
# def goBackToDashboard():
#     return render_template('dashboard.html')
# @app.route('/logout')
# def logOut():
#     return render_template('index.html')

# # @app.route('/saved_recordings')
# # def saved_recordings():
# #     user_id = session.get('user_id')
# #     # Fetch user's saved recordings from the database
# #     cursor = mysql.connection.cursor()
# #     cursor.execute('SELECT * FROM recordings WHERE user_id=%s', (user_id,))
# #     recordings = cursor.fetchall()
# #     cursor.close()
# #     return render_template('saved_recordings.html', recordings=recordings)

# @app.route('/upload_recording', methods=['POST'])
# def upload_recording():
#     if 'recording' not in request.files:
#         return jsonify({'status': 'fail', 'message': 'No recording part'}), 400
#     file = request.files['recording']
#     if file.filename == '':
#         return jsonify({'status': 'fail', 'message': 'No selected file'}), 400
#     if file:
#         filename = secure_filename(file.filename)
#         filedata = file.read()
#         user_id = session.get('user_id')  # Assuming user is logged in and user_id is in session
#         try:
#             cursor = mysql.connection.cursor()
#             cursor.execute('INSERT INTO mp3_files (userId, filename, filedata) VALUES (%s, %s, %s)', (user_id, filename, filedata))
#             mysql.connection.commit()
#             cursor.close()
#             logging.debug('Recording %s successfully uploaded and saved.', filename)
#             return jsonify({'status': 'success'}), 200
#         except MySQLdb.Error as e:
#             logging.error('MySQL error: %s', str(e))
#             return jsonify({'status': 'fail', 'message': str(e)}), 500
#         except Exception as e:
#             logging.error('General error: %s', str(e))
#             return jsonify({'status': 'fail', 'message': str(e)}), 500
#     return jsonify({'status': 'fail', 'message': 'Failed to upload recording'}), 400

# @app.route('/download_recording/<int:recording_id>')
# def download_recording(recording_id):
#     cursor = mysql.connection.cursor()
#     cursor.execute('SELECT filename, filedata FROM mp3_files WHERE id=%s', (recording_id,))
#     recording = cursor.fetchone()
#     cursor.close()

#     if recording:
#         filename = recording['filename']
#         filedata = recording['filedata']
#         return Response(filedata,
#                         mimetype='audio/wav',  # Adjust mime type if necessary
#                         headers={'Content-Disposition': f'attachment; filename={filename}'})
#     else:
#         return 'File not found', 404

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'mp3'

# @app.route("/changePassword", methods=['POST'])
# def changePassword():
#     user_id = session.get('user_id')
#     oldp = request.form['oldp']
#     newp = request.form['newp']
    
#     cursor = mysql.connection.cursor()
    
#     # Ensure that user_id is passed as a tuple with a trailing comma
#     cursor.execute('SELECT password FROM users WHERE id = %s', (user_id,))
#     stored_password_row = cursor.fetchone()
#     cursor.close()  # Close the cursor after use

#     # Extract the password from the dictionary
#     if stored_password_row:
#         stored_password = stored_password_row['password']
#         if stored_password == oldp:
#             cursor = mysql.connection.cursor()
#             cursor.execute('UPDATE users SET password = %s WHERE id = %s', (newp, user_id))
#             mysql.connection.commit()
#             cursor.close()
#             text = "Password changed successfully"
#         else:
#             text = "Your old password is incorrect. Please try again."
#     else:
#         text = "User not found."
    
#     return render_template('profile.html', text=text)
# if __name__ == '__main__':
#     app.run(debug=True)

from flask import Flask, request, render_template, Response, redirect, url_for, session, jsonify
from flask_mysqldb import MySQL
from pydub import AudioSegment
from werkzeug.utils import secure_filename
from datetime import datetime
import MySQLdb.cursors
import logging
import cv2
import mediapipe as mp
import numpy as np
import pygame
import os
import threading
import signal
import sys

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Flask App Configuration
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.secret_key = 'vms'

# MySQL Configuration
app.config.from_object('config.Config')
mysql = MySQL(app)

# Global variables with safer initialization
current_instrument = 'piano'
cap = None
hands = None
notes = {}
sound_channels = {}

# Instrument and Sound Configuration
def initialize_instruments():
    global current_instrument, cap, hands, notes, sound_channels

    # Initialize MediaPipe Hand module
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
    mp_draw = mp.solutions.drawing_utils

    # Initialize Pygame and Mixer
    pygame.init()
    mixer = pygame.mixer
    mixer.init()

    # Define paths for personal sound files (update with your actual paths)
    sound_dir_gui = 'static/guitarSounds'
    sound_dir_pia = 'static/pianoSounds'
    sound_dir_drum = 'static/drumsSounds'

    # Update with paths to your downloaded sounds
    instruments = {
        'piano': {note: os.path.join(sound_dir_pia, f"{note}.mp3") for note in 'CDEFGAB'},
        'guitar': {note: os.path.join(sound_dir_gui, f"{note}.mp3") for note in 'CDEFGAB'},
        'drums': {note: os.path.join(sound_dir_drum, f"{note}.mp3") for note in 'CDEFGAB'}
    }

    # Load sounds for current instrument
    notes = {note: mixer.Sound(instruments[current_instrument][note]) for note in 'CDEFGAB'}
    sound_channels = {note: mixer.Channel(i) for i, note in enumerate(notes.keys())}

    # Initialize webcam
    cap = cv2.VideoCapture(0)

    return hands, cap, notes, sound_channels

# Signal Handler for Safe Exit
def signal_handler(sig, frame):
    print('\nSafely shutting down...')
    if cap is not None and cap.isOpened():
        cap.release()
    cv2.destroyAllWindows()
    pygame.quit()
    sys.exit(0)

# Register signal handler
signal.signal(signal.SIGINT, signal_handler)

# Existing helper functions (gen_frames, switch_instrument, etc.) remain the same
# ... (keep your existing helper functions)

# Route Definitions
@app.route('/')
def homepage():
    return render_template('homepage.html')

@app.route('/login/index', methods=['GET', 'POST'])
def login_index():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Add your user authentication logic here
        if username == 'user' and password == 'userpassword':
            session['user'] = username
            return redirect(url_for('user_dashboard'))
        else:
            return "Invalid credentials", 401

    return render_template('index.html')

# Remove duplicate routes
# Remove the second @app.route('/login/index')

# Keep other routes as they are...

# Main Application Startup
if __name__ == '__main__':
    # Initialize instruments and components before running
    try:
        hands, cap, notes, sound_channels = initialize_instruments()
        app.run(debug=True)
    except Exception as e:
        logging.error(f"Startup error: {e}")
        if cap is not None and cap.isOpened():
            cap.release()
        cv2.destroyAllWindows()

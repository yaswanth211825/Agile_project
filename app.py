

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

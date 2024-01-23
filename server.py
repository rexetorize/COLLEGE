# server.py
import io
import base64
import threading
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from PIL import ImageGrab
import keyboard
import mouse

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")  # Allow all origins for development


def screen_stream():
    while True:
        screenshot = ImageGrab.grab()
        img_byte_array = io.BytesIO()
        screenshot.save(img_byte_array, format='JPEG')
        img_data = base64.b64encode(img_byte_array.getvalue()).decode('utf-8')
        socketio.emit('stream', img_data, namespace='/')

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect', namespace='/')
def handle_connect():
    emit('stream_thread_started', broadcast=True)

@socketio.on('keyboard_event', namespace='/')
def handle_keyboard_event(data):
    try:
        key_event = data['event']
        if key_event == 'press':
            keyboard.press(data['key'])
        elif key_event == 'release':
            keyboard.release(data['key'])
    except Exception as e:
        print(f"Error handling keyboard event: {e}")

@socketio.on('mouse_event', namespace='/')
def handle_mouse_event(data):
    try:
        print(f"Received mouse event: {data}")
        event_type = data.get('event')
        button_code = data.get('button')

        # Process the mouse event as needed
        if event_type == 'click' and button_code is not None:
            mouse.click(button_code)
    except Exception as e:
        print(f"Error handling mouse event: {e}")

@socketio.on('touch_event', namespace='/')
def handle_touch_event(data):
    try:  
        delta_x = data.get('deltaX', 0)
        delta_y = data.get('deltaY', 0)

        # Process touch events as needed (e.g., move the mouse)
        # Example: move the mouse cursor on the PC based on touch input
        mouse.move(delta_x, delta_y)
    except Exception as e:
        print(f"Error handling touch event: {e}")

if __name__ == '__main__':
    stream_thread = threading.Thread(target=screen_stream)
    stream_thread.daemon = True
    stream_thread.start()
    # Listen on all available network interfaces
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)

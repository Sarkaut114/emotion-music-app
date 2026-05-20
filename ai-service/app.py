from flask import Flask, Response, jsonify
from flask_cors import CORS
from deepface import DeepFace
import cv2
import threading
import time

app = Flask(__name__)
CORS(app)

# buka webcam
cap = cv2.VideoCapture(0)

current_emotion = "detecting..."
current_frame = None

def webcam_loop():
    global current_frame

    while True:
        success, frame = cap.read()

        if success:
            current_frame = frame.copy()

def emotion_loop():
    global current_emotion, current_frame

    while True:
        try:
            if current_frame is None:
                continue

            result = DeepFace.analyze(
                current_frame,
                actions=['emotion'],
                enforce_detection=False,
                detector_backend='opencv'
            )
            current_emotion = result[0]['dominant_emotion']
            print("Emotion:", current_emotion)

        except Exception as e:
            print(e)

        # delay x detik
        time.sleep(0.1)


# jalankan thread webcam
threading.Thread(
    target=webcam_loop,
    daemon=True
).start()

# jalankan thread AI
threading.Thread(
    target=emotion_loop,
    daemon=True
).start()

# ROUTES
@app.route('/')
def home():

    return jsonify({
        "status": "running"
    })


@app.route('/emotion')
def emotion():

    return jsonify({
        "emotion": current_emotion
    })


@app.route('/video_feed')
def video_feed():

    def generate():
        global current_frame

        while True:
            if current_frame is None:
                continue

            ret, buffer = cv2.imencode('.jpg', current_frame)
            frame = buffer.tobytes()

            yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' +
                frame +
                b'\r\n'
            )

            # 0.03 = 30 fps
            time.sleep(0.03)

    return Response(
        generate(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


if __name__ == '__main__':

    try:
        app.run(debug=False, threaded=True)

    finally:
        cap.release()
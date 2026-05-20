from flask import Flask, Response, jsonify
from deepface import DeepFace
import cv2

app = Flask(__name__)

cap = cv2.VideoCapture(0)

current_emotion = "refresh..."

def generate_frames():

    global current_emotion

    while True:

        success, frame = cap.read()

        if not success:
            break

        try:

            result = DeepFace.analyze(
                frame,
                actions=['emotion'],
                enforce_detection=False
            )

            current_emotion = result[0]['dominant_emotion']

        except Exception as e:
            print(e)

        # convert frame ke jpg
        ret, buffer = cv2.imencode('.jpg', frame)

        frame = buffer.tobytes()

        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' +
            frame +
            b'\r\n'
        )

@app.route('/video_feed')
def video_feed():

    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

@app.route('/emotion')
def emotion():

    return jsonify({
        "emotion": current_emotion
    })

if __name__ == '__main__':
    app.run(debug=True)
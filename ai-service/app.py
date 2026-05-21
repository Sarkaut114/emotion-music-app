from flask import Flask, Response, jsonify
from flask_cors import CORS
from deepface import DeepFace
import cv2
import threading
import time
from collections import Counter

app = Flask(__name__)
CORS(app)

# buka webcam
cap = cv2.VideoCapture(0)

current_frame = None

# hasil terakhir
last_result = {
    "emotion": "Belum ada deteksi",
    "music": "",
    "advice": ""
}

# rekomendasi spotify + saran
recommendations = {
    "happy": {
        "music": "https://open.spotify.com/playlist/37i9dQZF1DXdPec7aLTmlC",
        "advice": "Pertahankan mood positif dan lakukan aktivitas yang kamu suka"
    },

    "sad": {
        "music": "https://open.spotify.com/playlist/0mcoURH64QKzzuAf3Wmwva?si=d8b5b80b9ea74444",
        "advice": "Coba istirahat sejenak dan dengarkan musik yang menenangkan"
    },

    "angry": {
        "music": "https://open.spotify.com/playlist/37i9dQZF1DX3rxVfibe1L0",
        "advice": "Tarik napas perlahan dan coba relaksasi beberapa menit"
    },

    "fear": {
        "music": "https://open.spotify.com/playlist/37i9dQZF1DWU0ScTcjJBdj",
        "advice": "Tenangkan diri dan fokus pada hal-hal positif"
    },

    "surprise": {
        "music": "https://open.spotify.com/playlist/37i9dQZF1DX4WYpdgoIcn6",
        "advice": "Nikmati momen dan tetap berpikir positif"
    },

    "neutral": {
        "music": "https://open.spotify.com/playlist/37i9dQZF1DX4sWSpwq3LiO",
        "advice": "Coba aktivitas ringan untuk menjaga mood tetap stabil"
    },

    "disgust": {
        "music": "https://open.spotify.com/playlist/37i9dQZF1DX889U0CL85jj",
        "advice": "Alihkan fokus ke hal yang membuat nyaman"
    }
}


# webcam realtime
def webcam_loop():

    global current_frame

    while True:

        success, frame = cap.read()

        if success:
            current_frame = frame.copy()


# thread webcam
threading.Thread(
    target=webcam_loop,
    daemon=True
).start()


@app.route('/')
def home():

    return jsonify({
        "status": "running"
    })


# scan emosi selama 3 detik
@app.route('/scan_emotion')
def scan_emotion():

    global current_frame, last_result

    emotion_list = []

    start_time = time.time()

    print("\n===== START SCAN =====")

    while time.time() - start_time < 3:

        try:

            if current_frame is None:
                continue

            result = DeepFace.analyze(
                current_frame,
                actions=['emotion'],
                enforce_detection=False,
                detector_backend='opencv'
            )

            emotion = result[0]['dominant_emotion']

            # tampil realtime di terminal
            print("Emotion Detected:", emotion)

            emotion_list.append(emotion)

            time.sleep(0.2)

        except Exception as e:
            print("ERROR:", e)

    # ambil emosi paling sering muncul
    if len(emotion_list) > 0:

        final_emotion = Counter(
            emotion_list
        ).most_common(1)[0][0]

    else:
        final_emotion = "neutral"

    recommendation = recommendations.get(
        final_emotion,
        recommendations['neutral']
    )

    last_result = {
        "emotion": final_emotion,
        "music": recommendation['music'],
        "advice": recommendation['advice']
    }

    # hasil final terminal
    print("\n===== FINAL RESULT =====")
    print("FINAL EMOTION:", final_emotion)
    print("SPOTIFY:", recommendation['music'])
    print("ADVICE:", recommendation['advice'])
    print("========================\n")

    return jsonify(last_result)


# streaming webcam
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

            time.sleep(0.03)

    return Response(
        generate(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


if __name__ == '__main__':

    try:
        app.run(
            debug=False,
            threaded=True
        )

    finally:
        cap.release()
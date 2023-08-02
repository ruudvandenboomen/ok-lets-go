import os

from dotenv import load_dotenv
from flask import Flask, render_template, send_from_directory, request
from flask_socketio import SocketIO
import re

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

online_users = set()
regex_pattern = re.compile(r"(?i)\bok\b.*\b(lets|let's)\b .*\bgo\b")


# Serve the index.html file
@app.route("/")
def index():
    return render_template("index.html")


# Handle WebSocket connections
@socketio.on("connect")
def handle_connect():
    online_users.add(request.sid)
    socketio.emit("update_online_count", {"count": len(online_users)})


@socketio.on("disconnect")
def handle_disconnect():
    online_users.discard(request.sid)
    socketio.emit("update_online_count", {"count": len(online_users)})


@socketio.on("message")
def handle_message(data):
    message = data["message"]
    if regex_pattern.match(message):
        socketio.emit("message", {"message": message})


@socketio.on("play_audio")
def handle_play_audio():
    print("Playing audio")
    # Trigger audio playback on the client side
    socketio.emit("play_audio")


@socketio.on("play_audio_2")
def handle_play_audio_2():
    print("Playing audio")
    # Trigger audio playback on the client side
    socketio.emit("play_audio_2")


@socketio.on("play_audio_3")
def handle_play_audio_3():
    print("Playing audio")
    # Trigger audio playback on the client side
    socketio.emit("play_audio_3")


@socketio.on("play_audio_4")
def handle_play_audio_4():
    print("Playing audio")
    # Trigger audio playback on the client side
    socketio.emit("play_audio_4")


@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory("static", filename)


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", debug=True)

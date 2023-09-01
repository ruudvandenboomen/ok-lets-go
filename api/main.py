import os

import requests
from dotenv import load_dotenv
from flask import Flask, abort, jsonify, render_template, request, send_from_directory
from flask_socketio import SocketIO
from history import HistoryFirebase
from pywebpush import WebPushException, webpush

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

SMIIRL_MAC = os.getenv("SMIIRL_MAC")
SMIIRL_TOKEN = os.getenv("SMIIRL_TOKEN")

socketio = SocketIO(app)

online_users = dict()
subscriptions: dict = {}

# For push notifications
PUBLIC_KEY = os.getenv("PUBLIC_KEY")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

FIREBASE_DSN = os.getenv("FIREBASE_DSN")
FIREBASE_AUTH = os.getenv("FIREBASE_AUTH")
history = HistoryFirebase(FIREBASE_DSN, FIREBASE_AUTH)


def send_number_to_smiirl(number: int) -> None:
    url = f"https://api.smiirl.com/{SMIIRL_MAC}/set-number/{SMIIRL_TOKEN}/{number}"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception if the request wasn't successful

        print(f"Send request to api.smiirl.com: {number}")
    except requests.exceptions.RequestException as e:
        print("Error:", e)


def _handle_user_list_changed(users: dict) -> None:
    user_count = len(users)
    socketio.emit("update_online_count", {"count": user_count})
    send_number_to_smiirl(user_count)


# Serve the index.html file
@app.route("/")
def index():
    return render_template("index.html", messages=history.get_items(300))


@socketio.on("disconnect")
def handle_disconnect():
    online_users.pop(request.sid, None)
    _handle_user_list_changed(online_users)


@app.route("/<user_id>/subscribed", methods=["GET"])
def subscribed_check(user_id):
    if user_id in subscriptions:
        return jsonify({"subscribed": True})
    return jsonify({"subscribed": False})


@app.route("/<user_id>/subscribe", methods=["PUT"])
def subscribe(user_id):
    subscription = request.get_json()

    if user_id:
        # Store the subscription details
        subscriptions[user_id] = subscription
        return jsonify({"message": "Subscribed successfully"})
    else:
        return jsonify({"error": "User ID not provided"})


@app.route("/<user_id>/unsubscribe", methods=["PUT"])
def unsubscribe(user_id):
    if user_id:
        try:
            # Remove the subscription details
            subscriptions.pop(user_id)
        except KeyError:
            abort(400, description="Bad request: invalid User ID.")
        return jsonify({"message": "Unsubscribed successfully"})
    else:
        return jsonify({"error": "User ID not provided"})


@socketio.on("message")
def handle_message(data):
    sender_user_id = data["user_id"]
    message = data["message"]
    name = online_users.get(request.sid, "")
    message = {
        "user": name,
        "content": message,
    }
    socketio.emit("message", {"message": message})
    history.insert(user=name, content=message["content"])

    for user_id, subscription in subscriptions.items():
        if user_id != sender_user_id:
            try:
                webpush(
                    subscription_info=subscription,
                    data=message["content"],
                    vapid_private_key=PRIVATE_KEY,
                    vapid_claims={"sub": "mailto:ruudvdboomen@hotmail.com"},
                )
            except WebPushException as e:
                print("Error sending notification:", e)

    return jsonify({"message": "Notifications sent successfully"})


@socketio.on("set_name")
def handle_set_name(data):
    online_users[request.sid] = data["name"]
    _handle_user_list_changed(online_users)


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

import asyncio
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import time
import device_utils

app = Flask(__name__)
CORS(app)
EVENTS_FILE = "googleAPI/events.json"
RED = 0
GREEN = 120
BLUE = 240
PURPLE = 300

def load_events():
    with open(EVENTS_FILE, "r") as f:
        return json.load(f)

def save_events(events):
    with open(EVENTS_FILE, "w") as f:
        json.dump(events, f, indent=4)

def set_bulb_color(hue: int):
    print("SETTING BULB COLOR", flush=True)
    bulb = device_utils.get_light()
    if bulb:
        retries = 3
        for attempt in range(retries):
            try:
                asyncio.run(bulb.set_hsv(hue, 100, 100))
                return
            except Exception as e:
                print(f"Attempt {attempt+1} failed: {e}", flush=True)
                time.sleep(0.5)
        print("Failed to set light color after several retries.", flush=True)

def set_in_color():
    print("SETTING IN COLOR", flush=True)
    set_bulb_color(RED)

def set_out_color():
    set_bulb_color(GREEN)

def set_upcoming_color():
    set_bulb_color(BLUE)

def set_ongoing_color():
    set_bulb_color(PURPLE)

@app.route('/in_meeting', methods=['GET', 'POST'])
def in_meeting():
    meeting_id = None
    if request.method == "POST":
        if request.is_json:
            data = request.get_json()
            meeting_id = data.get("meeting_id")
        else:
            return jsonify({"error": "Unsupported Media Type, expecting application/json"}), 415
    else:  # GET request
        meeting_id = request.args.get("meeting_id")

    if meeting_id:
        events = load_events()
        found = False
        for event in events:
            if ("conferenceData" in event and
                "conferenceId" in event["conferenceData"] and
                event["conferenceData"]["conferenceId"] == meeting_id):
                event["joined"] = True
                found = True
                break
        if found:
            save_events(events)

    set_in_color()
    print("FINISHED", flush=True)
    return jsonify(device_utils.get_status()), 200

@app.route('/out_meeting', methods=['GET'])
def out_meeting():
    set_out_color()
    return jsonify(device_utils.get_status()), 200

@app.route('/ongoing_meeting', methods=['GET'])
def ongoing_meeting():
    set_ongoing_color()
    return jsonify(device_utils.get_status()), 200

@app.route('/upcoming_meeting', methods=['GET'])
def upcoming_meeting():
    set_upcoming_color()
    return jsonify(device_utils.get_status()), 200

@app.route('/status', methods=['GET'])
def get_status():
    status = device_utils.get_status()
    return jsonify(status), 200

if __name__ == '__main__':
    print("STARTING UP!!!", flush=True)
    app.run(host="0.0.0.0", port=5000, debug=True)


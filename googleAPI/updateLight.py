import json
import datetime
import requests

# Constants
EVENTS_FILE = "events.json"
API_BASE_URL = "https://kasa.mcgeld.com/api"
UPCOMING_THRESHOLD = datetime.timedelta(minutes=15)
RED = 0
GREEN = 120

def load_events():
    """Load events from the JSON file"""
    with open(EVENTS_FILE, "r") as f:
        return json.load(f)

def save_events(events):
    """Save events back to the JSON file."""
    with open(EVENTS_FILE, "w") as f:
        json.dump(events, f, indent=4)


def parse_event_datetime(dt_str):
    """Parse an ISO8601 datetime string; assume UTC."""
    if dt_str.endswith("Z"):
        dt_str = dt_str[:-1] + "+00:00"
    return datetime.datetime.fromisoformat(dt_str)

def get_current_light_state():
    """Call API status endpoint to get the current light state."""
    try:
        response = requests.get(f"{API_BASE_URL}/status")
        data = response.json()
        return data.get("hue")
    except Exception as e:
        print("Error fetching light state:", e)
        return None

def update_light_state():
    """Determine the correct light state based on events and update the light accordingly."""
    events = load_events()
    now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
    # For upcoming threshold
    upcoming_limit = now + UPCOMING_THRESHOLD

    # Flags to track meeting conditions.
    meeting_current = None
    meeting_upcoming = None

    for event in events:
        start_str = event.get("start", {}).get("dateTime")
        end_str = event.get("end", {}).get("dateTime")
        if not start_str or not end_str:
            continue

        try:
            start_time = parse_event_datetime(start_str)
            end_time = parse_event_datetime(end_str)
        except Exception as e:
            print(f"Error parsing event {event.get('id')}: {e}")
            continue

        # Only consider events for today.
        if start_time.date() != now.date():
            continue

        # If the event is marked as joined, skip processing it.
        if event.get("joined", False):
            continue

        # Check if meeting is in progress.
        if start_time <= now <= end_time:
            meeting_current = event
        #Else if it is upcoming (starting within threshold)
        elif now < start_time <= upcoming_limit:
            meeting_upcoming = event
    
    current_state = get_current_light_state()
    # Assume that red indicates you've joined a meeting.
    # If you're in a meeting that you've joined (red), automated updates should not override.
    if current_state == RED:
        print("Light is already red (joined meeting); not updating.")
        return

    # Decide on new state.
    if meeting_current:
        # Meeting is in progress and not joined: set to orange.
        print("Current meeting not joined; setting light to purple.")
        requests.get(f"{API_BASE_URL}/ongoing_meeting")
    elif meeting_upcoming:
        # Meeting upcoming and light is not red: set to yellow.
        print("Meeting upcoming; setting light to blue.")
        requests.get(f"{API_BASE_URL}/upcoming_meeting")
    elif current_state != RED and current_state != GREEN:
        # No meeting and light is not red or green: set to green.
        print("No meeting; setting light to green.")
        requests.get(f"{API_BASE_URL}/out_meeting")


if __name__ == "__main__":
    update_light_state()

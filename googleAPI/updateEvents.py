import datetime
import json
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

CONFIG_FILE = "events.json"

def load_events(filename):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_events(filename, events):
    with open(filename, "w") as f:
        json.dump(events, f, indent=4)

def remove_old_events(events):
    """Keep only events from today."""
    today = datetime.datetime.utcnow().date()
    new_events = []
    for event in events:
        start = event.get("start", {})
        # Handle all-day events or events with dateTime
        event_date_str = start.get("date") or start.get("dateTime")
        if event_date_str:
            try:
                # For dateTime strings that include time info, take the date portion.
                event_date = datetime.datetime.fromisoformat(event_date_str.replace("Z", "+00:00")).date()
            except ValueError:
                # If parsing fails, skip the event.
                continue
            if event_date == today:
                new_events.append(event)
        else:
            # If there's no start date info, keep the event.
            new_events.append(event)
    return new_events

def get_todays_events(service):
    """Retrieve today's events from Google Calendar (UTC)."""
    now = datetime.datetime.utcnow()
    start_of_day = datetime.datetime.combine(now.date(), datetime.time.min).isoformat() + "Z"
    end_of_day = datetime.datetime.combine(now.date(), datetime.time.max).isoformat() + "Z"
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=start_of_day,
            timeMax=end_of_day,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    return events_result.get("items", [])

def merge_events(existing, new):
    """Merge new events into the existing list based on event ID."""
    existing_ids = {event["id"] for event in existing if "id" in event}
    for event in new:
        if "id" in event and event["id"] not in existing_ids:
            existing.append(event)
    return existing

def get_credentials():
    """Load credentials from token.json, refreshing or reauthorizing if needed."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.refresh_token:
            creds.refresh(Request())
        else:
            from google_auth_oauthlib.flow import InstalledAppFlow
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_console(prompt='consent')
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds

def main():
    # Load existing events from the JSON file.
    events = load_events(CONFIG_FILE)
    events = remove_old_events(events)

    # Get Google Calendar credentials and build the service.
    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)

    # Retrieve today's events.
    todays_events = get_todays_events(service)
    print(f"Found {len(todays_events)} events today.")

    # Merge any new events that aren't already in our list.
    updated_events = merge_events(events, todays_events)

    # Save the updated events list back to the JSON file.
    save_events(CONFIG_FILE, updated_events)
    print("Events updated and saved to", CONFIG_FILE)

if __name__ == "__main__":
    main()

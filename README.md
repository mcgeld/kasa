---
title: Kasa Google Calendar Event Signaler
status: active
tags: [kasa, smart home, google calendar, flask, python]
vision: "To provide automated, visual status signaling of upcoming scheduled events using Kasa smart lighting devices."
---

# Kasa Integration Project

## Description

This project is a centralized Python backend that integrates TP-Link Kasa smart devices, specifically lighting, with Google Calendar events.

The core service utilizes a Flask API (`app.py`) for managing device state and receiving updates. Helper scripts (`googleAPI/updateEvents.py` and `googleAPI/updateLight.py`) periodically pull calendar data and trigger color changes on the Kasa bulb based on the proximity of upcoming events.

Device discovery and low-level control are handled via the `python-kasa` library, ensuring robust local network interaction with smart devices.

## Setup/Installation

### Prerequisites

1.  Python 3.8+
2.  A configured TP-Link Kasa smart bulb/light.
3.  A Google API Project with the Calendar API enabled, and generated OAuth 2.0 Client credentials (stored in `googleAPI/credentials.json`).

### 1. Dependencies

Install the required Python packages:

```bash
pip install flask python-kasa google-api-python-client google-auth-oauthlib
```

### 2. Google Calendar Authentication

Run the quickstart script to generate the necessary `token.json` file, which handles OAuth flows for calendar access.

```bash
python googleAPI/quickstart.py
```

### 3. Configuration

Configure device details in the `config.json` file. This file stores the alias or IP address of the target Kasa device to ensure consistent connection.

Example `config.json`:

```json
{
    "device_alias": "Office Light",
    "device_ip": "192.168.1.50"
}
```

### 4. Operation

1.  **Start the API Server:**
    Run the Flask application, which hosts the endpoints for setting light status.

    ```bash
    python app.py
    ```

2.  **Schedule Event Updates:**
    Set up a scheduler (e.g., Cron job, systemd timer) to run the following two scripts frequently (e.g., every 5 minutes):

    *   `googleAPI/updateEvents.py`: Fetches and caches new calendar events into `googleAPI/events.json`.
    *   `googleAPI/updateLight.py`: Reads the cached events and calls the running Flask API to update the light status if an event is imminent.

## Tech Stack

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Backend** | Python 3 | Primary language for logic and control. |
| **Web Framework** | Flask | Provides RESTful API endpoints for light control. |
| **Smart Home Control** | `python-kasa` | Library for local discovery and control of TP-Link Kasa devices. |
| **Data Source** | Google Calendar API | Used for fetching schedule events and timing information. |
| **Data Storage** | JSON (`config.json`, `events.json`) | Configuration and temporary caching of calendar events. |
| **Concurrency** | `asyncio` | Used internally by the Kasa library for non-blocking device communication. |
from datetime import datetime, timedelta, timezone
import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from iso8601 import parse_date
from termcolor import colored
from pathlib import Path

CURDIRT = Path(__file__).parent
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
_GOOGLE_SERVICE = None

def _init_google_service():
    global _GOOGLE_SERVICE
    if _GOOGLE_SERVICE is not None:
        return

    creds = None
    path_to_secret = os.path.join(CURDIRT, "secret/client_secret.json")
    path_to_token = os.path.join(CURDIRT, "secret/token.json")
    if os.path.exists(path_to_token):
        creds = Credentials.from_authorized_user_file(path_to_token, scopes=SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(path_to_secret, scopes=SCOPES)
            creds = flow.run_local_server(port=0)
        with open(path_to_token, 'w') as f:
            f.write(creds.to_json())
    
    _GOOGLE_SERVICE = build('calendar', 'v3', credentials=creds)


def print_events_today():
    _init_google_service()
    now = datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    later = (datetime.utcnow() + timedelta(days=1)).isoformat() + 'Z'
    print('Getting today\'s events...\n')
    events_result = _GOOGLE_SERVICE.events().list(
        calendarId='primary', 
        timeMin=now,
        timeMax=later,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', None)
        reminder = False
        if start is None:
            start = event['start'].get('date')
        else:
            start = parse_date(start)
            difference = (start - datetime.now(timezone.utc)).total_seconds()
            mins = divmod(difference, 60)[0]
            start = start.strftime("%Y-%m-%d, %H:%M:%S")
            if mins < 15 and mins >= 0:
                reminder = True

        if reminder:
            print(colored(start + " "+ event['summary'] + "\t <-- incoming", 'cyan', attrs=['bold']))
        else:
            print(start, event['summary'])

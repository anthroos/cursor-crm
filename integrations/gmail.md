# Gmail API

Read emails and calendar events through the Gmail API.

## What You Get

- Search emails (by sender, subject, date)
- Read email contents
- View calendar events
- Read-only access (no sending, for safety)

---

## Step 1: Create Google Cloud Project

1. Go to https://console.cloud.google.com
2. Create a new project (or select an existing one)
3. Name it `CRM Integration` (or anything you like)

---

## Step 2: Enable APIs

1. In Google Cloud Console: **APIs & Services** > **Library**
2. Find **Gmail API** > click **Enable**
3. Find **Google Calendar API** > click **Enable** (optional)

---

## Step 3: Create OAuth Credentials

1. **APIs & Services** > **Credentials**
2. **Create Credentials** > **OAuth client ID**
3. If prompted, configure **OAuth consent screen**:
   - User Type: **External**
   - App name: `CRM Integration`
   - User support email: your email
   - Developer contact: your email
   - Scopes: add `gmail.readonly`, `calendar.readonly`
   - Test users: add your email
4. Go back to **Credentials** > **Create Credentials** > **OAuth client ID**
5. Application type: **Desktop app**
6. Name: `CRM Desktop`
7. **Download JSON** > save as `credentials.json`

---

## Step 4: Install Dependencies

```bash
pip3 install google-auth google-auth-oauthlib google-api-python-client
```

---

## Step 5: Authorization

Create `gmail_auth.py`:

```python
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/calendar.readonly'
]

def authenticate():
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    print("Authorization successful!")
    return creds

if __name__ == '__main__':
    authenticate()
```

Run:
```bash
python3 gmail_auth.py
```

A browser window will open -- log in and grant permissions. Token is saved to `token.json`.

---

## Step 6: Add to .gitignore

```
credentials.json
token.json
```

Never commit these files!

---

## Usage

After authorization, ask your AI assistant:

> "Show emails from john@company.com this week"

> "Find all emails with subject 'invoice'"

> "What's the latest thread with Acme Corp?"

---

## Code Examples

### Search Emails

```python
from googleapiclient.discovery import build

def search_emails(creds, query, max_results=10):
    service = build('gmail', 'v1', credentials=creds)

    results = service.users().messages().list(
        userId='me',
        q=query,
        maxResults=max_results
    ).execute()

    messages = results.get('messages', [])

    for msg in messages:
        msg_data = service.users().messages().get(
            userId='me',
            id=msg['id'],
            format='metadata',
            metadataHeaders=['From', 'Subject', 'Date']
        ).execute()

        headers = {h['name']: h['value'] for h in msg_data['payload']['headers']}
        print(f"From: {headers.get('From')}")
        print(f"Subject: {headers.get('Subject')}")
        print(f"Date: {headers.get('Date')}")
        print("---")

# Usage
creds = authenticate()
search_emails(creds, "from:client@example.com")
```

### Get Calendar Events

```python
from googleapiclient.discovery import build
from datetime import datetime, timedelta

def get_calendar_events(creds, days=7):
    service = build('calendar', 'v3', credentials=creds)

    now = datetime.utcnow().isoformat() + 'Z'
    end = (datetime.utcnow() + timedelta(days=days)).isoformat() + 'Z'

    events = service.events().list(
        calendarId='primary',
        timeMin=now,
        timeMax=end,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    for event in events.get('items', []):
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(f"{start}: {event['summary']}")
```

---

## Troubleshooting

### "Access blocked: This app's request is invalid"
- Make sure you added your email to Test users
- OAuth consent screen must be configured

### Token expired
- Delete `token.json`
- Run `gmail_auth.py` again

### "Insufficient Permission"
- Check that you added the correct scopes
- Delete `token.json` and re-authorize

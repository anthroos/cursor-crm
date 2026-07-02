# LinkedIn Integration

Track LinkedIn connections, messages, and outreach alongside your CRM data.

## What You Get

- Track LinkedIn connections in your CRM contacts
- Log LinkedIn messages as CRM activities
- Use LinkedIn profile URLs as unique identifiers
- Coordinate outreach across LinkedIn + other channels

---

## How It Works

LinkedIn doesn't offer a public messaging API for individuals. This integration works through **manual logging** assisted by your AI:

1. You interact with prospects on LinkedIn
2. You tell your AI to log the activity
3. CRM tracks the full conversation history across all channels

---

## Setup

### 1. Store LinkedIn URLs in Contacts

When adding a person to `people.csv`, include their LinkedIn URL:

```
person_id,first_name,last_name,linkedin_url,company_id,...
p-acme-1,John,Smith,https://linkedin.com/in/johnsmith,comp-acme,...
```

When adding a company to `companies.csv`:

```
company_id,name,linkedin_url,...
comp-acme,Acme Corp,https://linkedin.com/company/acme,...
```

### 2. Log LinkedIn Activities

After any LinkedIn interaction, tell your AI:

> "Log LinkedIn message sent to John at Acme -- introduced our services"

This creates an activity record:
- **type**: `message`
- **channel**: `linkedin`
- **direction**: `outbound`

### 3. Track Connection Requests

> "Log LinkedIn connection request sent to Sarah at BetaWorks"

---

## Workflow

### Outbound Outreach via LinkedIn

1. **Research** -- check the prospect's LinkedIn profile
2. **Connect** -- send a connection request with a personalized note
3. **Log** -- tell your AI to log the outreach
4. **Follow up** -- if they accept, send a message and log it
5. **Move to email** -- once engaged, transition to email for proposals

### Inbound from LinkedIn

1. Someone connects or messages you on LinkedIn
2. Tell your AI:
   > "John from Acme connected on LinkedIn and asked about our services"
3. AI creates company + person + activity records
4. Continue the conversation on LinkedIn or move to email

---

## Common Commands

```
"Log LinkedIn message to John -- discussed pricing"
"Add person from LinkedIn: Sarah Chen, VP Engineering at Acme, linkedin.com/in/sarahchen"
"Show all LinkedIn activities this week"
"Who did I connect with on LinkedIn recently?"
"Find contacts without LinkedIn URLs"
```

---

## Advanced: Browser Automation (CDP)

For power users who want to automate LinkedIn reading, you can use Chrome DevTools Protocol (CDP) to read your LinkedIn inbox programmatically:

### Prerequisites

```bash
pip3 install pychrome
```

### Launch Chrome with Remote Debugging

```bash
# macOS
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
    --remote-debugging-port=9222 \
    --user-data-dir=/tmp/chrome-debug
```

### Read LinkedIn Messages

```python
import pychrome

browser = pychrome.Browser(url="http://127.0.0.1:9222")
tab = browser.list_tab()[0]
tab.start()

# Navigate to LinkedIn messages
tab.Page.navigate(url="https://www.linkedin.com/messaging/")

# Extract conversation list via DOM
result = tab.Runtime.evaluate(
    expression="""
    Array.from(document.querySelectorAll('.msg-conversation-listitem'))
        .map(el => ({
            name: el.querySelector('.msg-conversation-card__participant-names')?.textContent?.trim(),
            preview: el.querySelector('.msg-conversation-card__message-snippet')?.textContent?.trim()
        }))
    """
)

for conv in result.get('result', {}).get('value', []):
    print(f"{conv['name']}: {conv['preview']}")
```

**Note:** This requires you to be logged into LinkedIn in the Chrome instance. Use responsibly -- LinkedIn may restrict automated access.

---

## Tips

- **LinkedIn URL as identifier** -- use `linkedin_url` in `people.csv` as a reliable unique identifier when email is unknown
- **Multi-channel outreach** -- start on LinkedIn, move to email for proposals, use Telegram for quick follow-ups
- **Track response rates** -- query activities to see which LinkedIn messages got responses
- **Connection request notes** -- always log the note you sent with the connection request

---

## Troubleshooting

### Can't find contact's LinkedIn URL
- Search on LinkedIn by name + company
- Check company's LinkedIn page for employees

### Activity not showing up
- Make sure `channel` is set to `linkedin`
- Check that `person_id` matches the correct contact

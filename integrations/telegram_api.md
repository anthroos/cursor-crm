# Telegram API (Telethon)

Read and send Telegram messages through the official API.

## What You Get

- Read messages from chats/groups
- Send messages
- Manage groups (create, rename)
- Search contacts

---

## Step 1: Get API Credentials

1. Go to https://my.telegram.org
2. Log in with your phone number
3. Go to **API development tools**
4. Create a new app:
   - App title: `MyCRM` (any name)
   - Short name: `mycrm`
   - Platform: `Desktop`
5. Copy **App api_id** and **App api_hash**

---

## Step 2: Install Dependencies

```bash
pip3 install telethon python-dotenv qrcode
```

---

## Step 3: Create .env File

```bash
# .env
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=abcdef1234567890abcdef1234567890
```

Add `.env` to `.gitignore`!

---

## Step 4: QR Authorization

Create `telegram_login.py`:

```python
from telethon import TelegramClient
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

client = TelegramClient(
    'telegram_session',
    int(os.getenv('TELEGRAM_API_ID')),
    os.getenv('TELEGRAM_API_HASH')
)

async def main():
    await client.connect()

    if not await client.is_user_authorized():
        qr_login = await client.qr_login()

        import qrcode
        qr = qrcode.QRCode(border=1)
        qr.add_data(qr_login.url)
        qr.print_ascii(invert=True)

        print("\nScan QR in Telegram:")
        print("   Settings > Devices > Link Desktop Device")

        await qr_login.wait(timeout=120)

    me = await client.get_me()
    print(f"\nLogged in as: {me.first_name} (@{me.username})")
    await client.disconnect()

asyncio.run(main())
```

Run:
```bash
python3 telegram_login.py
```

Scan the QR code in Telegram on your phone. The session is saved to `telegram_session.session`.

---

## Usage

After authorization, ask your AI assistant:

> "Show last 10 messages from group [name]"

> "Send message to @username: Hello!"

> "Find all chats mentioning 'project'"

---

## Code Examples

### Read Messages

```python
async with client:
    async for message in client.iter_messages('username', limit=10):
        print(f"{message.sender.first_name}: {message.text}")
```

### Send Message

```python
async with client:
    await client.send_message('username', 'Hello!')
```

### List Chats

```python
async with client:
    async for dialog in client.iter_dialogs():
        print(dialog.name)
```

---

## Rate Limits

| Parameter | Value |
|-----------|-------|
| Messages to new contacts in a row | 10-15 max |
| Delay between messages | 5 seconds minimum |
| Pause after hitting limit | 5-30 minutes |

```python
import asyncio
from telethon.errors import FloodWaitError

try:
    await client.send_message(user, text)
except FloodWaitError as e:
    print(f"Waiting {e.seconds} seconds...")
    await asyncio.sleep(e.seconds)
```

---

## Troubleshooting

### QR code doesn't scan
- Make sure Telegram on your phone is up to date
- Try increasing screen brightness

### Session expired
- Delete `telegram_session.session`
- Run `telegram_login.py` again

### FloodWaitError
- Wait the specified number of seconds
- Reduce message frequency

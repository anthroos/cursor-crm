# WhatsApp (Baileys)

Read WhatsApp chats through Baileys -- an unofficial WhatsApp Web library.

## What You Get

- Read messages from chats
- Read group chats
- View contact list
- Send messages (use with caution -- rate limits apply!)

---

## Important Before You Start

1. **Baileys is an unofficial library**. WhatsApp may block your account for suspicious activity.
2. **Do not spam!** Use only for reading or infrequent messages.
3. **Keep your phone online** -- WhatsApp Web requires a phone connection.

---

## Step 1: Install Node.js

```bash
# macOS
brew install node

# Verify
node --version  # should be 18+
npm --version
```

---

## Step 2: Create Project

```bash
mkdir whatsapp-integration
cd whatsapp-integration
npm init -y
npm install @whiskeysockets/baileys qrcode-terminal
```

---

## Step 3: Create Login Script

Create `whatsapp_login.js`:

```javascript
const { default: makeWASocket, useMultiFileAuthState } = require('@whiskeysockets/baileys');
const qrcode = require('qrcode-terminal');

async function main() {
    const { state, saveCreds } = await useMultiFileAuthState('./whatsapp_session');

    const sock = makeWASocket({
        auth: state,
        printQRInTerminal: false
    });

    sock.ev.on('creds.update', saveCreds);

    sock.ev.on('connection.update', async (update) => {
        const { connection, qr } = update;

        if (qr) {
            console.log('\nScan QR code in WhatsApp:');
            console.log('   WhatsApp > Menu > Linked Devices > Link a Device\n');
            qrcode.generate(qr, { small: true });
        }

        if (connection === 'open') {
            console.log('\nConnected to WhatsApp!');

            const chats = await sock.groupFetchAllParticipating();
            console.log(`\nGroups: ${Object.keys(chats).length}`);

            for (const [jid, chat] of Object.entries(chats).slice(0, 5)) {
                console.log(`  - ${chat.subject}`);
            }

            console.log('\nSession saved to ./whatsapp_session');
            console.log('You can close the script (Ctrl+C)');
        }

        if (connection === 'close') {
            console.log('Disconnected');
        }
    });
}

main();
```

Run:
```bash
node whatsapp_login.js
```

Scan the QR code in WhatsApp on your phone.

---

## Step 4: Add to .gitignore

```
whatsapp_session/
node_modules/
```

---

## Usage

After authorization, ask your AI assistant:

> "Show last messages from group [name]"

> "Find chat with [contact name]"

> "How many unread messages?"

---

## Code Examples

### List Chats

```javascript
const chats = await sock.groupFetchAllParticipating();

for (const [jid, chat] of Object.entries(chats)) {
    console.log(`${chat.subject} (${jid})`);
}
```

### Read Messages

```javascript
sock.ev.on('messages.upsert', async (m) => {
    const msg = m.messages[0];
    if (!msg.key.fromMe) {
        console.log(`From: ${msg.pushName}`);
        console.log(`Text: ${msg.message?.conversation}`);
    }
});
```

### Send Message (use carefully!)

```javascript
// Only for existing contacts!
await sock.sendMessage('1234567890@s.whatsapp.net', {
    text: 'Hello!'
});
```

---

## Rate Limits and Safety

| Parameter | Recommendation |
|-----------|----------------|
| New contacts | Do NOT message first |
| Messages per day | < 50 |
| Delay between messages | 10+ seconds |
| Mass messaging | Prohibited |

**Violating limits = account ban!**

---

## Troubleshooting

### QR code doesn't scan
- Make sure WhatsApp on your phone is up to date
- Try deleting `whatsapp_session/` and start over

### "Connection closed"
- Check internet on your phone
- WhatsApp on your phone must be active

### "Logged out"
- Session expired
- Delete `whatsapp_session/` and re-authorize

### Messages won't send
- Check number format: `1234567890@s.whatsapp.net`
- Contact must be in your phone book

---

## Alternative: WhatsApp Business API

For serious business use, consider the official API:
- https://business.whatsapp.com/products/business-platform

Pros:
- Official, no ban risk
- Higher limits
- Message templates

Cons:
- Paid
- Requires business verification

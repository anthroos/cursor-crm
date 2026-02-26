# Telegram Remote Control

Control your IDE from your phone via a Telegram bot.

## What You Get

- Send prompts to your IDE from your phone
- Take screenshots of IDE state
- Accept/reject changes
- Scroll up/down

---

## Step 1: Create a Telegram Bot

1. Open Telegram and find **@BotFather**
2. Send `/newbot`
3. Enter a name: `Cursor Remote` (or your own)
4. Enter a username: `cursor_remote_yourname_bot`
5. Copy the **token** (looks like `8056197506:AAHz...`)

---

## Step 2: Find Your Telegram ID

1. Open Telegram and find **@userinfobot**
2. Press Start
3. Copy your **Id** (a number like `394755411`)

---

## Step 3: Install cursor-remote

```bash
git clone https://github.com/anthroos/cursor-remote.git
cd cursor-remote
pip3 install -r requirements.txt
```

---

## Step 4: Create .env File

```bash
# .env
TELEGRAM_BOT_TOKEN=8056197506:AAHz...your_token...
ALLOWED_USER_ID=394755411
```

`ALLOWED_USER_ID` ensures only you can control the bot!

---

## Step 5: Grant macOS Permissions

**Required!** Without this, the bot cannot control your IDE.

1. **System Settings** > **Privacy & Security** > **Accessibility**
2. Click **+**
3. Add **Terminal** (or iTerm)
4. Make sure the checkbox is enabled

---

## Step 6: Start

```bash
python3 examples/run_telegram.py
```

Should show:
```
[INFO] Starting Cursor Remote Bot (Telegram)...
[INFO] Bot is running!
```

---

## Bot Commands

| Command | What it does |
|---------|-------------|
| `/screen` | Screenshot of IDE |
| `/up` | Scroll up + screenshot |
| `/down` | Scroll down + screenshot |
| `/accept` | Accept changes (Cmd+Enter) |
| `/reject` | Reject changes (Cmd+Backspace) |
| `/stop` | Stop (Escape) |
| `/mode` | Switch Agent/Ask mode |
| `any text` | Send as prompt |

---

## Example Workflow

1. Open your IDE on your computer
2. Open the bot in Telegram on your phone
3. Type: `Create a hello world function`
4. IDE starts generating code
5. Send `/screen` to see the result
6. Send `/accept` to accept

---

## Quick Start (alias)

Add to `~/.zshrc`:

```bash
alias cursor-bot="cd ~/cursor-remote && python3 examples/run_telegram.py"
```

Then just:
```bash
cursor-bot
```

---

## Troubleshooting

### Bot doesn't respond
- Check that your IDE is running
- Check that Terminal has Accessibility permission

### "Conflict: terminated by other getUpdates"
- Another instance of the bot is already running
- Stop it: `pkill -f run_telegram.py`

### Screenshot doesn't arrive
- Check Accessibility permission
- Restart Terminal

# Integrations

Connect messaging platforms and email to your CRM -- read messages, send outreach, manage contacts from your IDE.

## Available Integrations

| Integration | What it does | Difficulty |
|-------------|-------------|------------|
| [Telegram API](telegram_api.md) | Read/send messages, manage groups | Medium |
| [Telegram Remote](telegram_remote.md) | Control your IDE from your phone | Easy |
| [Gmail](gmail.md) | Read emails, search messages | Medium |
| [WhatsApp](whatsapp.md) | Read chats and groups | Hard |
| [LinkedIn](linkedin.md) | Connection management, messaging | Manual |
| [MCP Agents](mcp-agents.md) | Agent-to-agent communication via MCP | Medium |
| [plaintext-pm](plaintext-pm.md) | Project management integration | Easy |

---

## Prerequisites

1. **Python 3.10+**
2. **Claude Code** or **Cursor IDE** with CRM configured
3. **API keys** (you create them yourself -- instructions in each guide)

---

## Quick Start

### I want to read Telegram
-> [telegram_api.md](telegram_api.md)

### I want to control my IDE from my phone
-> [telegram_remote.md](telegram_remote.md)

### I want to see emails in CRM
-> [gmail.md](gmail.md)

### I want to read WhatsApp
-> [whatsapp.md](whatsapp.md)

### I want to track LinkedIn connections
-> [linkedin.md](linkedin.md)

### I want to connect with AI agents
-> [mcp-agents.md](mcp-agents.md)

### I want project management
-> [plaintext-pm.md](plaintext-pm.md)

---

## Security

**Never commit API keys to git!**

Store all keys in `.env` files. Add to `.gitignore`:

```
.env
*.session
token.json
credentials.json
```

---

## File Structure After Setup

```
your-project/
├── .env                     <- API keys (DO NOT commit!)
├── telegram_session.session  <- Telegram session
├── token.json                <- Gmail token
└── credentials.json          <- Gmail OAuth credentials
```

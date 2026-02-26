# MCP Agent Integration

Connect with AI agents through the Model Context Protocol (MCP) -- the machine-to-machine equivalent of email or phone.

## What You Get

- Store MCP endpoint URLs in your CRM contacts (companies + people)
- Discover AI agent capabilities via `/.well-known/agent.json`
- Call agent tools directly (scheduling, queries, support, etc.)
- Log agent interactions as CRM activities (channel: `mcp`)
- Treat AI agents as first-class CRM contacts

---

## How It Works

MCP (Model Context Protocol) lets AI agents call each other's tools over HTTP. Think of it as an API that your AI assistant can discover and use automatically.

```
Your CRM Contact          Agent Discovery              MCP Tools
┌──────────────┐    ┌──────────────────────┐    ┌──────────────────┐
│ Acme Corp    │    │ GET /.well-known/    │    │ get_services()   │
│ mcp_url: ... │───>│     agent.json       │───>│ book_meeting()   │
│              │    │                      │    │ check_status()   │
└──────────────┘    └──────────────────────┘    └──────────────────┘
```

### The flow

1. A company or person publishes an MCP endpoint (e.g., `https://schedule.example.com/mcp/`)
2. They publish `/.well-known/agent.json` describing their agent's capabilities
3. You store their `mcp_url` in your CRM
4. Your AI assistant connects to their MCP server
5. Their tools become available -- book meetings, ask questions, check availability, etc.

### What is agent.json?

A JSON file at `/.well-known/agent.json` that describes an agent:

```json
{
  "schema_version": "0.1",
  "name": "Scheduling Agent",
  "description": "Book meetings and check availability",
  "url": "https://schedule.example.com",
  "capabilities": {
    "scheduling": {
      "url": "https://schedule.example.com/mcp/",
      "transport": "streamable-http",
      "tools": [
        "get_available_slots",
        "book_consultation",
        "cancel_booking"
      ]
    }
  }
}
```

---

## Setup

### 1. Store mcp_url in Contacts

When a contact has an AI agent, add their MCP endpoint URL to the CRM.

**For a company** (`companies.csv`):
```
company_id,name,website,...,mcp_url
comp-acme,Acme Corp,https://acme.com,...,https://schedule.acme.com/mcp/
```

**For a person** (`people.csv`):
```
person_id,first_name,last_name,...,mcp_url
p-acme-1,John,Smith,...,https://john-agent.example.com/mcp/
```

The `mcp_url` field must be a valid URL ending with `/` (trailing slash).

### 2. Register the MCP Server in Claude Code

```bash
claude mcp add acme-schedule --transport http https://schedule.acme.com/mcp/
```

Or for Cursor IDE, add to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "acme-schedule": {
      "url": "https://schedule.acme.com/mcp/"
    }
  }
}
```

### 3. Restart Your Session

MCP servers are loaded at session start. After adding a new one, restart Claude Code or Cursor to make the tools available.

---

## Workflow

### Discovering an Agent

1. Someone shares their agent URL: `https://schedule.example.com`
2. Check their discovery endpoint:
   ```
   GET https://schedule.example.com/.well-known/agent.json
   ```
3. Review capabilities and available tools
4. Add `mcp_url` to their CRM record
5. Register as MCP server in your IDE
6. Restart session -- tools are now available

### Using Agent Tools

Once registered, interact naturally:

```
You: "Check John's scheduling agent for available meeting slots"
AI:  [calls get_available_slots() via MCP] "John has these open slots: ..."

You: "Book the Tuesday 2pm slot"
AI:  [calls book_consultation() via MCP] "Meeting booked. Google Meet link: ..."
```

### Logging Agent Interactions

After any MCP interaction, log it as a CRM activity:

```
activity_id,person_id,company_id,type,channel,direction,subject,notes,date,created_by
act-042,p-acme-1,comp-acme,meeting,mcp,outbound,Booked via MCP agent,Used scheduling agent to book 30min call,2026-02-26,ai
```

Key fields:
- **channel**: `mcp`
- **type**: depends on what happened (`meeting` for bookings, `message` for queries)
- **direction**: `outbound` when you call their agent, `inbound` when they call yours

---

## Common Commands

```
"Check if Acme has an MCP agent"
"Show all contacts with MCP endpoints"
"Book a meeting with John through his scheduling agent"
"Add MCP URL https://schedule.example.com/mcp/ to Acme's company record"
"What tools does Acme's agent provide?"
"Log the MCP booking as a CRM activity"
```

---

## Advanced: Publishing Your Own Agent

To make yourself discoverable by other agents, you need:

1. **An MCP server** exposing your tools (scheduling, support, etc.)
2. **A `/.well-known/agent.json`** file for discovery
3. **A public URL** where your agent is hosted

### Example: Open Schedule Agent

[Open Schedule Agent](https://github.com/anthroos/open-schedule-agent) is an open-source scheduling bot that:
- Exposes MCP tools for booking meetings
- Serves `/.well-known/agent.json` for auto-discovery
- Integrates with Google Calendar
- Handles timezone conversion automatically

### Minimal agent.json

```json
{
  "schema_version": "0.1",
  "name": "Your Agent Name",
  "description": "What your agent does",
  "url": "https://your-agent.example.com",
  "capabilities": {
    "your_capability": {
      "url": "https://your-agent.example.com/mcp/",
      "transport": "streamable-http",
      "tools": ["tool_1", "tool_2"]
    }
  }
}
```

### Hosting Options

Deploy your MCP server on any platform that supports Python/Node.js:
- [Railway](https://railway.app)
- [Fly.io](https://fly.io)
- [Render](https://render.com)
- Self-hosted on VPS

---

## Tips

- **mcp_url as capability signal** -- if a contact has `mcp_url` set, their AI agent can be reached programmatically. Prioritize MCP for automated interactions over manual channels.
- **Multi-channel coordination** -- use MCP for scheduling and data exchange, email for proposals, Telegram for quick follow-ups
- **Agent discovery first** -- always check `/.well-known/agent.json` before adding `mcp_url` to verify the endpoint is live and see available tools
- **Trailing slash** -- MCP URLs must end with `/`
- **Session restart required** -- after `claude mcp add`, restart your IDE session for tools to appear
- **One slug per agent** -- use a descriptive slug like `acme-schedule` or `john-calendar`

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Tools not appearing after add | Restart Claude Code / Cursor session |
| Connection refused | Check URL is correct and ends with `/` |
| agent.json not found | Verify `/.well-known/agent.json` is accessible (try in browser) |
| "Unknown tool" error | The tool name may have changed -- re-check agent.json |
| Timeout on tool call | Agent server may be down or slow -- check status |
| MCP URL returns 404 | Ensure URL path is correct (usually `/mcp/` not `/mcp`) |

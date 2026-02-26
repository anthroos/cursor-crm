# Cursor CRM

**AI-native CRM that runs in your IDE.** No SaaS, no dashboards -- just talk to your sales data.

Built for founders and developers who close deals from their IDE. Works with [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview) and [Cursor](https://cursor.sh) IDE.

## Why Cursor CRM?

| Traditional CRM | Cursor CRM |
|-----------------|------------|
| Click through 10 screens to log a call | Say "log call with John, he's interested" |
| Export to CSV to analyze | Ask "which leads are closing this month?" |
| Pay $50-500/month | Free, runs locally |
| Data locked in vendor | Your data, your files, your git |
| Learn complex UI | Just talk to AI |

## What You Get

- **Companies & Contacts** -- universal contact database with relationships
- **Products** -- define your offerings (services, reseller, community)
- **Sales pipeline** -- leads with stages from new to won/lost
- **Client management** -- active clients, contracts, MRR tracking
- **Partner tracking** -- partnerships with revenue share
- **Deal tracking** -- from proposal to paid with invoice tracking
- **Activity log** -- every call, email, message logged
- **Machine-readable schema** -- schema.yaml for automated validation
- **Integrations** -- Telegram, Gmail, WhatsApp, LinkedIn
- **Skills framework** -- optional advanced automation via [claude-skills](https://github.com/anthroos/claude-skills)

## Quick Start

```bash
# 1. Clone
git clone https://github.com/anthroos/cursor-crm.git
cd cursor-crm

# 2. Install dependencies
pip3 install pandas pyyaml

# 3. Open in your IDE
claude   # Claude Code
# or: cursor .

# 4. Configure
# Edit CLAUDE.md -- replace [YOUR_COMPANY_NAME] etc.

# 5. Start using
# "Add company Acme Inc, they just raised Series A"
# "Find the CEO and add as contact"
# "Create a lead for our data labeling service"
```

## Project Structure

```
cursor-crm/
├── CLAUDE.md                      # AI rules (schema, skills, validation)
├── sales/
│   ├── crm/
│   │   ├── contacts/
│   │   │   ├── companies.csv      # All companies
│   │   │   └── people.csv         # All contacts
│   │   ├── products.csv           # Your products/services
│   │   ├── relationships/
│   │   │   ├── leads.csv          # Sales pipeline
│   │   │   ├── clients.csv        # Active clients
│   │   │   ├── partners.csv       # Partner relationships
│   │   │   └── deals.csv          # Deal & invoice tracking
│   │   ├── activities.csv         # All communications
│   │   └── schema.yaml            # Machine-readable validation
│   └── outreach/
│       └── OUTREACH_PROMPT.md     # Message templates
├── docs/
│   ├── SCHEMA.md                  # Field definitions
│   ├── WORKFLOW.md                # Daily workflow
│   └── CRM_FLOW_DIAGRAM.md       # System diagram
├── integrations/
│   ├── telegram_api.md
│   ├── gmail.md
│   ├── whatsapp.md
│   ├── linkedin.md
│   ├── telegram_remote.md
│   └── cursor-pm.md              # PM integration guide
└── scripts/
    └── validate_csv.py            # Data validation
```

## Data Model

```
Companies <--- People
    |              |
    +-- Leads      | (via primary_contact_id)
    +-- Clients ---+
    +-- Partners   |
    |      |
    |   Deals (proposal -> paid)
    |
    +-- Activities -- People
```

**Key design decisions:**
- Contacts (companies + people) are universal -- they exist once
- Relationships (leads, clients, partners) track how you interact with them per product
- One company can be a client for product A and a lead for product B

## Sample Data

The CSV files come pre-populated with realistic fictional data (6 companies, 8 people, 4 leads, 2 clients, 1 partner, 3 deals, 8 activities). Explore it to see how the data model works before adding your own.

## Key Concepts

### Lead Pipeline

```
new -> qualified -> proposal -> negotiation -> won / lost
```

When a lead is `won`, convert to a client record.

### Deal Lifecycle

```
proposal -> negotiation -> won -> in_progress -> delivered -> invoiced -> paid
```

Track delivery, invoicing, and payment in one table.

### Activity Tracking

Log every touchpoint:
- Type: call / email / meeting / message / note
- Channel: email / telegram / whatsapp / phone / in_person / linkedin
- Direction: inbound / outbound

## Common Commands

### Find leads
```
"Show hot leads"
"What leads need follow-up today?"
"Find all qualified leads for data labeling"
```

### Manage pipeline
```
"Add lead for Acme Corp -- interested in our AI service"
"Move lead-001 to proposal stage"
"Convert lead to client -- they signed the contract"
```

### Track deals
```
"Create deal for Acme pilot -- $5000 USD"
"Mark deal-001 as delivered"
"Generate invoice for deal-001"
```

### Log activities
```
"Log call with John -- discussed pricing, will follow up Friday"
"Log email sent to Jane with proposal"
"Show all activities with Acme this month"
```

## Ecosystem

Cursor CRM is part of a three-repo system. Each works standalone, together they form a complete business operating system:

| Repo | Purpose |
|------|---------|
| **cursor-crm** (this repo) | CRM: contacts, leads, deals, activities |
| [cursor-pm](https://github.com/anthroos/cursor-pm) | Project & task management |
| [claude-skills](https://github.com/anthroos/claude-skills) | Skills framework, agents, multi-channel automation |

### Integration with cursor-pm

For project and task management, pair with [cursor-pm](https://github.com/anthroos/cursor-pm):
- Link PM projects to CRM companies/deals
- Link tasks to specific contacts
- Daily briefing combines PM tasks and CRM follow-ups

See [integrations/cursor-pm.md](integrations/cursor-pm.md) for setup.

### Integration with claude-skills

For advanced automation:
- Multi-channel outreach (Telegram, Email, WhatsApp)
- Automated lead enrichment and import pipelines
- Scheduled CRM reporting and follow-up reminders

See [claude-skills](https://github.com/anthroos/claude-skills) for the full skills framework.

## Integrations

| Integration | What it does | Guide |
|-------------|--------------|-------|
| Telegram API | Read/send messages, manage groups | [Setup](integrations/telegram_api.md) |
| Telegram Remote | Control your IDE from your phone | [Setup](integrations/telegram_remote.md) |
| Gmail | Search emails, read threads | [Setup](integrations/gmail.md) |
| WhatsApp | Read chats via Baileys | [Setup](integrations/whatsapp.md) |
| LinkedIn | Connection management, messaging | [Setup](integrations/linkedin.md) |

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview) or [Cursor IDE](https://cursor.sh)
- Python 3.10+
- pandas, pyyaml (`pip3 install pandas pyyaml`)

## Philosophy

1. **Your data stays yours** -- CSV files, version controlled, no vendor lock-in
2. **AI does the work** -- research, draft, log, analyze
3. **Simple beats complex** -- if you need Salesforce, this isn't for you
4. **Schema-first** -- machine-readable validation prevents bad data

## Who This Is For

- Solo founders doing outreach
- Small teams (1-5) without dedicated sales ops
- Developers who live in their IDE
- Anyone tired of bloated CRM software

## Migrating from v1

If you used the previous version with `.cursorrules`, the change is simple: rename it to `CLAUDE.md` or copy the new one from this repo. Your CSV data is fully compatible.

## License

MIT

## Credits

Built by [@anthroos](https://github.com/anthroos) at [WeLabelData](https://welabeldata.com).

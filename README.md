# Plaintext CRM

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/anthroos/plaintext-crm)](https://github.com/anthroos/plaintext-crm/stargazers)
[![Works with Claude Code](https://img.shields.io/badge/Works%20with-Claude%20Code-blueviolet)](https://docs.anthropic.com/en/docs/claude-code/overview)
[![Works with Cursor](https://img.shields.io/badge/Works%20with-Cursor-orange)](https://cursor.sh)

**AI-native CRM that runs in your IDE.** No SaaS, no dashboards -- just talk to your sales data.

```
You: "Add company Stripe, fintech, SF. CEO is Patrick Collison."
AI:  Done. Created comp-stripe + p-stripe-001 (Patrick Collison, CEO).

You: "Create a lead for our consulting service, $10k estimated"
AI:  Created lead-stripe-001, stage: new, $10,000 USD.

You: "Log call with Patrick -- discussed pilot, sending proposal Friday"
AI:  Logged activity. Set next_action: "Send proposal", next_action_date: 2026-03-07.
```

---

## Why Plaintext CRM?

| Traditional CRM | Plaintext CRM |
|-----------------|------------|
| Click through 10 screens to log a call | Say "log call with John, he's interested" |
| Export to CSV to analyze | Ask "which leads are closing this month?" |
| Pay $50-500/month | Free, open source |
| Data locked in vendor | Git-controlled CSV files you own |
| Learn complex UI | Just talk to AI |
| Needs internet | Works offline |

## Quick Start

```bash
# 1. Clone
git clone https://github.com/anthroos/plaintext-crm.git
cd plaintext-crm

# 2. Install
pip3 install pandas pyyaml

# 3. Open in your AI IDE
claude                    # Claude Code
# or: cursor .           # Cursor IDE

# 4. Start using -- just talk
"Add company Acme Inc, Series A startup in SF"
"Show my hot leads"
"What needs follow-up today?"
```

That's it. The AI reads `CLAUDE.md` and understands the full CRM schema, validation rules, and available operations.

## What You Get

- **Companies & Contacts** -- universal contact database with relationships
- **Products** -- define your offerings (services, reseller, community)
- **Sales pipeline** -- leads with stages: `new -> qualified -> proposal -> negotiation -> won / lost`
- **Client management** -- active clients, contracts, MRR tracking
- **Partner tracking** -- partnerships with revenue share
- **Deal tracking** -- from proposal to paid with invoice tracking
- **Activity log** -- every call, email, message logged with direction and channel
- **Schema validation** -- `schema.yaml` + `validate_csv.py` prevent bad data
- **CSV injection protection** -- safe against formula injection attacks

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
- Relationships (leads, clients, partners) track how you interact per product
- One company can be a client for product A and a lead for product B

## Project Structure

```
plaintext-crm/
├── CLAUDE.md                      # AI context (schema, skills, rules)
├── sales/crm/
│   ├── contacts/
│   │   ├── companies.csv          # All companies
│   │   └── people.csv             # All contacts
│   ├── products.csv               # Your products/services
│   ├── relationships/
│   │   ├── leads.csv              # Sales pipeline
│   │   ├── clients.csv            # Active clients
│   │   ├── partners.csv           # Partner relationships
│   │   └── deals.csv              # Deal & invoice tracking
│   ├── activities.csv             # All communications
│   └── schema.yaml                # Machine-readable validation
├── docs/
│   ├── SCHEMA.md                  # Field definitions
│   └── WORKFLOW.md                # Daily workflow
├── integrations/                  # Channel setup guides
│   ├── telegram_api.md
│   ├── gmail.md
│   ├── whatsapp.md
│   └── linkedin.md
└── scripts/
    └── validate_csv.py            # Data validation & integrity checks
```

## Common Commands

### Manage contacts
```
"Add company Acme Inc, SaaS, New York"
"Add John Doe as CTO at Acme, john@acme.com"
"Find all contacts at Deutsche Telekom"
```

### Sales pipeline
```
"Show hot leads"
"What leads need follow-up today?"
"Move lead-001 to proposal stage"
"Convert lead to client -- they signed"
```

### Track deals
```
"Create deal for Acme pilot -- $5000 USD"
"Mark deal-001 as delivered"
"Generate invoice for deal-001"
```

### Log activities
```
"Log call with John -- discussed pricing, follow up Friday"
"Log email sent to Jane with proposal"
"Show all activities with Acme this month"
```

### Analytics
```
"What's our total MRR?"
"Which leads have been in 'qualified' stage for over 2 weeks?"
"Show activity breakdown by channel this month"
```

## Validation

Run the validation script to check data integrity:

```bash
python3 scripts/validate_csv.py
```

Checks: required fields, foreign key references, enum values, unique IDs, date formats, CSV injection prevention.

```bash
python3 scripts/validate_csv.py --fix  # Auto-fix missing last_updated
```

## Ecosystem

Plaintext CRM works standalone. For a complete business OS, pair with:

| Repo | Purpose | Stars |
|------|---------|-------|
| **plaintext-crm** (this) | CRM: contacts, leads, deals, activities | ![GitHub stars](https://img.shields.io/github/stars/anthroos/plaintext-crm?style=flat) |
| [plaintext-pm](https://github.com/anthroos/plaintext-pm) | Project & task management | ![GitHub stars](https://img.shields.io/github/stars/anthroos/plaintext-pm?style=flat) |
| [claude-code-review-skill](https://github.com/anthroos/claude-code-review-skill) | AI code review (280+ checks) | ![GitHub stars](https://img.shields.io/github/stars/anthroos/claude-code-review-skill?style=flat) |

## Integrations

| Channel | What it does | Guide |
|---------|--------------|-------|
| Telegram | Read/send messages, manage groups | [Setup](integrations/telegram_api.md) |
| Gmail | Search emails, read threads | [Setup](integrations/gmail.md) |
| WhatsApp | Read chats via Baileys | [Setup](integrations/whatsapp.md) |
| LinkedIn | Connection management, messaging | [Setup](integrations/linkedin.md) |

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview) or [Cursor IDE](https://cursor.sh)
- Python 3.10+
- `pip3 install pandas pyyaml`

## Philosophy

1. **Your data stays yours** -- CSV files, version controlled, no vendor lock-in
2. **AI does the work** -- research, draft, log, analyze
3. **Simple beats complex** -- if you need Salesforce, this isn't for you
4. **Schema-first** -- machine-readable validation prevents bad data

## Who This Is For

- Solo founders doing sales from their IDE
- Small teams (1-5) without dedicated sales ops
- Developers who hate context-switching to browser CRM
- Anyone who thinks CRM should be a conversation, not a dashboard

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT

## Credits

Built by [@anthroos](https://github.com/anthroos) at [WeLabelData](https://welabeldata.com).

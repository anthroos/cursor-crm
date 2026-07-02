# Integration with plaintext-pm

## Overview

Plaintext CRM handles sales, contacts, and outreach. For project and task management, pair it with [plaintext-pm](https://github.com/anthroos/plaintext-pm).

## How It Works

PM projects and tasks can reference CRM entities:

- **Project -> Company**: `crm_link_type: company, crm_link_id: comp-acme`
- **Task -> Person**: `crm_person_linkedin_url: https://linkedin.com/in/john`
- **Task -> Activity**: `crm_activity_id: act-001`

## Setup

Clone both repos side by side:

```bash
git clone https://github.com/anthroos/plaintext-crm.git
git clone https://github.com/anthroos/plaintext-pm.git
```

In plaintext-pm `CLAUDE.md`, set:
```
CRM_INTEGRATION: true
CRM_PATH: ../plaintext-crm/sales/crm
```

For advanced automation (multi-channel outreach, scheduled follow-ups, agent workflows), see [claude-skills](https://github.com/anthroos/claude-skills).

See [plaintext-pm/integrations/plaintext-crm.md](https://github.com/anthroos/plaintext-pm/blob/main/integrations/plaintext-crm.md) for full details.

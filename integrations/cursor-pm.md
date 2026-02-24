# Integration with cursor-pm

## Overview

Cursor CRM handles sales, contacts, and outreach. For project and task management, pair it with [cursor-pm](https://github.com/anthroos/cursor-pm).

## How It Works

PM projects and tasks can reference CRM entities:

- **Project -> Company**: `crm_link_type: company, crm_link_id: comp-acme`
- **Task -> Person**: `crm_person_linkedin_url: https://linkedin.com/in/john`
- **Task -> Activity**: `crm_activity_id: act-001`

## Setup

Clone both repos side by side:

```bash
git clone https://github.com/anthroos/cursor-crm.git
git clone https://github.com/anthroos/cursor-pm.git
```

In cursor-pm `.cursorrules`, set:
```
CRM_INTEGRATION: true
CRM_PATH: ../cursor-crm/sales/crm
```

See [cursor-pm/integrations/cursor-crm.md](https://github.com/anthroos/cursor-pm/blob/main/integrations/cursor-crm.md) for full details.

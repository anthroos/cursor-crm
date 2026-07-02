# Daily CRM Workflow

## Morning Routine (15 min)

### 1. Check Follow-ups

Ask your AI assistant:

> "Show leads where next_action_date is today"
> "Who needs follow-up this week?"

Or query directly:
```python
import pandas as pd
from datetime import date

leads = pd.read_csv('sales/crm/relationships/leads.csv')
today = str(date.today())
due = leads[leads['next_action_date'] <= today]
print(due[['lead_id', 'company_id', 'next_action', 'next_action_date']])
```

### 2. Check Pipeline

> "Show all leads by stage"
> "What's in negotiation right now?"

### 3. Check Deals

> "Any deals waiting for invoice?"
> "What's been delivered but not invoiced?"

---

## Adding New Contacts

### Step 1: Add Company

> "Add company Acme Inc, AI startup, based in San Francisco"

What happens:
1. Check for duplicates by website
2. Generate `company_id` (format: `comp-xxx`)
3. Add to `contacts/companies.csv`
4. Set `created_date` and `last_updated`

### Step 2: Add People

> "Add John Smith, CEO at Acme, email john@acme.com"

What happens:
1. Check for duplicates by email/LinkedIn
2. Generate `person_id` (format: `p-xxx-N`)
3. Verify `company_id` exists
4. Ensure email OR phone OR telegram_username
5. Add to `contacts/people.csv`

---

## Lead Management

### Creating a Lead

> "Create lead for Acme -- interested in our data labeling service"

What happens:
1. Verify company exists (or create first)
2. Verify product exists
3. Generate `lead_id` (format: `lead-xxx-N`)
4. Set `stage = new`, link company and product
5. Add to `relationships/leads.csv`

### Lead Pipeline

```
new -> qualified -> proposal -> negotiation -> won / lost
```

### Qualifying a Lead

Before moving to "qualified":
1. Check company website
2. Check LinkedIn profiles
3. Look for signals (funding, hiring, product launches)
4. Update lead notes with findings
5. Set priority (low / medium / high / critical)

> "Move lead-acme-1 to qualified, they just raised Series A"

### Converting a Lead

When a lead is won:
1. Update lead stage to "won"
2. Create client record in `clients.csv`
3. Create deal record in `deals.csv`
4. Link primary contact

> "Convert lead-acme-1 to client -- they signed the contract, $5000/mo"

---

## Activity Tracking

### Log Every Touchpoint

> "Log call with John at Acme -- discussed pricing, will follow up Friday"

What gets recorded in `activities.csv`:
- **type**: call / email / meeting / message / note
- **channel**: email / telegram / whatsapp / phone / in_person / linkedin
- **direction**: inbound / outbound
- **subject** and **notes**

After logging:
1. Person's `last_contact` is updated
2. Lead's `next_action_date` is updated if relevant

---

## Outreach Flow

### Step 1: Check History

> "What's the conversation history with John at Acme?"

### Step 2: Draft Message

Use `sales/outreach/OUTREACH_PROMPT.md` template.

Key principles:
- Equal to equal -- business partners, not begging
- Specific hypothesis about their problem
- Direct question -- ask if problem is relevant
- Easy out -- let them say no gracefully

### Step 3: Send & Log

After sending, log the activity:

> "Log email sent to John with pricing proposal"

---

## Deal Tracking

### Deal Lifecycle

```
proposal -> negotiation -> won -> in_progress -> delivered -> invoiced -> paid
```

### Common Actions

> "Create deal for Acme pilot -- $5000 USD"
> "Mark deal-acme-1 as delivered"
> "Invoice deal-acme-1, invoice number INV-2026-001"
> "Mark deal-acme-1 as paid, received $5000"

---

## Client Management

### Active Clients

> "Show all active clients"
> "What's our total MRR?"
> "Which clients have contracts ending this month?"

### Client Statuses

```
active / paused / churned
```

---

## Weekly Review (30 min)

### 1. Pipeline Review

> "Show pipeline summary -- how many leads per stage?"
> "What moved this week?"

### 2. Revenue Check

> "What's total MRR from active clients?"
> "Any deals waiting for payment?"
> "Show unpaid invoices"

### 3. Activity Summary

> "How many activities this week?"
> "Who haven't I contacted in 2 weeks?"

### 4. Clean Up

- Update stale leads (move to lost if no response)
- Update next_action_date for active leads
- Verify all recent activities are logged

---

## Validation

Always validate before committing:

```bash
python3 scripts/validate_csv.py
```

Auto-fix missing `last_updated` fields:

```bash
python3 scripts/validate_csv.py --fix
```

---

## Common Queries

### Finding Leads
- "Show hot leads"
- "Find all qualified leads for [product]"
- "What leads need follow-up today?"

### Pipeline Analysis
- "Count leads by stage"
- "Show leads by priority"
- "What's the estimated pipeline value?"

### Client Queries
- "Show active clients sorted by MRR"
- "Which clients are up for renewal?"

### Activity Queries
- "Show all activities with Acme this month"
- "What was my last contact with John?"
- "How many meetings this week?"

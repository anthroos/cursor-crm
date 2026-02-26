# CRM Schema Reference

Full machine-readable schema: `sales/crm/schema.yaml`

## Overview

| Table | File | Primary Key | Description |
|-------|------|-------------|-------------|
| Companies | contacts/companies.csv | company_id | All companies |
| People | contacts/people.csv | person_id | All contacts |
| Products | products.csv | product_id | Your offerings |
| Leads | relationships/leads.csv | lead_id | Sales pipeline |
| Clients | relationships/clients.csv | client_id | Active clients |
| Partners | relationships/partners.csv | partner_id | Partner relationships |
| Deals | relationships/deals.csv | deal_id | Deal & invoice tracking |
| Activities | activities.csv | activity_id | All communications |

---

## Contacts

### companies.csv

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `company_id` | string | Yes | PK (format: comp-xxx) |
| `name` | string | Yes | Company name |
| `website` | string | No | Company website (unique if set) |
| `linkedin_url` | string | No | LinkedIn company page URL |
| `type` | enum | No | company / enterprise / ngo / individual |
| `industry` | string | No | Industry vertical |
| `geo` | string | No | Geographic location |
| `size` | enum | No | small / medium / enterprise / individual |
| `description` | string | No | Free-form description |
| `created_date` | YYYY-MM-DD | Yes | When record was created |
| `last_updated` | YYYY-MM-DD | Yes | When record was last modified |

### people.csv

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `person_id` | string | Yes | PK (format: p-xxx-N) |
| `first_name` | string | Yes | First name |
| `last_name` | string | No | Last name |
| `email` | string | No | Email address (unique if set) |
| `phone` | string | No | Phone number |
| `linkedin_url` | string | No | LinkedIn profile URL |
| `company_id` | string | No | FK to companies |
| `role` | string | No | Job title |
| `notes` | string | No | Free-form notes |
| `created_date` | YYYY-MM-DD | Yes | When record was created |
| `last_updated` | YYYY-MM-DD | Yes | When record was last modified |
| `telegram_username` | string | No | Telegram handle |
| `last_contact` | YYYY-MM-DD | No | Last contact date |

**Rule:** Must have at least one of: email, phone, or telegram_username.

---

## Products

### products.csv

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `product_id` | string | Yes | PK (format: prod-xxx) |
| `business_line` | string | Yes | Business unit |
| `name` | string | Yes | Product name |
| `type` | enum | Yes | service / reseller / community |
| `description` | string | No | Product description |
| `owner` | string | No | Product owner |
| `status` | enum | Yes | active / paused / discontinued |
| `created_date` | YYYY-MM-DD | Yes | When created |

---

## Relationships

### leads.csv

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `lead_id` | string | Yes | PK (format: lead-xxx-N) |
| `company_id` | string | Yes | FK to companies |
| `product_id` | string | Yes | FK to products |
| `stage` | enum | Yes | new / qualified / proposal / negotiation / won / lost |
| `source` | string | No | Lead source |
| `priority` | enum | No | low / medium / high / critical |
| `primary_contact_id` | string | No | FK to people |
| `estimated_value` | float | No | Expected deal value |
| `currency` | string | No | Currency code |
| `next_action` | string | No | What to do next |
| `next_action_date` | YYYY-MM-DD | No | When to do it |
| `notes` | string | No | Free-form notes |
| `created_date` | YYYY-MM-DD | Yes | When created |
| `last_updated` | YYYY-MM-DD | Yes | When modified |
| `last_contact_via_primary` | YYYY-MM-DD | No | Last contact via primary contact |

### clients.csv

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `client_id` | string | Yes | PK (format: cli-xxx-N) |
| `company_id` | string | Yes | FK to companies |
| `product_id` | string | Yes | FK to products |
| `status` | enum | Yes | active / paused / churned |
| `contract_start` | YYYY-MM-DD | No | Contract start date |
| `contract_end` | YYYY-MM-DD | No | Contract end date |
| `mrr` | float | No | Monthly recurring revenue |
| `currency` | string | No | Currency code |
| `primary_contact_id` | string | No | FK to people |
| `notes` | string | No | Free-form notes |
| `created_date` | YYYY-MM-DD | Yes | When created |
| `last_updated` | YYYY-MM-DD | Yes | When modified |
| `last_contact_via_primary` | YYYY-MM-DD | No | Last contact via primary contact |

### partners.csv

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `partner_id` | string | Yes | PK (format: ptnr-xxx-N) |
| `company_id` | string | Yes | FK to companies |
| `product_id` | string | Yes | FK to products |
| `partnership_type` | enum | Yes | training_partner / workforce_partner / reseller_agreement / referral_partner |
| `status` | enum | Yes | active / paused / ended |
| `since` | YYYY-MM-DD | No | Partnership start date |
| `primary_contact_id` | string | No | FK to people |
| `revenue_share` | string | No | Revenue share terms |
| `notes` | string | No | Free-form notes |
| `created_date` | YYYY-MM-DD | Yes | When created |
| `last_updated` | YYYY-MM-DD | Yes | When modified |

### deals.csv

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `deal_id` | string | Yes | PK (format: deal-xxx-N) |
| `client_id` | string | Yes | FK to clients |
| `name` | string | Yes | Deal description |
| `value` | float | Yes | Deal value |
| `currency` | enum | Yes | USD / EUR / GBP / CAD / AUD / CHF / JPY / SGD / PLN / UAH / SEK / INR / BRL |
| `stage` | enum | Yes | proposal / negotiation / won / in_progress / delivered / invoiced / paid / lost |
| `created_date` | YYYY-MM-DD | Yes | When created |
| `delivered_date` | YYYY-MM-DD | No | When delivered |
| `invoice_date` | YYYY-MM-DD | No | When invoiced |
| `invoice_number` | string | No | Invoice reference |
| `paid_date` | YYYY-MM-DD | No | When paid |
| `paid_amount` | float | No | Amount received |
| `notes` | string | No | Free-form notes |

**Rule:** If stage = "paid", invoice_date must be set.

---

## Activities

### activities.csv

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `activity_id` | string | Yes | PK |
| `person_id` | string | No | FK to people |
| `company_id` | string | No | FK to companies |
| `product_id` | string | No | FK to products |
| `type` | enum | Yes | call / email / meeting / message / note |
| `channel` | enum | Yes | email / telegram / whatsapp / phone / in_person / linkedin |
| `direction` | enum | No | inbound / outbound |
| `subject` | string | No | Short description |
| `notes` | string | No | Detailed notes |
| `date` | YYYY-MM-DD | Yes | When it happened |
| `created_by` | string | Yes | Who logged it |

---

## Pipeline Stages

### Lead Pipeline
```
new -> qualified -> proposal -> negotiation -> won / lost
```

### Deal Lifecycle
```
proposal -> negotiation -> won -> in_progress -> delivered -> invoiced -> paid
                                                                      ↘ lost
```

---

## Validation Rules

See `sales/crm/schema.yaml` for machine-readable rules.

### Before adding a Company:
- [ ] company_id is unique
- [ ] name is not empty
- [ ] Set created_date and last_updated to today

### Before adding a Person:
- [ ] person_id is unique
- [ ] first_name is not empty
- [ ] Has email OR phone OR telegram_username
- [ ] If company_id set, it must exist in companies
- [ ] Set created_date and last_updated to today

### Before adding a Lead:
- [ ] company_id exists in companies
- [ ] product_id exists in products
- [ ] stage is valid enum
- [ ] Set created_date and last_updated to today

### When updating any record:
- [ ] ALWAYS update last_updated to today
- [ ] Foreign keys must reference existing records
- [ ] Enum values must be valid

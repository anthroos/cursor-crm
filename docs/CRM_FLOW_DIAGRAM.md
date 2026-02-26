# CRM Flow -- System Map

## Overview

```mermaid
flowchart LR
    subgraph CONTACTS["Contacts"]
        C1[companies.csv]
        C2[people.csv]
    end

    subgraph PRODUCTS["Products"]
        P1[products.csv]
    end

    subgraph PIPELINE["Sales Pipeline"]
        L1[leads.csv]
        CL1[clients.csv]
        PT1[partners.csv]
        D1[deals.csv]
    end

    subgraph ACTIVITY["Activity Log"]
        A1[activities.csv]
    end

    subgraph CHANNELS["Channels"]
        CH1[Email]
        CH2[Telegram]
        CH3[WhatsApp]
        CH4[Phone]
        CH5[LinkedIn]
        CH6[In Person]
        CH7[MCP Agent]
    end

    %% Relationships
    C1 --> L1
    C1 --> CL1
    C1 --> PT1
    P1 --> L1
    P1 --> CL1
    P1 --> PT1
    C2 -->|primary_contact| L1
    C2 -->|primary_contact| CL1
    CL1 --> D1
    L1 -->|won| CL1
    CHANNELS --> A1
    A1 --> C2
    A1 --> C1
```

---

## Lead Pipeline

```mermaid
flowchart LR
    NEW[New] --> QUAL[Qualified]
    QUAL --> PROP[Proposal]
    PROP --> NEG[Negotiation]
    NEG --> WON[Won]
    NEG --> LOST[Lost]

    WON -->|convert| CLIENT[Client Record]
    WON -->|create| DEAL[Deal Record]

    style NEW fill:#e8f4fd
    style QUAL fill:#d4edda
    style PROP fill:#fff3cd
    style NEG fill:#ffeaa7
    style WON fill:#d4edda
    style LOST fill:#f8d7da
    style CLIENT fill:#d4edda
    style DEAL fill:#d4edda
```

---

## Deal Lifecycle

```mermaid
flowchart LR
    PROP[Proposal] --> NEG[Negotiation]
    NEG --> WON[Won]
    WON --> IP[In Progress]
    IP --> DEL[Delivered]
    DEL --> INV[Invoiced]
    INV --> PAID[Paid]
    NEG --> LOST[Lost]

    style PROP fill:#e8f4fd
    style NEG fill:#fff3cd
    style WON fill:#d4edda
    style IP fill:#d4edda
    style DEL fill:#d4edda
    style INV fill:#ffeaa7
    style PAID fill:#d4edda
    style LOST fill:#f8d7da
```

---

## Data Flow

```mermaid
flowchart TD
    subgraph INPUT["Input"]
        I1[Research / Referral / Inbound]
    end

    subgraph CONTACTS["Contacts Layer"]
        C1["companies.csv<br/>(company_id)"]
        C2["people.csv<br/>(person_id)"]
    end

    subgraph QUALIFY["Qualification"]
        Q1["products.csv<br/>(product_id)"]
        Q2["leads.csv<br/>(lead_id)"]
    end

    subgraph CONVERT["Conversion"]
        CV1["clients.csv<br/>(client_id)"]
        CV2["partners.csv<br/>(partner_id)"]
    end

    subgraph REVENUE["Revenue"]
        R1["deals.csv<br/>(deal_id)"]
    end

    subgraph LOG["Activity Log"]
        L1["activities.csv<br/>(activity_id)"]
    end

    INPUT --> CONTACTS
    C1 --> Q2
    C2 -->|primary_contact| Q2
    Q1 --> Q2
    Q2 -->|won| CV1
    Q2 -->|partnership| CV2
    CV1 --> R1
    CONTACTS <--> L1
    Q2 <-->|updates| L1

    style INPUT fill:#e8f4fd
    style REVENUE fill:#d4edda
```

---

## Activity Tracking Flow

```mermaid
flowchart TD
    TOUCH[Touchpoint occurs] --> TYPE{What type?}

    TYPE --> CALL[Call]
    TYPE --> EMAIL[Email]
    TYPE --> MEET[Meeting]
    TYPE --> MSG[Message]
    TYPE --> NOTE[Note]

    CALL --> LOG[Log to activities.csv]
    EMAIL --> LOG
    MEET --> LOG
    MSG --> LOG
    NOTE --> LOG

    LOG --> UPD1[Update person.last_contact]
    LOG --> UPD2[Update lead.next_action_date]
    LOG --> UPD3[Update last_updated on related records]
```

---

## File Map

```
sales/
├── crm/
│   ├── contacts/
│   │   ├── companies.csv        -- All companies (PK: company_id)
│   │   └── people.csv           -- All contacts (PK: person_id)
│   ├── products.csv             -- Products/services (PK: product_id)
│   ├── relationships/
│   │   ├── leads.csv            -- Sales pipeline (PK: lead_id)
│   │   ├── clients.csv          -- Active clients (PK: client_id)
│   │   ├── partners.csv         -- Partnerships (PK: partner_id)
│   │   └── deals.csv            -- Deals & invoices (PK: deal_id)
│   ├── activities.csv           -- All communications (PK: activity_id)
│   └── schema.yaml              -- Machine-readable validation rules
└── outreach/
    └── OUTREACH_PROMPT.md       -- Message templates
```

---

## Foreign Key Map

```
companies.csv
  ├──> people.csv (company_id)
  ├──> leads.csv (company_id)
  ├──> clients.csv (company_id)
  ├──> partners.csv (company_id)
  └──> activities.csv (company_id)

products.csv
  ├──> leads.csv (product_id)
  ├──> clients.csv (product_id)
  ├──> partners.csv (product_id)
  └──> activities.csv (product_id)

people.csv
  ├──> leads.csv (primary_contact_id)
  ├──> clients.csv (primary_contact_id)
  ├──> partners.csv (primary_contact_id)
  └──> activities.csv (person_id)

clients.csv
  └──> deals.csv (client_id)
```

---

## Key Metrics

| Metric | How to Calculate |
|--------|------------------|
| Pipeline value | Sum `estimated_value` where stage != won/lost |
| Active leads | Count leads where stage not in (won, lost) |
| Conversion rate | won / (won + lost) |
| Monthly revenue | Sum `mrr` from active clients |
| Outstanding invoices | Deals where stage = invoiced and paid_date is empty |
| Avg deal size | Mean `value` from deals where stage = paid |

---

## Integration Points

| Channel | Integration | Guide |
|---------|-------------|-------|
| **Telegram** | Telethon API | [Setup](../integrations/telegram_api.md) |
| **Gmail** | Gmail API | [Setup](../integrations/gmail.md) |
| **WhatsApp** | Baileys | [Setup](../integrations/whatsapp.md) |
| **LinkedIn** | Manual / CDP | [Setup](../integrations/linkedin.md) |
| **MCP Agents** | Model Context Protocol | [Setup](../integrations/mcp-agents.md) |
| **cursor-pm** | CSV cross-reference | [Setup](../integrations/cursor-pm.md) |

#!/usr/bin/env python3
"""
Validate CRM CSV files for common issues.

Usage:
    python3 scripts/validate_csv.py
    python3 scripts/validate_csv.py --fix  # Auto-fix missing last_updated
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
CRM_DIR = BASE_DIR / "sales" / "crm"


FORMULA_INJECTION_CHARS = {"=", "+", "-", "@", "\t", "\r"}
TEXT_FIELDS = {
    "name", "description", "notes", "subject", "next_action",
    "role", "revenue_share", "source", "invoice_number",
}

# ID format patterns from schema.yaml
ID_PATTERNS = {
    "company_id": re.compile(r"^comp-[a-z0-9-]+$"),
    "person_id": re.compile(r"^p-[a-z0-9]+-\d+$"),
    "product_id": re.compile(r"^prod-[a-z0-9-]+$"),
    "client_id": re.compile(r"^cli-[a-z0-9]+-\d+$"),
    "partner_id": re.compile(r"^ptnr-[a-z0-9]+-\d+$"),
    "lead_id": re.compile(r"^lead-[a-z0-9]+-\d+$"),
    "deal_id": re.compile(r"^deal-[a-z0-9]+-\d+$"),
}

# Date fields that should match YYYY-MM-DD
DATE_FIELDS = {
    "created_date", "last_updated", "next_action_date", "date",
    "contract_start", "contract_end", "since", "delivered_date",
    "invoice_date", "paid_date", "last_contact",
}
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# Email format from schema.yaml
EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


def today_iso() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def load_csv(path):
    """Load CSV, return empty DataFrame if file is empty."""
    try:
        df = pd.read_csv(path)
        return df
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


def check_formula_injection(df, table_name: str) -> list[str]:
    """Check text fields for CSV formula injection characters."""
    errors = []
    for col in df.columns:
        if col not in TEXT_FIELDS:
            continue
        for i, val in df[col].items():
            if pd.isna(val):
                continue
            s = str(val).strip()
            if s and s[0] in FORMULA_INJECTION_CHARS:
                errors.append(
                    f"{table_name} row {i+2}: '{col}' starts with '{s[0]}' "
                    f"(possible CSV formula injection)"
                )
    return errors


def validate_id_format(value, field_name: str, row_num: int) -> list[str]:
    """Validate that an ID field matches its expected format."""
    errors = []
    if field_name in ID_PATTERNS and pd.notna(value):
        s = str(value).strip()
        if s and not ID_PATTERNS[field_name].match(s):
            errors.append(
                f"Row {row_num}: {field_name} '{s}' does not match "
                f"expected format {ID_PATTERNS[field_name].pattern}"
            )
    return errors


def validate_date_fields(row, row_num: int) -> list[str]:
    """Validate that all date fields in a row match YYYY-MM-DD format."""
    errors = []
    for field in DATE_FIELDS:
        val = row.get(field)
        if pd.notna(val):
            s = str(val).strip()
            if s and not DATE_PATTERN.match(s):
                errors.append(
                    f"Row {row_num}: {field} '{s}' does not match YYYY-MM-DD format"
                )
            elif s:
                # Also validate it's a real date
                try:
                    datetime.strptime(s, "%Y-%m-%d")
                except ValueError:
                    errors.append(
                        f"Row {row_num}: {field} '{s}' is not a valid date"
                    )
    return errors


def validate_email(value, row_num: int) -> list[str]:
    """Validate email format if present."""
    errors = []
    if pd.notna(value):
        s = str(value).strip()
        if s and not EMAIL_PATTERN.match(s):
            errors.append(
                f"Row {row_num}: email '{s}' does not match expected format"
            )
    return errors


def validate_companies(fix: bool = False) -> list[str]:
    """Validate contacts/companies.csv"""
    errors = []
    path = CRM_DIR / "contacts" / "companies.csv"

    if not path.exists():
        return ["contacts/companies.csv not found"]

    df = load_csv(path)
    if df.empty:
        return []

    valid_types = {"company", "enterprise", "ngo", "individual"}
    valid_sizes = {"small", "medium", "enterprise", "individual"}

    for i, row in df.iterrows():
        row_num = i + 2

        # company_id required
        if pd.isna(row.get("company_id")):
            errors.append(f"Row {row_num}: company_id missing")
        else:
            errors.extend(validate_id_format(row.get("company_id"), "company_id", row_num))

        # name required
        if pd.isna(row.get("name")) or not str(row.get("name")).strip():
            errors.append(f"Row {row_num}: name missing")

        # last_updated required
        if pd.isna(row.get("last_updated")):
            if fix:
                df.at[i, "last_updated"] = today_iso()
            else:
                errors.append(f"Row {row_num}: last_updated missing")

        # Enum: type
        ctype = row.get("type")
        if pd.notna(ctype) and str(ctype).strip().lower() not in valid_types:
            errors.append(f"Row {row_num}: invalid type '{ctype}'")

        # Enum: size
        csize = row.get("size")
        if pd.notna(csize) and str(csize).strip().lower() not in valid_sizes:
            errors.append(f"Row {row_num}: invalid size '{csize}'")

        # Date format validation
        errors.extend(validate_date_fields(row, row_num))

    # Unique company_id
    if "company_id" in df.columns:
        dupes = df[df["company_id"].duplicated(keep=False)]
        if not dupes.empty:
            for cid in dupes["company_id"].unique():
                errors.append(f"Duplicate company_id: {cid}")

    if fix:
        df.to_csv(path, index=False)

    return errors


def validate_people(fix: bool = False) -> list[str]:
    """Validate contacts/people.csv"""
    errors = []
    path = CRM_DIR / "contacts" / "people.csv"

    if not path.exists():
        return ["contacts/people.csv not found"]

    df = load_csv(path)
    if df.empty:
        return []

    # Load companies for FK validation
    companies_path = CRM_DIR / "contacts" / "companies.csv"
    companies_df = load_csv(companies_path) if companies_path.exists() else pd.DataFrame()

    for i, row in df.iterrows():
        row_num = i + 2

        # person_id required
        if pd.isna(row.get("person_id")):
            errors.append(f"Row {row_num}: person_id missing")
        else:
            errors.extend(validate_id_format(row.get("person_id"), "person_id", row_num))

        # first_name required
        if pd.isna(row.get("first_name")) or not str(row.get("first_name")).strip():
            errors.append(f"Row {row_num}: first_name missing")

        # Must have email OR phone OR telegram_username
        has_email = pd.notna(row.get("email")) and str(row.get("email")).strip()
        has_phone = pd.notna(row.get("phone")) and str(row.get("phone")).strip()
        has_tg = pd.notna(row.get("telegram_username")) and str(row.get("telegram_username")).strip()
        if not (has_email or has_phone or has_tg):
            errors.append(f"Row {row_num}: must have email OR phone OR telegram_username")

        # Email format validation
        if has_email:
            errors.extend(validate_email(row.get("email"), row_num))

        # last_updated required
        if pd.isna(row.get("last_updated")):
            if fix:
                df.at[i, "last_updated"] = today_iso()
            else:
                errors.append(f"Row {row_num}: last_updated missing")

        # FK: company_id must exist
        if not companies_df.empty and "company_id" in companies_df.columns:
            cid = row.get("company_id")
            if pd.notna(cid) and cid not in companies_df["company_id"].values:
                errors.append(f"Row {row_num}: company_id '{cid}' not found")

        # Date format validation
        errors.extend(validate_date_fields(row, row_num))

    # Unique person_id
    if "person_id" in df.columns:
        dupes = df[df["person_id"].duplicated(keep=False)]
        if not dupes.empty:
            for pid in dupes["person_id"].unique():
                errors.append(f"Duplicate person_id: {pid}")

    if fix:
        df.to_csv(path, index=False)

    return errors


def validate_products(fix: bool = False) -> list[str]:
    """Validate products.csv"""
    errors = []
    path = CRM_DIR / "products.csv"

    if not path.exists():
        return ["products.csv not found"]

    df = load_csv(path)
    if df.empty:
        return []

    valid_types = {"service", "reseller", "community"}
    valid_statuses = {"active", "paused", "discontinued"}

    for i, row in df.iterrows():
        row_num = i + 2

        # product_id required
        if pd.isna(row.get("product_id")):
            errors.append(f"Row {row_num}: product_id missing")
        else:
            errors.extend(validate_id_format(row.get("product_id"), "product_id", row_num))

        # business_line required
        if pd.isna(row.get("business_line")) or not str(row.get("business_line")).strip():
            errors.append(f"Row {row_num}: business_line missing")

        # name required
        if pd.isna(row.get("name")) or not str(row.get("name")).strip():
            errors.append(f"Row {row_num}: name missing")

        # type required + enum
        ptype = row.get("type")
        if pd.isna(ptype) or not str(ptype).strip():
            errors.append(f"Row {row_num}: type missing")
        elif str(ptype).strip().lower() not in valid_types:
            errors.append(f"Row {row_num}: invalid type '{ptype}'")

        # status required + enum
        status = row.get("status")
        if pd.isna(status) or not str(status).strip():
            errors.append(f"Row {row_num}: status missing")
        elif str(status).strip().lower() not in valid_statuses:
            errors.append(f"Row {row_num}: invalid status '{status}'")

        # created_date required
        if pd.isna(row.get("created_date")):
            errors.append(f"Row {row_num}: created_date missing")

        # Date format validation
        errors.extend(validate_date_fields(row, row_num))

    # Unique product_id
    if "product_id" in df.columns:
        dupes = df[df["product_id"].duplicated(keep=False)]
        if not dupes.empty:
            for pid in dupes["product_id"].unique():
                errors.append(f"Duplicate product_id: {pid}")

    return errors


def validate_activities() -> list[str]:
    """Validate activities.csv"""
    errors = []
    path = CRM_DIR / "activities.csv"

    if not path.exists():
        return ["activities.csv not found"]

    df = load_csv(path)
    if df.empty:
        return []

    valid_types = {"call", "email", "meeting", "message", "note"}
    valid_channels = {"email", "telegram", "whatsapp", "phone", "in_person", "linkedin", "mcp"}
    valid_directions = {"inbound", "outbound"}

    # Load FKs for validation
    people_path = CRM_DIR / "contacts" / "people.csv"
    people_df = load_csv(people_path) if people_path.exists() else pd.DataFrame()
    companies_path = CRM_DIR / "contacts" / "companies.csv"
    companies_df = load_csv(companies_path) if companies_path.exists() else pd.DataFrame()
    products_path = CRM_DIR / "products.csv"
    products_df = load_csv(products_path) if products_path.exists() else pd.DataFrame()

    for i, row in df.iterrows():
        row_num = i + 2

        # activity_id required
        if pd.isna(row.get("activity_id")):
            errors.append(f"Row {row_num}: activity_id missing")

        # type required
        atype = str(row.get("type") or "").lower()
        if not atype or pd.isna(row.get("type")):
            errors.append(f"Row {row_num}: type missing")
        elif atype not in valid_types:
            errors.append(f"Row {row_num}: invalid type '{atype}'")

        # channel required
        channel = str(row.get("channel") or "").lower()
        if not channel or pd.isna(row.get("channel")):
            errors.append(f"Row {row_num}: channel missing")
        elif channel not in valid_channels:
            errors.append(f"Row {row_num}: invalid channel '{channel}'")

        # direction enum (optional but validate if present)
        direction = row.get("direction")
        if pd.notna(direction) and str(direction).strip().lower() not in valid_directions:
            errors.append(f"Row {row_num}: invalid direction '{direction}'")

        # date required
        if pd.isna(row.get("date")):
            errors.append(f"Row {row_num}: date missing")

        # created_by required
        if pd.isna(row.get("created_by")) or not str(row.get("created_by")).strip():
            errors.append(f"Row {row_num}: created_by missing")

        # FK: person_id
        if not people_df.empty and "person_id" in people_df.columns:
            pid = row.get("person_id")
            if pd.notna(pid) and pid not in people_df["person_id"].values:
                errors.append(f"Row {row_num}: person_id '{pid}' not found")

        # FK: company_id
        if not companies_df.empty and "company_id" in companies_df.columns:
            cid = row.get("company_id")
            if pd.notna(cid) and cid not in companies_df["company_id"].values:
                errors.append(f"Row {row_num}: company_id '{cid}' not found")

        # FK: product_id
        if not products_df.empty and "product_id" in products_df.columns:
            prodid = row.get("product_id")
            if pd.notna(prodid) and prodid not in products_df["product_id"].values:
                errors.append(f"Row {row_num}: product_id '{prodid}' not found")

        # Date format validation
        errors.extend(validate_date_fields(row, row_num))

    return errors


def validate_leads(companies_df) -> list[str]:
    """Validate relationships/leads.csv"""
    errors = []
    path = CRM_DIR / "relationships" / "leads.csv"

    if not path.exists():
        return ["relationships/leads.csv not found"]

    df = load_csv(path)
    if df.empty:
        return []

    valid_stages = {"new", "qualified", "proposal", "negotiation", "won", "lost"}
    valid_priorities = {"low", "medium", "high", "critical"}

    # Load products and people for FK validation
    products_path = CRM_DIR / "products.csv"
    products_df = load_csv(products_path) if products_path.exists() else pd.DataFrame()
    people_path = CRM_DIR / "contacts" / "people.csv"
    people_df = load_csv(people_path) if people_path.exists() else pd.DataFrame()

    for i, row in df.iterrows():
        row_num = i + 2

        # lead_id required
        if pd.isna(row.get("lead_id")):
            errors.append(f"Row {row_num}: lead_id missing")
        else:
            errors.extend(validate_id_format(row.get("lead_id"), "lead_id", row_num))

        # stage validation
        stage = str(row.get("stage") or "").lower()
        if not stage or pd.isna(row.get("stage")):
            errors.append(f"Row {row_num}: stage missing")
        elif stage not in valid_stages:
            errors.append(f"Row {row_num}: invalid stage '{stage}'")

        # priority enum (optional but validate if present)
        priority = row.get("priority")
        if pd.notna(priority) and str(priority).strip().lower() not in valid_priorities:
            errors.append(f"Row {row_num}: invalid priority '{priority}'")

        # last_updated required
        if pd.isna(row.get("last_updated")):
            errors.append(f"Row {row_num}: last_updated missing")

        # FK: company_id must exist
        if not companies_df.empty and "company_id" in companies_df.columns:
            cid = row.get("company_id")
            if pd.notna(cid) and cid not in companies_df["company_id"].values:
                errors.append(f"Row {row_num}: company_id '{cid}' not found")

        # FK: product_id must exist
        if not products_df.empty and "product_id" in products_df.columns:
            pid = row.get("product_id")
            if pd.notna(pid) and pid not in products_df["product_id"].values:
                errors.append(f"Row {row_num}: product_id '{pid}' not found")

        # FK: primary_contact_id must exist
        if not people_df.empty and "person_id" in people_df.columns:
            pcid = row.get("primary_contact_id")
            if pd.notna(pcid) and pcid not in people_df["person_id"].values:
                errors.append(f"Row {row_num}: primary_contact_id '{pcid}' not found")

        # Date format validation
        errors.extend(validate_date_fields(row, row_num))

    # Unique lead_id
    if "lead_id" in df.columns:
        dupes = df[df["lead_id"].duplicated(keep=False)]
        if not dupes.empty:
            for lid in dupes["lead_id"].unique():
                errors.append(f"Duplicate lead_id: {lid}")

    return errors


def validate_clients(companies_df, fix: bool = False) -> list[str]:
    """Validate relationships/clients.csv"""
    errors = []
    path = CRM_DIR / "relationships" / "clients.csv"

    if not path.exists():
        return ["relationships/clients.csv not found"]

    df = load_csv(path)
    if df.empty:
        return []

    valid_statuses = {"active", "paused", "churned"}

    # Load FKs
    products_path = CRM_DIR / "products.csv"
    products_df = load_csv(products_path) if products_path.exists() else pd.DataFrame()
    people_path = CRM_DIR / "contacts" / "people.csv"
    people_df = load_csv(people_path) if people_path.exists() else pd.DataFrame()

    for i, row in df.iterrows():
        row_num = i + 2

        # client_id required
        if pd.isna(row.get("client_id")):
            errors.append(f"Row {row_num}: client_id missing")
        else:
            errors.extend(validate_id_format(row.get("client_id"), "client_id", row_num))

        # company_id required
        if pd.isna(row.get("company_id")):
            errors.append(f"Row {row_num}: company_id missing")
        elif not companies_df.empty and "company_id" in companies_df.columns:
            cid = row.get("company_id")
            if cid not in companies_df["company_id"].values:
                errors.append(f"Row {row_num}: company_id '{cid}' not found")

        # product_id required
        if pd.isna(row.get("product_id")):
            errors.append(f"Row {row_num}: product_id missing")
        elif not products_df.empty and "product_id" in products_df.columns:
            pid = row.get("product_id")
            if pid not in products_df["product_id"].values:
                errors.append(f"Row {row_num}: product_id '{pid}' not found")

        # status required + enum
        status = row.get("status")
        if pd.isna(status) or not str(status).strip():
            errors.append(f"Row {row_num}: status missing")
        elif str(status).strip().lower() not in valid_statuses:
            errors.append(f"Row {row_num}: invalid status '{status}'")

        # created_date required
        if pd.isna(row.get("created_date")):
            errors.append(f"Row {row_num}: created_date missing")

        # last_updated required
        if pd.isna(row.get("last_updated")):
            if fix:
                df.at[i, "last_updated"] = today_iso()
            else:
                errors.append(f"Row {row_num}: last_updated missing")

        # FK: primary_contact_id
        if not people_df.empty and "person_id" in people_df.columns:
            pcid = row.get("primary_contact_id")
            if pd.notna(pcid) and pcid not in people_df["person_id"].values:
                errors.append(f"Row {row_num}: primary_contact_id '{pcid}' not found")

        # Date format validation
        errors.extend(validate_date_fields(row, row_num))

    # Unique client_id
    if "client_id" in df.columns:
        dupes = df[df["client_id"].duplicated(keep=False)]
        if not dupes.empty:
            for cid in dupes["client_id"].unique():
                errors.append(f"Duplicate client_id: {cid}")

    if fix:
        df.to_csv(path, index=False)

    return errors


def validate_partners(companies_df, fix: bool = False) -> list[str]:
    """Validate relationships/partners.csv"""
    errors = []
    path = CRM_DIR / "relationships" / "partners.csv"

    if not path.exists():
        return ["relationships/partners.csv not found"]

    df = load_csv(path)
    if df.empty:
        return []

    valid_types = {"training_partner", "workforce_partner", "reseller_agreement", "referral_partner"}
    valid_statuses = {"active", "paused", "ended"}

    # Load FKs
    products_path = CRM_DIR / "products.csv"
    products_df = load_csv(products_path) if products_path.exists() else pd.DataFrame()
    people_path = CRM_DIR / "contacts" / "people.csv"
    people_df = load_csv(people_path) if people_path.exists() else pd.DataFrame()

    for i, row in df.iterrows():
        row_num = i + 2

        # partner_id required
        if pd.isna(row.get("partner_id")):
            errors.append(f"Row {row_num}: partner_id missing")
        else:
            errors.extend(validate_id_format(row.get("partner_id"), "partner_id", row_num))

        # company_id required
        if pd.isna(row.get("company_id")):
            errors.append(f"Row {row_num}: company_id missing")
        elif not companies_df.empty and "company_id" in companies_df.columns:
            cid = row.get("company_id")
            if cid not in companies_df["company_id"].values:
                errors.append(f"Row {row_num}: company_id '{cid}' not found")

        # product_id required
        if pd.isna(row.get("product_id")):
            errors.append(f"Row {row_num}: product_id missing")
        elif not products_df.empty and "product_id" in products_df.columns:
            pid = row.get("product_id")
            if pid not in products_df["product_id"].values:
                errors.append(f"Row {row_num}: product_id '{pid}' not found")

        # partnership_type required + enum
        ptype = row.get("partnership_type")
        if pd.isna(ptype) or not str(ptype).strip():
            errors.append(f"Row {row_num}: partnership_type missing")
        elif str(ptype).strip().lower() not in valid_types:
            errors.append(f"Row {row_num}: invalid partnership_type '{ptype}'")

        # status required + enum
        status = row.get("status")
        if pd.isna(status) or not str(status).strip():
            errors.append(f"Row {row_num}: status missing")
        elif str(status).strip().lower() not in valid_statuses:
            errors.append(f"Row {row_num}: invalid status '{status}'")

        # created_date required
        if pd.isna(row.get("created_date")):
            errors.append(f"Row {row_num}: created_date missing")

        # last_updated required
        if pd.isna(row.get("last_updated")):
            if fix:
                df.at[i, "last_updated"] = today_iso()
            else:
                errors.append(f"Row {row_num}: last_updated missing")

        # FK: primary_contact_id
        if not people_df.empty and "person_id" in people_df.columns:
            pcid = row.get("primary_contact_id")
            if pd.notna(pcid) and pcid not in people_df["person_id"].values:
                errors.append(f"Row {row_num}: primary_contact_id '{pcid}' not found")

        # Date format validation
        errors.extend(validate_date_fields(row, row_num))

    # Unique partner_id
    if "partner_id" in df.columns:
        dupes = df[df["partner_id"].duplicated(keep=False)]
        if not dupes.empty:
            for pid in dupes["partner_id"].unique():
                errors.append(f"Duplicate partner_id: {pid}")

    if fix:
        df.to_csv(path, index=False)

    return errors


def validate_deals(fix: bool = False) -> list[str]:
    """Validate relationships/deals.csv"""
    errors = []
    path = CRM_DIR / "relationships" / "deals.csv"

    if not path.exists():
        return ["relationships/deals.csv not found"]

    df = load_csv(path)
    if df.empty:
        return []

    valid_stages = {"proposal", "negotiation", "won", "in_progress", "delivered", "invoiced", "paid", "lost"}
    valid_currencies = {
        "USD", "EUR", "GBP", "CAD", "AUD", "CHF", "JPY", "SGD", "PLN", "UAH", "SEK", "INR", "BRL"
    }

    # Load clients for FK validation
    clients_path = CRM_DIR / "relationships" / "clients.csv"
    clients_df = load_csv(clients_path) if clients_path.exists() else pd.DataFrame()

    for i, row in df.iterrows():
        row_num = i + 2

        # deal_id required
        if pd.isna(row.get("deal_id")):
            errors.append(f"Row {row_num}: deal_id missing")
        else:
            errors.extend(validate_id_format(row.get("deal_id"), "deal_id", row_num))

        # client_id required + FK
        if pd.isna(row.get("client_id")):
            errors.append(f"Row {row_num}: client_id missing")
        elif not clients_df.empty and "client_id" in clients_df.columns:
            cid = row.get("client_id")
            if cid not in clients_df["client_id"].values:
                errors.append(f"Row {row_num}: client_id '{cid}' not found")

        # name required
        if pd.isna(row.get("name")) or not str(row.get("name")).strip():
            errors.append(f"Row {row_num}: name missing")

        # value required
        if pd.isna(row.get("value")):
            errors.append(f"Row {row_num}: value missing")

        # currency required + enum
        currency = row.get("currency")
        if pd.isna(currency) or not str(currency).strip():
            errors.append(f"Row {row_num}: currency missing")
        elif str(currency).strip().upper() not in valid_currencies:
            errors.append(f"Row {row_num}: invalid currency '{currency}'")

        # stage required + enum
        stage = row.get("stage")
        if pd.isna(stage) or not str(stage).strip():
            errors.append(f"Row {row_num}: stage missing")
        elif str(stage).strip().lower() not in valid_stages:
            errors.append(f"Row {row_num}: invalid stage '{stage}'")

        # created_date required
        if pd.isna(row.get("created_date")):
            errors.append(f"Row {row_num}: created_date missing")

        # Business rule: paid requires invoice_date
        if pd.notna(stage) and str(stage).strip().lower() == "paid":
            if pd.isna(row.get("invoice_date")):
                errors.append(f"Row {row_num}: paid deal must have invoice_date")

        # Date format validation
        errors.extend(validate_date_fields(row, row_num))

    # Unique deal_id
    if "deal_id" in df.columns:
        dupes = df[df["deal_id"].duplicated(keep=False)]
        if not dupes.empty:
            for did in dupes["deal_id"].unique():
                errors.append(f"Duplicate deal_id: {did}")

    return errors


def print_errors(table_name: str, errors: list[str]) -> None:
    """Print validation errors for a table."""
    if errors:
        print(f"  {len(errors)} issues:")
        for e in errors[:5]:
            print(f"     - {e}")
        if len(errors) > 5:
            print(f"     ... and {len(errors) - 5} more")
    else:
        print("  OK")


def main():
    parser = argparse.ArgumentParser(description="Validate CRM CSV files")
    parser.add_argument("--fix", action="store_true", help="Auto-fix missing last_updated")
    args = parser.parse_args()

    print("=" * 50)
    print("CRM VALIDATION REPORT")
    print("=" * 50)

    all_errors = []

    # Load companies for FK validation
    companies_path = CRM_DIR / "contacts" / "companies.csv"
    companies_df = load_csv(companies_path) if companies_path.exists() else pd.DataFrame()

    # Collect all DataFrames for formula injection check
    csv_files = {
        "companies": CRM_DIR / "contacts" / "companies.csv",
        "people": CRM_DIR / "contacts" / "people.csv",
        "products": CRM_DIR / "products.csv",
        "leads": CRM_DIR / "relationships" / "leads.csv",
        "clients": CRM_DIR / "relationships" / "clients.csv",
        "partners": CRM_DIR / "relationships" / "partners.csv",
        "deals": CRM_DIR / "relationships" / "deals.csv",
        "activities": CRM_DIR / "activities.csv",
    }

    # Companies
    print("\nValidating companies...")
    errors = validate_companies(fix=args.fix)
    print_errors("companies", errors)
    all_errors.extend(errors)

    # People
    print("\nValidating people...")
    errors = validate_people(fix=args.fix)
    print_errors("people", errors)
    all_errors.extend(errors)

    # Products
    print("\nValidating products...")
    errors = validate_products(fix=args.fix)
    print_errors("products", errors)
    all_errors.extend(errors)

    # Activities
    print("\nValidating activities...")
    errors = validate_activities()
    print_errors("activities", errors)
    all_errors.extend(errors)

    # Leads
    print("\nValidating leads...")
    errors = validate_leads(companies_df)
    print_errors("leads", errors)
    all_errors.extend(errors)

    # Clients
    print("\nValidating clients...")
    errors = validate_clients(companies_df, fix=args.fix)
    print_errors("clients", errors)
    all_errors.extend(errors)

    # Partners
    print("\nValidating partners...")
    errors = validate_partners(companies_df, fix=args.fix)
    print_errors("partners", errors)
    all_errors.extend(errors)

    # Deals
    print("\nValidating deals...")
    errors = validate_deals(fix=args.fix)
    print_errors("deals", errors)
    all_errors.extend(errors)

    # CSV formula injection check (all tables)
    print("\nChecking for CSV formula injection...")
    injection_errors = []
    for table_name, path in csv_files.items():
        if path.exists():
            df = load_csv(path)
            if not df.empty:
                injection_errors.extend(check_formula_injection(df, table_name))
    if injection_errors:
        print(f"  {len(injection_errors)} issues:")
        for e in injection_errors[:5]:
            print(f"     - {e}")
        if len(injection_errors) > 5:
            print(f"     ... and {len(injection_errors) - 5} more")
    else:
        print("  OK")
    all_errors.extend(injection_errors)

    # Summary
    print("\n" + "=" * 50)
    if all_errors:
        print(f"Total: {len(all_errors)} issues found")
        if not args.fix:
            print("   Run with --fix to auto-fix what can be fixed")
    else:
        print("All validations passed!")

    return min(len(all_errors), 1)


if __name__ == "__main__":
    sys.exit(main())

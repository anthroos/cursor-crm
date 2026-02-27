#!/usr/bin/env python3
"""
Validate CRM CSV files for common issues.

Usage:
    python3 scripts/validate_csv.py
    python3 scripts/validate_csv.py --fix  # Auto-fix missing last_updated
"""

import argparse
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


def validate_companies(fix: bool = False) -> list[str]:
    """Validate contacts/companies.csv"""
    errors = []
    path = CRM_DIR / "contacts" / "companies.csv"

    if not path.exists():
        return ["contacts/companies.csv not found"]

    df = load_csv(path)
    if df.empty:
        return []

    for i, row in df.iterrows():
        # company_id required
        if pd.isna(row.get("company_id")):
            errors.append(f"Row {i+2}: company_id missing")

        # name required
        if pd.isna(row.get("name")) or not str(row.get("name")).strip():
            errors.append(f"Row {i+2}: name missing")

        # last_updated required
        if pd.isna(row.get("last_updated")):
            if fix:
                df.at[i, "last_updated"] = today_iso()
            else:
                errors.append(f"Row {i+2}: last_updated missing")

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

    for i, row in df.iterrows():
        # person_id required
        if pd.isna(row.get("person_id")):
            errors.append(f"Row {i+2}: person_id missing")

        # first_name required
        if pd.isna(row.get("first_name")) or not str(row.get("first_name")).strip():
            errors.append(f"Row {i+2}: first_name missing")

        # Must have email OR phone OR telegram_username
        has_email = pd.notna(row.get("email")) and str(row.get("email")).strip()
        has_phone = pd.notna(row.get("phone")) and str(row.get("phone")).strip()
        has_tg = pd.notna(row.get("telegram_username")) and str(row.get("telegram_username")).strip()
        if not (has_email or has_phone or has_tg):
            errors.append(f"Row {i+2}: must have email OR phone OR telegram_username")

        # last_updated required
        if pd.isna(row.get("last_updated")):
            if fix:
                df.at[i, "last_updated"] = today_iso()
            else:
                errors.append(f"Row {i+2}: last_updated missing")

    # Unique person_id
    if "person_id" in df.columns:
        dupes = df[df["person_id"].duplicated(keep=False)]
        if not dupes.empty:
            for pid in dupes["person_id"].unique():
                errors.append(f"Duplicate person_id: {pid}")

    if fix:
        df.to_csv(path, index=False)

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

    for i, row in df.iterrows():
        # activity_id required
        if pd.isna(row.get("activity_id")):
            errors.append(f"Row {i+2}: activity_id missing")

        # type required
        atype = str(row.get("type") or "").lower()
        if not atype or pd.isna(row.get("type")):
            errors.append(f"Row {i+2}: type missing")
        elif atype not in valid_types:
            errors.append(f"Row {i+2}: invalid type '{atype}'")

        # channel required
        channel = str(row.get("channel") or "").lower()
        if not channel or pd.isna(row.get("channel")):
            errors.append(f"Row {i+2}: channel missing")
        elif channel not in valid_channels:
            errors.append(f"Row {i+2}: invalid channel '{channel}'")

        # date required
        if pd.isna(row.get("date")):
            errors.append(f"Row {i+2}: date missing")

        # created_by required
        if pd.isna(row.get("created_by")) or not str(row.get("created_by")).strip():
            errors.append(f"Row {i+2}: created_by missing")

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

    # Load products for FK validation
    products_path = CRM_DIR / "products.csv"
    products_df = load_csv(products_path) if products_path.exists() else pd.DataFrame()

    for i, row in df.iterrows():
        # lead_id required
        if pd.isna(row.get("lead_id")):
            errors.append(f"Row {i+2}: lead_id missing")

        # stage validation
        stage = str(row.get("stage") or "").lower()
        if not stage or pd.isna(row.get("stage")):
            errors.append(f"Row {i+2}: stage missing")
        elif stage not in valid_stages:
            errors.append(f"Row {i+2}: invalid stage '{stage}'")

        # last_updated required
        if pd.isna(row.get("last_updated")):
            errors.append(f"Row {i+2}: last_updated missing")

        # FK: company_id must exist
        if not companies_df.empty and "company_id" in companies_df.columns:
            cid = row.get("company_id")
            if pd.notna(cid) and cid not in companies_df["company_id"].values:
                errors.append(f"Row {i+2}: company_id '{cid}' not found")

        # FK: product_id must exist
        if not products_df.empty and "product_id" in products_df.columns:
            pid = row.get("product_id")
            if pd.notna(pid) and pid not in products_df["product_id"].values:
                errors.append(f"Row {i+2}: product_id '{pid}' not found")

    return errors


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
    if errors:
        print(f"  {len(errors)} issues:")
        for e in errors[:5]:
            print(f"     - {e}")
        if len(errors) > 5:
            print(f"     ... and {len(errors) - 5} more")
    else:
        print("  OK")
    all_errors.extend(errors)

    # People
    print("\nValidating people...")
    errors = validate_people(fix=args.fix)
    if errors:
        print(f"  {len(errors)} issues:")
        for e in errors[:5]:
            print(f"     - {e}")
        if len(errors) > 5:
            print(f"     ... and {len(errors) - 5} more")
    else:
        print("  OK")
    all_errors.extend(errors)

    # Activities
    print("\nValidating activities...")
    errors = validate_activities()
    if errors:
        print(f"  {len(errors)} issues:")
        for e in errors[:5]:
            print(f"     - {e}")
    else:
        print("  OK")
    all_errors.extend(errors)

    # Leads
    print("\nValidating leads...")
    errors = validate_leads(companies_df)
    if errors:
        print(f"  {len(errors)} issues:")
        for e in errors[:5]:
            print(f"     - {e}")
    else:
        print("  OK")
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

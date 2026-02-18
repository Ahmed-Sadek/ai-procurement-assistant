
import csv
import os
import sys
from datetime import datetime

# Add the backend directory to the sys.path so we can import from app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db import get_database

DATE_FIELDS = ["Creation Date", "Purchase Date"]
AMOUNT_FIELDS = ["Unit Price", "Total Price"]
NUMERIC_FIELDS = ["Quantity"]


def parse_date(value: str):
    """Convert MM/DD/YYYY string to datetime, or None if empty/invalid."""
    if not value:
        return None
    try:
        return datetime.strptime(value, "%m/%d/%Y")
    except ValueError:
        return None


def parse_amount(value: str):
    """Convert '$1,234.56' to float 1234.56, or None if empty/invalid."""
    if not value:
        return None
    try:
        return float(value.replace("$", "").replace(",", ""))
    except ValueError:
        return None


def parse_number(value: str):
    """Convert numeric string to float, or None if empty/invalid."""
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def derive_quarter(dt):
    """Compute fiscal quarter string like '2013-Q3' from a datetime."""
    if dt is None:
        return None
    q = (dt.month - 1) // 3 + 1
    return f"{dt.year}-Q{q}"


def convert_row(row: dict) -> dict:
    """Apply type conversions to a cleaned CSV row."""
    for field in DATE_FIELDS:
        if field in row:
            row[field] = parse_date(row[field])
    for field in AMOUNT_FIELDS:
        if field in row:
            row[field] = parse_amount(row[field])
    for field in NUMERIC_FIELDS:
        if field in row:
            row[field] = parse_number(row[field])
    # Derive Quarter from Creation Date
    row["Quarter"] = derive_quarter(row.get("Creation Date"))
    return row


def load_data():
    db = get_database()
    collection = db.purchase_orders
    
    csv_file_path = os.path.join(os.path.dirname(__file__), 'data', 'PURCHASE ORDER DATA EXTRACT 2012-2015_0.csv')
    
    if not os.path.exists(csv_file_path):
        print(f"Error: File not found at {csv_file_path}")
        return

    print(f"Reading data from {csv_file_path}...")
    
    documents = []
    try:
        with open(csv_file_path, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                # Basic data cleaning: strip whitespace from keys and values
                clean_row = {k.strip(): v.strip() for k, v in row.items() if k}
                # Convert types
                clean_row = convert_row(clean_row)
                documents.append(clean_row)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return

    if documents:
        print(f"Found {len(documents)} records. Inserting into MongoDB...")
        try:
            # Clear existing data to avoid duplicates during development/testing
            collection.delete_many({})
            result = collection.insert_many(documents)
            print(f"Successfully inserted {len(result.inserted_ids)} records.")

            # Create indexes on commonly queried fields
            collection.create_index("Fiscal Year")
            collection.create_index("Department Name")
            collection.create_index("Supplier Name")
            collection.create_index("Acquisition Type")
            collection.create_index("Quarter")
            collection.create_index("Creation Date")
            collection.create_index("Total Price")
            print("Created indexes on key fields.")
        except Exception as e:
            print(f"Error inserting data into MongoDB: {e}")
    else:
        print("No data found in CSV file.")

if __name__ == "__main__":
    load_data()

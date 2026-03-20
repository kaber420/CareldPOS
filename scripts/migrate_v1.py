import sqlite3
import os

db_path = "data/repair_shop.db"

if not os.path.exists(db_path):
    print(f"Error: Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("Checking for missing columns in 'payments' table...")
try:
    cursor.execute("SELECT sale_id FROM payments LIMIT 1")
    print("Column 'sale_id' already exists in 'payments'.")
except sqlite3.OperationalError:
    print("Adding 'sale_id' column to 'payments' table...")
    cursor.execute("ALTER TABLE payments ADD COLUMN sale_id INTEGER REFERENCES sales(id)")
    cursor.execute("CREATE INDEX ix_payments_sale_id ON payments (sale_id)")
    print("Column 'sale_id' added successfully.")

print("Ensuring 'sales' and 'sale_items' tables exist (via initial creation if missing)...")
# SQLModel should have created them if create_db_and_tables was called after importing models,
# but we can manually ensure they exist here if needed, or just let SQLAlchemy handle it next time the app starts.
# To be safe, we let the app handle it via SQLModel.metadata.create_all(engine) in main.py.

conn.commit()
conn.close()
print("Migration completed.")

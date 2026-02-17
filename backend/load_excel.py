import pandas as pd
from sqlalchemy import create_engine, text

engine = create_engine("sqlite:///sample_data.db")

df = pd.read_excel("sales_data.xlsx")

with engine.connect() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product TEXT,
            category TEXT,
            quantity INTEGER,
            price REAL,
            sale_date TEXT
        )
    """))

    conn.execute(text("DELETE FROM sales"))

    for _, row in df.iterrows():
        conn.execute(text("""
            INSERT INTO sales (product, category, quantity, price, sale_date)
            VALUES (:product, :category, :quantity, :price, :sale_date)
        """), {
            "product": row["product"],
            "category": row["category"],
            "quantity": int(row["quantity"]),
            "price": float(row["price"]),
            "sale_date": str(row["sale_date"])
        })

    conn.commit()

print("✅ Excel data loaded into SQLite")

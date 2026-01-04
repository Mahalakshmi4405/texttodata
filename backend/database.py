import sqlite3
import pandas as pd
from sqlalchemy import create_engine, text

# Define the database URL
DB_URL = "sqlite:///./sample_data.db"

def init_db():
    print("Initializing database...")
    engine = create_engine(DB_URL)
    
    # Create sample data
    # 1. Customers
    customers_data = {
        "id": [1, 2, 3, 4, 5],
        "name": ["Acme Corp", "Globex", "Soylent Corp", "Initech", "Umbrella Corp"],
        "region": ["North", "East", "West", "North", "South"],
        "signup_date": ["2023-01-15", "2023-02-20", "2023-03-10", "2023-04-05", "2023-05-12"]
    }
    df_customers = pd.DataFrame(customers_data)
    
    # 2. Products
    products_data = {
        "id": [101, 102, 103, 104],
        "name": ["Widget A", "Widget B", "Gadget X", "Gadget Y"],
        "category": ["Widgets", "Widgets", "Gadgets", "Gadgets"],
        "price": [10.0, 15.5, 50.0, 75.0]
    }
    df_products = pd.DataFrame(products_data)
    
    # 3. Sales
    sales_data = {
        "id": [1001, 1002, 1003, 1004, 1005, 1006, 1007],
        "customer_id": [1, 2, 1, 3, 4, 5, 2],
        "product_id": [101, 103, 102, 104, 101, 103, 102],
        "quantity": [10, 2, 5, 1, 20, 3, 8],
        "total_amount": [100.0, 100.0, 77.5, 75.0, 200.0, 150.0, 124.0],
        "sale_date": ["2024-01-10", "2024-01-12", "2024-01-15", "2024-02-01", "2024-02-05", "2024-02-10", "2024-02-15"]
    }
    df_sales = pd.DataFrame(sales_data)
    
    # Write to SQLite
    df_customers.to_sql("customers", engine, if_exists="replace", index=False)
    df_products.to_sql("products", engine, if_exists="replace", index=False)
    df_sales.to_sql("sales", engine, if_exists="replace", index=False)
    
    print("Database initialized with sample data!")
    print("Tables created: customers, products, sales")

    # Verify
    with engine.connect() as conn:
        result = conn.execute(text("SELECT count(*) FROM sales")).scalar()
        print(f"Total sales records: {result}")



if __name__ == "__main__":
    init_db()

from sqlalchemy import create_engine, text

engine = create_engine("sqlite:///./sample_data.db")

def run_query(query):
    with engine.connect() as conn:
        result = conn.execute(text(query))
        return result.fetchall()


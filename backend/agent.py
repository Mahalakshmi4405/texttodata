from database import run_query

def process_question(question: str):
    q = question.lower()

    # 1️⃣ TOTAL SALES
    if "total" in q and "sales" in q:
        query = "SELECT SUM(total_amount) FROM sales"
        rows = run_query(query)
        value = rows[0][0] if rows and rows[0][0] else 0
        return {
            "type": "metric",
            "label": "Total Sales",
            "value": round(value, 2)
        }

    # 2️⃣ TOP PRODUCT (highest sales or top N)
    elif "top" in q and "product" in q:
        limit = 5  # default top 5
        import re
        match = re.search(r"top (\d+)", q)
        if match:
            limit = int(match.group(1))

        query = f"""
        SELECT p.name, SUM(s.total_amount) AS total_sales
        FROM sales s
        JOIN products p ON s.product_id = p.id
        GROUP BY p.name
        ORDER BY total_sales DESC
        LIMIT {limit}
        """
        rows = run_query(query)
        if not rows:
            return {"type": "metric", "label": "Top Products", "value": "No data found"}

        return {
            "type": "chart",
            "labels": [r[0] for r in rows],
            "values": [r[1] for r in rows]
        }

    # 3️⃣ AVERAGE ORDER VALUE
    elif "average" in q and "order" in q:
        query = "SELECT AVG(total_amount) FROM sales"
        rows = run_query(query)
        value = rows[0][0] if rows and rows[0][0] else 0
        return {"type": "metric", "label": "Average Order Value", "value": round(value, 2)}

    # 4️⃣ SALES BY PRODUCT
    elif "sales by product" in q:
        query = """
        SELECT p.name, SUM(s.total_amount)
        FROM sales s
        JOIN products p ON s.product_id = p.id
        GROUP BY p.name
        """
        data = run_query(query)
        return {"type": "chart", "labels": [r[0] for r in data], "values": [r[1] for r in data]}

    # 5️⃣ TOP CUSTOMERS
    elif "top" in q and "customer" in q:
        query = """
        SELECT c.name, SUM(s.total_amount)
        FROM sales s
        JOIN customers c ON s.customer_id = c.id
        GROUP BY c.name
        ORDER BY SUM(s.total_amount) DESC
        LIMIT 3
        """
        data = run_query(query)
        return {"type": "chart", "labels": [r[0] for r in data], "values": [r[1] for r in data]}

    # 6️⃣ SALES BY DATE
    elif "sales by date" in q:
        query = """
        SELECT sale_date, SUM(total_amount)
        FROM sales
        GROUP BY sale_date
        ORDER BY sale_date
        """
        data = run_query(query)
        return {"type": "chart", "labels": [r[0] for r in data], "values": [r[1] for r in data]}

    # 7️⃣ RECENT SALES
    elif "recent" in q:
        query = """
        SELECT s.sale_date, p.name, c.name, s.total_amount
        FROM sales s
        JOIN products p ON s.product_id = p.id
        JOIN customers c ON s.customer_id = c.id
        ORDER BY s.sale_date DESC
        LIMIT 5
        """
        rows = run_query(query)
        return {
            "type": "table",
            "rows": [
                {"date": r[0], "product": r[1], "customer": r[2], "amount": r[3]}
                for r in rows
            ]
        }

    # ❌ UNKNOWN QUESTION
    else:
        return {"type": "metric", "label": "Sorry", "value": "Question not supported"}

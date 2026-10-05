import csv
import os
import sqlite3

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "meesho_reseller.db")
OUTPUT_DIR = os.path.join(BASE_DIR, "part1_sql", "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Query 1: Monthly category revenue
q1 = """
SELECT month, category, ROUND(SUM(quantity * unit_price), 2) AS revenue, COUNT(*) AS n_orders
FROM orders
GROUP BY month, category
ORDER BY CASE month WHEN 'April' THEN 1 WHEN 'May' THEN 2 WHEN 'June' THEN 3 END, category;
"""

# Query 2: Region-wise revenue & order count
q2 = """
SELECT r.region, ROUND(SUM(o.quantity * o.unit_price), 2) AS total_revenue, COUNT(o.order_id) AS order_count
FROM orders o JOIN resellers r ON o.reseller_id = r.reseller_id
GROUP BY r.region ORDER BY total_revenue DESC;
"""

# Query 3: Top 5 resellers > ₹50,000 spend
q3 = """
SELECT r.reseller_id, r.reseller_name, ROUND(SUM(o.quantity * o.unit_price), 2) AS total_spend
FROM resellers r JOIN orders o ON r.reseller_id = o.reseller_id
GROUP BY r.reseller_id, r.reseller_name HAVING total_spend > 50000
ORDER BY total_spend DESC LIMIT 5;
"""

# Query 4: Zero-order reseller
q4 = """
SELECT r.reseller_id, r.reseller_name, r.region
FROM resellers r LEFT JOIN orders o ON r.reseller_id = o.reseller_id
WHERE o.order_id IS NULL;
"""

# Query 4 (b): COUNT(*) vs COUNT(order_id) demonstration
q4_demo = """
SELECT r.reseller_id, r.reseller_name, COUNT(*) AS count_star, COUNT(o.order_id) AS count_order_id
FROM resellers r LEFT JOIN orders o ON r.reseller_id = o.reseller_id
WHERE r.reseller_id = 'RS024'
GROUP BY r.reseller_id, r.reseller_name;
"""

# Query 5: June Delivered AOV
q5 = """
SELECT 'June' AS month, 'Delivered' AS status, ROUND(SUM(quantity * unit_price) / COUNT(*), 2) AS june_delivered_aov
FROM orders WHERE month = 'June' AND status = 'Delivered';
"""


def export_query_to_csv(query, filename):
  cursor.execute(query)
  columns = [desc for desc in cursor.description]
  rows = cursor.fetchall()
  filepath = os.path.join(OUTPUT_DIR, filename)
  with open(filepath, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(columns)
    writer.writerows(rows)
  print(f"Exported {filename} ({len(rows)} rows)")


export_query_to_csv(q1, "monthly_category_revenue.csv")
export_query_to_csv(q2, "region_revenue.csv")
export_query_to_csv(q3, "top_resellers.csv")
export_query_to_csv(q4, "zero_order_reseller.csv")
export_query_to_csv(q4_demo, "count_star_vs_count_id.csv")
export_query_to_csv(q5, "june_delivered_aov.csv")

conn.close()
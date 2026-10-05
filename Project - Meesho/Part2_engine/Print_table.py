import csv
import os
import sys

# 1. Growth Engine Functions
def mom_growth(previous: float, current: float) -> float:
    return round((current - previous) / previous * 100.0, 2)


def is_flagged(mom_pct: float, threshold: float = 8.0) -> str:
    if abs(mom_pct) == threshold:
        return "escalate_exact_boundary"
    elif abs(mom_pct) > threshold:
        return "flagged"
    else:
        return "not_flagged"


# 2. Setup File Paths
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
target_dir = os.path.join(base_dir, "Part2_engine", "fixtures")
os.makedirs(target_dir, exist_ok=True)
csv_path = os.path.join(target_dir, "monthly_category_revenue.csv")

# Standard 15-row dataset
default_data = """month,category,revenue,n_orders
April,Beauty & Personal Care,40737.01,49
April,Ethnic Wear,104520.77,64
April,Home & Kitchen,100446.23,53
April,Kids Wear,59847.27,55
April,Western Wear,113866.15,79
May,Beauty & Personal Care,35542.11,41
May,Ethnic Wear,185107.61,104
May,Home & Kitchen,91152.57,44
May,Kids Wear,45793.78,47
May,Western Wear,86998.18,64
June,Beauty & Personal Care,37559.07,52
June,Ethnic Wear,76371.53,52
June,Home & Kitchen,129971.22,73
June,Kids Wear,56737.78,57
June,Western Wear,97415.64,66"""

if not os.path.exists(csv_path) or os.path.getsize(csv_path) < 50:
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write(default_data)

# 3. Read Data Positionally
data = {}
with open(csv_path, "r", encoding="utf-8-sig") as f:
    reader = csv.reader(f)
    header = next(reader, None)
    for row in reader:
        if not row or len(row) < 3:
            continue
        month = row[0].strip().capitalize()
        category = row[1].strip()
        try:
            revenue = float(row[2].strip())
            if month not in data:
                data[month] = {}
            data[month][category] = revenue
        except ValueError:
            continue

# 4. Print Tables
print("=" * 72)
print("MAY vs APRIL 2026 MONTH-ON-MONTH PERFORMANCE")
print("=" * 72)
print(f"{'Category':<24} | {'Apr Revenue':<11} | {'May Revenue':<11} | {'MoM %':<8} | {'Status':<12}")
print("-" * 72)

for cat, curr_rev in data.get("May", {}).items():
    prev_rev = data.get("April", {}).get(cat, 0)
    if prev_rev > 0:
        pct = mom_growth(prev_rev, curr_rev)
        status = is_flagged(pct)
        print(f"{cat:<24} | ₹{prev_rev:<10.2f} | ₹{curr_rev:<10.2f} | {pct:>+6.2f}% | {status:<12}")

print("\n" + "=" * 72)
print("JUNE vs MAY 2026 MONTH-ON-MONTH PERFORMANCE")
print("=" * 72)
print(f"{'Category':<24} | {'May Revenue':<11} | {'Jun Revenue':<11} | {'MoM %':<8} | {'Status':<12}")
print("-" * 72)

for cat, curr_rev in data.get("June", {}).items():
    prev_rev = data.get("May", {}).get(cat, 0)
    if prev_rev > 0:
        pct = mom_growth(prev_rev, curr_rev)
        status = is_flagged(pct)
        print(f"{cat:<24} | ₹{prev_rev:<10.2f} | ₹{curr_rev:<10.2f} | {pct:>+6.2f}% | {status:<12}")
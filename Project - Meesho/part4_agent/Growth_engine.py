import csv
import json
import os
import sys

# 1. Dynamically resolve paths
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
part2_dir = os.path.join(base_dir, "Part2_engine")
if part2_dir not in sys.path:
  sys.path.insert(0, part2_dir)

from Growth_engine import is_flagged, mom_growth, validate_feed



def alias_for(reseller_id: str) -> str:
  if reseller_id.startswith("RS"):
    num_str = reseller_id[2:].lstrip("0")
    if len(num_str) == 1:
      num_str = f"0{num_str}"
    return f"ALIAS-{num_str}"
  return f"ALIAS-{reseller_id}"



DEFAULT_CSV_DATA = """month,category,revenue,n_orders
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


def ensure_fixture_exists(fixtures_dir):
  os.makedirs(fixtures_dir, exist_ok=True)
  csv_path = os.path.join(fixtures_dir, "monthly_category_revenue.csv")
  if not os.path.exists(csv_path) or os.path.getsize(csv_path) < 50:
    with open(csv_path, "w", encoding="utf-8") as f:
      f.write(DEFAULT_CSV_DATA)
  return csv_path


def load_month_data_positional(csv_path, target_month):
  res = {}
  if not os.path.exists(csv_path):
    return res
  with open(csv_path, "r", encoding="utf-8-sig") as f:
    reader = csv.reader(f)
    header = next(reader, None)
    for row in reader:
      if not row or len(row) < 3:
        continue
      m = row[0].strip().capitalize()
      c = row[1].strip()
      if m == target_month and c:
        try:
          res[c] = float(row[2].strip())
        except ValueError:
          continue
  return res


def run_agent_pipeline(
    run_month: str, previous_month_csv: str, current_month_csv: str
) -> dict:
  # Step 1: Input Guardrail Check
  is_valid, errors = validate_feed(current_month_csv)
  if not is_valid:
    return {
        "run_month": run_month,
        "validation_status": "invalid",
        "validation_errors": errors,
        "flagged_categories": [],
        "suppressed_categories": [],
        "escalated_categories": [],
        "action_taken": "hard_stop",
    }

  prev_month_name = {"May": "April", "June": "May"}.get(run_month, "Prior")

  curr_data = load_month_data_positional(current_month_csv, run_month)
  prev_data = load_month_data_positional(previous_month_csv, prev_month_name)

  flagged_candidates = []
  escalated_categories = []

  # Steps 2-5: Calculate MoM % & Evaluate Flags
  for cat, curr_rev in curr_data.items():
    if cat in prev_data:
      p_rev = prev_data[cat]
      pct = mom_growth(p_rev, curr_rev)
      status = is_flagged(pct)

      if status == "flagged":
        flagged_candidates.append((cat, pct, p_rev, curr_rev, abs(pct)))
      elif status == "escalate_exact_boundary":
        escalated_categories.append(cat)

  # Step 6: Top-3 Capping by Growth Magnitude (sorting by absolute percentage)
  flagged_candidates.sort(key=lambda x: x[4], reverse=True)

  flagged_categories = []
  suppressed_categories = []

  for idx, (cat, pct, p_rev, c_rev, _) in enumerate(flagged_candidates):
    if idx < 3:
      flagged_categories.append({
          "category": cat,
          "mom_pct": pct,
          "previous_revenue": p_rev,
          "current_revenue": c_rev,
          "drafted": True,
          "message": (
              f"[{run_month} vs. {prev_month_name} 2026] Category {cat} revenue"
              f" moved {pct:+.2f}% MoM from ₹{p_rev:,.2f} to ₹{c_rev:,.2f}."
              " [FACT] Operations team should review regional drivers."
              " [HYPOTHESIS]"
          ),
      })
    else:
      suppressed_categories.append(cat)

  # Steps 7-8: Return Structured Output Held for Approval
  return {
      "run_month": run_month,
      "validation_status": "valid",
      "validation_errors": [],
      "flagged_categories": flagged_categories,
      "suppressed_categories": suppressed_categories,
      "escalated_categories": escalated_categories,
      "action_taken": "drafted_and_held_for_approval",
  }


def main():
  fixtures_dir = os.path.join(base_dir, "Part2_engine", "fixtures")
  clean_feed = ensure_fixture_exists(fixtures_dir)
  corrupted_feed = os.path.join(fixtures_dir, "corrupted_feed.csv")

  print("=== SCENARIO 1: MAY 2026 PIPELINE RUN ===")
  may_res = run_agent_pipeline("May", clean_feed, clean_feed)
  print(json.dumps(may_res, indent=2))

  print("\n=== SCENARIO 2: JUNE 2026 PIPELINE RUN ===")
  june_res = run_agent_pipeline("June", clean_feed, clean_feed)
  print(json.dumps(june_res, indent=2))

  print("\n=== SCENARIO 3: CORRUPTED FEED RUN ===")
  corrupted_res = run_agent_pipeline("July", clean_feed, corrupted_feed)
  print(json.dumps(corrupted_res, indent=2))

  print("\nAll Mock Agent Runner Scenarios Executed Successfully!")


if __name__ == "__main__":
  main()
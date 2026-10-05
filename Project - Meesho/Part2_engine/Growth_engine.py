import csv


def mom_growth(previous: float, current: float) -> float:
  """Calculates Month-on-Month growth percentage rounded to 2 decimal places."""
  return round((current - previous) / previous * 100.0, 2)


def is_flagged(mom_pct: float, threshold: float = 8.0) -> str:
  """Evaluates growth against 8% threshold: 'flagged', 'not_flagged', or 'escalate_exact_boundary'."""
  if abs(mom_pct) == threshold:
    return "escalate_exact_boundary"
  elif abs(mom_pct) > threshold:
    return "flagged"
  else:
    return "not_flagged"


def validate_feed(csv_path: str) -> tuple[bool, list[str]]:
  """Input guardrail checking missing category, missing/non-numeric/negative revenue."""
  errors = []
  with open(csv_path, "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    header = next(reader, None)
    line_number = 1
    for row in reader:
      line_number += 1
      if not row:
        continue
      # Access element indices row[0], row[1], row[2] instead of row
      month = row[0].strip() if len(row) > 0 else ""
      category = row[1].strip() if len(row) > 1 else ""
      revenue_str = row[2].strip() if len(row) > 2 else ""

      if not category:
        errors.append(f"line {line_number}: missing category (month={month})")
        continue
      if not revenue_str:
        errors.append(
            f"line {line_number}: missing revenue (category={category})"
        )
        continue
      try:
        revenue_val = float(revenue_str)
      except ValueError:
        errors.append(
            f"line {line_number}: revenue not numeric: {revenue_str!r}"
        )
        continue
      if revenue_val < 0:
        errors.append(
            f"line {line_number}: negative revenue ({revenue_val}) for"
            f" category={category}"
        )
        continue

  if errors:
    return (False, errors)
  return (True, [])
import os
import sys

# Ensure current directory is in Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Growth_engine import is_flagged, mom_growth, validate_feed

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


def test_growth_engine_all():
  # 1. GIVEN April->May Ethnic Wear
  assert mom_growth(104520.77, 185107.61) == 77.1
  assert is_flagged(77.1) == "flagged"

  # 2. GIVEN May->June Beauty & Personal Care
  assert mom_growth(35542.11, 37559.07) == 5.67
  assert is_flagged(5.67) == "not_flagged"

  # 3. GIVEN synthetic pair on threshold boundary (100000 -> 108000)
  assert mom_growth(100000.0, 108000.0) == 8.0
  assert is_flagged(8.0) == "escalate_exact_boundary"

  # 4. GIVEN corrupted feed fixture
  corrupted_path = os.path.join(FIXTURES_DIR, "corrupted_feed.csv")
  is_valid, errors = validate_feed(corrupted_path)
  assert is_valid is False
  assert len(errors) == 3
  assert (
      errors[0]
      == "line 3: negative revenue (-4200.0) for category=Western Wear"
  )
  assert errors[1] == "line 4: missing category (month=July)"
  assert errors[2] == "line 6: missing revenue (category=Home & Kitchen)"

  # 5. GIVEN valid Part 1 monthly category revenue feed
  valid_path = os.path.join(FIXTURES_DIR, "monthly_category_revenue.csv")
  is_valid_clean, clean_errors = validate_feed(valid_path)
  assert is_valid_clean is True
  assert clean_errors == []

  print("All Part 2 Acceptance Criteria & Tests Passed Successfully!")


if __name__ == "__main__":
  test_growth_engine_all()
import sys


def alias_for(reseller_id: str) -> str:
  """Masks raw reseller_id: RS019 -> ALIAS-19, RS006 -> ALIAS-06."""
  if reseller_id.startswith("RS"):
    num_str = reseller_id[2:].lstrip("0")
    if len(num_str) == 1:
      num_str = f"0{num_str}"
    return f"ALIAS-{num_str}"
  return f"ALIAS-{reseller_id}"


def assert_no_raw_names_leak(text: str, reseller_names: list) -> bool:
  """Returns False if any raw reseller name appears verbatim in text."""
  for name in reseller_names:
    if name and name in text:
      return False
  return True


def test_masking():
  assert alias_for("RS019") == "ALIAS-19", (
      f"Expected ALIAS-19, got {alias_for('RS019')}"
  )
  assert alias_for("RS006") == "ALIAS-06", (
      f"Expected ALIAS-06, got {alias_for('RS006')}"
  )

  raw_names = ["Mumbai Reseller 1", "Jaipur Reseller 5", "Lucknow Reseller 6"]
  safe_text = (
      "Category Ethnic Wear revenue grew for ALIAS-19 in region West. [FACT]"
  )
  unsafe_text = "Category Ethnic Wear revenue grew for Mumbai Reseller 1. [FACT]"

  assert assert_no_raw_names_leak(safe_text, raw_names) is True
  assert assert_no_raw_names_leak(unsafe_text, raw_names) is False

  print("All Part 3 Masking Tests Passed Successfully!")


if __name__ == "__main__":
  test_masking()
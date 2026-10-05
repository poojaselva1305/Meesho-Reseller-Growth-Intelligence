 Part 4: Agent Workflow Specification

## 1. Trigger
Scheduled monthly execution following CSV data ingestion (e.g., end of May, end of June).

## 2. Input Data
- Current month category revenue CSV (e.g., `monthly_category_revenue.csv`)
- Previous month category revenue baseline
- Reseller identity dictionary (for alias mapping)

## 3. 8-Step Execution Workflow
1. **Guardrail Check**: Run `validate_feed()` on incoming CSV. If invalid, halt immediately (`action_taken: "hard_stop"`) and report errors.
2. **Data Ingestion**: Parse validated monthly category revenue into memory.
3. **Growth Math**: Calculate MoM growth percentage using `mom_growth(previous, current)`.
4. **Flagging Evaluation**: Evaluate each category using `is_flagged(mom_pct, threshold=8.0)`.
5. **Exact Boundary Escalation**: If growth magnitude is exactly 8.0%, route category to `escalated_categories` for immediate manager review.
6. **Top-3 Capping (Anti-Spam)**: Sort flagged categories by absolute growth percentage magnitude and draft alerts for only the top 3. Move remaining flagged categories to `suppressed_categories`.
7. **Identity Masking**: Apply `alias_for(reseller_id)` to ensure zero raw reseller names appear in drafted alerts.
8. **Human-in-the-Loop Hold**: Output structured JSON status with `action_taken: "drafted_and_held_for_approval"`. Wait for human confirmation before sending.

## 4. Output Schema (JSON)
```json
{
  "run_month": "May",
  "validation_status": "valid",
  "validation_errors": [],
  "flagged_categories": [...],
  "suppressed_categories": [...],
  "escalated_categories": [...],
  "action_taken": "drafted_and_held_for_approval"
}
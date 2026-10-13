# Thesis Tracker Data Contract

## Raw Inputs

The generator looks for these files inside `--data-dir`:

- `thesis_definition.json` (optional)
- `instrument_meta.json`
- `latest_financials.json`
- `historical_financials.json`
- `roe.json`
- `price_6m.json`
- `hs300_6m.json`
- `pe_ratio.json`
- `pb_ratio.json`
- `dividend.json`
- `shareholder_top10.json`
- `announcement_raw.json`
- `web_search_findings.json` (optional)

Each file may be:

- `{ "data": [...] }`
- `{ "data": { ... } }`
- `[...]`
- `{ ... }`

## Thesis Definition

`thesis_definition.json` is optional. When provided, it may include:

- `thesis_name`
- `core_view`
- `confidence_label`
- `holding_period`
- `position_date`
- `target_price`
  - `value`
  - `currency`
- `pillars`
  - `name`
  - `metric`
  - `operator`
  - `threshold`
  - `falsifier` (optional)
  - `rationale` (optional)
- `planned_catalysts`
  - `title`
  - `expected_window`
  - `expected_impact` (optional)
- `risk_items`
  - `title`
  - `initial_assessment` (optional)
  - `monitor`
  - `response` (optional)

Additional optional fields:

- `current_position` / `position`
- `direction`

Supported metric keys for custom pillars:

- `latest_revenue_yoy_pct`
- `latest_net_profit_yoy_pct`
- `latest_cash_profit_ratio`
- `latest_roe`
- `price_return_6m_pct`
- `excess_return_6m_pct`
- `top1_holder_pct`
- `top10_holder_pct`

Supported operators:

- `>`
- `>=`
- `<`
- `<=`
- `==`

If `falsifier` is omitted, the generator will derive a client-readable default refutation condition from the metric rule.

## Common Identifier Fields

Ticker fields:

- `order_book_id`
- `ticker`
- `stock_code`
- `symbol`
- `code`

Company name fields:

- `display_name`
- `name`
- `stock_name`
- `company_name`
- `symbol_name`
- `symbol`

## Financial Records

`latest_financials.json` and `historical_financials.json` are expected to include:

- `order_book_id`
- `quarter`
- `info_date`
- `revenue`
- `net_profit`
- `cash_from_operating_activities`

The generator deduplicates records by quarter and keeps the latest disclosed version.

## Financial Indicator Records

`roe.json` is expected to come from `stock cn financial-indicator` using:

- `factor = return_on_equity_weighted_average`

Returned fields typically include:

- `order_book_id`
- `date`
- `return_on_equity_weighted_average`

`pe_ratio.json` / `pb_ratio.json` should also come from `stock cn financial-indicator` using:

- `factor = pe_ratio`
- `factor = pb_ratio`

Returned fields typically include:

- `order_book_id`
- `date`
- `pe_ratio` or `pb_ratio`

Historical valuation ranges use valid observations no later than the report date, deduplicated by date. At least two distinct dates are required; the report shows the actual date span and count. A single-date snapshot supplies the current value only, with history marked insufficient.

## Announcement Availability

`announcement_raw.json` must distinguish an absent file, a failed query and an empty result. Bare `[]` has no confirmed collection status and is reported as unavailable input, not proof of no announcements. An explicitly completed empty query may use `{"status": "ok", "data": []}` or `{"success": true, "data": []}`; failures may use `{"status": "error", "error": "...", "data": []}` or `{"success": false, "data": []}`. Preserve the actual query status; do not invent it after a failed or unexecuted request.

Catalysts include only valid disclosure dates from 30 days before the report date through the report date. No-match statements describe the provided sample, not the absence of all company announcements.

## Price Records

`price_6m.json` should include:

- `order_book_id`
- `datetime`
- `close`
- `total_turnover` (optional)

`hs300_6m.json` should include:

- `order_book_id`
- `datetime`
- `close`

## Dividend Records

`dividend.json` may include:

- `quarter`
- `advance_date`
- `declaration_announcement_date`
- `book_closure_date`
- `ex_dividend_date`
- `payable_date`
- `dividend_cash_before_tax`
- `round_lot`

## Shareholder Records

`shareholder_top10.json` may include:

- `end_date`
- `info_date`
- `rank`
- `shareholder_name`
- `hold_percent_total`
- `hold_percent_float`

The generator summarizes the latest disclosure period and compares concentration with the previous period when possible.

## Announcement Records

`announcement_raw.json` may include:

- `info_date`
- `title`
- `info_type`
- `media`
- `announcement_link`

Low-signal governance boilerplate is filtered out before catalyst classification.
When `announcement_link` exists, material realized catalysts should keep the source link so later workflows can read the original PDF/HTML.

## External Findings

`web_search_findings.json` is optional. When provided, each record should include:

- `query`
- `source_name`
- `source_type`
- `title`
- `url`
- `published_at`
- `retrieved_at`
- `summary`
- `why_relevant`
- `confidence`
- `finding_type`

Allowed `source_type`:

- `official`
- `government`
- `association`
- `authoritative_media`
- `general_news`
- `inference`

Allowed `finding_type`:

- `company_news`
- `management_change`
- `industry_trend`
- `competition_context`
- `analyst_view`

Confidence ceiling by `source_type`:

- `official`: `5`
- `government`: `4`
- `association`: `4`
- `authoritative_media`: `4`
- `general_news`: `3`
- `inference`: `1`

The generator uses external findings only as supplementary thesis-validation context. Low-confidence findings should be treated as watch items rather than thesis-changing facts.

- 财务记录先排除缺失 / 无效 `info_date` 及 `info_date > report-date`，再按同一股票同一季度选择当时最新披露版本；采集参数必须传 `date=REPORT_DATE`

- 净利润同比口径：`(本期净利润 - 同期净利润) / abs(同期净利润) * 100`；同期为零或缺失时结果为 `null`。负基数反映盈亏改善 / 恶化，报告须区分减亏、亏损扩大与扭亏。

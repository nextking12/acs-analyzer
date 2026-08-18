# Interview Guide

## One-minute explanation

This project analyzes an access-control CSV and reports records that need
attention. The workflow is deliberately split into small stages:

```text
CSV -> load and validate -> normalize -> run rules -> summarize and export
```

The Streamlit app only handles input and display. The package contains the
business logic, so the rules can be tested without starting a web application.

## How to walk through the code

- `loader.py` reads CSV data as strings. This preserves badge numbers such as
  `00123` and rejects empty or malformed files.
- `normalizer.py` makes column names and text values consistent. It also adds a
  source row number so a finding can be traced back to the CSV.
- `rules.py` contains one function per audit rule. Each function builds a mask,
  then creates a typed `Finding` for matching rows.
- `analyzer.py` runs all rules, calculates summary counts, and converts findings
  into a dataframe for export.
- `app.py` calls those package functions and renders the results. It does not
  contain audit decisions.

## Design decisions

### Why normalize before applying rules?

Input exports are inconsistent. Trimming values and lowercasing statuses once
keeps each rule simple and prevents slightly different interpretations between
rules.

### Why use explicit analysis dates?

An expiration rule based on today's date would produce different results every
day. Passing `as_of_date` makes tests reproducible and makes reports explainable.

### Why return one finding per affected record?

An auditor needs to locate and correct individual records. A duplicate badge
therefore creates a finding for every row involved, not one finding for the
badge number alone.

### Why keep source data on a finding?

The report can include vendor-specific columns without making the rule code know
about every possible CSV export. Reserved report columns are renamed when the
export is built.

## Complexity

For `n` records, each rule scans the dataframe once, so the analysis is roughly
`O(n)` per rule and `O(n)` overall because there are a fixed number of rules.
The findings and source data require `O(n)` additional memory.

## Tradeoffs and next improvements

- Pandas keeps the CSV and rule code concise, at the cost of loading the full
  file into memory.
- Pydantic validates the shape of findings, while pandas remains convenient for
  tabular input and export.
- A production version could add upload-size limits, configurable vendor column
  mappings, and CSV formula-injection protection.

## Example interview questions

**How would you add a rule?** Add a function in `rules.py` that returns
`Finding` objects, call it from `analyze_cardholders`, then add focused tests for
matching and non-matching records.

**How would you test the UI?** Keep the logic in package functions and test it
with unit tests. Add a small Streamlit startup smoke test only for wiring and
rendering; do not duplicate business-logic tests in the UI layer.

**What happens with invalid dates?** Pandas converts invalid values to missing
dates. Active records with missing dates produce a high-severity finding, while
inactive records are ignored by expiration rules.

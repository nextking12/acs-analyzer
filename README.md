# Access Control Data Analyzer

A Python-based audit utility for analyzing synthetic access-control
cardholder exports.

The Streamlit interface runs a set of access-control audit rules, summarizes
the results by severity, and exports consolidated findings as CSV.

> Use synthetic or approved test data only. Do not upload operational security
> data or personally identifiable information.

## Requirements

- Python 3.13 or later
- [uv](https://docs.astral.sh/uv/)

## Install

```bash
uv sync
```

## Run

Start the Streamlit application:

```bash
uv run streamlit run app.py
```

Open the local URL shown in the terminal, then upload a cardholder CSV. A
synthetic example is available at `sample_data/sample_cardholders.csv`.

## Audit Rules

The analyzer currently reports:

| Rule | Severity |
| --- | --- |
| Expired active credential | High |
| Missing or invalid expiration date on an active credential | High |
| Duplicate nonblank badge number | High |
| Active credential missing a department | Medium |

Duplicate badges produce one finding for each affected record. The source row
identifies its position after CSV parsing, with the first data row numbered 2.
Use the rule and severity filters to review results in the application, or
download the complete consolidated report.

## CSV Format

The CSV must contain these columns:

| Column | Description |
| --- | --- |
| `cardholder_name` | Cardholder display name |
| `badge_number` | Credential or badge identifier |
| `department` | Cardholder department or organizational group |
| `credential_status` | Credential state, such as `active` or `inactive` |
| `expiration_date` | Credential expiration date |

Additional columns are preserved in the results. Column names are normalized
by trimming whitespace and converting them to lowercase. A source column that
conflicts with a report field is prefixed with `source_` in the output.

Example:

```csv
cardholder_name,badge_number,department,credential_status,expiration_date
Alex Morgan,10001,Operations,active,2025-12-31
Jordan Lee,10002,Engineering,active,2027-01-15
```

Empty, malformed, or incomplete CSV files produce an error in the application.

## Development

Run linting, formatting checks, and tests:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

## License

This project is licensed under the [MIT License](LICENSE).

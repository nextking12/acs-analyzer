# Access Control Data Analyzer

A Python-based audit utility for analyzing synthetic access-control
cardholder exports.

The Streamlit interface identifies active credentials that expired before the
current date, summarizes the results, and exports findings as CSV.

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

## CSV Format

The CSV must contain these columns:

| Column | Description |
| --- | --- |
| `cardholder_name` | Cardholder display name |
| `badge_number` | Credential or badge identifier |
| `credential_status` | Credential state, such as `active` or `inactive` |
| `expiration_date` | Credential expiration date |

Additional columns are preserved in the results. Column names are normalized
by trimming whitespace and converting them to lowercase.

Example:

```csv
cardholder_name,badge_number,credential_status,expiration_date
Alex Morgan,10001,active,2025-12-31
Jordan Lee,10002,active,2027-01-15
```

Missing or invalid expiration dates are excluded from the expired-credential
finding. Empty, malformed, or incomplete CSV files produce an error in the
application.

## Development

Run linting, formatting checks, and tests:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

## License

This project is licensed under the [MIT License](LICENSE).

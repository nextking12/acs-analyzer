# Access Control Data Analyzer: Terminal Handoff

Last updated: 2026-08-05

## Purpose of this document

This file is the working handoff for continuing development from a terminal or
another coding-agent session. Read this file together with
[`PROJECT_CONTEXT.md`](PROJECT_CONTEXT.md) and the root [`README.md`](../README.md)
before making changes.

## Repository state

- Repository: `https://github.com/nextking12/acs-analyzer`
- Working branch: `v1-reporting`
- Remote branch: `origin/v1-reporting`
- Latest committed work: `6868db5 add analysis summary and product context`
- Base branch: `main`
- Base commit when this branch was created: `828e538`
- Package version: `0.1.0`
- Python requirement: 3.13 or later
- Environment and package manager: `uv`

At the start of this handoff, the local branch and remote branch both pointed to
`6868db5`. This handoff file is a new working-tree change until it is committed.

## Overall vision

The Access Control Data Analyzer is the first product in an **Engineering
Toolkit** for physical security engineers, consultants, system administrators,
and integrators.

The toolkit should consist of focused products that solve recurring operational
problems in physical security. The value is the combination of domain knowledge
and maintainable software, not the use of a specific language or framework.

Each product should be presentable as a real, useful tool with:

- A clearly defined user and problem
- A repeatable workflow
- Explainable results and recommended actions
- Synthetic demonstration data
- Tests and documented architecture
- Screenshots, outputs, and a portfolio case study
- Local-first handling of sensitive operational data

The long-term direction may support open-source tools, consulting work, or paid
products. Do not build a universal toolkit platform prematurely. Complete at
least two focused products before extracting shared infrastructure.

## Current application behavior

The application currently provides this workflow:

```text
Cardholder CSV
    -> CSV validation and loading
    -> Field normalization
    -> Four audit rules
    -> Consolidated findings
    -> Streamlit filters and metrics
    -> Findings CSV download
```

The Streamlit app currently displays:

- Records analyzed
- Total findings
- High-severity findings
- Rule and severity filters
- Consolidated findings table
- CSV download containing all findings

The application accepts synthetic or approved CSV data with these required
columns:

- `cardholder_name`
- `badge_number`
- `department`
- `credential_status`
- `expiration_date`

Additional source columns are preserved in finding exports.

## Implemented audit rules

| Rule ID | Rule | Severity |
| --- | --- | --- |
| `expired_active_credential` | Expired active credential | High |
| `missing_or_invalid_expiration` | Missing or invalid expiration date on an active credential | High |
| `duplicate_badge_number` | Duplicate nonblank badge number | High |
| `active_missing_department` | Active credential missing a department | Medium |

Every finding includes a stable rule ID, source row, identifying fields,
description, recommended action, severity, and preserved source data.

## What was added on `v1-reporting`

The branch introduces the reporting foundation without changing the current
Streamlit interface.

### `AnalysisSummary`

`src/access_control_analyzer/models.py` now defines a typed summary containing:

- Analysis date
- Records analyzed
- Active credential count
- Inactive credential count
- Other or missing status count
- Total findings
- Zero-inclusive counts by severity
- Zero-inclusive counts for every current rule

### Summary calculation

`summarize_cardholders()` in `src/access_control_analyzer/analyzer.py` builds the
summary from the source dataframe and the typed findings. It normalizes status
values and uses an explicit analysis date when supplied.

### Tests

The analyzer tests cover:

- Status and finding totals
- Other and missing credential statuses
- Counts by severity and rule
- Zero-finding summaries

The last completed validation produced:

- Ruff lint: passed
- Ruff formatting check: passed
- Pytest: 18 passed
- Source distribution build: passed
- Wheel build: passed
- Sample-data summary smoke test: passed

## Important current boundary

`AnalysisSummary` is backend infrastructure only at this point. `app.py` does
not call `summarize_cardholders()`, so users do not see the new summary fields
yet. The existing application behavior remains unchanged.

Do not describe the executive report or expanded summary UI as complete until
they are implemented and tested.

## Architecture and constraints

Keep these boundaries intact:

- `loader.py`: CSV loading and file-level validation
- `normalizer.py`: canonical column and value normalization
- `rules.py`: individual audit-rule evaluation
- `analyzer.py`: rule orchestration, summaries, and finding conversion
- `models.py`: typed domain results
- `app.py`: Streamlit presentation only

Business logic must remain outside `app.py`. Streamlit should call package APIs
and render their results.

Other constraints:

- Keep analysis deterministic when an analysis date is provided.
- Preserve badge identifiers as strings, including leading zeroes.
- Preserve additional source columns in exported findings.
- Use synthetic or explicitly approved data for demos and testing.
- Keep processing local by default.
- Add tests for new rules, summary calculations, and reporting behavior.
- Run Ruff, formatting checks, tests, and a package build before publishing.

## Immediate goal

Complete the version 1 reporting workflow on the existing `v1-reporting`
branch.

The target user workflow is:

```text
Upload or load synthetic cardholder data
    -> Run the audit
    -> Review an analysis summary
    -> Filter detailed findings
    -> Download raw findings as CSV
    -> Download or print a client-readable executive report
```

## Ordered next steps

### 1. Integrate `AnalysisSummary` into Streamlit

Keep typed findings separate from the dataframe used for display:

```python
typed_findings = analyze_cardholders(records)
summary = summarize_cardholders(records, typed_findings)
findings = findings_to_dataframe(typed_findings)
```

Use the summary instead of recalculating metrics from the dataframe in
`app.py`.

Display at least:

- Records analyzed
- Active credentials
- Inactive credentials
- Other or missing statuses when nonzero
- Total findings
- High-severity findings
- Medium-severity findings

Preserve the existing finding filters and CSV download.

### 2. Add Streamlit-facing tests or testable presentation helpers

Avoid putting substantial formatting logic directly in `app.py`. Extract small
pure helpers when necessary and test them with ordinary unit tests. Add a basic
Streamlit startup smoke test if practical.

### 3. Implement the executive report layer

Create a package module such as `reporting.py`. Start with printable HTML rather
than adding PDF-generation complexity immediately.

The report should include:

- Product name
- Analysis date and scope
- Executive summary
- Credential-status counts
- Finding counts by severity and rule
- Detailed findings
- Recommended corrective actions
- Local-processing and data-handling disclaimer

The report generator must be callable independently of Streamlit and covered by
tests. Streamlit should only request the report and expose its download.

### 4. Validate the complete reporting workflow

Run:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
uv build
uv run streamlit run app.py
```

Manually verify the synthetic sample data, no-finding behavior, filtering, CSV
download, report download, and application startup.

### 5. Publish the reporting branch

Use focused commits on `v1-reporting`. When the reporting workflow is complete:

1. Push the final branch commits.
2. Open a pull request into `main`.
3. Review the full diff and validation output.
4. Merge only after the reporting definition of done is satisfied.

## Reporting definition of done

The `v1-reporting` branch is complete when:

- `AnalysisSummary` is used by the Streamlit interface.
- Summary counts render correctly for ordinary and empty-finding analyses.
- Existing finding filters and CSV export still work.
- A printable executive report is generated outside the UI layer.
- The report can be downloaded from Streamlit.
- Summary and report behavior have automated tests.
- All quality checks and the package build pass.
- The full application workflow is manually verified with synthetic data.

## Work after this branch

Use separate branches after the reporting pull request is merged:

1. Demo experience: built-in sample-data loading and explanatory UI.
2. Production hardening: upload limits, encoding diagnostics, CSV formula
   injection protection, CI, type checking, and broader smoke testing.
3. Vendor import profiles: configurable column, status, date, and badge mappings.
4. Portfolio release: screenshots, short demo, architecture narrative, outcomes,
   and lessons learned.
5. Version 1 release and tag.

Only after version 1 is complete should work begin on the next Engineering
Toolkit product. The current recommendation is a Commissioning Checklist
Generator because it demonstrates document generation and workflow automation
rather than duplicating another CSV analyzer.

## Terminal startup

From a new terminal session:

```bash
cd /Users/edwardking/Projects/PythonProjects/access-control-analyzer
git switch v1-reporting
git status -sb
uv sync
uv run pytest
uv run streamlit run app.py
```

Before pulling, check whether this handoff file or other local changes need to
be committed. When the worktree is clean, synchronize with:

```bash
git pull --ff-only
```

## Suggested continuation prompt

Use this prompt in a terminal coding-agent session:

```text
Continue the Access Control Data Analyzer on the v1-reporting branch. Read
docs/TERMINAL_HANDOFF.md, docs/PROJECT_CONTEXT.md, and README.md first. Verify
the branch and worktree before editing. Implement the next incomplete step:
integrate AnalysisSummary into Streamlit while keeping business logic outside
app.py. Preserve existing filters and CSV export, add appropriate tests, and run
Ruff, formatting checks, pytest, the package build, and a Streamlit smoke test.
Do not commit or push unless explicitly asked.
```

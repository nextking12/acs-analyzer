# Engineering Toolkit Project Context

## Product vision

The Engineering Toolkit is a growing collection of focused software products
for physical security engineers, consultants, and system integrators. Each tool
should turn a recurring engineering task into a clear, repeatable workflow that
produces useful evidence or documentation.

The toolkit is grounded in physical-security domain experience. Its value comes
from solving real operational problems, not from demonstrating a particular
programming language or framework.

## Why this project exists

Access-control exports commonly require manual review before they can support an
audit, migration, commissioning effort, or cleanup project. Important issues can
be hidden in large spreadsheets, while the review process is difficult to repeat
and document consistently.

The Access Control Data Analyzer is the first Engineering Toolkit product. It
converts a cardholder CSV export into structured findings and a client-readable
executive report.

## Intended users

- Physical security engineers and consultants
- Access-control system administrators
- Security system integrators
- Project teams preparing audits, migrations, or commissioning records

## Current product scope

The analyzer currently:

- Loads and validates a cardholder CSV export
- Normalizes fields needed for analysis
- Detects expired active credentials
- Detects active credentials with missing or invalid expiration dates
- Detects duplicate nonblank badge numbers
- Detects active credentials without a department
- Presents consolidated findings in a local Streamlit application
- Exports detailed findings as CSV
- Generates a printable executive HTML report with summary counts and actions

## Version 1 direction

Version 1 turns the working analyzer into a portfolio-ready product. The
remaining product work is to:

1. Keep the analysis summary and report trustworthy as rules evolve.
2. Harden file handling, report export, tests, and automated validation.
3. Document the problem, architecture, privacy decisions, and results as a case
   study.

## Product principles

### Local first

Access-control information can be operationally sensitive and may include
personally identifiable information. Analysis should remain local by default.
Public demonstrations must use synthetic or explicitly approved test data.

### Deterministic and explainable

Rules should produce repeatable results for a supplied analysis date. Every
finding should explain what was detected, identify the source record, and
recommend a concrete next action.

### Business logic outside the interface

Loading, normalization, analysis, and reporting belong in the Python package.
Streamlit is a presentation layer and should not own audit logic.

### Focused products before a shared platform

The Engineering Toolkit is initially a cohesive collection of standalone
products. Shared infrastructure should be extracted only after multiple tools
demonstrate the same requirement. Consistent audience, quality, terminology,
documentation, and visual identity are more important than forcing every tool
onto one runtime.

### Portfolio and product quality

Each tool should be understandable as a small product: problem, workflow,
screenshots, architecture, outputs, tests, and lessons learned. A tool may remain
open source, support consulting work, or later become a paid product without
changing the toolkit's overall story.

## Likely future tools

- Commissioning Checklist Generator
- Security Log Analyzer
- Security Design Validator
- Network and Device Documentation Generator
- AI-assisted knowledge or design-review tool

The next tool should not begin until the Access Control Data Analyzer has a
complete version 1 workflow and presentation.

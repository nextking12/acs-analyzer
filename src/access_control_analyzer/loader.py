import csv
from collections import Counter
from pathlib import Path
from typing import BinaryIO

import pandas as pd

CsvSource = str | Path | BinaryIO


def _validate_header(source: CsvSource) -> None:
    if isinstance(source, (str, Path)):
        with Path(source).open(encoding="utf-8-sig", newline="") as file:
            header = next((line for line in file if line.strip()), "")
    else:
        position = source.tell()
        header = source.readline()
        while header and not header.strip():
            header = source.readline()
        source.seek(position)
        if isinstance(header, bytes):
            header = header.decode("utf-8-sig")

    columns = [column.strip().lower() for column in next(csv.reader([header]), [])]
    counts = Counter(columns)
    duplicates = sorted(column for column, count in counts.items() if count > 1)
    if duplicates:
        raise ValueError(
            f"Duplicate columns after normalization: {', '.join(duplicates)}"
        )


def load_cardholder_csv(source: CsvSource) -> pd.DataFrame:
    """Load cardholder records while preserving badge numbers as text."""
    _validate_header(source)

    try:
        dataframe = pd.read_csv(source, dtype="string")
    except (pd.errors.EmptyDataError, pd.errors.ParserError) as exc:
        raise ValueError("The uploaded file is not a valid CSV.") from exc

    if dataframe.empty:
        raise ValueError("The uploaded CSV contains no records.")

    dataframe.columns = [column.strip().lower() for column in dataframe.columns]

    return dataframe

from pathlib import Path
from typing import BinaryIO

import pandas as pd

CsvSource = str | Path | BinaryIO


def load_cardholder_csv(source: CsvSource) -> pd.DataFrame:
    """Load cardholder records while preserving badge numbers as text."""
    try:
        dataframe = pd.read_csv(
            source,
            dtype={
                "badge_number": "string",
            },
        )
    except (pd.errors.EmptyDataError, pd.errors.ParserError) as exc:
        raise ValueError("The uploaded file is not a valid CSV.") from exc

    if dataframe.empty:
        raise ValueError("The uploaded CSV contains no records.")

    dataframe.columns = [column.strip().lower() for column in dataframe.columns]

    return dataframe

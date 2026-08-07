import csv
from collections import Counter
from io import BytesIO, StringIO
from pathlib import Path
from typing import BinaryIO

import pandas as pd

CsvSource = str | Path | BinaryIO

MAX_UPLOAD_BYTES = 5 * 1024 * 1024
MAX_RECORDS = 50_000
SUPPORTED_ENCODINGS = ("utf-8-sig", "cp1252")


def _coerce_bytes(raw: bytes | str | bytearray | memoryview) -> bytes:
    if isinstance(raw, str):
        return raw.encode("utf-8")
    if isinstance(raw, bytes):
        return raw
    return bytes(raw)


def _read_source_bytes(source: CsvSource, *, max_bytes: int) -> bytes:
    if isinstance(source, (str, Path)):
        path = Path(source)
        size = path.stat().st_size
        if size > max_bytes:
            raise ValueError(
                f"CSV exceeds the maximum size of {max_bytes // (1024 * 1024)} MB."
            )
        return path.read_bytes()

    if hasattr(source, "seek") and hasattr(source, "tell"):
        position = source.tell()
        source.seek(0, 2)
        size = source.tell()
        source.seek(0)
        if size > max_bytes:
            source.seek(position)
            raise ValueError(
                f"CSV exceeds the maximum size of {max_bytes // (1024 * 1024)} MB."
            )
        raw = source.read()
        source.seek(position)
    else:
        raw = source.read()
        if len(raw) > max_bytes:
            raise ValueError(
                f"CSV exceeds the maximum size of {max_bytes // (1024 * 1024)} MB."
            )

    return _coerce_bytes(raw)


def _decode_csv_text(raw: bytes) -> str:
    try:
        return raw.decode("utf-8-sig")
    except UnicodeDecodeError as utf8_error:
        try:
            return raw.decode("cp1252")
        except UnicodeDecodeError as cp1252_error:
            raise ValueError(
                "Could not decode the CSV as UTF-8 or Windows-1252 "
                f"(UTF-8: {utf8_error.reason} at byte {utf8_error.start}). "
                "Save the export as UTF-8 and try again."
            ) from cp1252_error


def _validate_header_text(text: str) -> None:
    header = next((line for line in text.splitlines() if line.strip()), "")
    columns = [column.strip().lower() for column in next(csv.reader([header]), [])]
    counts = Counter(columns)
    duplicates = sorted(column for column, count in counts.items() if count > 1)
    if duplicates:
        raise ValueError(
            f"Duplicate columns after normalization: {', '.join(duplicates)}"
        )


def load_cardholder_csv(
    source: CsvSource,
    *,
    max_bytes: int = MAX_UPLOAD_BYTES,
    max_records: int = MAX_RECORDS,
) -> pd.DataFrame:
    """Load cardholder records while preserving badge numbers as text."""
    raw = _read_source_bytes(source, max_bytes=max_bytes)
    if not raw.strip():
        raise ValueError("The uploaded file is not a valid CSV.")

    text = _decode_csv_text(raw)
    _validate_header_text(text)

    try:
        dataframe = pd.read_csv(StringIO(text), dtype="string")
    except (pd.errors.EmptyDataError, pd.errors.ParserError) as exc:
        raise ValueError("The uploaded file is not a valid CSV.") from exc

    if dataframe.empty:
        raise ValueError("The uploaded CSV contains no records.")

    if len(dataframe) > max_records:
        raise ValueError(f"CSV exceeds the maximum of {max_records:,} records.")

    dataframe.columns = [str(column).strip().lower() for column in dataframe.columns]

    return dataframe


def load_cardholder_csv_from_bytes(
    raw: bytes,
    *,
    max_bytes: int = MAX_UPLOAD_BYTES,
    max_records: int = MAX_RECORDS,
) -> pd.DataFrame:
    """Load cardholder records from already-read bytes."""
    if len(raw) > max_bytes:
        raise ValueError(
            f"CSV exceeds the maximum size of {max_bytes // (1024 * 1024)} MB."
        )
    return load_cardholder_csv(
        BytesIO(raw),
        max_bytes=max_bytes,
        max_records=max_records,
    )

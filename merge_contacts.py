#!/usr/bin/env python3
"""Combine multiple Excel exports of agents into a deduplicated table."""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path
from typing import Iterable, List

import pandas as pd

SCHEMA = [
    "zdroj",
    "jmeno_maklere",
    "telefon",
    "email",
    "realitni_kancelar",
    "kraj",
    "mesto",
    "specializace",
    "detailni_informace",
    "odkazy",
]


def _read_excel(path: Path) -> pd.DataFrame:
    try:
        df = pd.read_excel(path)
    except Exception as exc:
        raise SystemExit(f"Nelze načíst '{path}': {exc}")
    missing = [col for col in SCHEMA if col not in df.columns]
    for col in missing:
        df[col] = None
    return df[SCHEMA]


def _normalise_text(value: object) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    text = str(value).strip()
    if not text:
        return ""
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"\s+", " ", text)
    return text.lower()


def _normalise_phone(value: object) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    digits = re.sub(r"\D", "", str(value))
    if len(digits) >= 9:
        return digits[-9:]
    return digits


def _build_identifier(row: pd.Series) -> str:
    name_key = _normalise_text(row.get("jmeno_maklere"))
    phone_key = _normalise_phone(row.get("telefon"))
    email_key = _normalise_text(row.get("email"))
    return "|".join([name_key, phone_key, email_key])


def _merge_group(group: pd.DataFrame) -> pd.Series:
    merged = {}
    for column in SCHEMA:
        values = [value for value in group[column].tolist() if isinstance(value, str) and value.strip()]
        if not values:
            values = [str(value) for value in group[column].tolist() if pd.notna(value)]
        if not values:
            merged[column] = None
            continue
        if column == "odkazy":
            parts: List[str] = []
            for value in values:
                parts.extend([part.strip() for part in str(value).split("|") if part.strip()])
            merged[column] = " | ".join(dict.fromkeys(parts)) or None
        else:
            merged[column] = values[0]
    return pd.Series(merged)


def merge_excels(paths: Iterable[Path]) -> pd.DataFrame:
    frames = [_read_excel(path) for path in paths]
    if not frames:
        return pd.DataFrame(columns=SCHEMA)
    combined = pd.concat(frames, ignore_index=True)
    combined["_id"] = combined.apply(_build_identifier, axis=1)
    merged = combined.groupby("_id", dropna=False).apply(_merge_group).reset_index(drop=True)
    return merged


def _parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", type=Path, help="Excel soubory k sloučení")
    parser.add_argument("--output", "-o", type=Path, required=True, help="Výstupní Excel soubor")
    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    merged = merge_excels(args.files)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    merged.to_excel(args.output, index=False)
    print(f"Uloženo {len(merged)} unikátních záznamů do {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

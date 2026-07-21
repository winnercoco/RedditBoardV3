"""
utils/helpers.py

Utility functions for RedditBoard.

Responsibilities
----------------
- Load JSON data
- Normalize records
- Build DataFrame
- Extract unique values for filters
- Safe helper functions
"""

from pathlib import Path
import json
import pandas as pd

# --------------------------------------------------
# Data Location
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "reddit_links.json"


# --------------------------------------------------
# JSON Loading
# --------------------------------------------------

def load_data():
    """
    Load reddit_links.json

    Returns
    -------
    list[dict]
    """

    if not DATA_PATH.exists():
        return []

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# --------------------------------------------------
# Safe Helpers
# --------------------------------------------------

def safe_list(value):
    """
    Convert value to list.

    None -> []
    string -> [string]
    list -> list
    """

    if value is None:
        return []

    if isinstance(value, list):
        return value

    return [value]


def normalize_string(value):
    """
    Clean string.

    None -> ""
    """

    if value is None:
        return ""

    return str(value).strip()


# --------------------------------------------------
# Record Normalization
# --------------------------------------------------

LIST_FIELDS = [
    "star",
    "categories",
    "positions",
]

STRING_FIELDS = [
    "reddit_id",
    "type",
    "reddit_link",
    "site_link",
    "subreddit",
    "user",
    "post_title",
    "post_body",
    "content_source",
    "core_cat",
    "language",
    "general_tags",
    "downloaded",
    "local_path",
    "download_note",
    "flag",
    "isDel",
]


def normalize_record(item):
    """
    Normalize one Reddit record.
    """

    item = dict(item)

    # ---------- strings ----------

    for field in STRING_FIELDS:
        item[field] = normalize_string(item.get(field))

    # ---------- lists ----------

    for field in LIST_FIELDS:

        values = []

        for value in safe_list(item.get(field)):
            value = normalize_string(value)

            if value:
                values.append(value)

        item[field] = values

    # ---------- numeric ----------

    try:
        item["rate"] = float(item.get("rate", 0))
    except Exception:
        item["rate"] = 0.0

    return item


# --------------------------------------------------
# DataFrame Preparation
# --------------------------------------------------

def prepare_dataframe(data):
    """
    Normalize every record and return DataFrame.
    """

    normalized = [normalize_record(x) for x in data]

    return pd.DataFrame(normalized)


# --------------------------------------------------
# Unique Values
# --------------------------------------------------

def extract_unique(df, column):
    """
    Extract unique values from normal columns.
    """

    if column not in df.columns:
        return []

    values = (
        df[column]
        .dropna()
        .astype(str)
        .str.strip()
        .replace("", pd.NA)
        .dropna()
        .unique()
        .tolist()
    )

    return sorted(values)


def extract_unique_from_lists(df, column):
    """
    Extract unique values from list columns.

    Example
    -------
    categories
    positions
    star
    """

    if column not in df.columns:
        return []

    values = set()

    for row in df[column]:

        if not isinstance(row, list):
            continue

        for item in row:

            item = normalize_string(item)

            if item:
                values.add(item)

    return sorted(values)


# --------------------------------------------------
# Build Filter Cache
# --------------------------------------------------

def build_filter_cache(df):
    """
    Build every dropdown once.

    Returns
    -------
    dict
    """

    return {

        "type":
            extract_unique(df, "type"),

        "subreddit":
            extract_unique(df, "subreddit"),

        "user":
            extract_unique(df, "user"),

        "content_source":
            extract_unique(df, "content_source"),

        "star":
            extract_unique_from_lists(df, "star"),

        "core_cat":
            extract_unique(df, "core_cat"),

        "categories":
            extract_unique_from_lists(df, "categories"),

        "positions":
            extract_unique_from_lists(df, "positions"),

        "downloaded":
            extract_unique(df, "downloaded"),

        "isDel":
            extract_unique(df, "isDel"),
    }


# --------------------------------------------------
# Statistics
# --------------------------------------------------

def count_types(df):
    """
    Count each content type.

    Returns
    -------
    dict
    """

    counts = {}

    if "type" not in df.columns:
        return counts

    for t in ["gif", "img", "text", "comment"]:

        counts[t] = int((df["type"] == t).sum())

    return counts


# --------------------------------------------------
# Utility
# --------------------------------------------------

def is_text_content(item):
    """
    True if record is text/comment.
    """

    return item.get("type") in ("text", "comment")


def has_site_link(item):
    """
    True if a usable site link exists.
    """

    link = normalize_string(item.get("site_link"))

    return (
        link != ""
        and link.lower() != "notapplicable"
        and link.lower() != "none"
    )
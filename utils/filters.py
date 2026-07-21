"""
utils/filters.py

Creates the sidebar filters and applies them to the dataframe.

This module ONLY handles:
    • Sidebar widgets
    • Standard filters
    • Rating slider

Advanced query language is handled separately in
query_parser.py
"""
from __future__ import annotations

import streamlit as st
import pandas as pd


# ------------------------------------------------------------
# Sidebar
# ------------------------------------------------------------

def create_sidebar(filter_cache: dict) -> dict:
    """
    Creates the sidebar and returns all selected values.

    Returns
    -------
    dict
    """

    st.sidebar.header("🔍 Filters")

    filters = {}

    filters["type"] = st.sidebar.multiselect(
        "Type",
        filter_cache["type"]
    )

    filters["subreddit"] = st.sidebar.multiselect(
        "Subreddit",
        filter_cache["subreddit"]
    )

    filters["user"] = st.sidebar.multiselect(
        "User",
        filter_cache["user"]
    )

    filters["content_source"] = st.sidebar.multiselect(
        "Content Source",
        filter_cache["content_source"]
    )

    filters["star"] = st.sidebar.multiselect(
        "Star",
        filter_cache["star"]
    )

    filters["core_cat"] = st.sidebar.multiselect(
        "Core Category",
        filter_cache["core_cat"]
    )

    filters["categories"] = st.sidebar.multiselect(
        "Categories",
        filter_cache["categories"]
    )

    filters["positions"] = st.sidebar.multiselect(
        "Positions",
        filter_cache["positions"]
    )

    filters["downloaded"] = st.sidebar.multiselect(
        "Downloaded",
        filter_cache["downloaded"]
    )

    filters["isDel"] = st.sidebar.multiselect(
        "Deleted",
        filter_cache["isDel"]
    )

    filters["rate"] = st.sidebar.slider(
        "Rating",
        min_value=0.0,
        max_value=10.0,
        value=(0.0, 10.0),
        step=0.5,
    )

    # st.sidebar.divider()

#     filters["advanced_query"] = st.sidebar.text_area(
#         "Advanced Query",
#         height=150,
#         placeholder="""
# Examples

# type IN (gif,img)

# rate >= 7

# categories=(feet AND heels)

# user=evilsofia
# """.strip(),
#     )

    return filters


# ------------------------------------------------------------
# Internal Helpers
# ------------------------------------------------------------

def _contains_any(record_values, selected_values):
    """
    True if ANY selected value exists in record_values.
    """

    if not selected_values:
        return True

    return any(value in record_values for value in selected_values)


def _equals(value, selected):
    """
    Equality helper.
    """

    if not selected:
        return True

    return value in selected


# ------------------------------------------------------------
# Apply Sidebar Filters
# ------------------------------------------------------------

def apply_sidebar_filters(
    df: pd.DataFrame,
    filters: dict
) -> pd.DataFrame:
    """
    Apply every normal sidebar filter.

    Advanced query is NOT handled here.
    """

    if df.empty:
        return df

    result = df.copy()

    # ----------------------------
    # Simple equality columns
    # ----------------------------

    simple_columns = [
        "type",
        "subreddit",
        "user",
        "content_source",
        "core_cat",
        "downloaded",
        "isDel",
    ]

    for column in simple_columns:

        selected = filters[column]

        if selected:

            result = result[
                result[column].isin(selected)
            ]

    # ----------------------------
    # Rating
    # ----------------------------

    min_rate, max_rate = filters["rate"]

    result = result[
        (result["rate"] >= min_rate)
        &
        (result["rate"] <= max_rate)
    ]

    # ----------------------------
    # Stars
    # ----------------------------

    if filters["star"]:

        result = result[
            result["star"].apply(
                lambda x: _contains_any(
                    x,
                    filters["star"]
                )
            )
        ]

    # ----------------------------
    # Categories
    # ----------------------------

    if filters["categories"]:

        result = result[
            result["categories"].apply(
                lambda x: _contains_any(
                    x,
                    filters["categories"]
                )
            )
        ]

    # ----------------------------
    # Positions
    # ----------------------------

    if filters["positions"]:

        result = result[
            result["positions"].apply(
                lambda x: _contains_any(
                    x,
                    filters["positions"]
                )
            )
        ]

    return result.reset_index(drop=True)


# ------------------------------------------------------------
# Sorting
# ------------------------------------------------------------

def create_sort_controls():
    """
    Sorting controls shown above results.

    Returns
    -------
    (column, ascending)
    """

    left, right = st.columns([2, 1])

    with left:

        column = st.selectbox(
            "Sort By",
            [
                "rate",
                "post_title",
                "subreddit",
                "user",
                "content_source",
            ]
        )

    with right:

        ascending = st.radio(
            "Order",
            [
                "Descending",
                "Ascending",
            ],
            horizontal=False
        )

    return column, ascending == "Ascending"


def apply_sort(
    df: pd.DataFrame,
    column: str,
    ascending: bool,
) -> pd.DataFrame:
    """
    Sort dataframe.
    """

    if df.empty:
        return df

    if column not in df.columns:
        return df

    return (
        df
        .sort_values(
            by=column,
            ascending=ascending,
            kind="stable"
        )
        .reset_index(drop=True)
    )


# Instead of hardcoding every filter widget, I'd eventually generate them from a configuration table
# FILTER_CONFIG = [
#     ("type", "Type", False),
#     ("subreddit", "Subreddit", False),
#     ("user", "User", False),
#     ("content_source", "Content Source", False),
#     ("star", "Star", True),
#     ("core_cat", "Core Category", False),
#     ("categories", "Categories", True),
#     ("positions", "Positions", True),
#     ("downloaded", "Downloaded", False),
#     ("isDel", "Deleted", False),
# ]
"""
utils/display.py

Rendering functions for RedditBoard.

Contains ONLY presentation logic.

No filtering.
No parsing.
No data loading.
"""

from __future__ import annotations

import streamlit as st

from utils.helpers import (
    count_types,
    has_site_link,
    is_text_content,
)


#####################################################################
# Statistics
#####################################################################

def show_statistics(df):
    """
    Displays summary statistics.
    """

    total = len(df)

    # counts = count_types(df)

    # st.subheader(f"Results : {total}")

    # c1, c2, c3, c4, c5 = st.columns(5)
    # c1.metric("GIF", counts.get("gif", 0))
    # c2.metric("IMG", counts.get("img", 0))
    # c3.metric("TEXT", counts.get("text", 0))
    # c4.metric("COMMENT", counts.get("comment", 0))
    # c5.metric("TOTAL", total)

    counts = count_types(df)
    first,second,thrid,fourth,maintotal = st.columns(5)
    with first:
        st.write(f"**GIF:** {counts.get("gif", 0)}")
    with second:
        st.write(f"**IMG:** {counts.get("img", 0)}")
    with thrid:
        st.write(f"**TXT:** {counts.get("text", 0)}")
    with fourth:
        st.write(f"**COM:** {counts.get("comment", 0)}")
    with maintotal:
        st.write(f"**SUM:** {total}")

    # st.write(f"Results : {total}")
    # topleft, topright = st.columns([1,1])
    # with topleft:
    #     st.write(f"**GIF:** {counts.get("gif", 0)}")
    #     st.write(f"**IMG:** {counts.get("img", 0)}")
    # with topright:
    #     st.write(f"**TEXT:** {counts.get("text", 0)}")
    #     st.write(f"**COMMENT:** {counts.get("comment", 0)}")


#####################################################################
# Helpers
#####################################################################

def render_list(items):

    if not items:
        return "-"

    if isinstance(items, str):
        return items

    return ", ".join(items)


def yes_no_badge(value):

    if str(value).casefold() == "yes":
        return "🟢 Yes"

    return "⚪ No"


#####################################################################
# Card
#####################################################################

# def render_card(record):

#     with st.container(border=True):

#         #############################################################

#         st.markdown(
#             f"### [{record['post_title']}]({record['reddit_link']})"
#         )

#         #############################################################

#         left, right = st.columns([3, 1])

#         with left:

#             st.write(f"**Type:** {record['type']}")

#             st.write(f"**Subreddit:** {record['subreddit']}")

#             st.write(f"**User:** {record['user']}")

#             st.write(
#                 f"**Content Source:** {record['content_source']}"
#             )

#             st.write(
#                 f"**Core Category:** {record['core_cat']}"
#             )

#         with right:

#             # st.metric(
#             #     "Rating",
#             #     record["rate"]
#             # )
#             st.write(f"**Rating:** {record['rate']}")

#         #############################################################

#         if record["star"]:

#             st.write(
#                 f"**Stars:** {render_list(record['star'])}"
#             )

#         if record["categories"]:

#             st.write(
#                 f"**Categories:** {render_list(record['categories'])}"
#             )

#         if record["positions"]:

#             st.write(
#                 f"**Positions:** {render_list(record['positions'])}"
#             )

#         #############################################################

#         if record["general_tags"]:

#             st.write(
#                 f"**Tags:** {record['general_tags']}"
#             )

#         #############################################################

#         if is_text_content(record):

#             st.info(
#                 "Text post. Refer Local or Reddit directly."
#             )

#         else:

#             if has_site_link(record):

#                 st.link_button(
#                     "Open Source",
#                     record["site_link"]
#                 )

#         #############################################################

#         c1, c2, c3 = st.columns(3)

#         with c1:

#             st.link_button(
#                 "Open Reddit",
#                 record["reddit_link"]
#             )

#         with c2:

#             st.write(
#                 yes_no_badge(
#                     record["downloaded"]
#                 )
#             )

#         with c3:

#             st.write(
#                 yes_no_badge(
#                     record["isDel"]
#                 )
#             )

def render_card(record):

    with st.container(border=True):

        #############################################################
        # Title
        #############################################################

        st.markdown(
            f"### [{record['post_title']}]({record['reddit_link']})"
        )

        if not is_text_content(record):

            if has_site_link(record):

                st.write(
                    "Source",
                    record["site_link"]
                )

        #############################################################
        # Two-column layout
        #############################################################

        left, right = st.columns([3, 3])

        # ---------------- LEFT ---------------- #

        with left:

            st.write(f"**Type:** {record['type']}")
            st.write(f"**Subreddit:** {record['subreddit']}")
            st.write(f"**User:** {record['user']}")
            st.write(f"**Content Source:** {record['content_source']}")
            st.write(f"**Core Category:** {record['core_cat']}")
            if record["star"]:
                st.write(
                    f"**Stars:** {render_list(record['star'])}"
                )

        # ---------------- RIGHT ---------------- #

        with right:

            st.write(f"**⭐Rating:** {record['rate']}")

            if record["categories"]:
                st.write(
                    f"**Categories:** {render_list(record['categories'])}"
                )

            if record["positions"]:
                st.write(
                    f"**Positions:** {render_list(record['positions'])}"
                )

            if record["general_tags"]:
                st.write(
                    f"**Tags:** {record['general_tags']}"
                )

            if str(record["downloaded"]).casefold() == "yes":
                st.write("⬇️ **Downloaded**")
            else:
                st.write("☁️ **Not Downloaded**")

            if str(record["isDel"]).casefold() == "yes":
                st.write("🗑️ **Deleted**")
            else:
                st.write("✅ **Active**")

            
        #############################################################
        # Metadata
        #############################################################


        # if record["categories"]:
        #     st.write(
        #         f"**Categories:** {render_list(record['categories'])}"
        #     )

        # if record["positions"]:
        #     st.write(
        #         f"**Positions:** {render_list(record['positions'])}"
        #     )

        # if record["general_tags"]:
        #     st.write(
        #         f"**Tags:** {record['general_tags']}"
        #     )

        #############################################################
        # Text Posts
        #############################################################

        if is_text_content(record):

            st.info(
                "Text post. Refer Local or Reddit directly."
            )


#####################################################################
# Result List
#####################################################################

def show_results(df):
    """
    Displays every card.
    """

    if df.empty:

        st.warning(
            "No matching results."
        )

        return

    for _, row in df.iterrows():

        render_card(
            row.to_dict()
        )
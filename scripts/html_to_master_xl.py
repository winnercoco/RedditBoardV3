"""
===========================================================
RedditBoard V2
htmltoxl.py

Part 1
- Imports
- Configuration
- Dataclass
- Utilities
- HTML Loading
- Saved Item Extraction
===========================================================
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional
from urllib.parse import urlparse

import pandas as pd
from bs4 import BeautifulSoup, Tag


# ===========================================================
# Configuration
# ===========================================================
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FOLDER_PATH = BASE_DIR / "data"
HTML_PATH = DATA_FOLDER_PATH / "source_html_contents.html"
MASTER_EXCEL_PATH = DATA_FOLDER_PATH / "1-master_reddit_links_scraped.xlsx"
print("CHECKING PATHS: ")
print(BASE_DIR)
print(DATA_FOLDER_PATH)
print(HTML_PATH)
print(MASTER_EXCEL_PATH)

# INPUT_HTML = "E:\\Cryo\\Private\\OTGX\\RedditBoardApplication\\RedditBoardV2\\scripts\\source_html_contents.html"
# OUTPUT_EXCEL = "E:\\Cryo\\Private\\OTGX\\RedditBoardApplication\\RedditBoardV2\\scripts\\master_links_data.xlsx"

SUPPORTED_TYPES = {
    "gif",
    "img",
    "text",
    "comment"
}


# Excel column order
EXCEL_COLUMNS = [

    "reddit_id",
    "type",

    "reddit_link",
    "site_link",

    "subreddit",
    "user",

    "post_title",
    "post_body",

    # populated later manually
    # "content_source",
    # "star",
    # "categories",
    # "positions",
    # "language",
    # "rate",
    # "general_tags",

    # downloader fills later
    # "downloaded",
    # "local_path",
    # "download_note",

    #parser status as a columns
    "parse_status"
]


# ===========================================================
# Dataclass
# ===========================================================

@dataclass
class RedditRecord:

    reddit_id: str = ""

    type: str = ""

    reddit_link: str = ""
    site_link: str = ""

    subreddit: str = ""
    user: str = ""

    post_title: str = ""
    post_body: str = ""

    # parse_warning: str = ""
    parse_status: str = ""

    #human populated
    # content_source: str = ""
    # star: str = ""
    # categories: str = ""
    # positions: str = ""
    # language: str = ""
    # rate: str = ""
    # general_tags: str = ""

    # download_status: str = ""
    # local_path: str = ""
    # download_note: str = ""


# ===========================================================
# Utility Functions
# ===========================================================

def clean_text(text: Optional[str]) -> str:
    """
    Normalizes whitespace and HTML entities.
    """

    if text is None:
        return ""

    text = html.unescape(text)

    text = text.replace("\u200b", "")
    text = text.replace("\xa0", " ")

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def normalize_url(url: Optional[str]) -> str:
    """
    Removes whitespace and trailing slash.
    """

    if not url:
        return ""

    return url.strip().rstrip("/")


def get_domain(url: str) -> str:
    """
    Returns lowercase domain.
    """

    if not url:
        return ""

    try:
        return urlparse(url).netloc.lower()
    except Exception:
        return ""


def safe_get(tag: Optional[Tag], attribute: str) -> str:
    """
    Safely gets an attribute from a BeautifulSoup Tag.
    """

    if tag is None:
        return ""

    return tag.get(attribute, "").strip()


def first_text(tag: Optional[Tag]) -> str:
    """
    Returns stripped text from tag.
    """

    if tag is None:
        return ""

    return clean_text(tag.get_text(" ", strip=True))

def find_post_entry(saved_item: Tag) -> Optional[Tag]:
    """
    Returns the main content container (<div class="entry">)
    for a saved post/comment.

    Every extraction function should use this instead of
    calling saved_item.find(...) directly.

    Returns
    -------
    Tag | None
        The entry div if found, otherwise None.
    """

    if saved_item is None:
        return None

    # Standard old.reddit structure
    entry = saved_item.find("div", class_="entry")

    if entry is not None:
        return entry

    # Extremely defensive fallback:
    # sometimes BeautifulSoup class matching can behave
    # differently if extra classes are present.

    for div in saved_item.find_all("div"):

        classes = div.get("class", [])

        if "entry" in classes:
            return div

    return None

def get_entry(saved_item: Tag) -> Tag:
    """
    Returns the entry div.

    Raises RuntimeError if the HTML structure is unexpected.
    """

    entry = find_post_entry(saved_item)

    if entry is None:
        raise RuntimeError(
            "Could not locate <div class='entry'> "
            "for a saved Reddit item."
        )

    return entry

# ===========================================================
# HTML Loading
# ===========================================================

def load_html(filepath: str = HTML_PATH) -> BeautifulSoup:
    """
    Loads source_html_contents.html
    """

    path = Path(filepath)

    if not path.exists():
        raise FileNotFoundError(filepath)

    print(f"Loading HTML: {filepath}")

    html_text = path.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    soup = BeautifulSoup(
        html_text,
        "html.parser"
    )

    return soup


# ===========================================================
# Saved Item Extraction
# ===========================================================

def get_saved_items(soup: BeautifulSoup) -> List[Tag]:
    """
    Returns every saved reddit object.

    old.reddit stores posts/comments as
    div.thing entries.

    Removes promoted/ads if present.
    """

    things = soup.find_all("div", class_="thing")

    saved_items = []

    for thing in things:

        classes = thing.get("class", [])

        if "promoted" in classes:
            continue

        if "sitetable" in classes:
            continue

        saved_items.append(thing)

    print(f"Found {len(saved_items)} saved items.")

    return saved_items


# ===========================================================
# Helper
# ===========================================================

def create_empty_record() -> RedditRecord:
    """
    Returns an empty RedditRecord.
    """

    return RedditRecord()

"""
===========================================================
RedditBoard V2
htmltoxl.py

Part 2
- Extractions
===========================================================
"""
# ===========================================================
# Extraction Functions
# ===========================================================

def find_post_entry(saved_item: Tag) -> Tag | None:
    """
    Returns the main entry for a saved object.
    """

    entry = saved_item.find("div", class_="entry")

    if entry:
        return entry

    return None


def extract_reddit_id(saved_item: Tag) -> str:
    """
    Extract reddit id.

    Example:
        t3_1uge8g9 -> 1uge8g9

        /comments/1uge8g9/... -> 1uge8g9
    """

    fullname = safe_get(saved_item, "data-fullname")

    if fullname.startswith(("t3_", "t1_")):
        return fullname.split("_", 1)[1]

    permalink = safe_get(saved_item, "data-permalink")

    match = re.search(r"/comments/([A-Za-z0-9]+)/", permalink)

    if match:
        return match.group(1)

    return ""


def extract_reddit_link(saved_item: Tag) -> str:
    """
    Returns absolute reddit permalink.
    """

    permalink = safe_get(saved_item, "data-permalink")

    if not permalink:
        return ""

    if permalink.startswith("http"):
        return normalize_url(permalink)

    return normalize_url(
        "https://old.reddit.com" + permalink
    )


def extract_site_link(saved_item: Tag) -> str:
    """
    Returns external media link.

    Empty string if no external media exists.
    """

    url = normalize_url(
        safe_get(saved_item, "data-url")
    )

    if not url:
        return ""

    domain = get_domain(url)

    if domain.endswith("reddit.com"):
        return ""

    if domain.startswith("old.reddit"):
        return ""

    return url


def extract_subreddit(saved_item: Tag) -> str:
    """
    Returns subreddit.
    """

    subreddit = safe_get(
        saved_item,
        "data-subreddit"
    )

    if subreddit:
        return subreddit

    entry = find_post_entry(saved_item)

    if entry:

        sr = entry.find("a", class_="subreddit")

        if sr:
            return first_text(sr)

    return ""


def extract_user(saved_item: Tag) -> str:
    """
    Returns uploader / commenter username.
    """

    author = safe_get(
        saved_item,
        "data-author"
    )

    if author:
        return author

    entry = find_post_entry(saved_item)

    if entry:

        a = entry.find("a", class_="author")

        if a:
            return first_text(a)

    return ""


def extract_title(saved_item: Tag) -> str:
    """
    Returns the title.

    Posts:
        actual post title

    Comments:
        parent post title
    """

    entry = find_post_entry(saved_item)

    if entry is None:
        return ""

    fullname = safe_get(saved_item, "data-fullname")

    # ----------------------------------
    # Comments
    # ----------------------------------

    if fullname.startswith("t1_"):

        parent = saved_item.find("p", class_="parent")

        if parent:

            a = parent.find("a", class_="title")

            if a:
                return first_text(a)

    # ----------------------------------
    # Posts
    # ----------------------------------

    p_title = entry.find("p", class_="title")

    if p_title:

        a = p_title.find("a", class_="title")

        if a:

            title = first_text(a)

            if title:
                return title

    return ""


def extract_body(saved_item: Tag) -> str:
    """
    Returns body text.

    Text posts:
        Returns selftext if present.
        Otherwise returns 'TEXT POST BODY NOT SCRAPED'.

    Comments:
        Returns comment body.

    GIF/Image:
        Empty string.
    """

    entry = find_post_entry(saved_item)

    if entry is None:
        return ""

    fullname = safe_get(saved_item, "data-fullname")

    # ----------------------------------
    # Comment
    # ----------------------------------

    if fullname.startswith("t1_"):

        md = entry.find("div", class_="md")

        if md:
            return first_text(md)

        return ""

    # ----------------------------------
    # Self Post
    # ----------------------------------

    md = entry.find("div", class_="md")

    if md:

        body = first_text(md)

        # Ignore empty markdown blocks
        if body and len(body) > 5:
            return body

    # HTML contains an uninitialized expando
    expando = saved_item.find(
        "div",
        class_="expando"
    )

    if expando:
        return "TEXT POST BODY NOT SCRAPED"

    return ""

"""
===========================================================
RedditBoard V2
htmltoxl.py

Part 3
- Extractions
===========================================================
"""
# ===========================================================
# Type Detection
# ===========================================================

def detect_type(saved_item: Tag, record: RedditRecord) -> str:
    """
    Detects Reddit object type.

    Priority

        comment
        gif
        img
        text
    """

    fullname = safe_get(saved_item, "data-fullname")
    data_type = safe_get(saved_item, "data-type").lower()

    url = record.site_link.lower()

    domain = get_domain(url)

    # ----------------------------------
    # Comments
    # ----------------------------------

    if fullname.startswith("t1_"):
        return "comment"

    if data_type == "comment":
        return "comment"

    # ----------------------------------
    # GIFs
    # ----------------------------------

    if ".gif" in url:
        return "gif"

    gif_domains = [

        "redgifs.com",
        "v3.redgifs.com",
        "gfycat.com",
        "gifdeliverynetwork.com",
        "v.redd.it"

    ]

    if any(d in domain for d in gif_domains):
        return "gif"

    # ----------------------------------
    # Images
    # ----------------------------------

    image_domains = [

        "i.redd.it",
        "preview.redd.it",
        "i.imgur.com",
        "imgur.com"

    ]

    if any(d in domain for d in image_domains):
        return "img"

    if re.search(
        r"\.(jpg|jpeg|png|webp)$",
        url
    ):
        return "img"

    # ----------------------------------
    # Reddit gallery / multiple images
    # ----------------------------------
    
    if safe_get(saved_item, "data-is-gallery").lower() == "true":
        return "img"
    
    reddit_domain = safe_get(saved_item, "data-domain").lower()
    reddit_url = safe_get(saved_item, "data-url").lower()

    if (
        reddit_domain in ("reddit.com", "www.reddit.com")
        and "/gallery/" in reddit_url
    ):
        return "img"

    # ----------------------------------
    # Text
    # ----------------------------------

    return "text"


# ===========================================================
# Validation
# ===========================================================

def validate_record(record: RedditRecord) -> None:
    """
    Validates a parsed record.

    Writes warnings into

        record.parse_status

    Does NOT modify any extracted values.
    """

    warnings = []

    if not record.reddit_id:
        warnings.append("Missing Reddit ID")

    if not record.reddit_link:
        warnings.append("Missing Reddit Link")

    if not record.post_title:
        warnings.append("Missing Title")

    if record.type == "text":

        if (
            not record.post_body
            or record.post_body == "OBTAIN BODY LATER"
        ):
            warnings.append("Missing Body")

    if record.type == "comment":

        if not record.post_body:
            warnings.append("Missing Comment")

    if record.type in ("gif", "img"):

        if not record.site_link:
            warnings.append("Missing Site Link")

    if record.type not in SUPPORTED_TYPES:
        warnings.append("Unknown Type")

    if warnings:
        record.parse_status = "; ".join(warnings)
    else:
        record.parse_status = "OK"


# ===========================================================
# Record Builder
# ===========================================================

def build_record(saved_item: Tag) -> RedditRecord:
    """
    Converts one saved HTML object into
    a RedditRecord.
    """

    record = create_empty_record()

    # ----------------------------------
    # Metadata
    # ----------------------------------

    record.reddit_id = extract_reddit_id(saved_item)

    record.reddit_link = extract_reddit_link(saved_item)

    record.site_link = extract_site_link(saved_item)

    record.subreddit = extract_subreddit(saved_item)

    record.user = extract_user(saved_item)

    # ----------------------------------
    # Content
    # ----------------------------------

    record.post_title = extract_title(saved_item)

    record.post_body = extract_body(saved_item)

    # ----------------------------------
    # Type
    # ----------------------------------

    record.type = detect_type(
        saved_item,
        record
    )

    # ----------------------------------
    # Defaults
    # ----------------------------------

    # record.content_source = ""

    # record.star = ""

    # record.categories = ""

    # record.positions = ""

    # record.language = "English"

    # record.rate = ""

    # record.general_tags = ""

    # record.download_status = "No"

    # record.local_path = ""

    # record.download_note = ""

    if (
        record.type == "img"
        and "/gallery/" in record.reddit_link
    ):
        record.post_body = "MULTI IMAGE SETUP"

    if (
    record.type == "img"
    and safe_get(saved_item, "data-is-gallery").lower() == "true"
    ):
        record.post_body = "MULTI IMAGE SETUP"
    # ----------------------------------
    # Validation
    # ----------------------------------

    validate_record(record)

    return record
"""
===========================================================
RedditBoard V2
htmltoxl.py

Part 4
- save to excel
===========================================================
"""
# ===========================================================
# Excel Export
# ===========================================================

def export_excel(records: List[RedditRecord],
                 output_path: str = MASTER_EXCEL_PATH) -> None:
    """
    Export RedditRecord list to Excel.
    """

    if not records:
        print("No records to export.")
        return

    rows = []

    for record in records:
        rows.append(asdict(record))

    df = pd.DataFrame(rows)

    # Ensure column order
    for col in EXCEL_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    df = df[EXCEL_COLUMNS]

    df.to_excel(
        output_path,
        index=False
    )

    print(f"\nExported {len(df)} records.")
    print(f"Saved to: {output_path}")


# ===========================================================
# Summary
# ===========================================================

def print_summary(records: List[RedditRecord]) -> None:
    """
    Print parser summary.
    """

    total = len(records)

    gifs = sum(r.type == "gif" for r in records)
    imgs = sum(r.type == "img" for r in records)
    texts = sum(r.type == "text" for r in records)
    comments = sum(r.type == "comment" for r in records)

    warnings = sum(
        r.parse_status != "OK"
        for r in records
    )

    print("\n")
    print("=" * 45)
    print(" RedditBoard V2 Import Summary")
    print("=" * 45)

    print(f"Total Saved Items : {total}")
    print(f"GIFs              : {gifs}")
    print(f"Images            : {imgs}")
    print(f"Text Posts        : {texts}")
    print(f"Comments          : {comments}")
    print(f"Warnings          : {warnings}")

    print("=" * 45)


# ===========================================================
# Main
# ===========================================================

def main():

    print("=" * 45)
    print(" RedditBoard V2 HTML Importer")
    print("=" * 45)

    soup = load_html()

    saved_items = get_saved_items(soup)

    records: List[RedditRecord] = []

    seen_ids = set()

    duplicates = 0

    for i, item in enumerate(saved_items, start=1):

        try:

            record = build_record(item)

            # Duplicate protection
            if record.reddit_id in seen_ids:
                duplicates += 1
                continue

            seen_ids.add(record.reddit_id)

            records.append(record)

        except Exception as e:

            print(
                f"[ERROR] Item {i}: {e}"
            )

    export_excel(records)

    print_summary(records)

    print(f"Duplicates Skipped : {duplicates}")

    print("\nDone.")


# ===========================================================
# Entry Point
# ===========================================================

if __name__ == "__main__":
    main()

from pathlib import Path
import json
import pandas as pd
import streamlit as st


#--------------
#CONFIG
#--------------
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "3-reddit_links.json"


#--------------
#DATA LOADING
#--------------
def load_data():
    if DATA_PATH.exists():
        with open(DATA_PATH,"r",encoding="utf-8") as f:
            return json.load(f)
    return []

def extract_unique_fields(data,field):
    values = set() #set has only unique records
    for item in data:   #for each item in the selected data
        for val in item.get(field,[]): #for each value of each item in the data
            if val:
                values.add(val)  #add to unique set if the value exists, ignore null
    return sorted(values)


#--------------
#INITIAL LOADING
#--------------
data = load_data()
df = pd.DataFrame(data)


#--------------
#NORMALIZE LIST FIELDS
#--------------
for redditPost in data:
    redditPost["star"] = [str(x).strip() for x in redditPost.get("stars", []) if str(x).strip()]
    redditPost["categories"] = [str(x).strip() for x in redditPost.get("categories", []) if str(x).strip()]
    redditPost["positions"] = [str(x).strip() for x in redditPost.get("positions", []) if str(x).strip()]


#--------------
#STREAMLIT CONFIG
#--------------
st.set_page_config(page_title="Reddit Board V3", layout="wide")
st.title("Reddit Board V3")


#--------------
#STREAMLIT FILTERS
#--------------
st.sidebar.markdown("## 🔍 Filters")

cat_fields = ["cat_1", "cat_2", "cat_3", "cat_4", "cat_5", "cat_6"]

duration_range = st.sidebar.slider("Duration (minutes)", 0, 300, (60, 150))
rating_range = st.sidebar.slider("Rating Range", 1, 10, (1, 10))

core_cats = sorted({item.get("core_cat") for item in data if item.get("core_cat")})
core_cat_selected = st.sidebar.multiselect("Core Categories", core_cats)

all_cats = extract_unique_fields(data, "categories")
cats_selected = st.sidebar.multiselect("Other Categories", all_cats)

tag_search = st.sidebar.text_input("Tags (comma-separated)")

all_actors = extract_unique_fields(data, "star")
actors_selected = st.sidebar.multiselect("Actors", all_actors)

all_studios = sorted({item.get("content_source") for item in data if item.get("content_source")})
studio_selected = st.sidebar.multiselect("Content Source", all_studios)

all_positions = extract_unique_fields(data, "positions")
positions_selected = st.sidebar.multiselect("Positions", all_positions)


# -----------------------------
# 🎯 Filter Logic
# -----------------------------
def matches_filters(redditPost):
    try:
        duration = int(redditPost.get("duration", 0))
    except ValueError:
        duration = 0
    if not (duration_range[0] <= duration <= duration_range[1]):
        return False

    try:
        rate = float(redditPost.get("rate", 0))
    except ValueError:
        rate = 0
    if not (rating_range[0] <= rate <= rating_range[1]):
        return False

    if core_cat_selected and redditPost.get("core_cat", "") not in core_cat_selected:
        return False

    redditPost_cats = [c.lower() for c in redditPost.get("categories", [])]
    if cats_selected and not any(cat.lower() in redditPost_cats for cat in cats_selected):
        return False

    if actors_selected:
        if not any(actor in redditPost.get("stars", []) for actor in actors_selected):
            return False

    redditPost_positions = redditPost.get("positions", [])
    if positions_selected and not any(pos in redditPost_positions for pos in positions_selected):
        return False

    if studio_selected and redditPost.get("studio", "") not in studio_selected:
        return False

    if tag_search:
        tags = [t.strip().lower() for t in tag_search.split(",") if t.strip()]
        redditPost_tags = str(redditPost.get("general_tags", "")).lower()
        if not all(tag in redditPost_tags for tag in tags):
            return False

    return True

# Filter the data
filtered = list(filter(matches_filters, data))
df_filtered = pd.DataFrame(filtered)


# -----------------------------
# 🔀 Sorting Controls (strip layout)
# -----------------------------
st.markdown(f"### 🎞️ Filtered Links — {len(df_filtered)} result(s) displayed")

cols = st.columns([3, 3, 3])
with cols[0]:
    primary_sort = st.radio("Priority", ["Duration", "Rating", "None"], horizontal=True)
with cols[1]:
    dur_order = st.radio("Duration", ["Max", "Min", "None"], horizontal=True)
with cols[2]:
    rate_order = st.radio("Rating", ["Max", "Min", "None"], horizontal=True)
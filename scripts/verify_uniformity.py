from pathlib import Path
import pandas as pd
import shutil

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR/ "data"
FILE_NAME = "3-reddit_links.xlsx"
LINKS_PATH = DATA_DIR/ FILE_NAME
df = pd.read_excel(LINKS_PATH)
print("Reading file:",FILE_NAME,"\n")

def uniformity(selectedColumn):
    columnName = selectedColumn.upper()  # create printable column name
    printerString = f"========================{columnName}========================"

    print(printerString)
    print("Total rows:", len(df[selectedColumn]))

    words = (
        df[selectedColumn]
        .dropna()
        .str.split(",")
        .explode()
        .str.strip()
    )

    freq = (
        words.value_counts()
        .sort_index()  # alphabetical sorting
    )

    print(f"Total count of unique {columnName} is: {len(freq)}")
    print("=" * len(printerString))

    # Find longest term for alignment
    max_len = max(len(word) for word in freq.index)

    for word, count in freq.items():
        print(f"{word:.<{max_len + 5}}({count})")

    print("=" * len(printerString))

header = df.columns.drop(["reddit_id", "reddit_link", "site_link", "post_title", "post_body", "language", "rate", "local_path", "flag"]).tolist()

#chatgpt code
def print_centered_box(title, items):
    terminal_width = shutil.get_terminal_size().columns

    box_width = max(len(title), max(len(item) for item in items)) + 8

    border = "=" * box_width
    title_line = f"| {title.center(box_width - 4)} |"

    print(border.center(terminal_width))
    print(title_line.center(terminal_width))
    print(border.center(terminal_width))

    for item in items:
        line = f"| {item.ljust(box_width - 4)} |"
        print(line.center(terminal_width))

    print(border.center(terminal_width))

    return box_width


menu_items = [
    "1: Type",
    "2: Subreddit",
    "3: Users",
    "4: Content Source",
    "5: Star",
    "6: Core Category",
    "7: Category",
    "8: Positions",
    "9: General Tags",
    "10: Downloaded"
    "11: Download Note"
    "12: Is Deleted"
    "13: Exit"
]

while True:
    box_width = print_centered_box("Verify Uniformity of Data", menu_items)

    terminal_width = shutil.get_terminal_size().columns
    left_padding = (terminal_width - box_width) // 2

    choice = int(input(" " * left_padding + "Enter Choice: "))

    match choice:
        case 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12:
            uniformity(header[choice - 1])
        case 13:
            print("Exiting.....")
            break
        case _:
            print("Invalid Choice")
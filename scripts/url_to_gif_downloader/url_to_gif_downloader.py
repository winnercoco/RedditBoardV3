from pathlib import Path
import subprocess
import requests
import time
import random
import sys

# ===== CONFIG =====

ROOT = Path(__file__).resolve().parent.parent.parent
print("ROOT",ROOT)
URL_FILE = ROOT / "scripts" / "url_to_gif_downloader" / "urls.txt"
print("URLFILE",URL_FILE)
OUTPUT_DIR = ROOT / "downloads" / "gifs"
print("OUTPUT DIR",OUTPUT_DIR)

OUTPUT_DIR.mkdir(exist_ok=True)

REDDIT_DIR = OUTPUT_DIR / "reddit"
REDDIT_DIR.mkdir(exist_ok=True)

# ===== CHECK =====

if not URL_FILE.exists():
    print(f"Missing: {URL_FILE}")
    sys.exit(1)

# ===== LOAD URLS =====

with open(URL_FILE, "r", encoding="utf-8") as f:
    urls = [
        line.strip()
        for line in f
        if line.strip()
        and not line.strip().startswith("#")
    ]

print(f"Loaded {len(urls)} URLs\n")


# ===== HELPERS =====

def download_reddit(url: str):
    filename = url.split("/")[-1].split("?")[0]

    if not filename:
        raise RuntimeError("Could not determine filename")

    outfile = REDDIT_DIR / filename

    if outfile.exists():
        print(f"[SKIP] {filename}")
        return

    print(f"[REDDIT] {filename}")

    with requests.get(
        url,
        stream=True,
        timeout=60,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    ) as r:

        r.raise_for_status()

        with open(outfile, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)

    print(f"  Saved -> {outfile.name}")


def download_ytdlp(url: str):
    print(f"[YT-DLP] {url}")

    cmd = [
        "yt-dlp",

        "--sleep-interval", "3",
        "--max-sleep-interval", "8",
        "--concurrent-fragments", "1",

        "--continue",

        "--retries", "5",
        "--fragment-retries", "5",

        "--merge-output-format", "mp4",

        "-o",
        str(
            OUTPUT_DIR /
            "%(extractor)s" /
            "%(upload_date>%Y-%m-%d)s_%(title).120B_[%(id)s].%(ext)s"
        ),

        url,
    ]

    subprocess.run(cmd, check=True)


# ===== MAIN =====

for idx, url in enumerate(urls, start=1):

    print()
    print("=" * 80)
    print(f"{idx}/{len(urls)}")
    print(url)

    try:

        lower = url.lower()

        if "i.redd.it" in lower:
            download_reddit(url)

        elif "redgifs.com" in lower:
            download_ytdlp(url)

        else:
            print("[SKIP] Unsupported domain")

    except Exception as e:
        print(f"[ERROR] {e}")

    sleep_time = random.randint(1, 2)
    print(f"Sleeping {sleep_time}s...")
    time.sleep(sleep_time)

print("\nDone.")
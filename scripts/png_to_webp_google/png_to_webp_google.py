from pathlib import Path
import subprocess

BASE_DIR = Path(__file__).resolve().parent
PNG_DIR = BASE_DIR / "add_png_files_here"
WEBP_DIR = BASE_DIR /  "get_webp_files_here"
CWEBP_PATH = BASE_DIR / "google_converter_engine" / "bin" / "cwebp.exe"

print(BASE_DIR)
print(PNG_DIR)
print(WEBP_DIR)
print(CWEBP_PATH)

for img in PNG_DIR.iterdir():
    if img.suffix.lower() not in {".png", ".jpg", ".jpeg"}:
        continue

    output = WEBP_DIR / f"{img.stem}.webp"

    subprocess.run(
        [str(CWEBP_PATH), "-q", "90", str(img), "-o", str(output)],
        check=True
    )

    print(f"Converted: {img.name}")
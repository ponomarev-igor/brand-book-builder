#!/usr/bin/env python3
"""
Verify a Google Font actually supports Cyrillic before recommending it.

Many popular display fonts (Bebas Neue, Anton, Archivo Black, Righteous...)
are Latin-only on Google Fonts despite "looking" like they should cover
everything. Never assume from the name or from memory -- check the real
glyph table.

Usage:
    python3 check_cyrillic.py "Space Grotesk"
    python3 check_cyrillic.py "Golos Text" --weight 700

Exits 0 and prints CYRILLIC / latin-only / FETCH_FAIL.
If CYRILLIC, prints the path to the downloaded .ttf so it can be reused
directly for a rendered preview (e.g. with Pillow) instead of re-downloading.
"""
import argparse
import os
import re
import sys
import urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_font_cache")


def fetch_css(family_url, weight):
    url = f"https://fonts.googleapis.com/css2?family={family_url}:wght@{weight}&display=swap"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=15).read().decode()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("family", help='Google Fonts family name, e.g. "Golos Text"')
    ap.add_argument("--weight", default="400")
    args = ap.parse_args()

    family_url = args.family.strip().replace(" ", "+")
    os.makedirs(CACHE_DIR, exist_ok=True)

    try:
        css = fetch_css(family_url, args.weight)
    except Exception as e:
        print(f"FETCH_FAIL: {e}")
        sys.exit(1)

    m = re.search(r"url\((https://fonts\.gstatic\.com[^)]+)\)", css)
    if not m:
        print("NO_URL: font family not found on Google Fonts, or weight unavailable")
        sys.exit(1)

    path = os.path.join(CACHE_DIR, f"{family_url}-{args.weight}.ttf")
    urllib.request.urlretrieve(m.group(1), path)

    from fontTools.ttLib import TTFont

    font = TTFont(path)
    cmap = font.getBestCmap()
    # ИЖЩЁй covers letters that are commonly missing even in partial Cyrillic subsets
    has_cyrillic = all(ord(c) in cmap for c in "ИЖЩЁй")

    if has_cyrillic:
        print(f"CYRILLIC: {path}")
    else:
        print(f"latin-only: {args.family} does not cover Cyrillic, do not use it for a Cyrillic brand")


if __name__ == "__main__":
    main()

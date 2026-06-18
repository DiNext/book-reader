#!/usr/bin/env python3
"""Build a static, read-only copy of the reader for GitHub Pages.

GitHub Pages serves static files only — there is no Python backend, so the
editing API is unavailable there and the app stays read-only by design.

This copies the front-end plus every chapter into ./docs, which you point
GitHub Pages at (Settings → Pages → Source: main branch, /docs folder).

Usage:  python3 build.py
"""
import json
import os
import shutil

from server import BOOK_DIR, HERE, list_files

OUT = os.path.join(HERE, "docs")


def main():
    if not os.path.isdir(BOOK_DIR):
        raise SystemExit(f"Book folder not found: {BOOK_DIR}")

    # Fresh output dir.
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)

    # Front-end shell + vendored marked.
    shutil.copy2(os.path.join(HERE, "index.html"), os.path.join(OUT, "index.html"))
    shutil.copytree(os.path.join(HERE, "vendor"), os.path.join(OUT, "vendor"))

    # Chapters → docs/content/<rel>, and a manifest the static app reads.
    # Russian-only edition: ship just the ru/ chapters (no EN on the public site).
    files = [f for f in list_files() if f.split("/")[0] == "ru"]
    for rel in files:
        dst = os.path.join(OUT, "content", *rel.split("/"))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(os.path.join(BOOK_DIR, *rel.split("/")), dst)
    with open(os.path.join(OUT, "files.json"), "w", encoding="utf-8") as fh:
        json.dump(files, fh)

    # Stop Jekyll from processing/ignoring the files.
    open(os.path.join(OUT, ".nojekyll"), "w").close()

    print(f"Built static site → {OUT}")
    print(f"  {len(files)} chapters, edit disabled (read-only).")
    print("  Commit & push, then set GitHub Pages source to: main /docs")


if __name__ == "__main__":
    main()

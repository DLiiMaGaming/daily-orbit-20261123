#!/usr/bin/env python3
"""The Daily Orbit - Monday 23 November 2026.

Copies the front-page image (drawn by gen.py in this repository) to
the output directory as entry.png. Standard library only.
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")


def main():
    src = os.path.join(HERE, "entry.png")
    os.makedirs(OUT, exist_ok=True)
    shutil.copyfile(src, os.path.join(OUT, "entry.png"))


if __name__ == "__main__":
    main()

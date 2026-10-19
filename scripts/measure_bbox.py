#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Measure a character's composition baseline in a (preferably transparent or
keyed) PNG: bounding box, L/R/T/B margins, occupancy %, bottom padding, center.

Set ONE baseline from the anchor and enforce it on every generated asset so they
don't jump in a sprite pack.
"""
import argparse
import sys
from PIL import Image


def measure(path):
    im = Image.open(path).convert("RGBA")
    w, h = im.size
    px = im.load()
    minx, miny, maxx, maxy = w, h, 0, 0
    found = False
    for y in range(h):
        for x in range(w):
            if px[x, y][3] > 16:
                found = True
                if x < minx:
                    minx = x
                if x > maxx:
                    maxx = x
                if y < miny:
                    miny = y
                if y > maxy:
                    maxy = y
    if not found:
        return None
    L, R, T, B = minx, w - 1 - maxx, miny, h - 1 - maxy
    cw, ch = maxx - minx + 1, maxy - miny + 1
    occ_w, occ_h = cw / w, ch / h
    return dict(size=(w, h), bbox=(minx, miny, maxx, maxy),
                L=L, R=R, T=T, B=B,
                occupancy_pct=(round(occ_w * 100, 1), round(occ_h * 100, 1)),
                bottom_padding=B, center_x=(minx + maxx) / 2,
                char_w_px=cw, char_h_px=ch)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    a = ap.parse_args()
    m = measure(a.src)
    if not m:
        print("no opaque pixels found")
        return 1
    print("size           : %dx%d" % m["size"])
    print("bbox           : %s" % (m["bbox"],))
    print("L / R / T / B   : %d / %d / %d / %d" % (m["L"], m["R"], m["T"], m["B"]))
    print("occupancy %%      : W %.1f  H %.1f" % m["occupancy_pct"])
    print("bottom padding  : %d" % m["bottom_padding"])
    print("center x        : %.1f" % m["center_x"])
    return 0


if __name__ == "__main__":
    sys.exit(main())

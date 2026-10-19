#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Chroma-key a solid key color to transparent using DUAL criteria:
  (a) per-pixel color distance to the key color <= --dist
  (b) pixel is connected to the frame border (flood fill from edges)

Pixels satisfying both become transparent (the background).

Then a cleanup pass keeps only the LARGEST connected foreground component, so
small disconnected specks and a watermark sitting ON the background (a different
color from the key, hence not caught by (a)) are dropped too.
"""
import argparse
import sys
from collections import deque
from PIL import Image


def hex2rgb(s):
    s = s.lstrip("#")
    if len(s) == 3:
        s = "".join(c * 2 for c in s)
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def cdist(a, b):
    return sum((a[i] - b[i]) ** 2 for i in range(3)) ** 0.5


def key(im, key_rgb, dist):
    im = im.convert("RGBA")
    w, h = im.size
    px = im.load()
    # (a)+(b): flood from border through key-colored pixels
    border_key = [[False] * w for _ in range(h)]
    q = deque()
    for x in range(w):
        for y in (0, h - 1):
            if cdist(px[x, y][:3], key_rgb) <= dist:
                border_key[y][x] = True
                q.append((x, y))
    for y in range(h):
        for x in (0, w - 1):
            if cdist(px[x, y][:3], key_rgb) <= dist:
                border_key[y][x] = True
                q.append((x, y))
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and not border_key[ny][nx]:
                if cdist(px[nx, ny][:3], key_rgb) <= dist:
                    border_key[ny][nx] = True
                    q.append((nx, ny))

    # foreground = not keyed
    fg = [[not border_key[y][x] for x in range(w)] for y in range(h)]

    # keep only the largest connected foreground component
    comp = [[-1] * w for _ in range(h)]
    best = (-1, -1)  # (size, id)
    cid = 0
    for y in range(h):
        for x in range(w):
            if fg[y][x] and comp[y][x] == -1:
                cid += 1
                size = 0
                q2 = deque([(x, y)])
                comp[y][x] = cid
                while q2:
                    cx, cy = q2.popleft()
                    size += 1
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = cx + dx, cy + dy
                        if 0 <= nx < w and 0 <= ny < h and fg[ny][nx] and comp[ny][nx] == -1:
                            comp[ny][nx] = cid
                            q2.append((nx, ny))
                if size > best[0]:
                    best = (size, cid)

    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    opx = out.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if fg[y][x] and comp[y][x] == best[1]:
                opx[x, y] = (r, g, b, a)
            else:
                opx[x, y] = (r, g, b, 0)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--key", default="#06EB0D")
    ap.add_argument("--dist", type=float, default=60)
    a = ap.parse_args()
    im = Image.open(a.src)
    out = key(im, hex2rgb(a.key), a.dist)
    out.save(a.dst)
    print("keyed  : %s -> %s  (key=%s dist=%.0f)" % (a.src, a.dst, a.key, a.dist))
    return 0


if __name__ == "__main__":
    sys.exit(main())

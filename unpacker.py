#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Tsuga
"""Get your data out of a needle: one Vortex file per entry.

unpacker.py FILE.needle [OUTDIR]

$ python3 unpacker.py 1234.needle
1234/rx__g.vortex
$ vx tree layout 1234/rx__g.vortex
"""

from concurrent.futures import ThreadPoolExecutor
import mmap
import os
import subprocess
import sys


def sections(buf):
    off, i = [], buf.find(b"VTXF")
    while i != -1:
        off.append(i)
        i = buf.find(b"VTXF", i + 1)
    return [(off[k], off[k + 1] + 4) for k in range(0, len(off), 2)]


def name_of(path):
    out = subprocess.run(
        ["vx", "tree", "layout", path], capture_output=True, text=True, check=True
    ).stdout
    head = out.split("\n", 1)[0]
    dtype = head[head.index("{") + 1 : head.rindex("}")]
    cols = [c.split("=")[0].strip() for c in dtype.split(",")]
    return os.path.commonprefix([c for c in cols if c != "timestamp"]).rstrip(".")


def unpack(buf, sec, outdir):
    tmp = os.path.join(outdir, f".{sec[0]}.vortex")
    with open(tmp, "wb") as g:
        g.write(buf[sec[0] : sec[1]])
    dst = os.path.join(outdir, name_of(tmp).lstrip("/") + ".vortex")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    os.replace(tmp, dst)
    return dst


def check_vx_installed():
    try:
        subprocess.run(
            ["vx", "--version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError:
        sys.exit(
            "Error: 'vx' command not found. Please install Vortex (https://docs.vortex.dev/getting-started/install) and ensure it is in your PATH."
        )
    except subprocess.CalledProcessError as e:
        sys.exit(f"Error: 'vx' command failed with error: {e.stderr.decode().strip()}")


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)

    check_vx_installed()

    path = sys.argv[1]
    outdir = sys.argv[2] if len(sys.argv) > 2 else os.path.basename(path).split(".")[0]
    os.makedirs(outdir, exist_ok=True)

    with (
        open(path, "rb") as f,
        mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as buf,
    ):
        with ThreadPoolExecutor(8) as pool:
            print(*pool.map(lambda s: unpack(buf, s, outdir), sections(buf)), sep="\n")


if __name__ == "__main__":
    main()

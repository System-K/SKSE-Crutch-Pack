#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Resolve Address Library IDs against a SkyrimSE.exe and dump the bytes at hook sites.

Usage: check_hooks.py <versionlib-*.bin> <SkyrimSE.exe> ID+OFFSET[:expect] ...
Example: check_hooks.py versionlib-1-7-104-0.bin SkyrimSE.exe 14988+0x6E:E8
"""
import struct, sys


def load_al(path):
    d = open(path, "rb").read()
    fmt = struct.unpack_from("<i", d, 0)[0]
    if fmt != 5:
        raise SystemExit(f"only AL v5 supported, got {fmt}")
    ver = struct.unpack_from("<4i", d, 4)
    ptr, dfmt, count = struct.unpack_from("<3i", d, 4 + 16 + 64)
    if dfmt != 0:
        raise SystemExit(f"packed v5 not supported (format {dfmt})")
    offs = struct.unpack_from(f"<{count}I", d, 0x60)
    return ver, offs


def load_pe(path):
    d = open(path, "rb").read()
    pe = struct.unpack_from("<I", d, 0x3C)[0]
    nsec = struct.unpack_from("<H", d, pe + 6)[0]
    opt = struct.unpack_from("<H", d, pe + 20)[0]
    sec = pe + 24 + opt
    secs = []
    for i in range(nsec):
        name, vsize, va, rsize, raw = struct.unpack_from("<8sIIII", d, sec + 40 * i)
        secs.append((name.rstrip(b"\0").decode(), va, vsize, raw, rsize))
    return d, secs


def rva2file(secs, rva):
    for name, va, vsize, raw, rsize in secs:
        if va <= rva < va + max(vsize, rsize):
            return raw + (rva - va), name
    return None, None


def main():
    ver, offs = load_al(sys.argv[1])
    exe, secs = load_pe(sys.argv[2])
    print("address library", ".".join(map(str, ver)), len(offs), "ids")
    bad = 0
    for spec in sys.argv[3:]:
        site, _, expect = spec.partition(":")
        idpart, _, add = site.partition("+")
        aid, add = int(idpart, 0), int(add or "0", 0)
        base = offs[aid] if aid < len(offs) else 0
        if not base:
            print(f"{spec:<22} ID NOT IN ADDRESS LIBRARY")
            bad += 1
            continue
        fo, sname = rva2file(secs, base + add)
        b = exe[fo:fo + 8] if fo is not None else b""
        ok = not expect or b.hex().upper().startswith(expect.upper())
        bad += not ok
        print(f"{spec:<22} rva {base:#09x}+{add:#x} [{sname}] bytes {b.hex(' ')}  {'ok' if ok else 'MISMATCH'}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()

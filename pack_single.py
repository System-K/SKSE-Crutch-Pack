#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Builds stand-alone hotfix packages (DLL archive + source archive) for mods
whose source has no explicit licence. These are only uploaded once the original
author has given permission, so they stay out of the Crutch Pack FOMOD.

Usage: pack_single.py [key ...]   (no key = all)
"""
import hashlib, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # skse-hotfixes/
OUT = Path(__file__).resolve().parent / "single"
GAME = "Skyrim SE 1.7.104 (Address Library v5, SKSE 2.3.1)"

MODS = [
    dict(key="SpreadOfFire", title="Spread of Fire", nexus=173703, ver="1", author="Alhimik",
         repo="spreadoffire", dlls=["build/linux/BowSpread.dll"], submodules=[],
         requires=["SKSE 2.3.1", "Address Library for SKSE Plugins (v5, for 1.7.99+)",
                   "Spread of Fire (the original mod) - keep it installed for BowSpread.ini and its scripts"],
         what=["Build system replaced with a minimal CMake/vcpkg setup against CommonLibSSE-NG 11 (the original could not read Address Library v5).",
               "Bug fix: the arrow hook (ArrowProjectile vtable, UpdateImpl slot 0xAB) now chains to the arrow's own original function. "
               "Upstream dropped it and called MissileProjectile::UpdateImpl for arrows, which also cut off other plugins hooking the same slot.",
               "RE::DebugNotification -> RE::SendHUDMessage::ShowHUDMessage (renamed in NG 11).",
               "No changes to the spread logic or the INI settings."]),
    dict(key="PMCM", title="PMCM", nexus=168551, ver="1.3", author="PaulMixMod",
         repo="pmcm", dlls=["build/linux/PMCM.dll"], submodules=["extern/DKUtil"],
         requires=["SKSE 2.3.1", "Address Library for SKSE Plugins (v5, for 1.7.99+)",
                   "PrismaUI (Nexus 148718)",
                   "PMCM (the original mod) - keep it installed for its UI files"],
         what=["The Nexus download only contains src/; a CMake/vcpkg build was added around it, against CommonLibSSE-NG 11.",
               "include/PrismaUI/PrismaUI_API.h is the official API header from PrismaUI-SKSE/framework; DKUtil (MIT) is a git submodule.",
               "Three NG 11 API updates: ButtonEvent::GetIDCode(), SKSE::WinAPI -> REX::W32, SKSEPluginLoad with generated version data. No behaviour changes."]),
]


def sh(*a, cwd=None):
    return subprocess.run(a, cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


def build(m):
    repo = ROOT / m["repo"]
    branch = "hotfix/1.7.104"
    commit = sh("git", "rev-parse", "--short", branch, cwd=repo)
    if sh("git", "status", "--porcelain", "--untracked-files=no", cwd=repo):
        sys.exit(f"{m['repo']}: working tree not clean")
    name = f"SKSE Hotfix - {m['title']} {m['ver']}-1.7.104"
    out = OUT / m["key"]
    if out.exists():
        shutil.rmtree(out)
    stage = out / "stage"
    plugins = stage / "SKSE" / "Plugins"
    plugins.mkdir(parents=True)
    hashes = []
    for d in m["dlls"]:
        src = repo / d
        shutil.copy2(src, plugins / src.name)
        hashes.append((src.name, hashlib.sha256(src.read_bytes()).hexdigest()))

    nexus = f"https://www.nexusmods.com/skyrimspecialedition/mods/{m['nexus']}"
    readme = "\n".join([
        f"# {name}", "",
        f"Unofficial hotfix of **{m['title']}** by **{m['author']}** ([Nexus {m['nexus']}]({nexus}), version {m['ver']}) for {GAME}.",
        "All credit for the mod goes to its author. This is a rebuild so the mod runs on the current game version",
        "until the author releases an update; it will be withdrawn when that happens or if the author asks.", "",
        "The original source has no explicit licence; this package is published with the author's permission.", "",
        "## Requirements", "", *[f"- {r}" for r in m["requires"]], "",
        "## Installation", "",
        "Install the original mod, then this package and let it overwrite the DLL.",
        "Only the DLL is replaced; everything else comes from the original.", "",
        "## What changed", "", *[f"- {w}" for w in m["what"]], "",
        "## Build", "",
        f"Source: branch `{branch}`, commit `{commit}` - the complete source is in the separate download \"{name} - Source\".",
        "The first commit of the branch is the source exactly as published on Nexus, so the hotfix is one readable diff.",
        "Cross-compiled on Linux with clang-cl + xwin (MSVC CRT / Windows SDK) and vcpkg against CommonLibSSE-NG v11.0.0, static CRT.", "",
        "| File | SHA-256 |", "|---|---|", *[f"| {n} | `{h}` |" for n, h in hashes], "",
    ])
    (stage / f"{m['key']} - Hotfix README.md").write_text(readme)
    (out / "README.md").write_text(readme)

    archive = out / f"{name}.7z"
    sh("7z", "a", "-mx=9", str(archive), ".", cwd=stage)

    # Source: git archive of the branch incl. its history-free submodule contents
    src_stage = out / "source-stage"
    src_root = src_stage / m["repo"]
    src_root.mkdir(parents=True)
    tar = out / "src.tar"
    sh("git", "archive", "--format=tar", "-o", str(tar), branch, cwd=repo)
    sh("tar", "-xf", str(tar), "-C", str(src_root))
    tar.unlink()
    for sub in m["submodules"]:
        subrepo = repo / sub
        subcommit = sh("git", "rev-parse", f"{branch}:{sub}", cwd=repo)
        target = src_root / sub
        target.mkdir(parents=True, exist_ok=True)
        star = out / "sub.tar"
        sh("git", "archive", "--format=tar", "-o", str(star), subcommit, cwd=subrepo)
        sh("tar", "-xf", str(star), "-C", str(target))
        star.unlink()
    patch = sh("git", "diff", f"upstream..{branch}", "--", ".", ":(exclude)extern", cwd=repo)
    (src_stage / "hotfix.diff").write_text(patch + "\n")
    shutil.copy2(out / "README.md", src_stage / "README.md")
    src_archive = out / f"{name} - Source.7z"
    sh("7z", "a", "-mx=9", str(src_archive), ".", cwd=src_stage)
    shutil.rmtree(stage)
    shutil.rmtree(src_stage)
    for a in (archive, src_archive):
        print(a, a.stat().st_size)


if __name__ == "__main__":
    keys = set(sys.argv[1:])
    for m in MODS:
        if not keys or m["key"] in keys:
            build(m)

#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Build the SKSE Crutch Pack FOMOD from the hotfix repos (SKSE-Hotfixes project).

Data-driven: add a fix to FIXES and run again. Every DLL is taken from the repo build that was
tested in-game (the hashes are written to the package's file list so they can be checked).
"""
import hashlib, html, shutil, subprocess
from pathlib import Path

VERSION = "1.2.0"
REPOS = Path("/mnt/h/dev/modding/skse-hotfixes")
OUT = REPOS / "crutch-pack"
STAGE = OUT / "stage"
NAME = "SKSE Crutch Pack"
SRC = OUT / "source-stage"
BUILDING = """# Building the SKSE Crutch Pack

Each zip is a snapshot of one hotfix branch (upstream repository + the changes for 1.7.104).
All DLLs were cross-compiled on Linux with clang-cl + xwin (MSVC CRT / Windows SDK) and vcpkg, against
CommonLibSSE-NG v11.0.0 (https://github.com/alandtse/CommonLibVR, branch ng, tag v11.0.0), static CRT.
Vendored copies of CommonLib in the upstream repos (lib/commonlibsse-ng) were not used and are omitted.
Exception: sandboxwhenidle (How to sit) is built like upstream, against powerofthree's CommonLibSSE fork
(https://github.com/powerof3/CommonLibSSE, commit 3adc3270, git submodule extern/CommonLibSSE).
Exception: survivalcontrolpanel is the authors' own unreleased upstream HEAD (466bc7a, version 1.1.3), built against
its Exit-9B CommonLibSSE submodule (commit 83ea4b9d) with patches/commonlibsse-clang.patch (5 compile fixes for
clang-cl, no behaviour change). Submodule contents are not part of the snapshot; build-linux.sh applies the patch.
On Windows the projects build with their usual CMake/vcpkg or xmake setup when pointed at CommonLibSSE-NG 11.
Each snapshot's git history is not included; the changes against upstream are listed in the mod's README.
"""

FIXES = [
    dict(key="RechargeFramework", title="Recharge Framework", nexus=157327, ver="1.0.2", author="shazdeh2",
         repo="recharge-framework", dlls=["build/linux-clangcl-release/RechargeFramework.dll"], lic="MIT",
         what="Rebuilt against a current CommonLibSSE-NG. The original could not read the new Address Library and stopped the game at start."),
    dict(key="LLOS", title="Leveled List Object Swapper", nexus=132765, ver="1.3.0", author="Eudalus",
         repo="llos", dlls=["build/linux-clangcl-release/w_LeveledListObjectSwapper.dll"], lic="MIT",
         what="Rebuilt against a current CommonLibSSE-NG (new Address Library format). No behaviour changes."),
    dict(key="PapyrusMessageBox", title="Papyrus MessageBox - SKSE NG", nexus=83578, ver="1.0.0", author="mrowrpurr",
         repo="messagebox", dlls=["build/linux-clangcl-release/SkyrimScripting.MessageBox.dll"], lic="0BSD",
         what="Rebuilt against a current CommonLibSSE-NG; two API calls updated for 1.7.99 (message queue, menu run flag)."),
    dict(key="CheatCodes", title="CHEAT CODES", nexus=174465, ver="1", author="cavy8",
         repo=["cheatcodemenu", "cheatpack"], dlls=["build/linux-clangcl-release/CheatCodeMenu.dll", "build/linux-clangcl-release/CheatPack.dll"],
         lic="LGPL-2.1 (menu) / GPL-3.0 (pack)",
         what="Both DLLs rebuilt. Fixes a crash in the image-space cheats (1.7.99 packs the effect index differently) and the changed button-event layout."),
    dict(key="Apprentice", title="Apprentice - A Class Overhaul", nexus=169288, ver="1.1.0", author="Simon Magus and LambdaCDM",
         repo="apprentice", dlls=["build/linux-clangcl-release/apprentice.dll"], lic="GPL-3.0",
         what="Rebuilt against a current CommonLibSSE-NG (same intent as the author's unreleased 1.7 update branch). No source changes."),
    dict(key="LightingToolkit", title="Lighting Toolkit", nexus=150279, ver="0.10.0", author="shdowraithe101",
         repo="lightingtoolkit", dlls=["build/linux/InGameLightingToolkit.dll"], lic="MIT",
         what="Ported to CommonLibSSE-NG 11. Fixes a silent 1.7.99 bug (the player's cell-change event source moved), the new input-event layout and a trampoline allocation crash at start."),
    dict(key="HairColourSync", title="Hair Colour Sync NG", nexus=156414, ver="1.3.1", author="jg1, NG port by kingeric1992",
         repo="haircoloursync", dlls=["build/linux-clangcl-release/HairColourSyncNg.dll"], lic="MIT",
         what="Rebuilt against CommonLibSSE-NG 11 (the original could not read the new Address Library); one renamed geometry field updated. The armour hook site is unchanged in 1.7.104."),
    dict(key="HowToSit", title="How to sit sleep meditate and fall... anywhere", nexus=167371, ver="1.8.9",
         author="Preguissoso (DLL based on powerofthree's Sandbox When Idle)",
         repo="sandboxwhenidle", dlls=["build/linux/Actions.dll"], lic="GPL-3.0",
         what="Replacement Actions.dll: powerofthree's Sandbox When Idle (already updated for 1.7.99 by po3) plus a reimplementation of the mod's Papyrus functions (NSA_SandBox), packages, mod events and input rules. Install over the original."),
    dict(key="SurvivalControlPanel", title="Survival Control Panel", nexus=41891, ver="1.1.2", author="Parapets and colinswrath",
         repo="survivalcontrolpanel", dlls=["build/linux/SurvivalControlPanel.dll"], lic="MIT",
         what="The authors' own update (1.1.3 on GitHub, Address Library v5, September 2026) built as-is - it is not on Nexus yet. Only the DLL is replaced; ESP, BSA and scripts of 1.1.2 are unchanged."),
    dict(key="ModelSwapper", title="Model Swapper", nexus=136461, ver="1.3", author="Thiago099",
         repo="modelswapper", dlls=["build/linux-clangcl-release/ModelSwapper.dll"], lic="MIT",
         what="Source of 1.3 rebuilt against CommonLibSSE-NG 11 (Address Library v5). No code change. Only the DLL is replaced; keep the original ModelSwapper.ini."),
    dict(key="FactionWardrobe", title="Faction Wardrobe", nexus=195450, ver="1", author="BlackKnight19 (GitHub: Theslushbeast)",
         repo="factionwardrobe", dlls=["build/linux-clangcl-release/FactionWardrobe.dll"], lic="GPL-3.0",
         what="Rebuilt against CommonLibSSE-NG 11; the runtime check now accepts 1.6.1170 and newer (it refused 1.7.x, which made S.L.A.C.K. crash). The menu is in the SKSE Menu Framework (F1). Log notes added when SMF is missing."),
    dict(key="UniversalArrowSpin", title="Universal Arrow Spin", nexus=171136, ver="1.1", author="RavenKZP",
         repo="arrowspin", dlls=["build/linux/UniversalArrowSpin.dll"], lic="MIT",
         what="Source of 1.1 rebuilt against CommonLibSSE-NG 11 (Address Library v5). No code change."),
]


def sh(*a, cwd=None):
    return subprocess.run(a, cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    shutil.rmtree(STAGE, ignore_errors=True)
    docs = STAGE / "Docs" / "SKSE" / "Plugins" / "SKSE Crutch Pack"
    (docs / "Licenses").mkdir(parents=True)
    shutil.rmtree(SRC, ignore_errors=True)
    SRC.mkdir(parents=True)
    (SRC / "BUILDING.md").write_text(BUILDING)
    (STAGE / "fomod").mkdir(parents=True)
    rows = []
    for i, f in enumerate(FIXES, 1):
        folder = STAGE / f"{i:02d} {f['title']}"
        dll_dir = folder / "SKSE" / "Plugins"
        dll_dir.mkdir(parents=True)
        repos = f["repo"] if isinstance(f["repo"], list) else [f["repo"]]
        pairs = zip(repos * len(f["dlls"]) if len(repos) == 1 else repos, f["dlls"])
        hashes = []
        for repo, dll in pairs:
            src = REPOS / repo / dll
            shutil.copy2(src, dll_dir / src.name)
            hashes.append(f"{src.name} sha256 {sha(src)[:16]}")
        for repo in repos:
            r = REPOS / repo
            lic = next(p for p in sorted(r.iterdir()) if p.name.upper().startswith("LICEN"))
            shutil.copy2(lic, docs / "Licenses" / f"{repo}-{lic.name}")
            commit = sh("git", "rev-parse", "--short", "HEAD", cwd=r)
            url = sh("git", "remote", "get-url", "origin", cwd=r)
            # complete corresponding source of exactly what ships (needed for GPL/LGPL, harmless for MIT/0BSD)
            # vendored third-party trees (lib/commonlibsse-ng with OpenVR samples, screenshots) are left out:
            # the DLLs were built against CommonLibSSE-NG v11.0.0 instead (see BUILDING.md)
            sh("git", "archive", "--format=zip", f"--prefix={repo}/", "-o",
               str(SRC / f"{repo}-{commit}.zip"), "HEAD", "--", ".", ":!lib", ":!images", cwd=r)
            f.setdefault("src", []).append(f"{url} + hotfix branch {commit}")
        f["hashes"] = hashes
        f["folder"] = folder.name
        rows.append(f)

    lines = [f"# {NAME} {VERSION}", "",
             "Temporary rebuilds of SKSE plugins that broke with Skyrim 1.7.99 / 1.7.104 - a crutch until the",
             "authors release their own updates. Each fix replaces ONLY the DLL: install the original mod as usual",
             "and let this pack overwrite it (place the Crutch Pack below / after the originals).",
             "When an author releases an official update, remove that fix and use the original again.", "",
             "Built for Skyrim SE 1.7.104 (Address Library v5, SKSE 2.3.1). Not for 1.5.97 / 1.6.x.", "",
             "| Fix | Original (Nexus) | Original author | Licence | What changed |", "|---|---|---|---|---|"]
    for f in rows:
        lines.append(f"| {f['title']} | [{f['nexus']}](https://www.nexusmods.com/skyrimspecialedition/mods/{f['nexus']}) v{f['ver']} "
                     f"| {f['author']} | {f['lic']} | {f['what']} |")
    lines += ["", "## Files", ""]
    for f in rows:
        lines.append(f"- {f['folder']}: " + ", ".join(f["hashes"]))
    lines += ["", "## Source", "",
              f"The complete source of every DLL is in the separate download \"{NAME} {VERSION} - Source\"",
              "(git snapshots of the hotfix branches, see BUILDING.md there). Upstream repositories:", ""]
    for f in rows:
        for s in f["src"]:
            lines.append(f"- {f['title']}: {s}")
    lines += ["", "All credit for these plugins goes to their authors. Licences: see Licenses/.", ""]
    readme = "\n".join(lines)
    (docs / "README.md").write_text(readme)
    (OUT / f"README-{VERSION}.md").write_text(readme)

    (STAGE / "fomod" / "info.xml").write_text(f"""<?xml version="1.0" encoding="UTF-8"?>
<fomod>
  <Name>{NAME}</Name>
  <Author>System-K</Author>
  <Version>{VERSION}</Version>
  <Description>Temporary 1.7.104 rebuilds of SKSE plugins until their authors update them.</Description>
  <Groups><element>Utilities</element><element>Patches</element></Groups>
</fomod>
""")
    plugins = []
    for f in rows:
        desc = html.escape(f"Needs: {f['title']} v{f['ver']} by {f['author']} (Nexus {f['nexus']}). "
                           f"{f['what']} Licence: {f['lic']}.")
        plugins.append(f"""            <plugin name="{html.escape(f['title'])}">
              <description>{desc}</description>
              <files><folder source="{html.escape(f['folder'])}" destination="" priority="0"/></files>
              <typeDescriptor><type name="Optional"/></typeDescriptor>
            </plugin>""")
    (STAGE / "fomod" / "ModuleConfig.xml").write_text(f"""<?xml version="1.0" encoding="UTF-8"?>
<config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://qconsulting.ca/fo3/ModConfig5.0.xsd">
  <moduleName>{NAME} {VERSION}</moduleName>
  <requiredInstallFiles><folder source="Docs" destination=""/></requiredInstallFiles>
  <installSteps order="Explicit">
    <installStep name="Choose your crutches">
      <optionalFileGroups order="Explicit">
        <group name="Tick only the fixes for mods you have installed" type="SelectAny">
          <plugins order="Explicit">
{chr(10).join(plugins)}
          </plugins>
        </group>
      </optionalFileGroups>
    </installStep>
  </installSteps>
</config>
""")
    archive = OUT / f"{NAME} {VERSION}.7z"
    archive.unlink(missing_ok=True)
    sh("7z", "a", "-t7z", "-mx=9", str(archive), ".", cwd=STAGE)
    src_archive = OUT / f"{NAME} {VERSION} - Source.7z"
    src_archive.unlink(missing_ok=True)
    sh("7z", "a", "-t7z", "-mx=9", str(src_archive), ".", cwd=SRC)
    for a in (archive, src_archive):
        print(a, a.stat().st_size)


if __name__ == "__main__":
    main()

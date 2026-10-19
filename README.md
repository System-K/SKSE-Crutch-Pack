# SKSE Crutch Pack

Temporary rebuilds of SKSE plugins that broke with Skyrim SE 1.7.99 / 1.7.104 (Address Library v5, SKSE 2.3.1) -
a crutch until the original authors release their own updates. Download: Nexus Mods (SKSE Crutch Pack).

This repository contains the packaging script and tools. The source of every DLL lives in a fork of the
original repository, on a `hotfix/...` branch, so the changes against upstream are visible commit by commit.

## Fixes in version 1.1.0

| Fix | Original (Nexus) | Original author | Licence | Hotfix source | What changed |
|---|---|---|---|---|---|
| Recharge Framework | [157327](https://www.nexusmods.com/skyrimspecialedition/mods/157327) v1.0.2 | shazdeh2 | MIT | [Recharge-Framework](https://github.com/System-K/Recharge-Framework/tree/hotfix/1.7.104) (upstream: [shazdeh/Recharge-Framework](https://github.com/shazdeh/Recharge-Framework)) | Rebuilt against a current CommonLibSSE-NG. The original could not read the new Address Library and stopped the game at start. |
| Leveled List Object Swapper | [132765](https://www.nexusmods.com/skyrimspecialedition/mods/132765) v1.3.0 | Eudalus | MIT | [LeveledListObjectSwapper](https://github.com/System-K/LeveledListObjectSwapper/tree/hotfix/1.7.104) (upstream: [Eudalus/LeveledListObjectSwapper](https://github.com/Eudalus/LeveledListObjectSwapper)) | Rebuilt against a current CommonLibSSE-NG (new Address Library format). No behaviour changes. |
| Papyrus MessageBox - SKSE NG | [83578](https://www.nexusmods.com/skyrimspecialedition/mods/83578) v1.0.0 | mrowrpurr | 0BSD | [MessageBox](https://github.com/System-K/MessageBox/tree/hotfix/1.7.104) (upstream: [SkyrimScripting/MessageBox](https://github.com/SkyrimScripting/MessageBox)) | Rebuilt against a current CommonLibSSE-NG; two API calls updated for 1.7.99 (message queue, menu run flag). |
| CHEAT CODES | [174465](https://www.nexusmods.com/skyrimspecialedition/mods/174465) v1 | cavy8 | LGPL-2.1 (menu) / GPL-3.0 (pack) | [CheatCodeMenu](https://github.com/System-K/CheatCodeMenu/tree/hotfix/1.7.104) (upstream: [cavy8/CheatCodeMenu](https://github.com/cavy8/CheatCodeMenu)), [CheatPack1](https://github.com/System-K/CheatPack1/tree/hotfix/1.7.104) (upstream: [cavy8/CheatPack1](https://github.com/cavy8/CheatPack1)) | Both DLLs rebuilt. Fixes a crash in the image-space cheats (1.7.99 packs the effect index differently) and the changed button-event layout. |
| Apprentice - A Class Overhaul | [169288](https://www.nexusmods.com/skyrimspecialedition/mods/169288) v1.1.0 | Simon Magus and LambdaCDM | GPL-3.0 | [Apprentice](https://github.com/System-K/Apprentice/tree/hotfix/1.7.104) (upstream: [lambdacdm1/Apprentice](https://github.com/lambdacdm1/Apprentice)) | Rebuilt against a current CommonLibSSE-NG (same intent as the author's unreleased 1.7 update branch). No source changes. |
| Lighting Toolkit | [150279](https://www.nexusmods.com/skyrimspecialedition/mods/150279) v0.10.0 | shdowraithe101 | MIT | [lighting-toolkit-skse](https://github.com/System-K/lighting-toolkit-skse/tree/hotfix/1.7.104) (upstream: [alexjiang200407/lighting-toolkit-skse](https://github.com/alexjiang200407/lighting-toolkit-skse)) | Ported to CommonLibSSE-NG 11. Fixes a silent 1.7.99 bug (the player's cell-change event source moved), the new input-event layout and a trampoline allocation crash at start. |
| Hair Colour Sync NG | [156414](https://www.nexusmods.com/skyrimspecialedition/mods/156414) v1.3.1 | jg1, NG port by kingeric1992 | MIT | [HairColourSyncNg](https://github.com/System-K/HairColourSyncNg/tree/hotfix/1.7.104) (upstream: [kingeric1992/HairColourSyncNg](https://github.com/kingeric1992/HairColourSyncNg)) | Rebuilt against CommonLibSSE-NG 11 (the original could not read the new Address Library); one renamed geometry field updated. The armour hook site is unchanged in 1.7.104. |
| How to sit sleep meditate and fall... anywhere | [167371](https://www.nexusmods.com/skyrimspecialedition/mods/167371) v1.8.9 | Preguissoso (DLL based on powerofthree's Sandbox When Idle) | GPL-3.0 | [SandboxWhenIdle](https://github.com/System-K/SandboxWhenIdle/tree/hotfix/how-to-sit) (upstream: [powerof3/SandboxWhenIdle](https://github.com/powerof3/SandboxWhenIdle)) | Replacement Actions.dll: powerofthree's Sandbox When Idle (already updated for 1.7.99 by po3) plus a reimplementation of the mod's Papyrus functions (NSA_SandBox), packages, mod events and input rules. Install over the original. |
| Survival Control Panel | [41891](https://www.nexusmods.com/skyrimspecialedition/mods/41891) v1.1.2 | Parapets and colinswrath | MIT | [SurvivalControlPanel](https://github.com/System-K/SurvivalControlPanel/tree/hotfix/1.7.104) (upstream: [colinswrath/SurvivalControlPanel](https://github.com/colinswrath/SurvivalControlPanel)) | The authors' own update (1.1.3 on GitHub, Address Library v5, September 2026) built as-is - it is not on Nexus yet. Only the DLL is replaced; ESP, BSA and scripts of 1.1.2 are unchanged. |

## Building


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

## This repository

- `pack.py` - builds the FOMOD and the source archive from the hotfix repositories (paths are set at the top).
- `tools/check_hooks.py` - resolves Address Library v5 IDs against a SkyrimSE.exe and checks the bytes at hook sites
  (`check_hooks.py versionlib-1-7-104-0.bin SkyrimSE.exe 14988+0x6E:E8 ...`).

All credit for the plugins goes to their authors; each fork keeps the original licence. The scripts in this
repository are MIT-licensed.

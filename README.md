# DOOM (2016) NewGame+ Customizer

<div align="center">
  <img alt="License: GPL-3.0" src="https://img.shields.io/badge/License-GPL--3.0-blue" />
</div>

A desktop modding tool for DOOM (2016) that lets players define custom starting
inventories and generates the `.decl` mod files the game engine reads. Python dataclasses
model the game's internal systems as a three-level inheritance hierarchy: abstract base
elements specialize into perks and items, which further specialize into eight concrete
types matching DOOM's inventory categories. A validation layer enforces the game's own
balance constraints, preventing configurations that would break progression.

Credit to [@elizabethany](https://github.com/elizabethany) for creating the original
[NewGamePlus mod](https://www.nexusmods.com/doom/mods/28), which inspired this project.

<div align="center">
  <a href="https://github.com/andrewcreekmore/DOOM-NewGamePlusCustomizer/assets/44483269/bb6ceb4c-a7d9-4d54-9b0a-0cf630c56324"><img src="https://github.com/andrewcreekmore/DOOM-NewGamePlusCustomizer/assets/44483269/bb6ceb4c-a7d9-4d54-9b0a-0cf630c56324" width="24%" alt="Praetor Suit upgrades" /></a>
  <a href="https://github.com/andrewcreekmore/DOOM-NewGamePlusCustomizer/assets/44483269/8bff97e8-3a9c-4d5e-8232-dbf369519507"><img src="https://github.com/andrewcreekmore/DOOM-NewGamePlusCustomizer/assets/44483269/8bff97e8-3a9c-4d5e-8232-dbf369519507" width="24%" alt="Equipment and Weapons" /></a>
  <a href="https://github.com/andrewcreekmore/DOOM-NewGamePlusCustomizer/assets/44483269/366445f3-3c60-4fa9-b0d0-94b32ef9dea5"><img src="https://github.com/andrewcreekmore/DOOM-NewGamePlusCustomizer/assets/44483269/366445f3-3c60-4fa9-b0d0-94b32ef9dea5" width="24%" alt="Weapon Mods" /></a>
  <a href="https://github.com/andrewcreekmore/DOOM-NewGamePlusCustomizer/assets/44483269/b16f9ce3-e23e-4581-8cb5-36589a958d54"><img src="https://github.com/andrewcreekmore/DOOM-NewGamePlusCustomizer/assets/44483269/b16f9ce3-e23e-4581-8cb5-36589a958d54" width="24%" alt="Runes" /></a>
</div>

<p align="center">
  <a href="https://github.com/andrewRCr/DOOM-NewGamePlusCustomizer/releases/latest">Download</a>
  &nbsp;&nbsp;|&nbsp;&nbsp;
  <a href="https://www.nexusmods.com/doom/mods/59">NexusMods</a>
  &nbsp;&nbsp;|&nbsp;&nbsp;
  <a href="https://andrewcreekmore.dev/projects/software/doom-newgame-plus-customizer">Portfolio</a>
</p>

## Details

*Players configure a custom starting loadout — selecting equipment, weapons, weapon mods,
suit upgrades, and runes with optional permanent equipping — and generate a ready-to-load
mod with one click.*

- Three-level dataclass hierarchy with eight concrete types modeling DOOM's full range
  of inventory categories
- Each inventory type implements its own serialization method, translating domain
  fields — upgrade levels, equipment flags, rune slot overrides — into the game engine's
  key-value format
- Code generation producing valid `.decl` mod files from user-configured loadout
  selections, matching the engine's `devInvLoadout` format
- Level inheritance map reproducing DOOM's loadout propagation chain — each level inherits
  its starting inventory from the previous, so a single generated base definition
  propagates correctly through the full campaign
- Validation preventing loadout configurations that would block campaign progression
- Automated mod deployment: Steam installation path detection with common-path scanning,
  mod directory creation, and automatic replacement of previously generated versions
- GUI with tabbed category navigation, in-game descriptions as tooltips, and
  auto-detected Steam installation paths

## Installation & Usage

Requires [DOOMModLoader](https://github.com/ZwipZwapZapony/DOOMModLoader/releases)
to load generated mods into the game.

For full installation instructions and detailed usage notes, see the
[NexusMods page](https://www.nexusmods.com/doom/mods/59).

## Technology

- **Language:** Python
- **GUI:** CustomTkinter, Pillow

## License

[GPL-3.0](LICENSE)

<p align="center"><a href="#doom-2016-newgame-customizer">↑ Back to top</a></p>

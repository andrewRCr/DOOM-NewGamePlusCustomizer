# DOOM (2016) NewGame+ Customizer

Custom simulated "new game plus" mod generation tool for DOOM (2016).  
Credit to [@elizabethany](https://github.com/elizabethany) for creating the original [NewGamePlus mod](https://www.nexusmods.com/doom/mods/28), which inspired this project.  

### Overview  
Define your own starting inventory from any potential combination of equipment (throwables / double-jump thrust boots), weapons, weapon mods, suit upgrades (Argent Cell and/or Praetor Token), and runes. Runes and weapon mods can be added with or without their upgrades.  

Additionally, runes can be "permanently equipped" without taking up a Rune slot - allowing you to equip as many as you like simultaneously.  

Take it. It will give you strength, help you on your journey - if you can withstand the power surge.  
  
 Praetor Suit | Equipment & Weapons | Weapon Mods | Runes
|------------|-------------|-------------|-------------|
| <img src="https://github.com/andrewcreekmore/DOOM-NewGamePlusCustomizer/assets/44483269/bb6ceb4c-a7d9-4d54-9b0a-0cf630c56324" width="250"> | <img src="https://github.com/andrewcreekmore/DOOM-NewGamePlusCustomizer/assets/44483269/8bff97e8-3a9c-4d5e-8232-dbf369519507" width="250"> | <img src="https://github.com/andrewcreekmore/DOOM-NewGamePlusCustomizer/assets/44483269/366445f3-3c60-4fa9-b0d0-94b32ef9dea5" width="250"> | <img src="https://github.com/andrewcreekmore/DOOM-NewGamePlusCustomizer/assets/44483269/b16f9ce3-e23e-4581-8cb5-36589a958d54" width="250"> |  

Hovering over any element will yield a tooltip message with an in-game description, for ease of use.  

### Usage

After selecting your loadout, press 'Generate Mod' and a .zip archive titled 'Custom New Game Plus' will be placed in the indicated directory path (if a Steam installation of DOOM is detected on the C:/ drive, this path will be pre-populated; otherwise you will need to specify it). Once this .zip has been placed into your local installation's Mods directory (i.e., 'steamapps/common/DOOM/Mods'), run [DOOMModLoader](https://github.com/jfmherokiller/DOOMExtract/releases/tag/1.8) to install the mod. [DOOMLauncher](https://github.com/PowerBall253/DOOMLauncher) is also recommended in order to bypass dev-mode restrictions. 

Note that at least one category (health, armor, ammo) of Argent Cell upgrades must not be fully added, in order to allow the player to pick up the mandatory first upgrade given at the end of Resource Ops. The tool enforces this restriction.

If you choose to add a weapon mod's upgrades but not the weapon mod itself, when you obtain it during the campaign it will already be fully upgraded. Note that you may need to unequip and reequip the mod in question for this to take effect.  Runes can't be preemptively upgraded in this way (i.e., without also unlocking them), due to how their inventory data is structured.

Starting a new game is required.

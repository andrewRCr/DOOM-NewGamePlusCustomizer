"""
common.py: 
- formatting + common static data definitions
- utility functions
"""

from enum import Enum

# basic layout sizing
WINDOW_SIZE = (1000, 800)

# WindowsOS styles required for task bar integration
GWL_EXSTYLE = -20
WS_EX_APPWINDOW = 0x00040000
WS_EX_TOOLWINDOW = 0x00000080

# text attributes
FONT = 'Helvetica'
FONT_SIZES = {
    'Dropdowns' : 16,
    'Buttons': 14,
    'Text': 14,
    'Headers': 16,
    'Checkboxes': 16,
    'Popups': 15
}

# color definitions
BLACK = '#000000'
WHITE = '#EEEEEE'
LIGHT_GRAY = '#696969'
DARK_GRAY = '#505050'
DARKEST_GRAY = '#1E1E1E'
GRAY = '#D9D9D9'
RED = '#6B060D'
RED_HIGHLIGHT = '#6b1c22'
TITLE_BAR_HEX_COLORS = {
    'black': 0x00000000,
    'dark': 0x001E1E1E,
    'light': 0x00EEEEEE
}

class PopupType(Enum):
    """ """
    
    PT_ERROR = 0,
    PT_INFO = 1,
    PT_PATH = 2

# indent defines for formatting output files
indent = '    '
doubleIndent = indent + indent
tripleIndent = doubleIndent + indent
quadIndent = tripleIndent + indent

# static UI data


ARGENT_DROPDOWN_DATA = {
    'healthCapacity': {'fName': 'Health:', 'Levels': {0: 'Default (100)', 1: 'Level 1 (125)', 2: 'Level 2 (150)', 3: 'Level 3 (175)', 4: 'Level 4 (200)'}, 'Dropdown': None},
    'armorCapacity': {'fName': 'Armor:', 'Levels': {0: 'Default (50)', 1: 'Level 1 (75)', 2: 'Level 2 (100)', 3: 'Level 3 (125)', 4: 'Level 4 (150)'}, 'Dropdown': None},
    'ammoCapacity' : {'fName': 'Ammo:', 'Levels': {0: 'Default', 1: 'Level 1', 2: 'Level 2', 3: 'Level 3', 4: 'Level 4'}, 'Dropdown': None}
}

RUNE_PANEL_DATA = {
    'vacuum': {'fName': 'Vacuum', 'imagePath' : 'res/images/rune_vacuum.png', 'panel': None}, 
    'dazedAndConfused': {'fName': 'Dazed and Confused', 'imagePath' : 'res/images/rune_dazedAndConfused.png', 'panel': None},
    'ammoBoost': {'fName': 'Ammo Boost', 'imagePath' : 'res/images/rune_ammoBoost.png', 'panel': None},
    'equipmentPower': {'fName': 'Equipment Power', 'imagePath' : 'res/images/rune_equipmentPower.png', 'panel': None},
    'seekAndDestroy': {'fName': 'Seek and Destroy', 'imagePath' : 'res/images/rune_seekAndDestroy.png', 'panel': None},
    'savagery': {'fName': 'Savagery', 'imagePath' : 'res/images/rune_savagery.png', 'panel': None},
    'inFlightMobility': {'fName': 'In-Flight Mobility', 'imagePath' : 'res/images/rune_inFlightMobility.png', 'panel': None},
    'armoredOffensive': {'fName': 'Armored Offensive', 'imagePath' : 'res/images/rune_armoredOffensive.png', 'panel': None},
    'bloodFueled': {'fName': 'Blood Fueled', 'imagePath' : 'res/images/rune_bloodFueled.png', 'panel': None},
    'intimacyIsBest': {'fName': 'Intimacy is Best', 'imagePath' : 'res/images/rune_intimacyIsBest.png', 'panel': None},
    'richGetRicher': {'fName': 'Rich Get Richer', 'imagePath' : 'res/images/rune_richGetRicher.png', 'panel': None},
    'savingThrow': {'fName': 'Saving Throw', 'imagePath' : 'res/images/rune_savingThrow.png', 'panel': None},
    }

IMAGE_SCALE = .85

WEAPON_MOD_PANEL_DATA = {
        'pistol': {
        'fName': 'Pistol',
        'hasMods': False,
        'imagePath': 'res/images/pistol.png',
        'imageSize': (534, 284)},
    'combatShotgun': {
        'fName': 'Combat Shotgun',
        'hasMods': True,
        'imagePath': 'res/images/combatShotgun.png',
        'imageSize': (800, 236)},
    'heavyAssaultRifle': {
        'fName': 'Heavy Assault Rifle',
        'hasMods': True,
        'imagePath': 'res/images/heavyAssaultRifle.png',
        'imageSize': (int(770 * IMAGE_SCALE), int(294 * IMAGE_SCALE))},
    'plasmaRifle': {
        'fName': 'Plasma Rifle',
        'hasMods': True,
        'imagePath': 'res/images/plasmaRifle.png',
        'imageSize': (int(630 * IMAGE_SCALE), int(296 * IMAGE_SCALE))},
    'rocketLauncher': {
        'fName': 'Rocket Launcher',
        'hasMods': True,
        'imagePath': 'res/images/rocketLauncher.png',
        'imageSize': (800, 237)},
    'superShotgun': {
        'fName': 'Super Shotgun',
        'hasMods': False,
        'imagePath': 'res/images/superShotgun.png',
        'imageSize': (800, 207)},
    'gaussCannon': {
        'fName': 'Gauss Cannon',
        'hasMods': True,
        'imagePath': 'res/images/gaussCannon.png',
        'imageSize': (799, 172)},
    'chaingun': {
        'fName': 'Chaingun',
        'hasMods': True,
        'imagePath': 'res/images/chaingun.png',
        'imageSize': (765, 285)},
}

# category to padx tuple map
SUIT_PANEL_DATA = {
    'Environmental Resistance': (0, 50),
    'Area-Scanning Technology': (0, 30),
    'Equipment System': (20, 0),
    'Powerup Effectiveness': (0, 60),
    'Dexterity': (0, 0)
}

BASE_ITEM = {'researchGroups' : '"main"', 'equip' : 'true'}

LEVEL_INHERITANCE_MAP = {
    'argent_tower': 'olympia_surface_1', 
    'bfg_division': 'olympia_surface_2',
    'blood_keep': 'argent_tower',
    'blood_keep_b': 'emt',
    'blood_keep_c': 'blood_keep_b',
    'emt': 'lazarus',
    'foundry': 'resource_operations',
    'intro': 'base',
    'lazarus': 'bfg_division',
    'olympia_surface_1': 'foundry',
    'olympia_surface_2': 'blood_keep',
    'polar_core': 'blood_keep_c',
    'resource_operations': 'intro',
    'titan': 'polar_core'}

# utility functions
def clamp(num: int, smallest: int, largest: int) -> int:
    """ Clamps an int within the passed range. """
    return max(smallest, min(num, largest))

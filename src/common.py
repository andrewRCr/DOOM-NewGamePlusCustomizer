"""
common.py: 
- formatting + common static data definitions
- utility functions
"""

# basic layout sizing
WINDOW_SIZE = (1000, 800)

# text attributes
FONT = 'Helvetica'
FONT_SIZES = {
    'Dropdowns' : 14,
    'Buttons': 14,
    'Text': 16,
    'Headers': 18
}

# color definitions
BLACK = '#000000'
WHITE = '#EEEEEE'
LIGHT_GRAY = '#E8E8E8'
DARK_GRAY = '#505050'
GRAY = '#D9D9D9'
RED = '#6B060D'
RED_HIGHLIGHT = '#6b1c22'
TITLE_BAR_HEX_COLORS = {
    'dark': 0x00000000,
    'light': 0x00EEEEEE
}

# indent defines for formatting output files
indent = '    '
doubleIndent = indent + indent
tripleIndent = doubleIndent + indent
quadIndent = tripleIndent + indent

# static data
ARGENT_HEALTH_LEVELS = {0: 'Default (100)', 1: 'Level 1 (125)', 2: 'Level 2 (150)', 3: 'Level 3 (175)', 4: 'Level 4 (200)'} 
ARGENT_ARMOR_LEVELS = {0: 'Default (50)', 1: 'Level 1 (75)', 2: 'Level 2 (100)', 3: 'Level 3 (125)', 4: 'Level 4 (150)'} 
ARGENT_AMMO_LEVELS = {0: 'Default', 1: 'Level 1', 2: 'Level 2', 3: 'Level 3', 4: 'Level 4'} 

BASE_ITEM = {'researchGroups' : '"main"', 'equip' : 'true'}

# utility functions
def clamp(num: int, smallest: int, largest: int) -> int:
    """ Clamps an int within the passed range. """
    return max(smallest, min(num, largest))

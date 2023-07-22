"""
app.py: 
- general application logic / entry-point
- creates instance of App, which:
--- initializes/manages a window + widgets
--- captures relevant keyboard events
--- creates instance of InventoryLoadout w/ defaults
--- runs main loop
"""

import customtkinter as ctk
from ctypes import windll, byref, sizeof, c_int

from inventory import *

class App():
    """ Main / core application class. """

    def __init__(self):

        # create default starting inventory
        self.inventory = Inventory()

        # access and modify
        self.modifyTestFunc()

        # generate declFile
        self.inventory.generateDeclFile()
        
    def modifyTestFunc(self):
        """ purely for testing """

        # making all praetor suit upgrades unlocked
        for eachPerk in self.inventory.praetorSuitUpgrades.modulePerks:
            eachPerk.equip = True

        # making rune available in inventory
        self.inventory.runes.vacuum.isRune = True
        # making rune permanently equipped
        self.inventory.runes.dazedAndConfused.runePermanentEquip = True

        # adding double jump boots to inventory (special)
        self.inventory.equipment.doubleJumpThrustBoots.available = True


if __name__ == '__main__':
    App()
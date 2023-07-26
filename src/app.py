"""
app.py: 
- general application logic / entry-point
- creates instance of App, which:
--- initializes/manages a window + widgets
--- captures relevant keyboard events
--- creates instance of Inventory w/ defaults
--- runs main loop
"""

import customtkinter as ctk
from functools import partial
import os
from PIL import Image
import shutil
try:
    from ctypes import windll, byref, sizeof, c_int
except:
    pass

from datalib.inventory import *


class App(ctk.CTk):
    """ Main / core application class. """

    def __init__(self):

        # setup window
        super().__init__(fg_color = BLACK) 
        self.geometry(f'{WINDOW_SIZE[0]}x{WINDOW_SIZE[1]}') # default window size
        self.resizable(False, False) # non-resizable

        # hide title and icon
        self.title('')
        self.iconbitmap('images/empty.ico')

        # set appearance
        ctk.set_appearance_mode('dark')
        self.changeTitleBarColor() # change title bar to match rest of window

        self.popupMsgWindow = None

        # create bottom frame: app title, generate mod button
        self.bottomFrame = ctk.CTkFrame(self, fg_color = 'transparent')
        self.bottomFrame.pack(side = 'bottom', fill = 'x')

        # scrollable main content frame
        self.scrollFrame = ctk.CTkScrollableFrame(self, fg_color= 'transparent')
        self.scrollFrame.pack(fill = 'both')

        # create widgets
        self.initWidgets()

        # create default starting inventory
        self.inventory = Inventory()

        # access and modify
        self.modifyTestFunc()

        # run
        self.mainloop()

    def changeTitleBarColor(self):
        """ Changes app's title bar color to match rest of window. """
        try: # windows only
            HWND = windll.user32.GetParent(self.winfo_id()) # get current window
            DWMA_ATTRIBUTE = 35 # target color attribute of window's title bar
            TITLE_BAR_COLOR = TITLE_BAR_HEX_COLORS['dark']
            windll.dwmapi.DwmSetWindowAttribute(HWND, DWMA_ATTRIBUTE, byref(c_int(TITLE_BAR_COLOR)), sizeof(c_int)) # set attribute
        except:
            pass

    def initWidgets(self):
        """ Creates top-level app widgets and calls widget init functions for each inventory module. """

        # setup widget fonts
        self.buttonWidgetFont = ctk.CTkFont(family = FONT, size = FONT_SIZES['Buttons'])
        self.textWidgetFont = ctk.CTkFont(family = FONT, size = FONT_SIZES['Text'])
        self.headerWidgetFont = ctk.CTkFont(family = FONT, size = FONT_SIZES['Headers'])

        # app title
        self.titleLabel = ctk.CTkLabel(self.bottomFrame, font = self.textWidgetFont, text = 'DOOM (2016) NewGame+ Customizer')
        self.titleLabel.grid(column = 0, row = 0, padx = 15) 

        # input to generate final output file from current app selections
        self.generateModButton = ctk.CTkButton(self.bottomFrame, font = self.buttonWidgetFont, 
                                               fg_color = RED,
                                               hover_color = DARK_GRAY,
                                               text_color = WHITE,
                                               text = 'Generate Mod', 
                                               command = self.generateMod)
        self.generateModButton.grid(column = 1, row = 0, padx = 540, pady = 10)

        # inventory module widgets
        self.initArgentWidgets()

    def initArgentWidgets(self):
        """ Creates widgets for the ArgentCellUpgrades inventory module. """

        self.argentCellHeaderLabel = ctk.CTkLabel(self.scrollFrame, font = self.headerWidgetFont, text = 'Argent Cell Upgrades')
        self.argentCellHeaderLabel.grid(column = 0, row = 0, padx = 10)

        # health - label
        self.argentHealthLabel = ctk.CTkLabel(self.scrollFrame, font = self.textWidgetFont, text = 'Health:')
        self.argentHealthLabel.grid(column = 0, row = 1, sticky = 'e')

        # health - callback func / dropdown menu
        argentHealthCallback = partial(self.argentCallback, 'healthCapacity')
        self.argentHealthDropdown = DropdownMenu(self.scrollFrame, list(ARGENT_HEALTH_LEVELS.values()), argentHealthCallback)
        self.argentHealthDropdown.grid(column = 1, row = 1, padx = 10)

        # armor - label
        self.argentArmorLabel = ctk.CTkLabel(self.scrollFrame, font = self.textWidgetFont, text = 'Armor:')
        self.argentArmorLabel.grid(column = 2, row = 1, padx = 10, sticky = 'e')

        # armor - callback func / dropdown menu
        argentArmorCallback = partial(self.argentCallback, 'armorCapacity')
        self.argentArmorDropdown = DropdownMenu(self.scrollFrame, list(ARGENT_ARMOR_LEVELS.values()), argentArmorCallback)
        self.argentArmorDropdown.grid(column = 3, row = 1, padx = 10)

        # ammo - label
        self.argentAmmoLabel = ctk.CTkLabel(self.scrollFrame, font = self.textWidgetFont, text = 'Ammo:')
        self.argentAmmoLabel.grid(column = 4, row = 1, padx = 10, sticky = 'e')

        # ammo - callback func / dropdown menu
        argentAmmoCallback = partial(self.argentCallback, 'ammoCapacity')
        self.argentAmmoDropdown = DropdownMenu(self.scrollFrame, list(ARGENT_AMMO_LEVELS.values()), argentAmmoCallback)
        self.argentAmmoDropdown.grid(column = 5, row = 1, padx = 10)

    def argentCallback(self, category: str, selection: str):
        """ """
  
        def showUpgradeLimitPopupMsg():
            """ Helper function; creates warning popup message. """
            
            self.createPopupMessage('At least one category (health, armor, ammo) of Argent Cell upgrades' \
                + ' must not be fully maxed so that you can still pick up the mandatory' \
                + ' first upgrade given at the end of Resource Ops.')

        def trySetArgentLevel() -> int:
            """ Helper function; attempts to set level and handles app-level response. """
            
            selectionKey: int = list(lookup)[list(lookup.values()).index(selection)]
            validatedSelectionKey: int = self.inventory.argentCellUpgrades.setArgentLevel(category, selectionKey)
            if validatedSelectionKey != selectionKey:
                showUpgradeLimitPopupMsg()
            return validatedSelectionKey
        
        match category:
            case 'healthCapacity':
                lookup: dict[int, str] = ARGENT_HEALTH_LEVELS
                validatedSelectionKey: int = trySetArgentLevel()
                self.argentHealthDropdown.set(lookup[validatedSelectionKey])

            case 'armorCapacity':
                lookup = ARGENT_ARMOR_LEVELS
                validatedSelectionKey = trySetArgentLevel()
                self.argentArmorDropdown.set(lookup[validatedSelectionKey])

            case 'ammoCapacity':
                lookup = ARGENT_AMMO_LEVELS
                validatedSelectionKey = trySetArgentLevel()
                self.argentAmmoDropdown.set(lookup[validatedSelectionKey])

    def createPopupMessage(self, message):
        """ Attempts to create a pop up message; will not create duplicates. Takes app focus. """

        if self.popupMsgWindow is None or not self.popupMsgWindow.winfo_exists():
            self.popupMsgWindow = popupMessage(self, message) 
            self.popupMsgWindow.grab_set()
    
        else:
            self.popupMsgWindow.focus()

    def modifyTestFunc(self):
        """ purely for testing """
        
        self.inventory.argentCellUpgrades.setArgentLevel('healthCapacity', -1)
        #print(self.inventory.argentCellUpgrades.healthCapacity.count)
        
        self.inventory.praetorSuitUpgrades.addToAvailable('hazardProtection')
        
        self.inventory.equipment.addToAvailable('doubleJumpThrustBoots')
        self.inventory.equipment.addToAvailable('siphonGrenade')
        
        self.inventory.weapons.addToAvailable('combatShotgun')
        self.inventory.ammo.addToAvailable('shells')
        self.inventory.weaponMods.addToAvailable('pistol', 'chargeEfficiency')
        
        self.inventory.runes.addToAvailable('vacuum')
        self.inventory.runes.setIsUpgraded('vacuum', True)
        self.inventory.runes.setIsPermanent('dazedAndConfused', True)
        
    def makeLevelInheritanceDecls(self, path):
        """ Creates decl files for each game level, with inventory inheriting from the previous level. """
        
        levelInheritanceMap = {'argent_tower': 'olympia_surface_1', 'bfg_division': 'olympia_surface_2'}

        for key, value in levelInheritanceMap.items():
            fileName = f'{path}/{key}.decl;devInvLoadout'
            with open(fileName, 'w+') as file:
                file.write('{\n' + indent)
                file.write('inherit = ' + f'"devinvloadout/sp/{value}";')
                file.write('\n' + indent + 'edit = {')
                file.write('\n' + indent + '}')
                file.write('\n}')

    def generateMod(self):
        """ Top-level function for generating final, usable mod output file from current app values. """

        # generate dir structure
        newPath = r'generated\decls\devinvloadout\devinvloadout\sp'
        if not os.path.exists(newPath):
            os.makedirs(newPath)

        # generate all declFiles
        self.inventory.generateDeclFile(newPath)
        self.makeLevelInheritanceDecls(newPath)
        
        # generate final zip archive of /generated + subdirs + declFiles
        zipName = 'Custom New Game Plus'
        shutil.make_archive(zipName, 'zip', '.', 'generated')

        # cleanup intermediate files
        shutil.rmtree('generated')


class popupMessage(ctk.CTkToplevel):
    """ Represents a top-level window containing a pop-up message. """

    def __init__(self, parent, message):
        
        super().__init__(master = parent)

        self.mainAppWindow = parent
        self.overrideredirect(True)

        # setup window 
        self.width = 500 
        self.height = 140
        self.spawn_x = int(self.mainAppWindow.winfo_width() * .5 + self.mainAppWindow.winfo_x() - .5 * self.width)
        self.spawn_y = int(self.mainAppWindow.winfo_height() * .5 + self.mainAppWindow.winfo_y() - .5 * self.height)
        self.geometry(f'{self.width}x{self.height}+{self.spawn_x}+{self.spawn_y}')

        # hide title and icon
        self.title('')
        self.iconbitmap('images/empty.ico')

        # set appearance
        ctk.set_appearance_mode('dark')
        self.changeTitleBarColor() # change title bar to match rest of window
        self.transparentColor = self._apply_appearance_mode(self.cget("fg_color"))
        self.attributes("-transparentcolor", self.transparentColor)
        self.cornerRadius = 15

        # setting up frame for widgets
        self.popupFrame = ctk.CTkFrame(self, 
                                       corner_radius = self.cornerRadius, 
                                       width=self.width, 
                                       height = self.height, 
                                       bg_color= self.transparentColor,
                                       border_width = 5)
        self.popupFrame.pack(fill = 'both', expand = True)

        self.widgetFont = ctk.CTkFont(family = FONT, size = FONT_SIZES['Buttons'])

        messageImage = ctk.CTkImage(light_image = Image.open('images/info.png'), 
                                    dark_image = Image.open('images/info.png'))
      
        self.imageLabel = ctk.CTkLabel(self.popupFrame, image = messageImage, text = '', anchor = 'w')
        self.imageLabel.grid(column = 0, row = 0, padx = 20, pady = 20)

        self.messageLabel = ctk.CTkLabel(self.popupFrame, font = self.widgetFont, text = f'{message}', wraplength= 400, anchor = 'w', padx = 5, pady = 5)
        self.messageLabel.grid(column = 1, row = 0, pady = 20, sticky = 'w')

        self.okButton = ctk.CTkButton(self.popupFrame, font = self.widgetFont, text = 'OK', fg_color = RED, hover_color = RED_HIGHLIGHT, command = self.destroy)
        self.okButton.grid(column = 1, row = 1)

    def changeTitleBarColor(self):
        """ Changes popup window's title bar color to match rest of window. """
        try: # windows only
            HWND = windll.user32.GetParent(self.winfo_id()) # get current window
            DWMA_ATTRIBUTE = 35 # target color attribute of window's title bar
            TITLE_BAR_COLOR = TITLE_BAR_HEX_COLORS['dark']
            windll.dwmapi.DwmSetWindowAttribute(HWND, DWMA_ATTRIBUTE, byref(c_int(TITLE_BAR_COLOR)), sizeof(c_int)) # set attribute
        except:
            pass


class DropdownMenu(ctk.CTkOptionMenu):
    """ App drop-down menu base class. """

    def __init__(self, parent, values, command):
        """ """

        self.dropdownWidgetFont = ctk.CTkFont(family = FONT, size = FONT_SIZES['Dropdowns'])

        super().__init__(master = parent, 
                         fg_color = DARK_GRAY, 
                         button_color = RED, 
                         button_hover_color = RED_HIGHLIGHT,
                         font = self.dropdownWidgetFont,
                         values = values,
                         command = command,
                         dropdown_font = self.dropdownWidgetFont)


if __name__ == '__main__':
    App()

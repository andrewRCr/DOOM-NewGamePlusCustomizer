"""
app.py: 
- general application logic / entry-point
- creates instance of App, which:
--- initializes/manages a window + widgets
--- captures relevant keyboard events
--- creates instance of Inventory w/ defaults
--- runs main loop
"""

import contextlib
import customtkinter as ctk
from customtkinter import filedialog
from CTkToolTip import CTkToolTip
from functools import partial
import os
from PIL import Image
import shutil
try:
    from ctypes import windll, byref, sizeof, c_int
except:
    pass
with contextlib.redirect_stdout(None):
    import pygame

from datalib.inventory import *


class App(ctk.CTk):
    """ Main / core application class. """

    def __init__(self):

        # setup window
        super().__init__(fg_color = BLACK) 
        self.geometry(f'{WINDOW_SIZE[0]}x{WINDOW_SIZE[1]}') # default window size
        self.resizable(False, False) # non-resizable
        
        # set app window title and icon
        self.title('DOOM (2016) NewGame+ Customizer')
        self.iconbitmap('res/images/slayer_icon.ico')

        # set appearance
        ctk.set_appearance_mode('dark')
        self.changeTitleBarColor() # change title bar to match rest of window

        # holds current pop-up message (if exists)
        self.popupMsgWindow = None
        
        # to hold path once determined
        self.doomInstallationPath = None

        # create bottom frame: generate mod button
        self.bottomFrame = ctk.CTkFrame(self, fg_color = 'transparent')
        self.bottomFrame.pack(side = 'bottom', fill = 'x')
        
        # create path status frame
        self.statusFrame = ctk.CTkFrame(self, fg_color = 'transparent')
        self.statusFrame.pack(side = 'bottom', fill = 'x')

        # main content frame
        self.mainContentFrame = ctk.CTkFrame(self, fg_color= 'transparent')
        self.mainContentFrame.pack(fill = 'both', expand = True)
        
        # setup fonts
        self.initFonts()
        
        # initialize pygame sound mixer
        pygame.mixer.init()

        # create default starting inventory
        self.inventory = Inventory()

        # create widgets
        self.initWidgets()

        # access and modify - TESTING
        self.modifyTestFunc()

        # run
        self.mainloop()

    def changeTitleBarColor(self):
        """ Changes app's title bar color to match rest of window. """
        try: # windows only
            HWND = windll.user32.GetParent(self.winfo_id()) # get current window
            DWMA_ATTRIBUTE = 35 # target color attribute of window's title bar
            TITLE_BAR_COLOR = TITLE_BAR_HEX_COLORS['black']
            windll.dwmapi.DwmSetWindowAttribute(HWND, DWMA_ATTRIBUTE, byref(c_int(TITLE_BAR_COLOR)), sizeof(c_int)) # set attribute
        except:
            pass
    
    def createPopupMessage(self, type: PopupType, offsetX: int, offsetY: int, message: str):
        """ Attempts to create a pop up message; will not create duplicates. Takes app focus. """
        
        newPopupMessage = None
        
        match type:
            case PopupType.PT_ERROR:
                pygame.mixer.music.load('res/sounds/dsoof.wav')
                pygame.mixer.music.play(loops = 0)
                newPopupMessage = errorPopupMsg(self, offsetX, offsetY, message)
                
            case PopupType.PT_INFO:
                newPopupMessage = infoPopupMsg(self, offsetX, offsetY, message)
                
            case PopupType.PT_PATH:
                newPopupMessage = promptPopupMsg(self, offsetX, offsetY, message)

        if self.popupMsgWindow is None or not self.popupMsgWindow.winfo_exists():
            self.popupMsgWindow = newPopupMessage
            self.popupMsgWindow.grab_set()
    
        else:
            self.popupMsgWindow.focus()
    
    def initFonts(self):
        """ """
        
        # import fonts
        ctk.FontManager.load_font('res/fonts/DooM.ttf')
        ctk.FontManager.load_font('res/fonts/EternalUiRegular-1Gap2.ttf')
        ctk.FontManager.load_font('res/fonts/EternalUiBold-jErYR.ttf')
        ctk.FontManager.load_font('res/fonts/EternalLogo-51X9B.ttf')
        
        # create font objects
        self.tabFont = ctk.CTkFont('Eternal UI Bold', 18)
        self.headerMainFont = ctk.CTkFont('Eternal UI Bold', 22)
        self.subheaderMainFont = ctk.CTkFont('Eternal UI Bold', 16)
        self.textMainFont = ctk.CTkFont('Eternal UI Regular', 16)
        
        # setup widget fonts
        self.buttonWidgetFont = ctk.CTkFont('Eternal UI Bold', 16)
        self.textWidgetFont = ctk.CTkFont('Eternal UI Bold', 16)
        self.headerWidgetFont = ctk.CTkFont(family = FONT, size = FONT_SIZES['Headers'])
        self.checkboxFont = ctk.CTkFont('Eternal UI Regular', FONT_SIZES['Checkboxes'])
        self.switchFont = ctk.CTkFont('Eternal UI Regular', FONT_SIZES['Checkboxes'])
        self.runeDescriptionFont = ctk.CTkFont('Eternal UI Regular', 14)
        self.runeSubOptionFont = ctk.CTkFont('Eternal UI Regular', 15)
            
    def initWidgets(self):
        """ Creates top-level app widgets and calls widget init functions for each inventory module. """

        def playTabChangeSound():
            """ Loads + plays tab changing sound. """
            tabChangeSound = pygame.mixer.Sound('res/sounds/sgreload.wav')
            tabChangeSound.play()
            
        # setup tabs for inventory module grouping
        self.tabMenu = ctk.CTkTabview(master = self.mainContentFrame, 
                                      width = WINDOW_SIZE[0] - 40, 
                                      height = WINDOW_SIZE[1] - 20,
                                      fg_color = DARKEST_GRAY,
                                      segmented_button_fg_color= DARKEST_GRAY,
                                      segmented_button_selected_color = RED,
                                      segmented_button_selected_hover_color =  RED_HIGHLIGHT,
                                      border_width = 2,
                                      border_color = WHITE,
                                      command = playTabChangeSound)
        
        self.tabMenu._segmented_button.configure(font = self.tabFont, border_width = 1, bg_color = WHITE)
        self.tabMenu.pack_propagate(True)
        self.tabMenu.pack()
        self.tabMenu.add('Praetor Suit')
        self.tabMenu.add('Equipment & Weapons')
        self.tabMenu.add('Weapon Mods')
        self.tabMenu.add('Runes')
        self.tabMenu.set('Praetor Suit')
        
        # path status info
        cDefaultPath = r'C:\Program Files (x86)\Steam\steamapps\common\DOOM'
        # if os.path.exists(cDefaultPath):
        #     self.doomInstallationPath = cDefaultPath
        
        outputPathStr = 'NOT FOUND'
        if self.doomInstallationPath:
            outputPathStr =  f'{self.doomInstallationPath}'+ r'/Mods'
            outputPathStr = outputPathStr.replace('\\', '/')
            
        self.outputPathLabel = ctk.CTkLabel(self.statusFrame,
                                            text = f'Install Path: {outputPathStr}',
                                            font = self.textMainFont)
        self.outputPathLabel.pack()
        
        # input to modify output path
        self.modifyPathButton = ctk.CTkButton(
            self.bottomFrame,
            height= 14,
            width = 60,
            text = 'modify path', 
            font = self.textMainFont,
            fg_color= DARK_GRAY,
            hover_color = LIGHT_GRAY,
            border_spacing = 0,
            command = self.promptUserForPath)
        self.modifyPathButton.pack(pady = (0, 2), anchor = 'center')
        
        # input to generate final output file from current app selections
        self.generateModButton = ctk.CTkButton(self.bottomFrame, font = self.buttonWidgetFont, 
                                               fg_color = RED,
                                               hover_color = RED_HIGHLIGHT,
                                               text_color = WHITE,
                                               text = 'Generate Mod', 
                                               command = self.generateMod,
                                               height= 32)
        self.generateModButton.pack(padx = 0, pady = 5, anchor = 'center')

        # inventory module widgets
        self.initArgentWidgets()
        self.initPraetorWidgets()
        self.initEquipmentWidgets()
        self.initWeaponWidgets()
        #
        self.initRuneWidgets()

    def initArgentWidgets(self):
        """ Creates widgets for the ArgentCellUpgrades inventory module. """
        
        parent = self.tabMenu.tab('Praetor Suit')
        
        self.argentCellHeaderLabel = ctk.CTkLabel(parent, font = self.headerMainFont, text = 'Argent Cell Routing')
        self.argentCellHeaderLabel.grid(column = 0, row = 0, padx = 20, pady = (35, 15), columnspan = 2, sticky = 'w')
        
        self.toggleAllArgentSwitch = ctk.CTkSwitch(
            master = parent, 
            text = 'All Upgrades', 
            command = self.toggleAllArgentUpgrades,
            font = self.switchFont,
            progress_color= RED,
            switch_height = 16,
            switch_width = 34)
        self.toggleAllArgentSwitch.grid(column = 0, row = 1, sticky = 'w', padx = (50, 0), pady = (10, 0))
        
        self.argentDropdownsFrame = ctk.CTkFrame(parent, fg_color = DARKEST_GRAY)
        self.argentDropdownsFrame.grid(column = 0, row = 2, padx = (100, 70), pady = (10, 0), columnspan = 6, sticky = 'n')

        # health - label
        self.argentHealthLabel = ctk.CTkLabel(self.argentDropdownsFrame, font = self.textWidgetFont, text = 'Health:')
        self.argentHealthLabel.grid(column = 0, row = 1, padx = 0, sticky = 'e')

        # health - callback func / dropdown menu
        argentHealthCallback = partial(self.argentCallback, 'healthCapacity')
        self.argentHealthDropdown = DropdownMenu(self.argentDropdownsFrame, list(ARGENT_HEALTH_LEVELS.values()), argentHealthCallback)
        self.argentHealthDropdown.grid(column = 1, row = 1, padx = 10)

        # armor - label
        self.argentArmorLabel = ctk.CTkLabel(self.argentDropdownsFrame, font = self.textWidgetFont, text = 'Armor:')
        self.argentArmorLabel.grid(column = 2, row = 1, padx = 0, sticky = 'e')

        # armor - callback func / dropdown menu
        argentArmorCallback = partial(self.argentCallback, 'armorCapacity')
        self.argentArmorDropdown = DropdownMenu(self.argentDropdownsFrame, list(ARGENT_ARMOR_LEVELS.values()), argentArmorCallback)
        self.argentArmorDropdown.grid(column = 3, row = 1, padx = 10)

        # ammo - label
        self.argentAmmoLabel = ctk.CTkLabel(self.argentDropdownsFrame, font = self.textWidgetFont, text = 'Ammo:')
        self.argentAmmoLabel.grid(column = 4, row = 1, padx = 0, sticky = 'e')

        # ammo - callback func / dropdown menu
        argentAmmoCallback = partial(self.argentCallback, 'ammoCapacity')
        self.argentAmmoDropdown = DropdownMenu(self.argentDropdownsFrame, list(ARGENT_AMMO_LEVELS.values()), argentAmmoCallback)
        self.argentAmmoDropdown.grid(column = 5, row = 1, padx = 10)

    def argentCallback(self, category: str, selection: str):
        """ Attempts to set the passed Argent category's value to the passed selection. """
  
        def showUpgradeLimitPopupMsg():
            """ Helper function; creates warning popup message. """
            
            self.createPopupMessage(PopupType.PT_ERROR, -60, -200, 'At least one category (health, armor, ammo) of Argent Cell upgrades' \
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

    def toggleAllArgentUpgrades(self):
        """ Adds/removes every (possible) upgrade, and sets dropdowns accordingly.  """
        
        allArgentCategories = ['healthCapacity', 'armorCapacity', 'ammoCapacity']
        allArgentLevels = [ARGENT_HEALTH_LEVELS, ARGENT_ARMOR_LEVELS, ARGENT_AMMO_LEVELS]
        
        allSwitchOn = self.toggleAllArgentSwitch.get()
        
        if allSwitchOn:
            for index, each in enumerate(allArgentCategories):
                self.argentCallback(each, allArgentLevels[index][4])
        else:
            for index, each in enumerate(allArgentCategories):
                self.argentCallback(each, allArgentLevels[index][0])   

    def initPraetorWidgets(self):
        """ Creates widgets for the PraetorSuitUpgrades inventory module. """
        parent = self.tabMenu.tab('Praetor Suit')
        
        parent.columnconfigure(0, weight = 1)
        
        self.praetorCheckboxWidgets = []
        
        self.praetorSuitHeaderLabel = ctk.CTkLabel(parent, font = self.headerMainFont, text = 'Suit Upgrades')
        self.praetorSuitHeaderLabel.grid(column = 0, row = 2, padx = 20, pady = (80, 10), columnspan = 2, sticky = 'w')
        
        self.toggleAllPraetorSwitch = ctk.CTkSwitch(
            master = parent, 
            text = 'All Upgrades', 
            command = self.toggleAllPraetorUpgrades,
            font = self.checkboxFont,
            progress_color= RED,
            switch_height = 16,
            switch_width = 34)
        self.toggleAllPraetorSwitch.grid(column = 0, row = 3, sticky = 'w', padx = (50, 0), pady = (10, 10))
        
        self.praetorCheckboxFrame1 = ctk.CTkFrame(parent, fg_color = 'transparent', border_color=WHITE, border_width=0)
        self.praetorCheckboxFrame1.grid(column = 0, row = 5)
        
        # ENVIRONMENTAL RESISTANCE
        self.environmentalResistanceLabel = ctk.CTkLabel(self.praetorCheckboxFrame1, font = self.subheaderMainFont, text = 'Environmental Resistance')
        self.environmentalResistanceLabel.grid(column = 0, row = 4, padx = (0, 50), pady = (20, 10), sticky = 'w')
        self.environmentalResistanceFrame = ctk.CTkFrame(self.praetorCheckboxFrame1, fg_color = DARKEST_GRAY)
        self.environmentalResistanceFrame.grid(column = 0, row = 5, padx = (0, 50), columnspan = 3, sticky = 'w')
        
        # hazard protection
        hazardProtectionCallback = partial(self.praetorCallback, 'hazardProtection')
        hazardProtectionTooltipText = self.inventory.praetorSuitUpgrades.hazardProtection.description
        self.hazardProtectionCheckbox = Checkbox(
            parent = self.environmentalResistanceFrame, 
            text = 'Hazard Protection', 
            column = 0, 
            row = 0, 
            command = hazardProtectionCallback,
            tooltipMsg = hazardProtectionTooltipText,
            sticky = 'w',
            pady = (0, 5))
        self.praetorCheckboxWidgets.append(self.hazardProtectionCheckbox)
        
        # self preservation
        selfPreservationCallback = partial(self.praetorCallback, 'selfPreservation')
        selfPreservationTooltipText = self.inventory.praetorSuitUpgrades.selfPreservation.description
        self.selfPreservationCheckbox = Checkbox(
            parent = self.environmentalResistanceFrame, 
            text = 'Self Preservation', 
            column = 0, 
            row = 1, 
            command = selfPreservationCallback,
            tooltipMsg = selfPreservationTooltipText,
            sticky = 'w',
            pady = (0, 5))
        self.praetorCheckboxWidgets.append(self.selfPreservationCheckbox)
        
        # barrels o' fun
        barrelsOfunCallback = partial(self.praetorCallback, 'barrelsOFun')
        barrelsOfunTooltipText = self.inventory.praetorSuitUpgrades.barrelsOFun.description
        self.barrelsOFunCheckbox = Checkbox(
            parent = self.environmentalResistanceFrame, 
            text = 'Barrels O\' Fun', 
            column = 0, 
            row = 2, 
            command = barrelsOfunCallback,
            tooltipMsg = barrelsOfunTooltipText,
            sticky = 'w',
            pady = (0, 5))
        self.praetorCheckboxWidgets.append(self.barrelsOFunCheckbox)
        
        # AREA-SCANNING TECHNOLOGY
        self.areaScanningLabel = ctk.CTkLabel(self.praetorCheckboxFrame1, font = self.subheaderMainFont, text = 'Area-Scanning Technology')
        self.areaScanningLabel.grid(column = 1, row = 4, padx = (0, 30), pady = (20, 10), sticky = 'w')
        self.areaScanningFrame = ctk.CTkFrame(self.praetorCheckboxFrame1, fg_color = DARKEST_GRAY)
        self.areaScanningFrame.grid(column = 1, row = 5, padx = (0, 30), columnspan = 3, sticky = 'w')
        
        # item awareness
        itemAwarenessCallback = partial(self.praetorCallback, 'itemAwareness')
        itemAwarenessTooltipText = self.inventory.praetorSuitUpgrades.itemAwareness.description
        self.itemAwarenessCheckbox = Checkbox(
            parent = self.areaScanningFrame, 
            text = 'Item Awareness', 
            column = 0, 
            row = 0, 
            command = itemAwarenessCallback,
            tooltipMsg = itemAwarenessTooltipText,
            sticky = 'w',
            pady = (0, 5))
        self.praetorCheckboxWidgets.append(self.itemAwarenessCheckbox)
        
        # secret sense
        secretSenseCallback = partial(self.praetorCallback, 'secretSense')
        secretSenseTooltipText = self.inventory.praetorSuitUpgrades.secretSense.description
        self.secretSenseCheckbox = Checkbox(
            parent = self.areaScanningFrame, 
            text = 'Secret Sense', 
            column = 0, row = 1, 
            command = secretSenseCallback,
            tooltipMsg = secretSenseTooltipText,
            sticky = 'w',
            pady = (0, 5))
        self.praetorCheckboxWidgets.append(self.secretSenseCheckbox)
        
        # full view
        fullViewCallback = partial(self.praetorCallback, 'fullView')
        fullViewTooltipText = self.inventory.praetorSuitUpgrades.fullView.description
        self.fullViewCheckbox = Checkbox(
            parent = self.areaScanningFrame, 
            text = 'Full View', 
            column = 0, 
            row = 2, 
            command = fullViewCallback,
            tooltipMsg = fullViewTooltipText,
            sticky = 'w',
            pady = (0, 5))
        self.praetorCheckboxWidgets.append(self.fullViewCheckbox)
        
        # EQUIPMENT SYSTEM
        self.equipmentSystemLabel = ctk.CTkLabel(self.praetorCheckboxFrame1, font = self.subheaderMainFont, text = 'Equipment System')
        self.equipmentSystemLabel.grid(column = 2, row = 4, padx = (20, 0), pady = (20, 10), sticky = 'w')
        self.equipmentSystemFrame = ctk.CTkFrame(self.praetorCheckboxFrame1, fg_color = DARKEST_GRAY)
        self.equipmentSystemFrame.grid(column = 2, row = 5, padx = (20, 0), columnspan = 3, sticky = 'w')
        
        # quick charge
        quickChargeCallback = partial(self.praetorCallback, 'quickCharge')
        quickChargeTooltipText = self.inventory.praetorSuitUpgrades.quickCharge.description
        self.quickChargeCheckbox = Checkbox(
            parent = self.equipmentSystemFrame, 
            text = 'Quick Charge', 
            column = 0, 
            row = 0, 
            command = quickChargeCallback,
            tooltipMsg = quickChargeTooltipText,
            sticky = 'w',
            pady = (0, 5))
        self.praetorCheckboxWidgets.append(self.quickChargeCheckbox)
        
        # stock up
        stockUpCallback = partial(self.praetorCallback, 'stockUp')
        stockUpTooltipText = self.inventory.praetorSuitUpgrades.stockUp.description
        self.stockUpCheckbox = Checkbox(
            parent = self.equipmentSystemFrame, 
            text = 'Stock Up', 
            column = 0, 
            row = 1, 
            command = stockUpCallback,
            tooltipMsg = stockUpTooltipText,
            sticky = 'w',
            pady = (0, 5))
        self.praetorCheckboxWidgets.append(self.stockUpCheckbox)
        
        # rapid charge
        rapidChargeCallback = partial(self.praetorCallback, 'rapidCharge')
        rapidChargeTooltipText = self.inventory.praetorSuitUpgrades.rapidCharge.description
        self.rapidChargeCheckbox = Checkbox(
            parent = self.equipmentSystemFrame, 
            text = 'Rapid Charge', 
            column = 0, 
            row = 2, 
            command = rapidChargeCallback,
            tooltipMsg = rapidChargeTooltipText,
            sticky = 'w',
            pady = (0, 5))
        self.praetorCheckboxWidgets.append(self.rapidChargeCheckbox)
        
        self.praetorCheckboxFrame2 = ctk.CTkFrame(parent, fg_color = 'transparent', border_color=WHITE, border_width=0)
        self.praetorCheckboxFrame2.grid(column = 0, row = 6, padx = (0, 30), pady = (20, 0))
        
        # POWERUP EFFECTIVENESS
        self.powerupEffectivenessLabel = ctk.CTkLabel(self.praetorCheckboxFrame2, font = self.subheaderMainFont, text = 'Powerup Effectiveness')
        self.powerupEffectivenessLabel.grid(column = 0, row = 6, padx = (0, 60), pady = (20, 10), sticky = 'w')
        self.powerupEffectivenessFrame = ctk.CTkFrame(self.praetorCheckboxFrame2, fg_color = DARKEST_GRAY)
        self.powerupEffectivenessFrame.grid(column = 0, row = 7, padx = (0, 60), columnspan = 3, sticky = 'w')
        
        # power surge
        powerSurgeCallback = partial(self.praetorCallback, 'powerSurge')
        powerSurgeTooltipText = self.inventory.praetorSuitUpgrades.powerSurge.description
        self.powerSurgeCheckbox = Checkbox(
            parent = self.powerupEffectivenessFrame, 
            text = 'Power Surge', 
            column = 0, 
            row = 0, 
            command = powerSurgeCallback,
            tooltipMsg = powerSurgeTooltipText,
            sticky = 'w',
            pady = (0, 5))
        self.praetorCheckboxWidgets.append(self.powerSurgeCheckbox)
        
        # healing power
        healingPowerCallback = partial(self.praetorCallback, 'healingPower')
        healingPowerTooltipText = self.inventory.praetorSuitUpgrades.healingPower.description
        self.healingPowerCheckbox = Checkbox(
            parent = self.powerupEffectivenessFrame, 
            text = 'Healing Power', 
            column = 0, 
            row = 1, 
            command = healingPowerCallback,
            tooltipMsg = healingPowerTooltipText,
            sticky = 'w',
            pady = (0, 5))
        self.praetorCheckboxWidgets.append(self.healingPowerCheckbox)
        
        # power extender
        powerExtenderCallback = partial(self.praetorCallback, 'powerExtender')
        powerExtenderTooltipText = self.inventory.praetorSuitUpgrades.powerExtender.description
        self.powerExtenderCheckbox = Checkbox(
            parent = self.powerupEffectivenessFrame, 
            text = 'Power Extender', 
            column = 0, 
            row = 2, 
            command = powerExtenderCallback,
            tooltipMsg = powerExtenderTooltipText,
            sticky = 'w',
            pady = (0, 5))
        self.praetorCheckboxWidgets.append(self.powerExtenderCheckbox)
        
        # DEXTERITY
        self.dexterityLabel = ctk.CTkLabel(self.praetorCheckboxFrame2, font = self.subheaderMainFont, text = 'Dexterity')
        self.dexterityLabel.grid(column = 1, row = 6, padx = (0, 0), pady = (20, 10), sticky = 'w')
        self.dexterityFrame = ctk.CTkFrame(self.praetorCheckboxFrame2, fg_color = DARKEST_GRAY)
        self.dexterityFrame.grid(column = 1, row = 7, padx = (0, 0), columnspan = 3, sticky = 'w')
        
        # adept
        adeptCallback = partial(self.praetorCallback, 'adept')
        adeptTooltipText = self.inventory.praetorSuitUpgrades.adept.description
        self.adeptCheckbox = Checkbox(
            parent = self.dexterityFrame, 
            text = 'Adept', 
            column = 0, 
            row = 0, 
            command = adeptCallback,
            tooltipMsg = adeptTooltipText,
            sticky = 'w',
            pady = (0, 5))
        self.praetorCheckboxWidgets.append(self.adeptCheckbox)
        
        # quick hands
        quickHandsCallback = partial(self.praetorCallback, 'quickHands')
        quickHandsTooltipText = self.inventory.praetorSuitUpgrades.quickHands.description
        self.quickHandsCheckbox = Checkbox(
            parent = self.dexterityFrame, 
            text = 'Quick Hands', 
            column = 0, 
            row = 1, 
            command = quickHandsCallback,
            tooltipMsg = quickHandsTooltipText,
            sticky = 'w',
            pady = (0, 5))
        self.praetorCheckboxWidgets.append(self.quickHandsCheckbox)
        
        # hot swap
        hotSwapCallback = partial(self.praetorCallback, 'hotSwap')
        hotSwapTooltipText = self.inventory.praetorSuitUpgrades.hotSwap.description
        self.hotSwapCheckbox = Checkbox(
            parent = self.dexterityFrame, 
            text = 'Hot Swap', 
            column = 0, 
            row = 2, 
            command = hotSwapCallback,
            tooltipMsg = hotSwapTooltipText,
            sticky = 'w',
            pady = (0, 5))
        self.praetorCheckboxWidgets.append(self.hotSwapCheckbox)

    def praetorCallback(self, perkName: str):
        """ Toggles a PraetorPerk's availability.  """
        
        # if not in available, add it; else, remove
        found = False
        for perk in self.inventory.praetorSuitUpgrades.available:
            if perk.name == perkName:
                found = True
                self.inventory.praetorSuitUpgrades.available.remove(perk)
                # clear toggleAll switch - all are no longer selected
                if self.toggleAllPraetorSwitch.get():
                    self.toggleAllPraetorSwitch.deselect()
                break
        if not found:
            self.inventory.praetorSuitUpgrades.addToAvailable(perkName)
    
    def toggleAllPraetorUpgrades(self):
        """ Adds/removes every upgrade, and selects/deselects checkboxes accordingly.  """
        
        allSwitchOn = self.toggleAllPraetorSwitch.get()
        
        if allSwitchOn:
            self.inventory.praetorSuitUpgrades.addAllToAvailable()
            # update UI - all praetor checkboxes
            for each in self.praetorCheckboxWidgets:
                each.select()
        else:
            self.inventory.praetorSuitUpgrades.available.clear()
            for each in self.praetorCheckboxWidgets:
                each.deselect()      
   
    def initEquipmentWidgets(self):
        """ Creates widgets for the Equipment inventory module. """
        
        parentTab = self.tabMenu.tab('Equipment & Weapons')
        
        parentTab.columnconfigure(0, weight = 1)
        
        self.equipmentCheckboxWidgets = []
        
        self.equipmentHeaderLabel = ctk.CTkLabel(parentTab, font = self.headerMainFont, text = 'Equipment')
        self.equipmentHeaderLabel.grid(column = 0, row = 0, padx = 20, pady = (80, 10), columnspan = 2, sticky = 'nw')
        
        self.toggleAllEquipmentSwitch = ctk.CTkSwitch(
            master = parentTab, 
            text = 'All Equipment', 
            command = self.toggleAllEquipment,
            font = self.checkboxFont,
            progress_color= RED,
            switch_height = 16,
            switch_width = 34)
        self.toggleAllEquipmentSwitch.grid(column = 0, row = 1, sticky = 'w', padx = (50, 0), pady = (10, 30))
        
        self.equipmentCheckboxFrame = ctk.CTkFrame(parentTab, fg_color = 'transparent', border_color=WHITE, border_width=0)
        self.equipmentCheckboxFrame.grid(column = 0, row = 2)
        
        # double jump thrust boots
        doubleJumpThrustBootsCallback = partial(self.equipmentCallback, 'doubleJumpThrustBoots')
        doubleJumpThrustBootsTooltipText = self.inventory.equipment.doubleJumpThrustBoots.description
        self.doubleJumpThrustBootsCheckbox = Checkbox(
            parent = self.equipmentCheckboxFrame, 
            text = 'Delta V Jump-Boots', 
            column = 0, 
            row = 0, 
            command = doubleJumpThrustBootsCallback,
            tooltipMsg = doubleJumpThrustBootsTooltipText,
            sticky = 'w',
            padx = (35, 0),
            pady = (0, 45))
        self.equipmentCheckboxWidgets.append(self.doubleJumpThrustBootsCheckbox)
        
        # frag grenade
        fragGrenadeCallback = partial(self.equipmentCallback, 'fragGrenade')
        fragGrenadeTooltipText = self.inventory.equipment.fragGrenade.description
        self.fragGrenadeCheckbox = Checkbox(
            parent = self.equipmentCheckboxFrame, 
            text = 'Frag Grenade', 
            column = 1, 
            row = 0, 
            command = fragGrenadeCallback,
            tooltipMsg = fragGrenadeTooltipText,
            sticky = 'w',
            padx = (35, 0),
            pady = (0, 45))
        self.equipmentCheckboxWidgets.append(self.fragGrenadeCheckbox)
        
        # decoy hologram
        decoyHologramCallback = partial(self.equipmentCallback, 'decoyHologram')
        decoyHologramTooltipText = self.inventory.equipment.decoyHologram.description
        self.decoyHologramCheckbox = Checkbox(
            parent = self.equipmentCheckboxFrame, 
            text = 'Decoy Hologram', 
            column = 2, 
            row = 0, 
            command = decoyHologramCallback,
            tooltipMsg = decoyHologramTooltipText,
            sticky = 'w',
            padx = (35, 0),
            pady = (0, 45))
        self.equipmentCheckboxWidgets.append(self.decoyHologramCheckbox)
        
        # siphon grenade
        siphonGrenadeCallback = partial(self.equipmentCallback, 'siphonGrenade')
        siphonGrenadeTooltipText = self.inventory.equipment.siphonGrenade.description
        self.siphonGrenadeCheckbox = Checkbox(
            parent = self.equipmentCheckboxFrame, 
            text = 'Siphon Grenade', 
            column = 3, 
            row = 0, 
            command = siphonGrenadeCallback,
            tooltipMsg = siphonGrenadeTooltipText,
            sticky = 'w',
            padx = (35, 0),
            pady = (0, 45))
        self.equipmentCheckboxWidgets.append(self.siphonGrenadeCheckbox)
    
    def equipmentCallback(self, equipmentItemName: str):
        """ Toggles an EquipmentItem's availability.  """
        
        # if not in available, add it; else, remove
        found = False
        for equipmentItem in self.inventory.equipment.available:
            if equipmentItem.name == equipmentItemName:
                found = True
                self.inventory.equipment.available.remove(equipmentItem)
                # clear toggleAll switch - all are no longer selected
                if self.toggleAllEquipmentSwitch.get():
                    self.toggleAllEquipmentSwitch.deselect()
                break
        if not found:
            self.inventory.equipment.addToAvailable(equipmentItemName)
    
    def toggleAllEquipment(self):
        """ Adds/removes all equipment, and selects/deselects checkboxes accordingly.  """
        
        allSwitchOn = self.toggleAllEquipmentSwitch.get()
        
        if allSwitchOn:
            self.inventory.equipment.addAllToAvailable()
            # update UI - all equipment checkboxes
            for each in self.equipmentCheckboxWidgets:
                each.select()
        else:
            self.inventory.equipment.available.clear()
            for each in self.equipmentCheckboxWidgets:
                each.deselect()     
    
    def initWeaponWidgets(self):
        """ Creates widgets for the Weapons inventory module. """
        
        parentTab = self.tabMenu.tab('Equipment & Weapons')
        
        self.weaponsCheckboxWidgets = []
        
        self.weaponsHeaderLabel = ctk.CTkLabel(parentTab, font = self.headerMainFont, text = 'Weapons')
        self.weaponsHeaderLabel.grid(column = 0, row = 3, padx = 20, pady = (20, 10), columnspan = 2, sticky = 'nw')
        
        self.toggleAllWeaponsSwitch = ctk.CTkSwitch(
            master = parentTab, 
            text = 'All Weapons', 
            command = self.toggleAllWeapons,
            font = self.checkboxFont,
            progress_color= RED,
            switch_height = 16,
            switch_width = 34)
        self.toggleAllWeaponsSwitch.grid(column = 0, row = 4, sticky = 'w', padx = (50, 0), pady = (10, 30))
        
        self.weaponsCheckboxFrame1 = ctk.CTkFrame(parentTab, fg_color = 'transparent', border_color=WHITE, border_width=0)
        self.weaponsCheckboxFrame1.grid(column = 0, row = 5)
        
        # chainsaw
        chainsawCallback = partial(self.weaponsCallback, 'chainsaw')
        chainsawTooltipText = self.inventory.weapons.chainsaw.description
        self.chainsawCheckbox = Checkbox(
            parent = self.weaponsCheckboxFrame1, 
            text = 'Chainsaw', 
            column = 0, 
            row = 0, 
            command = chainsawCallback,
            tooltipMsg = chainsawTooltipText,
            sticky = 'w',
            padx = (0, 50),
            pady = (0, 10))
        self.weaponsCheckboxWidgets.append(self.chainsawCheckbox)
        
        # combat shotgun
        combatShotgunCallback = partial(self.weaponsCallback, 'combatShotgun')
        combatShotgunTooltipText = self.inventory.weapons.combatShotgun.description
        self.combatShotgunCheckbox = Checkbox(
            parent = self.weaponsCheckboxFrame1, 
            text = 'Combat Shotgun', 
            column = 0, 
            row = 1, 
            command = combatShotgunCallback,
            tooltipMsg = combatShotgunTooltipText,
            sticky = 'w',
            padx = (0, 50),
            pady = (0, 10))
        self.weaponsCheckboxWidgets.append(self.combatShotgunCheckbox)
        
        # heavy assault rifle
        heavyAssaultRifleCallback = partial(self.weaponsCallback, 'heavyAssaultRifle')
        heavyAssaultRifleTooltipText = self.inventory.weapons.heavyAssaultRifle.description
        self.heavyAssaultRifleCheckbox = Checkbox(
            parent = self.weaponsCheckboxFrame1, 
            text = 'Heavy Assault Rifle', 
            column = 0, 
            row = 2, 
            command = heavyAssaultRifleCallback,
            tooltipMsg = heavyAssaultRifleTooltipText,
            sticky = 'w',
            padx = (0, 50),
            pady = (0, 10))
        self.weaponsCheckboxWidgets.append(self.heavyAssaultRifleCheckbox)
        
        # plasma rifle
        plasmaRifleCallback = partial(self.weaponsCallback, 'plasmaRifle')
        plasmaRifleTooltipText = self.inventory.weapons.plasmaRifle.description
        self.plasmaRifleCheckbox = Checkbox(
            parent = self.weaponsCheckboxFrame1, 
            text = 'Plasma Rifle', 
            column = 1, 
            row = 0, 
            command = plasmaRifleCallback,
            tooltipMsg = plasmaRifleTooltipText,
            sticky = 'w',
            padx = (0, 50),
            pady = (0, 10))
        self.weaponsCheckboxWidgets.append(self.plasmaRifleCheckbox)
        
        # rocket launcher
        rocketLauncherCallback = partial(self.weaponsCallback, 'rocketLauncher')
        rocketLauncherTooltipText = self.inventory.weapons.rocketLauncher.description
        self.rocketLauncherCheckbox = Checkbox(
            parent = self.weaponsCheckboxFrame1, 
            text = 'Rocket Launcher', 
            column = 1, 
            row = 1, 
            command = rocketLauncherCallback,
            tooltipMsg = rocketLauncherTooltipText,
            sticky = 'w',
            padx = (0, 50),
            pady = (0, 10))
        self.weaponsCheckboxWidgets.append(self.rocketLauncherCheckbox)
        
        # super shotgun
        superShotgunCallback = partial(self.weaponsCallback, 'superShotgun')
        superShotgunTooltipText = self.inventory.weapons.superShotgun.description
        self.superShotgunCheckbox = Checkbox(
            parent = self.weaponsCheckboxFrame1, 
            text = 'Super Shotgun', 
            column = 1, 
            row = 2, 
            command = superShotgunCallback,
            tooltipMsg = superShotgunTooltipText,
            sticky = 'w',
            padx = (0, 50),
            pady = (0, 10))
        self.weaponsCheckboxWidgets.append(self.superShotgunCheckbox)
        
        # gauss cannon
        gaussCannonCallback = partial(self.weaponsCallback, 'gaussCannon')
        gaussCannonTooltipText = self.inventory.weapons.gaussCannon.description
        self.gaussCannonCheckbox = Checkbox(
            parent = self.weaponsCheckboxFrame1, 
            text = 'Gauss Cannon', 
            column = 3, 
            row = 0, 
            command = gaussCannonCallback,
            tooltipMsg = gaussCannonTooltipText,
            sticky = 'w',
            padx = (0, 0),
            pady = (0, 10))
        self.weaponsCheckboxWidgets.append(self.gaussCannonCheckbox)
        
        # chaingun
        chaingunCallback = partial(self.weaponsCallback, 'chaingun')
        chaingunTooltipText = self.inventory.weapons.chaingun.description
        self.chaingunCheckbox = Checkbox(
            parent = self.weaponsCheckboxFrame1, 
            text = 'Chaingun', 
            column = 3, 
            row = 1, 
            command = chaingunCallback,
            tooltipMsg = chaingunTooltipText,
            sticky = 'w',
            padx = (0, 0),
            pady = (0, 10))
        self.weaponsCheckboxWidgets.append(self.chaingunCheckbox)
        
        # bfg-9000
        bfg9000Callback = partial(self.weaponsCallback, 'bfg9000')
        bfg9000TooltipText = self.inventory.weapons.bfg9000.description
        self.bfg9000Checkbox = Checkbox(
            parent = self.weaponsCheckboxFrame1, 
            text = 'BFG-9000', 
            column = 3, 
            row = 2, 
            command = bfg9000Callback,
            tooltipMsg = bfg9000TooltipText,
            sticky = 'w',
            padx = (0, 0),
            pady = (0, 10))
        self.weaponsCheckboxWidgets.append(self.bfg9000Checkbox)
    
    def weaponsCallback(self, weaponItemName: str):
        """ Toggles a WeaponItem's availability.  """
        
        # if not in available, add it; else, remove
        found = False
        for weaponItem in self.inventory.weapons.available:
            if weaponItem.name == weaponItemName:
                found = True
                self.inventory.equipment.available.remove(weaponItem)
                # clear toggleAll switch - all are no longer selected
                if self.toggleAllEquipmentSwitch.get():
                    self.toggleAllEquipmentSwitch.deselect()
                break
        if not found:
            self.inventory.equipment.addToAvailable(weaponItemName)
    
    def toggleAllWeapons(self):
        """ Adds/removes all weapons, and selects/deselects checkboxes accordingly.  """
        
        allSwitchOn = self.toggleAllWeaponsSwitch.get()
        
        if allSwitchOn:
            self.inventory.weapons.addAllToAvailable()
            # update UI - all weapon checkboxes
            for each in self.weaponsCheckboxWidgets:
                each.select()
        else:
            self.inventory.weapons.available.clear()
            for each in self.weaponsCheckboxWidgets:
                each.deselect()    
    
    def initRuneWidgets(self) -> None:
        """ Creates widgets for the Runes inventory module. """
        
        parentTab = self.tabMenu.tab('Runes')
        parentTab.columnconfigure(0, weight = 1)
        
        self.runesAvailableCheckboxWidgets = []
        self.runesUpgradedCheckboxWidgets = []
        self.runesPermEquipCheckboxWidgets = []
        
        self.runesHeaderLabel = ctk.CTkLabel(parentTab, font = self.headerMainFont, text = 'Runes')
        self.runesHeaderLabel.grid(column = 0, row = 3, padx = 20, pady = (20, 10), columnspan = 2, sticky = 'nw')
        
        self.runesSwitchFrame = ctk.CTkFrame(parentTab, fg_color = 'transparent')
        self.runesSwitchFrame.grid(column = 0, row =  4, pady = (0, 20))
        
        self.toggleAllRunesAvailableSwitch = ctk.CTkSwitch(
            master = self.runesSwitchFrame, 
            text = 'All Runes Unlocked', 
            command = self.toggleAllRunesAvailable,
            font = self.checkboxFont,
            progress_color= RED,
            switch_height = 16,
            switch_width = 34)
        self.toggleAllRunesAvailableSwitch.grid(column = 0, row = 0, sticky = 'w', padx = (0, 0), pady = (0, 0))
        
        self.toggleAllRunesUpgradedSwitch = ctk.CTkSwitch(
            master = self.runesSwitchFrame, 
            text = 'All Runes Upgraded', 
            command = self.toggleAllRunesUpgraded,
            font = self.checkboxFont,
            progress_color= RED,
            switch_height = 16,
            switch_width = 34,
            state = 'disabled')
        self.toggleAllRunesUpgradedSwitch.grid(column = 1, row = 0, sticky = 'w', padx = (20, 0), pady = (0, 0))
        
        self.toggleAllRunesPermEquipSwitch = ctk.CTkSwitch(
            master = self.runesSwitchFrame, 
            text = 'All Runes Permanently Equipped', 
            command = self.toggleAllRunesPermEquip,
            font = self.checkboxFont,
            progress_color= RED,
            switch_height = 16,
            switch_width = 34,
            state = 'disabled')
        self.toggleAllRunesPermEquipSwitch.grid(column = 2, row = 0, sticky = 'w', padx = (20, 0), pady = (0, 0))
        
        self.runesCheckboxFrame1 = ctk.CTkFrame(parentTab, fg_color = 'transparent', border_color = WHITE, border_width = 0)
        self.runesCheckboxFrame1.grid(column = 0, row = 5, pady = (10, 10))
        
        # VACUUM
        self.vacuumPanel = RunePanel(
            parentApp = self, 
            parentFrame = self.runesCheckboxFrame1, 
            parentFrameColumn = 0,
            parentFrameRow = 0,
            runePerkName = 'vacuum')
        
        # DAZED AND CONFUSED
        self.dazedAndConfusedPanel = RunePanel(
            parentApp = self, 
            parentFrame = self.runesCheckboxFrame1, 
            parentFrameColumn = 1,
            parentFrameRow = 0,
            runePerkName = 'dazedAndConfused',
            panelPadX = (30, 0))
        
        # AMMO BOOST
        self.ammoBoostPanel = RunePanel(
            parentApp = self, 
            parentFrame = self.runesCheckboxFrame1, 
            parentFrameColumn = 2,
            parentFrameRow = 0,
            runePerkName = 'ammoBoost',
            panelPadX = (30, 0))
        
        self.runesCheckboxFrame2 = ctk.CTkFrame(parentTab, fg_color = 'transparent', border_color = WHITE, border_width = 0)
        self.runesCheckboxFrame2.grid(column = 0, row = 6, pady = (10, 10))
        
        # EQUIPMENT POWER
        self.equipmentPowerPanel = RunePanel(
            parentApp = self, 
            parentFrame = self.runesCheckboxFrame2, 
            parentFrameColumn = 0,
            parentFrameRow = 0,
            runePerkName = 'equipmentPower')
        
        # SEEK AND DESTROY
        self.seekAndDestroyPanel = RunePanel(
            parentApp = self, 
            parentFrame = self.runesCheckboxFrame2, 
            parentFrameColumn = 1,
            parentFrameRow = 0,
            runePerkName = 'seekAndDestroy',
            panelPadX = (30, 0))
        
        # SAVAGERY
        self.savageryPanel = RunePanel(
            parentApp = self, 
            parentFrame = self.runesCheckboxFrame2, 
            parentFrameColumn = 2,
            parentFrameRow = 0,
            runePerkName = 'savagery',
            panelPadX = (30, 0))
        
        self.runesCheckboxFrame3 = ctk.CTkFrame(parentTab, fg_color = 'transparent', border_color = WHITE, border_width = 0)
        self.runesCheckboxFrame3.grid(column = 0, row = 7, pady = (10, 10))
        
        # IN-FLIGHT MOBILITY
        self.inFlightMobilityPanel = RunePanel(
            parentApp = self, 
            parentFrame = self.runesCheckboxFrame3, 
            parentFrameColumn = 0,
            parentFrameRow = 0,
            runePerkName = 'inFlightMobility')
        
        # ARMORED OFFENSIVE
        self.armoredOffensivePanel = RunePanel(
            parentApp = self, 
            parentFrame = self.runesCheckboxFrame3, 
            parentFrameColumn = 1,
            parentFrameRow = 0,
            runePerkName = 'armoredOffensive',
            panelPadX = (30, 0))
        
        # BLOOD FUELED
        self.bloodFueledPanel = RunePanel(
            parentApp = self, 
            parentFrame = self.runesCheckboxFrame3, 
            parentFrameColumn = 2,
            parentFrameRow = 0,
            runePerkName = 'bloodFueled',
            panelPadX = (30, 0))
        
        self.runesCheckboxFrame4 = ctk.CTkFrame(parentTab, fg_color = 'transparent', border_color = WHITE, border_width = 0)
        self.runesCheckboxFrame4.grid(column = 0, row = 8, pady = (10, 0))
        
        # INTIMACY IS BEST
        self.intimacyIsBestPanel = RunePanel(
            parentApp = self, 
            parentFrame = self.runesCheckboxFrame4, 
            parentFrameColumn = 0,
            parentFrameRow = 0,
            runePerkName = 'intimacyIsBest')
        
        # RICH GET RICHER
        self.richGetRicherPanel = RunePanel(
            parentApp = self, 
            parentFrame = self.runesCheckboxFrame4, 
            parentFrameColumn = 1,
            parentFrameRow = 0,
            runePerkName = 'richGetRicher',
            panelPadX = (30, 0))
        
        # SAVING THROW
        self.savingThrowPanel = RunePanel(
            parentApp = self, 
            parentFrame = self.runesCheckboxFrame4, 
            parentFrameColumn = 2,
            parentFrameRow = 0,
            runePerkName = 'savingThrow',
            panelPadX = (30, 0))
     
    def runeAvailableCallback(self, runePerkName: str):
        """ Toggles a RunePerk's availability.  """
        
        runePanel = RUNE_PANEL_DATA[runePerkName]['panel']
        
        # if not in available, add it; else, remove
        found = False
        for runePerk in self.inventory.runes.available:
            if runePerk.name == runePerkName:
                found = True
                self.inventory.runes.available.remove(runePerk)
                # clear toggleAll switch - all are no longer selected
                if self.toggleAllRunesAvailableSwitch.get():
                    self.toggleAllRunesAvailableSwitch.deselect()
                # disable sub-options
                runePanel.runeUpgradedCheckbox.configure(state = 'disabled')
                runePanel.runePermEquipCheckbox.configure(state = 'disabled')
                break
        if not found:
            self.inventory.runes.addToAvailable(runePerkName)
            runePanel.runeUpgradedCheckbox.configure(state = 'normal')
            runePanel.runePermEquipCheckbox.configure(state = 'normal')       
    
    def runeUpgradedCallback(self, runePerkName: str):
        """ Toggles a RunePerk's Upgraded status. """
        
        rune = self.inventory.runes.getRunePerkFromName(runePerkName)
        if rune:
            if rune.applyUpgradesForPerk:
                rune.applyUpgradesForPerk = False
                # clear toggleAll switch - all are no longer selected
                if self.toggleAllRunesUpgradedSwitch.get():
                    self.toggleAllRunesUpgradedSwitch.deselect()
            else:
                rune.applyUpgradesForPerk = True
    
    def runePermEquipCallback(self, runePerkName: str):
        """ Toggles a RunePerk's Permanently Equipped status. """
        
        rune = self.inventory.runes.getRunePerkFromName(runePerkName)
        if rune:
            if rune.runePermanentEquip:
                rune.runePermanentEquip = False
                # clear toggleAll switch - all are no longer selected
                if self.toggleAllRunesPermEquipSwitch.get():
                    self.toggleAllRunesPermEquipSwitch.deselect()
            else:
                rune.runePermanentEquip = True
    
    def toggleAllRunesAvailable(self):
        """ Adds/removes all RunePerks, and selects/deselects checkboxes + enables/disables sub-options accordingly.  """
        
        allSwitchOn = self.toggleAllRunesAvailableSwitch.get()
        
        if allSwitchOn:
            self.inventory.runes.addAllToAvailable()
            # update UI - all rune checkboxes
            for each in self.runesAvailableCheckboxWidgets:
                each.select()
            for each in self.runesUpgradedCheckboxWidgets:
                each.configure(state = 'normal')
            for each in self.runesPermEquipCheckboxWidgets:
                each.configure(state = 'normal')
            # update UI - other 'toggle all' rune switches
            self.toggleAllRunesUpgradedSwitch.configure(state = 'normal')
            self.toggleAllRunesPermEquipSwitch.configure(state = 'normal')
            
        else:
            # clear available status for all runes + update UI
            self.inventory.runes.available.clear()
            for each in self.runesAvailableCheckboxWidgets:
                each.deselect()
            # clear upgraded status for all runes + update UI
            self.inventory.runes.setAllAreUpgraded(False)
            for each in self.runesUpgradedCheckboxWidgets:
                each.deselect()
                each.configure(state = 'disabled')
            # clear perm equip status for all runes + update UI
            self.inventory.runes.setAllArePermEquip(False)
            for each in self.runesPermEquipCheckboxWidgets:
                each.deselect()
                each.configure(state = 'disabled')
            # update UI for sub-option toggle all switches
            self.toggleAllRunesUpgradedSwitch.deselect() 
            self.toggleAllRunesUpgradedSwitch.configure(state = 'disabled')
            self.toggleAllRunesPermEquipSwitch.deselect()
            self.toggleAllRunesPermEquipSwitch.configure(state = 'disabled')
    
    def toggleAllRunesUpgraded(self):
        """ Toggles applyUpgradesForPerk flag for all RunePerks, and selects/deselects checkboxes + enables/disables sub-options accordingly. """
                
        allSwitchOn = self.toggleAllRunesUpgradedSwitch.get()
        
        if allSwitchOn:
            self.inventory.runes.setAllAreUpgraded(True)
            # updating UI - make each Upgraded checkbox selected
            for each in self.runesUpgradedCheckboxWidgets:
                each.select()
        else:
            self.inventory.runes.setAllAreUpgraded(False)
            for each in self.runesUpgradedCheckboxWidgets:
                each.deselect()
            
    def toggleAllRunesPermEquip(self):
        """ Toggles runePermanentEquip flag for all RunePerks, and selects/deselects checkboxes + enables/disables sub-options accordingly. """
        
        allSwitchOn = self.toggleAllRunesPermEquipSwitch.get()
        
        if allSwitchOn:
            self.inventory.runes.setAllArePermEquip(True)
            # updating UI - make each Perm Equip checkbox selected
            for each in self.runesPermEquipCheckboxWidgets:
                each.select()
        else:
            self.inventory.runes.setAllArePermEquip(False)
            for each in self.runesPermEquipCheckboxWidgets:
                each.deselect()
    
    def modifyTestFunc(self):
        """ purely for testing """
        
        #self.inventory.argentCellUpgrades.setArgentLevel('healthCapacity', -1)
        #print(self.inventory.argentCellUpgrades.healthCapacity.count)
        
        #self.inventory.praetorSuitUpgrades.addToAvailable('hazardProtection')
        
        # self.inventory.equipment.addToAvailable('doubleJumpThrustBoots')
        # self.inventory.equipment.addToAvailable('siphonGrenade')
        
        # self.inventory.weapons.addToAvailable('combatShotgun')
        # self.inventory.ammo.addToAvailable('shells')
        # self.inventory.weaponMods.addToAvailable('pistol', 'chargeEfficiency')
        
        # self.inventory.runes.addToAvailable('vacuum')
        # self.inventory.runes.setIsUpgraded('vacuum', True)
        # self.inventory.runes.setIsPermanent('dazedAndConfused', True)
        
    def makeLevelInheritanceDecls(self, path):
        """ Creates decl files for each game level, with inventory inheriting from the previous level. """
        
        levelInheritanceMap = {'argent_tower': 'olympia_surface_1', 'bfg_division': 'olympia_surface_2'}
        # ^ TODO: add the rest!

        for key, value in levelInheritanceMap.items():
            fileName = f'{path}/{key}.decl;devInvLoadout'
            with open(fileName, 'w+') as file:
                file.write('{\n' + indent)
                file.write('inherit = ' + f'"devinvloadout/sp/{value}";')
                file.write('\n' + indent + 'edit = {')
                file.write('\n' + indent + '}')
                file.write('\n}')

    def promptUserForPath(self):
        """ Opens a dialog asking user to select a directory. Sets internal values accordingly. """
        
        selectedDirStr = filedialog.askdirectory(initialdir = '/')
        
        # if 'cancel' wasn't selected
        if len(selectedDirStr) > 0: 
            self.outputPathLabel.configure(text = selectedDirStr + r'/Mods')
            self.doomInstallationPath = selectedDirStr

        if self.popupMsgWindow:
            self.popupMsgWindow.destroy()
       
    def generateMod(self):
        """ Top-level function for generating final, usable mod output file from current app values. """
        
        if self.doomInstallationPath is None:
            # c:\ DOOM installation wasn't found during app init; need path
            pygame.mixer.music.load('res/sounds/dsoof.wav')
            pygame.mixer.music.play(loops = 0)
            message = 'Local C:/ installation of DOOM not found. Browse for /DOOM install directory?'
            self.createPopupMessage(PopupType.PT_PATH, -60, -100, message)
            return
            
        else:
            modSubDir = r'\Mods'
            topLevelPath = self.doomInstallationPath + modSubDir
            if not os.path.exists(topLevelPath):
                os.makedirs(topLevelPath)

        # generate dir structure
        generatedPath = r'generated\decls\devinvloadout\devinvloadout\sp'
        if not os.path.exists(generatedPath):
            os.makedirs(generatedPath)

        # generate all declFiles
        self.inventory.generateDeclFile(generatedPath)
        self.makeLevelInheritanceDecls(generatedPath)
        
        # generate final zip archive of /generated + subdirs + declFiles
        zipName = 'Custom New Game Plus'
        shutil.make_archive(zipName, 'zip', '.', 'generated')
        
        # place in top level path
        outputFileSource = zipName + '.zip'
        outputFileDest = topLevelPath
        shutil.copy(outputFileSource, outputFileDest)

        # cleanup intermediate files
        shutil.rmtree('generated')
        os.remove(outputFileSource)
        
        # play confirmation sound
        confirmationSound = pygame.mixer.Sound('res/sounds/dsgetpow.wav')
        confirmationSound.play()
        
        outputPathStr = topLevelPath.replace('\\', '/')
        confirmMessage: str = f'Mod generated and placed in:\n{str(outputPathStr)}'
        self.createPopupMessage(PopupType.PT_INFO, -60, 0, confirmMessage)


class popupMessage(ctk.CTkToplevel):
    """ Represents a top-level window containing a pop-up message. """

    def __init__(self, parent, width: int, height: int, xOffset: int, yOffset: int, message: str):
        
        super().__init__(master = parent)
        
        self.popupFont = ctk.CTkFont('Eternal UI Regular', FONT_SIZES['Popups'])
        self.mainAppWindow = parent

        # setup window size / position
        self.width = width 
        self.height = height
        spawn_x = int(self.mainAppWindow.winfo_width() * .5 + self.mainAppWindow.winfo_x() - .5 * self.width) + xOffset
        spawn_y = int(self.mainAppWindow.winfo_height() * .5 + self.mainAppWindow.winfo_y() - .5 * self.height) + yOffset
        self.geometry(f'{self.width}x{self.height}+{spawn_x}+{spawn_y}')

        # set appearance
        ctk.set_appearance_mode('dark')
        self.transparentColor = self._apply_appearance_mode(self.cget("fg_color"))
        self.attributes("-transparentcolor", self.transparentColor)
        self.cornerRadius = 15
        self.overrideredirect(True)

        # setting up frame for widgets
        self.popupFrame = ctk.CTkFrame(self, 
                                       corner_radius = self.cornerRadius, 
                                       width=self.width, 
                                       height = self.height,
                                       fg_color = DARK_GRAY, 
                                       bg_color= self.transparentColor,
                                       border_width = 2,
                                       border_color = WHITE)
        self.popupFrame.pack(fill = 'both', expand = True)


class errorPopupMsg(popupMessage):
    """ """
    
    def __init__(self, parent, xOffset: int, yOffset: int, message: str):
        
        super().__init__(
            parent = parent,
            width = 500,
            height = 140,
            xOffset = xOffset,
            yOffset = yOffset,
            message = message)
        
        messageImage = ctk.CTkImage(light_image = Image.open('res/images/info.png'), 
                                    dark_image = Image.open('res/images/info.png'))
      
        self.imageLabel = ctk.CTkLabel(self.popupFrame, image = messageImage, text = '', anchor = 'w')
        self.imageLabel.grid(column = 0, row = 0, padx = 20, pady = 20)

        self.messageLabel = ctk.CTkLabel(self.popupFrame, font = self.popupFont, text = f'{message}', wraplength= 400, padx = 5, pady = 5)
        self.messageLabel.grid(column = 1, row = 0, pady = 20, sticky = 'w')

        self.okButton = ctk.CTkButton(self.popupFrame, font = self.popupFont, text = 'OK', fg_color = RED, hover_color = RED_HIGHLIGHT, command = self.destroy)
        self.okButton.grid(column = 1, row = 1)
        
        
class infoPopupMsg(popupMessage):
    """ """
    
    def __init__(self, parent, xOffset: int, yOffset: int, message: str):
        
        super().__init__(
            parent = parent,
            width = 520,
            height = 120,
            xOffset = xOffset,
            yOffset = yOffset,
            message = message)
        
        messageImage = ctk.CTkImage(light_image = Image.open('res/images/slayer_icon.png'), 
                                    dark_image = Image.open('res/images/slayer_icon.png'), 
                                    size = (60, 60))
      
        self.imageLabel = ctk.CTkLabel(self.popupFrame, image = messageImage, text = '')
        self.imageLabel.grid(column = 0, row = 0, padx = (10, 0), pady = (20, 0))

        self.messageLabel = ctk.CTkLabel(self.popupFrame, font = self.popupFont, text = f'{message}', wraplength= 400, padx = 0, pady = 0)
        self.messageLabel.grid(column = 1, row = 0, padx = (5, 20), pady = 10, sticky = 'w')

        self.okButton = ctk.CTkButton(self.popupFrame, font = self.popupFont, text = 'OK', fg_color = RED, hover_color = RED_HIGHLIGHT, command = self.destroy)
        self.okButton.grid(column = 1, row = 1, padx = (0, 20), pady = (0, 15))
        
        
class promptPopupMsg(popupMessage):
    """ """
    
    def __init__(self, parent, xOffset: int, yOffset: int, message: str):
        
        super().__init__(
            parent = parent,
            width = 520,
            height = 130,
            xOffset = xOffset,
            yOffset = yOffset,
            message = message)
        
        messageImage = ctk.CTkImage(light_image = Image.open('res/images/info.png'), 
                                    dark_image = Image.open('res/images/info.png'))
      
        self.imageLabel = ctk.CTkLabel(self.popupFrame, image = messageImage, text = '')
        self.imageLabel.grid(column = 0, row = 0, padx = (30, 0), pady = (30, 0))

        self.messageLabel = ctk.CTkLabel(self.popupFrame, font = self.popupFont, text = f'{message}', wraplength= 400, padx = 0, pady = 0)
        self.messageLabel.grid(column = 1, row = 0, padx = (30, 0), pady = (30, 0), sticky = 'w', columnspan = 2)

        self.browseButton = ctk.CTkButton(self.popupFrame, width = 80, font = self.popupFont, text = 'Browse', fg_color = RED, hover_color = RED_HIGHLIGHT, command = parent.promptUserForPath)
        self.browseButton.grid(column = 1, row = 1, padx = (40, 0), pady = (15, 15), sticky = 'e')
        
        self.cancelButton = ctk.CTkButton(self.popupFrame, width = 80, font = self.popupFont, text = 'Cancel', fg_color = LIGHT_GRAY, hover_color = RED_HIGHLIGHT, command = self.destroy)
        self.cancelButton.grid(column = 2, row = 1, padx = (10, 0), pady = (15, 15), sticky = 'w')
    

class DropdownMenu(ctk.CTkOptionMenu):
    """ App drop-down menu widget base class. """

    def __init__(self, parent, values, command):

        self.dropdownWidgetFont = ctk.CTkFont('Eternal UI Regular', FONT_SIZES['Dropdowns'])

        super().__init__(master = parent, 
                         fg_color = DARK_GRAY, 
                         button_color = RED, 
                         button_hover_color = RED_HIGHLIGHT,
                         font = self.dropdownWidgetFont,
                         values = values,
                         command = command,
                         dropdown_font = self.dropdownWidgetFont)


class Checkbox(ctk.CTkCheckBox):
    """ App checkbox widget base class. """

    def __init__(self, parent, text, column, row, command, tooltipMsg, padx: tuple = (20, 0), pady: tuple = (0, 0), sticky = None, state = 'normal', font = None, checkboxHeight = 24, checkboxWidth = 24):
        
        if font is None:
            font = ctk.CTkFont('Eternal UI Regular', FONT_SIZES['Checkboxes'])
        
        super().__init__(
            master = parent,
            fg_color = RED,
            hover_color = RED_HIGHLIGHT,
            font = font,
            text = text,
            command = command,
            state = state,
            checkbox_height = checkboxHeight,
            checkbox_width = checkboxWidth)
        
        self.grid(column = column, row = row, padx = padx, pady = pady, sticky = sticky)
        tooltipText = tooltipMsg
        CTkToolTip(self, message = tooltipText)


class RunePanel():
    """ """
    
    def __init__(self, parentApp, parentFrame, parentFrameColumn, parentFrameRow, runePerkName: str, panelPadX: tuple = (0, 0), panelPadY: tuple = (0, 0)):
        
        self.runePerk = parentApp.inventory.runes.getRunePerkFromName(runePerkName)
        if self.runePerk is None:
            return
        
        # add to static tracking data
        RUNE_PANEL_DATA[runePerkName]['panel'] = self
        
        # rune: available / header
        runeAvailableCallback = partial(parentApp.runeAvailableCallback, runePerkName)
        self.runeHeaderCheckbox = ctk.CTkCheckBox(
            master = parentFrame, 
            font = parentApp.subheaderMainFont, 
            text = RUNE_PANEL_DATA[self.runePerk.name]['fName'],
            command = runeAvailableCallback,
            fg_color = RED,
            hover_color = RED_HIGHLIGHT)
        self.runeHeaderCheckbox.grid(column = parentFrameColumn, row = parentFrameRow, padx = panelPadX, pady = (0, 10), sticky = 'w')
        CTkToolTip(self.runeHeaderCheckbox, message = self.runePerk.description)
        parentApp.runesAvailableCheckboxWidgets.append(self.runeHeaderCheckbox)
        
        self.runeSubOptionFrame = ctk.CTkFrame(parentFrame, fg_color = 'transparent', border_color= WHITE, border_width=0)
        self.runeSubOptionFrame.grid(column = parentFrameColumn, row = parentFrameRow + 1, padx = panelPadX, sticky = 'w')
        
        runeImage = ctk.CTkImage(light_image = Image.open(RUNE_PANEL_DATA[runePerkName]['imagePath']), dark_image = Image.open(RUNE_PANEL_DATA[runePerkName]['imagePath']), size = (70, 70))
        runeImageLabel = ctk.CTkLabel(self.runeSubOptionFrame, image = runeImage, text = '')
        runeImageLabel.grid(column = 0, row = 0, padx = (0, 0), pady = (0, 0), rowspan = 2, sticky = 'nsew')
        
        # rune: upgraded
        runeUpgradedCallback = partial(parentApp.runeUpgradedCallback, 'vacuum')
        runeUpgradedTooltipText = self.runePerk.upgradeDescription
        self.runeUpgradedCheckbox = Checkbox(
            parent = self.runeSubOptionFrame, 
            text = 'Upgraded', 
            font = parentApp.runeSubOptionFont,
            column = 1, 
            row = 0, 
            command = runeUpgradedCallback,
            tooltipMsg = runeUpgradedTooltipText,
            sticky = 'w',
            pady = (0, 0),
            checkboxHeight = 20,
            checkboxWidth = 20,
            state = 'disabled')
        parentApp.runesUpgradedCheckboxWidgets.append(self.runeUpgradedCheckbox)
        
        # rune: permanent equip
        runePermEquipCallback = partial(parentApp.runePermEquipCallback, 'vacuum')
        permEquipTooltipMsg = 'Permanently equip rune without it taking up a slot.'
        self.runePermEquipCheckbox = Checkbox(
            parent = self.runeSubOptionFrame, 
            text = 'Permanently Equipped', 
            font = parentApp.runeSubOptionFont,
            column = 1, 
            row = 1, 
            command = runePermEquipCallback,
            tooltipMsg = permEquipTooltipMsg,
            sticky = 'w',
            pady = (0, 0),
            checkboxHeight = 20,
            checkboxWidth = 20,
            state = 'disabled')
        parentApp.runesPermEquipCheckboxWidgets.append(self.runePermEquipCheckbox)


if __name__ == '__main__':
    App()
    
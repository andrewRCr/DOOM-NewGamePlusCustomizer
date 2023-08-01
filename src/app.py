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
        self.tabMenu.add('Equipment')
        self.tabMenu.add('Weapons')
        self.tabMenu.add('Runes')
        self.tabMenu.set('Praetor Suit')
        
        # path status info
        cDefaultPath = r'C:\Program Files (x86)\Steam\steamapps\common\DOOM'
        if os.path.exists(cDefaultPath):
            self.doomInstallationPath = cDefaultPath
        
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

    def initArgentWidgets(self):
        """ Creates widgets for the ArgentCellUpgrades inventory module. """
        
        #parent = self.scrollFrame
        parent = self.tabMenu.tab('Praetor Suit')

        self.argentCellHeaderLabel = ctk.CTkLabel(parent, font = self.headerMainFont, text = 'Argent Cell Routing')
        self.argentCellHeaderLabel.grid(column = 0, row = 0, padx = 20, pady = (35, 15), columnspan = 2, sticky = 'w')
        
        self.argentDropdownsFrame = ctk.CTkFrame(parent, fg_color = DARKEST_GRAY)
        self.argentDropdownsFrame.grid(column = 0, row = 1, padx = (100, 70), pady = (10, 0), columnspan = 6)

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
        """ """
  
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

    def initPraetorWidgets(self):
        """ """
        parent = self.tabMenu.tab('Praetor Suit')
        
        parent.columnconfigure(0, weight = 9)
        
        self.praetorCheckboxWidgets = []
        
        self.checkboxFont = ctk.CTkFont('Eternal UI Regular', FONT_SIZES['Checkboxes'])
        
        self.praetorSuitHeaderLabel = ctk.CTkLabel(parent, font = self.headerMainFont, text = 'Suit Upgrades')
        self.praetorSuitHeaderLabel.grid(column = 0, row = 2, padx = 20, pady = (50, 10), columnspan = 2, sticky = 'w')
        
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
                
        for each in self.inventory.praetorSuitUpgrades.available:
            print(each.name)         
            
    def modifyTestFunc(self):
        """ purely for testing """
        
        #self.inventory.argentCellUpgrades.setArgentLevel('healthCapacity', -1)
        #print(self.inventory.argentCellUpgrades.healthCapacity.count)
        
        #self.inventory.praetorSuitUpgrades.addToAvailable('hazardProtection')
        
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
            self.doomInstallationPath = selectedDirStr
            self.outputPathLabel.configure(text = self.doomInstallationPath + r'/Mods')
        
        if self.popupMsgWindow:
            self.popupMsgWindow.destroy()
       
    def generateMod(self):
        """ Top-level function for generating final, usable mod output file from current app values. """

        # look for c:\ DOOM installation and Mods dir
        
        if self.doomInstallationPath is None:
        # PRODUCTION VERSION
        # cPath = r'C:\Program Files (x86)\Steam\steamapps\common\DOOM'
        # if os.path.exists(cPath):
        #     topLevelPath = r'C:\Program Files (x86)\Steam\steamapps\common\DOOM\Mods'
        #     if not os.path.exists(topLevelPath):
        #         os.makedirs(topLevelPath)
        # DEBUG VERSION
        # topLevelPath = r'.\Mods'
        # if not os.path.exists(topLevelPath):
        #         os.makedirs(topLevelPath)
        # c:\ DOOM installation not found; need path
            pygame.mixer.music.load('res/sounds/dsoof.wav')
            pygame.mixer.music.play(loops = 0)
            message = 'Local C:/ installation of DOOM not found. Browse for /DOOM install directory?'
            self.createPopupMessage(PopupType.PT_PATH, 0, 0, message)
            return
            
        else:
            modSubDir = r'\Mods'
            topLevelPath = self.doomInstallationPath + modSubDir

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
        
        # place in top level path (hopefully local DOOM installation's /Mods dir, else program root)
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
            height = 120,
            xOffset = xOffset,
            yOffset = yOffset,
            message = message)
        
        messageImage = ctk.CTkImage(light_image = Image.open('res/images/info.png'), 
                                    dark_image = Image.open('res/images/info.png'))
      
        self.imageLabel = ctk.CTkLabel(self.popupFrame, image = messageImage, text = '')
        self.imageLabel.grid(column = 0, row = 0, padx = (10, 0), pady = (20, 0))

        self.messageLabel = ctk.CTkLabel(self.popupFrame, font = self.popupFont, text = f'{message}', wraplength= 400, padx = 0, pady = 0)
        self.messageLabel.grid(column = 1, row = 0, padx = (5, 20), pady = 10, sticky = 'w')

        self.browseButton = ctk.CTkButton(self.popupFrame, font = self.popupFont, text = 'Browse', fg_color = RED, hover_color = RED_HIGHLIGHT, command = parent.promptUserForPath)
        self.browseButton.grid(column = 1, row = 1, padx = (0, 0), pady = (0, 15))
        
        self.cancelButton = ctk.CTkButton(self.popupFrame, font = self.popupFont, text = 'Cancel', fg_color = RED, hover_color = RED_HIGHLIGHT, command = self.destroy)
        self.cancelButton.grid(column = 2, row = 1, padx = (5, 0), pady = (0, 15))
    

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

    def __init__(self, parent, text, column, row, command, tooltipMsg, padx: tuple = (20, 0), pady: tuple = (0, 0), sticky = None):
        
        self.checkboxFont = ctk.CTkFont('Eternal UI Regular', FONT_SIZES['Checkboxes'])
        
        super().__init__(
            master = parent,
            fg_color = RED,
            hover_color = RED_HIGHLIGHT,
            font = self.checkboxFont,
            text = text,
            command = command)
        
        self.grid(column = column, row = row, padx = padx, pady = pady, sticky = sticky)
        tooltipText = tooltipMsg
        CTkToolTip(self, message = tooltipText)


if __name__ == '__main__':
    App()
    
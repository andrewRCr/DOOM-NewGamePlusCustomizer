"""
app.py:
- general application logic / entry-point
- creates instance of App, which:
--- initializes/manages windows + widgets
--- creates instance of Inventory w/ default modules
--- runs main loop
"""

import contextlib
import customtkinter as ctk
from customtkinter import filedialog
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
from popups import errorPopupMsg, infoPopupMsg, promptPopupMsg
from widgets import DropdownMenu, Checkbox
from panels import WeaponTab, WeaponTabNoMods, RunePanel


class App(ctk.CTk):
    """ Main / core application class. """

    def __init__(self):

        # setup window
        super().__init__(fg_color=BLACK)
        self.geometry(f'{WINDOW_SIZE[0]}x{WINDOW_SIZE[1]}')  # default window size
        self.resizable(False, True)  # allow vertical resize
        self.minsize(WINDOW_SIZE[0], 600)

        # set app window title and icon
        self.title('DOOM (2016) NewGame+ Customizer')
        self.iconbitmap(resource_path(r'images\slayer_icon.ico'))

        # set appearance
        ctk.set_appearance_mode('dark')
        self.changeTitleBarColor()  # change title bar to match rest of window

        # holds current pop-up message (if exists)
        self.popupMsgWindow = None

        # to hold path once determined
        self.doomInstallationPath = None

        # create bottom frame: holds generate mod button
        self.bottomFrame = ctk.CTkFrame(self, fg_color='transparent')
        self.bottomFrame.pack(side='bottom', fill='x')

        # create path status frame, above bottom frame / below main content frame
        self.statusFrame = ctk.CTkFrame(self, fg_color='transparent')
        self.statusFrame.pack(side='bottom', fill='x')

        # main content frame
        self.mainContentFrame = ctk.CTkFrame(self, fg_color='transparent')
        self.mainContentFrame.pack(fill='both', expand=True)

        # setup fonts, SFX
        self.initFonts()
        self.initSFX()

        # create default starting inventory
        self.inventory = Inventory()

        # create widgets
        self.initWidgets()

        # run
        self.mainloop()

    def changeTitleBarColor(self):
        """ Changes app's title bar color to match rest of window. """
        try:  # windows only
            HWND = windll.user32.GetParent(self.winfo_id())  # get current window
            DWMA_ATTRIBUTE = 35  # target color attribute of window's title bar
            TITLE_BAR_COLOR = TITLE_BAR_HEX_COLORS['black']
            windll.dwmapi.DwmSetWindowAttribute(HWND, DWMA_ATTRIBUTE, byref(
                c_int(TITLE_BAR_COLOR)), sizeof(c_int))  # set attribute
        except:
            pass

    def createPopupMessage(self, type: PopupType, offsetX: int, offsetY: int, message: str):
        """ Attempts to create a pop up message; will not create duplicates. Takes app focus. """

        newPopupMessage = None

        match type:
            case PopupType.PT_ERROR:
                self.errorSound.play()
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
        """ Loads .ttf files and creates CTKFonts for widget use. """

        # import fonts
        ctk.FontManager.load_font(resource_path('fonts/DooM.ttf'))
        ctk.FontManager.load_font(resource_path('fonts/EternalUiRegular-1Gap2.ttf'))
        ctk.FontManager.load_font(resource_path('fonts/EternalUiBold-jErYR.ttf'))
        ctk.FontManager.load_font(resource_path('fonts/EternalLogo-51X9B.ttf'))

        # setup widget fonts
        self.tabFont = ctk.CTkFont('Eternal UI Bold', FONT_SIZES['CategoryTabs'])
        self.headerFont = ctk.CTkFont('Eternal UI Bold', FONT_SIZES['Headers'])
        self.subheaderFont = ctk.CTkFont('Eternal UI Bold', FONT_SIZES['Subheaders'])
        self.pathFont = ctk.CTkFont('Eternal UI Regular', FONT_SIZES['Subheaders'])
        self.checkboxFont = ctk.CTkFont('Eternal UI Regular', FONT_SIZES['Checkboxes'])
        self.switchFont = ctk.CTkFont('Eternal UI Regular', FONT_SIZES['Switches'])
        self.runeSubOptionFont = ctk.CTkFont(
            'Eternal UI Regular', FONT_SIZES['RuneSubOption'])

    def initSFX(self):
        """ Initializes pygame sound mixer, loads all app Sounds, and sets their volume. """

        pygame.mixer.init()

        self.tabChangeSound = pygame.mixer.Sound(resource_path(r'sounds/sgreload.wav'))
        self.toggleSound = pygame.mixer.Sound(resource_path(r'sounds/dsitemup.wav'))
        self.errorSound = pygame.mixer.Sound(resource_path(r'sounds/dsoof.wav'))
        self.confirmationSound = pygame.mixer.Sound(
            resource_path(r'sounds/dsgetpow.wav'))

        allSFX = [self.tabChangeSound, self.toggleSound,
                  self.errorSound, self.confirmationSound]

        for sound in allSFX:
            sound.set_volume(0.25)

    def _createScrollableTab(self, tabName):
        """ Creates a scrollable frame inside a tab, with auto-hiding scrollbar. """
        tab = self.tabMenu.tab(tabName)
        scrollable = ctk.CTkScrollableFrame(
            tab,
            fg_color='transparent',
            corner_radius=0,
            scrollbar_button_color=DARK_GRAY,
            scrollbar_button_hover_color=LIGHT_GRAY)
        scrollable.pack(fill='both', expand=True)

        # auto-hide scrollbar when content fits
        canvas = scrollable._parent_canvas
        scrollbar = scrollable._scrollbar
        def on_scroll(first, last):
            if float(first) <= 0.0 and float(last) >= 1.0:
                scrollbar.grid_forget()
            else:
                scrollbar.grid(row=0, column=1, sticky='ns')
                scrollbar.set(first, last)
        canvas.configure(yscrollcommand=on_scroll)

        return scrollable

    def initWidgets(self):
        """ Creates top-level app widgets and calls widget init functions for each inventory module. """

        # setup category tabs for inventory module grouping
        self.tabMenu = ctk.CTkTabview(
            master=self.mainContentFrame,
            width=WINDOW_SIZE[0] - 40,
            height=WINDOW_SIZE[1] - 20,
            fg_color=DARKEST_GRAY,
            segmented_button_fg_color=DARKEST_GRAY,
            segmented_button_selected_color=RED,
            segmented_button_selected_hover_color=RED_HIGHLIGHT,
            border_width=2,
            border_color=WHITE,
            command=self.tabChangeSound.play)

        self.tabMenu._segmented_button.configure(
            font=self.tabFont, border_width=1, bg_color=WHITE)
        self.tabMenu.pack_propagate(True)
        self.tabMenu.pack()
        self.tabMenu.add('Praetor Suit')
        self.tabMenu.add('Equipment & Weapons')
        self.tabMenu.add('Weapon Mods')
        self.tabMenu.add('Runes')
        self.tabMenu.set('Praetor Suit')

        # wrap each tab's content in a scrollable frame for smaller displays
        self.praetorSuitContent = self._createScrollableTab('Praetor Suit')
        self.equipWeaponsContent = self._createScrollableTab('Equipment & Weapons')
        self.weaponModsContent = self._createScrollableTab('Weapon Mods')
        self.runesContent = self._createScrollableTab('Runes')

        # path status info
        cDefaultPath = r'C:\Program Files (x86)\Steam\steamapps\common\DOOM'
        if os.path.exists(cDefaultPath):
            self.doomInstallationPath = cDefaultPath
        else:
            drivesToCheck = ["D", "E", "F", "G"]
            otherDefaultPath = None
            for drive in drivesToCheck:
                if os.path.exists(f"{drive}:\\SteamLibrary\\steamapps\\common\\DOOM"):
                    otherDefaultPath = f"{drive}:\\SteamLibrary\\steamapps\\common\\DOOM"
                    break
            if otherDefaultPath:
                self.doomInstallationPath = otherDefaultPath
            else:  # if no doom installation found, default to current working directory
                self.doomInstallationPath = os.getcwd()

        outputPathStr = 'NOT FOUND'
        if self.doomInstallationPath:
            outputPathStr = f'{self.doomInstallationPath}' + r'/Mods'
            outputPathStr = outputPathStr.replace('\\', '/')

        self.outputPathLabel = ctk.CTkLabel(
            self.statusFrame,
            text=f'Install Path: {outputPathStr}',
            font=self.pathFont)
        self.outputPathLabel.pack()

        # input to modify output path
        self.modifyPathButton = ctk.CTkButton(
            self.bottomFrame,
            height=14,
            width=60,
            text='modify path',
            font=self.pathFont,
            fg_color=DARK_GRAY,
            hover_color=LIGHT_GRAY,
            border_spacing=0,
            command=self.promptUserForPath)
        self.modifyPathButton.pack(pady=(0, 2), anchor='center')

        # input to generate final output file from current app selections
        self.generateModButton = ctk.CTkButton(
            self.bottomFrame,
            font=self.subheaderFont,
            fg_color=RED,
            hover_color=RED_HIGHLIGHT,
            text_color=WHITE,
            text='Generate Mod',
            command=self.generateMod,
            height=32)
        self.generateModButton.pack(padx=0, pady=5, anchor='center')

        # inventory module widgets
        self.initArgentWidgets()
        self.initPraetorWidgets()
        self.initEquipmentWidgets()
        self.initWeaponWidgets()
        self.initWeaponModWidgets()
        self.initRuneWidgets()

    def initArgentWidgets(self):
        """ Creates widgets for the ArgentCellUpgrades inventory module. """

        parent = self.praetorSuitContent

        self.argentCellHeaderLabel = ctk.CTkLabel(
            parent, font=self.headerFont, text='Argent Cell Routing')
        self.argentCellHeaderLabel.grid(
            column=0, row=0, padx=20, pady=(35, 15), columnspan=2, sticky='w')

        self.toggleAllArgentSwitch = ctk.CTkSwitch(
            master=parent,
            text='All Upgrades',
            command=self.toggleAllArgentUpgrades,
            font=self.switchFont,
            progress_color=RED,
            switch_height=16,
            switch_width=34)
        self.toggleAllArgentSwitch.grid(
            column=0, row=1, sticky='w', padx=(50, 0), pady=(10, 15))

        self.argentDropdownsFrame = ctk.CTkFrame(parent, fg_color=DARKEST_GRAY)
        self.argentDropdownsFrame.grid(column=0, row=2, padx=(
            100, 70), pady=(10, 0), columnspan=6, sticky='n')

        columnIndex, rowIndex = 0, 1
        for category in list(ARGENT_DROPDOWN_DATA.keys()):
            categoryLabel = ctk.CTkLabel(
                self.argentDropdownsFrame, font=self.subheaderFont, text=ARGENT_DROPDOWN_DATA[category]['fName'])
            categoryLabel.grid(column=columnIndex, row=rowIndex, padx=0, sticky='e')
            columnIndex += 1

            callbackFunc = partial(self.argentCallback, category)
            categoryDropdown = DropdownMenu(self.argentDropdownsFrame, list(
                ARGENT_DROPDOWN_DATA[category]['Levels'].values()), callbackFunc)
            categoryDropdown.grid(column=columnIndex, row=1, padx=10)
            ARGENT_DROPDOWN_DATA[category]['Dropdown'] = categoryDropdown
            columnIndex += 1

    def argentCallback(self, category: str, selection: str, fromAllSwitch: bool = False):
        """ Attempts to set the passed Argent category's value to the passed selection. """

        def showUpgradeLimitPopupMsg():
            """ Helper function; creates warning popup message. """

            self.createPopupMessage(
                PopupType.PT_ERROR, -60, -
                200, 'At least one category (health, armor, ammo) of Argent Cell upgrades'
                + ' must not be fully maxed so that you can still pick up the mandatory'
                + ' first upgrade given at the end of Resource Ops.')

        def checkIfMaxed():
            """ Returns a bool indicating whether 2/3 categories are at 4/4 capacity, with the remaining category at 3/4 capacity. """

            allDropdowns = [ARGENT_DROPDOWN_DATA[category]['Dropdown']
                            for category in list(ARGENT_DROPDOWN_DATA.keys())]
            maxedCategoryTally, almostMaxedCategoryTally = 0, 0
            for dropdown in allDropdowns:
                dropdownValues = dropdown.cget('values')
                valueIndex = dropdownValues.index(dropdown.get())
                if valueIndex == 4:
                    maxedCategoryTally += 1
                if valueIndex == 3:
                    almostMaxedCategoryTally += 1

            if maxedCategoryTally == 2 and almostMaxedCategoryTally == 1:
                return True
            return False

        def trySetArgentLevel() -> int:
            """ Helper function; attempts to set level and handles app-level response. """

            selectionKey: int = list(lookup)[list(lookup.values()).index(selection)]
            validatedSelectionKey: int = self.inventory.argentCellUpgrades.setArgentLevel(
                category, selectionKey)
            if validatedSelectionKey != selectionKey:
                showUpgradeLimitPopupMsg()
            else:
                if not fromAllSwitch:
                    self.toggleSound.play()
            return validatedSelectionKey

        lookup = ARGENT_DROPDOWN_DATA[category]['Levels']
        validatedSelectionKey: int = trySetArgentLevel()
        ARGENT_DROPDOWN_DATA[category]['Dropdown'].set(lookup[validatedSelectionKey])

        # if this callback 'maxed' all levels, update toggle all switch's UI to reflect that (without calling its command)
        if checkIfMaxed():
            self.toggleAllArgentSwitch.select()
        else:
            self.toggleAllArgentSwitch.deselect()

    def toggleAllArgentUpgrades(self):
        """ Adds/removes every (possible) upgrade, and sets dropdowns accordingly.  """

        allArgentCategories = list(ARGENT_DROPDOWN_DATA.keys())
        allArgentLevels = [ARGENT_DROPDOWN_DATA[category]['Levels']
                           for category in allArgentCategories]

        allSwitchOn = self.toggleAllArgentSwitch.get()

        if allSwitchOn:
            for index, category in enumerate(allArgentCategories):
                self.argentCallback(category, allArgentLevels[index][4], True)
        else:
            self.toggleSound.play()
            for index, category in enumerate(allArgentCategories):
                self.argentCallback(category, allArgentLevels[index][0], True)

    def initPraetorWidgets(self):
        """ Creates widgets for the PraetorSuitUpgrades inventory module. """

        parent = self.praetorSuitContent
        parent.columnconfigure(0, weight=1)

        self.praetorCheckboxWidgets = []

        self.praetorSuitHeaderLabel = ctk.CTkLabel(
            parent, font=self.headerFont, text='Suit Upgrades')
        self.praetorSuitHeaderLabel.grid(
            column=0, row=2, padx=20, pady=(90, 10), columnspan=2, sticky='w')

        self.toggleAllPraetorSwitch = ctk.CTkSwitch(
            master=parent,
            text='All Upgrades',
            command=self.toggleAllPraetorUpgrades,
            font=self.checkboxFont,
            progress_color=RED,
            switch_height=16,
            switch_width=34)
        self.toggleAllPraetorSwitch.grid(
            column=0, row=3, sticky='w', padx=(50, 0), pady=(10, 10))

        self.praetorCheckboxFrame1 = ctk.CTkFrame(
            parent, fg_color='transparent', border_color=WHITE, border_width=0)
        self.praetorCheckboxFrame1.grid(column=0, row=5, pady=(20, 0))
        self.praetorCheckboxFrame2 = ctk.CTkFrame(
            parent, fg_color='transparent', border_color=WHITE, border_width=0)
        self.praetorCheckboxFrame2.grid(column=0, row=6, padx=(0, 30), pady=(20, 0))

        allSuitUpgradeCategories = list(SUIT_PANEL_DATA.keys())

        correctType = self.inventory.praetorSuitUpgrades.elementType
        allPraetorPerks = [
            each for each in self.inventory.praetorSuitUpgrades.all() if type(each) is correctType]

        categoryColumnIndex, categoryRowIndex = 0, 4
        parentFrame = self.praetorCheckboxFrame1

        for category in allSuitUpgradeCategories:
            headersPad_x = SUIT_PANEL_DATA[category]
            categoryLabel = ctk.CTkLabel(
                parentFrame, font=self.subheaderFont, text=category)
            categoryLabel.grid(column=categoryColumnIndex, row=categoryRowIndex,
                               padx=headersPad_x, pady=(0, 10), sticky='w')
            categoryFrame = ctk.CTkFrame(parentFrame, fg_color=DARKEST_GRAY)
            categoryFrame.grid(column=categoryColumnIndex, row=categoryRowIndex +
                               1, padx=headersPad_x, columnspan=3, sticky='w')

            categoryPerks = [
                each for each in allPraetorPerks if each.category == category]

            perkColumnIndex, perkRowIndex = 0, 0
            for perk in categoryPerks:
                callbackFunc = partial(self.praetorCallback, perk.name)
                tooltipText = perk.description
                perkCheckbox = Checkbox(
                    parent=categoryFrame,
                    text=perk.fName,
                    column=perkColumnIndex,
                    row=perkRowIndex,
                    command=callbackFunc,
                    tooltipMsg=tooltipText,
                    sticky='w',
                    pady=(0, 5))

                self.praetorCheckboxWidgets.append(perkCheckbox)
                perkRowIndex += 1

            categoryColumnIndex += 1
            if categoryColumnIndex > 2:
                categoryColumnIndex = 0
                categoryRowIndex += 2
                parentFrame = self.praetorCheckboxFrame2

    def _toggleItemCallback(self, module, itemName, toggleAllSwitch, totalCount):
        """ Generic toggle callback for simple inventory modules. Adds/removes item and updates toggle switch. """

        self.toggleSound.play()

        found = False
        for item in module.available:
            if item.name == itemName:
                found = True
                module.available.remove(item)
                if toggleAllSwitch.get():
                    toggleAllSwitch.deselect()
                break
        if not found:
            module.addToAvailable(itemName)
            if len(module.available) == totalCount:
                toggleAllSwitch.select()

    def _toggleAllItems(self, module, toggleAllSwitch, checkboxWidgets):
        """ Generic toggleAll for simple inventory modules. Adds/removes all items and updates checkboxes. """

        self.toggleSound.play()
        allSwitchOn = toggleAllSwitch.get()

        if allSwitchOn:
            module.addAllToAvailable()
            for each in checkboxWidgets:
                each.select()
        else:
            module.available.clear()
            for each in checkboxWidgets:
                each.deselect()

    def praetorCallback(self, perkName: str):
        """ Toggles a PraetorPerk's availability.  """
        self._toggleItemCallback(
            self.inventory.praetorSuitUpgrades, perkName,
            self.toggleAllPraetorSwitch, 15)

    def toggleAllPraetorUpgrades(self):
        """ Adds/removes every upgrade, and selects/deselects checkboxes accordingly.  """
        self._toggleAllItems(
            self.inventory.praetorSuitUpgrades,
            self.toggleAllPraetorSwitch,
            self.praetorCheckboxWidgets)

    def initEquipmentWidgets(self):
        """ Creates widgets for the Equipment inventory module. """

        parentTab = self.equipWeaponsContent
        parentTab.columnconfigure(0, weight=1)

        self.equipmentCheckboxWidgets = []

        self.equipmentHeaderLabel = ctk.CTkLabel(
            parentTab, font=self.headerFont, text='Equipment')
        self.equipmentHeaderLabel.grid(
            column=0, row=0, padx=20, pady=(35, 10), columnspan=2, sticky='nw')

        self.toggleAllEquipmentSwitch = ctk.CTkSwitch(
            master=parentTab,
            text='All Equipment',
            command=self.toggleAllEquipment,
            font=self.checkboxFont,
            progress_color=RED,
            switch_height=16,
            switch_width=34)
        self.toggleAllEquipmentSwitch.grid(
            column=0, row=1, sticky='w', padx=(50, 0), pady=(10, 15))

        self.equipmentCheckboxFrame = ctk.CTkFrame(
            parentTab, fg_color='transparent', border_color=WHITE, border_width=0)
        self.equipmentCheckboxFrame.grid(column=0, row=2, padx=(0, 15))

        allEquipment = [each for each in self.inventory.equipment.all() if type(
            each) == self.inventory.equipment.elementType]

        columnIndex, rowIndex = 0, 0
        padx = (0, 35)
        for each in allEquipment:
            callbackFunc = partial(self.equipmentCallback, each.name)
            tooltipText = each.description
            equipmentCheckbox = Checkbox(
                parent=self.equipmentCheckboxFrame,
                text=each.fName,
                column=columnIndex,
                row=rowIndex,
                command=callbackFunc,
                tooltipMsg=tooltipText,
                sticky='w',
                padx=padx,
                pady=(0, 10))

            self.equipmentCheckboxWidgets.append(equipmentCheckbox)
            rowIndex += 1
            if rowIndex > 1:
                rowIndex = 0
                columnIndex += 1
                padx = (0, 0)

    def equipmentCallback(self, equipmentItemName: str):
        """ Toggles an EquipmentItem's availability.  """
        self._toggleItemCallback(
            self.inventory.equipment, equipmentItemName,
            self.toggleAllEquipmentSwitch, 4)

    def toggleAllEquipment(self):
        """ Adds/removes all equipment, and selects/deselects checkboxes accordingly.  """
        self._toggleAllItems(
            self.inventory.equipment,
            self.toggleAllEquipmentSwitch,
            self.equipmentCheckboxWidgets)

    def initWeaponWidgets(self):
        """ Creates widgets for the Weapons inventory module. """

        parentTab = self.equipWeaponsContent

        self.weaponsCheckboxWidgets = []

        self.weaponsHeaderLabel = ctk.CTkLabel(
            parentTab, font=self.headerFont, text='Weapons')
        self.weaponsHeaderLabel.grid(
            column=0, row=3, padx=20, pady=(20, 10), columnspan=2, sticky='nw')

        self.toggleAllWeaponsSwitch = ctk.CTkSwitch(
            master=parentTab,
            text='All Weapons',
            command=self.toggleAllWeapons,
            font=self.checkboxFont,
            progress_color=RED,
            switch_height=16,
            switch_width=34)
        self.toggleAllWeaponsSwitch.grid(
            column=0, row=4, sticky='w', padx=(50, 0), pady=(10, 15))

        self.weaponsCheckboxFrame1 = ctk.CTkFrame(
            parentTab, fg_color='transparent', border_color=WHITE, border_width=0)
        self.weaponsCheckboxFrame1.grid(column=0, row=5, padx=(50, 0))

        allWeaponMembers = self.inventory.weapons.all()
        correctType = self.inventory.weapons.elementType
        ignoredWeaponNames = ['fists', 'pistol']
        allWeapons = [each for each in allWeaponMembers if type(
            each) is correctType and each.name not in ignoredWeaponNames]

        columnIndex, rowIndex = 0, 0
        padx = (0, 35)
        for each in allWeapons:
            callbackFunc = partial(self.weaponsCallback, each.name)
            tooltipText = each.description
            weaponCheckbox = Checkbox(
                parent=self.weaponsCheckboxFrame1,
                text=each.fName,
                column=columnIndex,
                row=rowIndex,
                command=callbackFunc,
                tooltipMsg=tooltipText,
                sticky='w',
                padx=padx,
                pady=(0, 10))

            self.weaponsCheckboxWidgets.append(weaponCheckbox)
            if columnIndex > 1:
                padx = (0, 0)
            if rowIndex < 2:
                rowIndex += 1
            else:
                rowIndex = 0
                columnIndex += 1

        chainsawSize_x = 800
        chainsawSize_y = 255
        self.chainsawImage = ctk.CTkImage(light_image=Image.open(resource_path(r'images\chainsaw.png')),
                                          dark_image=Image.open(
                                              resource_path(r'images\chainsaw.png')),
                                          size=(int(chainsawSize_x * .75), int(chainsawSize_y * .75)))

        self.chainsawImageLabel = ctk.CTkLabel(
            parentTab, image=self.chainsawImage, text='')
        self.chainsawImageLabel.grid(column=0, row=6, padx=(30, 0), pady=(30, 0))

    def weaponsCallback(self, weaponItemName: str):
        """ Toggles a WeaponItem's availability.  """

        def areOtherAvailableWeaponsUsingSameAmmo(ammoType) -> bool:
            """ Returns whether any currently Available weapons are using the passed ammoType. """

            for weapon in self.inventory.weapons.available:
                if self.inventory.weapons.getAmmoTypeForWeapon(weapon.name) == ammoType:
                    return True
            return False

        self.toggleSound.play()
        ammoType = self.inventory.weapons.getAmmoTypeForWeapon(weaponItemName)

        # if not in available, add it; else, remove
        found = False
        for weaponItem in self.inventory.weapons.available:
            if weaponItem.name == weaponItemName:
                found = True
                self.inventory.weapons.available.remove(weaponItem)

                # remove its ammo as well, if no other avail weapons use it
                if not areOtherAvailableWeaponsUsingSameAmmo(ammoType):
                    if ammoType:
                        ammo = getattr(self.inventory.ammo, ammoType)
                        self.inventory.ammo.available.remove(ammo)

                # clear toggleAll switch - all are no longer selected
                if self.toggleAllWeaponsSwitch.get():
                    self.toggleAllWeaponsSwitch.deselect()
                break

        if not found:
            self.inventory.weapons.addToAvailable(weaponItemName)  # add it

            # if all are available, update UI toggle all switch to reflect that
            if len(self.inventory.weapons.available) == 11:
                self.toggleAllWeaponsSwitch.select()

            # add corresponding ammo to available, if not
            if ammoType:
                self.inventory.ammo.addToAvailable(ammoType)

    def toggleAllWeapons(self):
        """ Adds/removes all weapons (and their ammo), and selects/deselects checkboxes accordingly.  """

        self.toggleSound.play()
        allSwitchOn = self.toggleAllWeaponsSwitch.get()

        if allSwitchOn:
            self.inventory.weapons.addAllToAvailable()
            self.inventory.ammo.addAllToAvailable()
            # update UI - all weapon checkboxes
            for each in self.weaponsCheckboxWidgets:
                each.select()
        else:
            self.inventory.weapons.available.clear()
            self.inventory.ammo.available.clear()
            for each in self.weaponsCheckboxWidgets:
                each.deselect()

    def initWeaponModWidgets(self):
        """ Creates widgets for the WeaponMods inventory module."""

        parentTab = self.weaponModsContent
        parentTab.columnconfigure(0, weight=1)

        self.weaponModsAvailableCheckboxWidgets = []
        self.weaponModUpgradesAvailableCheckboxWidgets = []

        self.weaponModsHeaderLabel = ctk.CTkLabel(
            parentTab, font=self.headerFont, text='Weapon Mods')
        self.weaponModsHeaderLabel.grid(
            column=0, row=3, padx=20, pady=(35, 10), columnspan=2, sticky='nw')

        self.weaponModsSwitchFrame = ctk.CTkFrame(parentTab, fg_color='transparent')
        self.weaponModsSwitchFrame.grid(column=0, row=4, pady=(0, 20))

        # setup toggle all switches
        self.toggleAllWeaponModsAvailableSwitch = ctk.CTkSwitch(
            master=self.weaponModsSwitchFrame,
            text='All Weapon Mods Unlocked',
            command=self.toggleAllWeaponModsAvailable,
            font=self.checkboxFont,
            progress_color=RED,
            switch_height=16,
            switch_width=34)
        self.toggleAllWeaponModsAvailableSwitch.grid(
            column=0, row=0, sticky='w', padx=(0, 0), pady=(0, 0))

        self.toggleAllWeaponModsUpgradedSwitch = ctk.CTkSwitch(
            master=self.weaponModsSwitchFrame,
            text='All Weapons / Mods Fully Upgraded',
            command=self.toggleAllWeaponModsUpgraded,
            font=self.checkboxFont,
            progress_color=RED,
            switch_height=16,
            switch_width=34)
        self.toggleAllWeaponModsUpgradedSwitch.grid(
            column=1, row=0, sticky='w', padx=(20, 0), pady=(0, 0))

        # setup tabs for grouping mods by applicable weapon
        self.weaponModsTabMenu = ctk.CTkTabview(master=parentTab,
                                                width=WINDOW_SIZE[0] - 150,
                                                height=WINDOW_SIZE[1] - 300,
                                                fg_color=DARKEST_GRAY,
                                                segmented_button_fg_color=DARKEST_GRAY,
                                                segmented_button_selected_color=RED,
                                                segmented_button_selected_hover_color=RED_HIGHLIGHT,
                                                border_width=2,
                                                border_color=WHITE)

        self.weaponModsTabMenu._segmented_button.configure(
            font=self.checkboxFont, border_width=1, bg_color=WHITE)
        self.weaponModsTabMenu.grid(column=0, row=5, padx=(0, 0), pady=(0, 0), rowspan=1)

        allWeaponsWithUpgrades = list(WEAPON_MOD_PANEL_DATA.keys())

        # build tab menu + each weapon's tab containing its mod/upgrade UI
        for each in allWeaponsWithUpgrades:
            self.weaponModsTabMenu.add(WEAPON_MOD_PANEL_DATA[each]['fName'])
            if WEAPON_MOD_PANEL_DATA[each]['hasMods']:
                WeaponTab(self, each)
            else:
                pass
        # special cases (no mods)
        WeaponTabNoMods(self, 'pistol')
        WeaponTabNoMods(self, 'superShotgun')

    def weaponModCallback(self, weaponModPerkName: str):
        """ Toggles a WeaponModPerk's availability.  """

        def checkIfAllBaseModsAvailable():
            """ Returns whether the user has made all weapon base mods (not upgrades) available. """

            availableTally = 0
            for each in self.inventory.weaponMods.available:
                if type(each) is WeaponModPerk and each.applicableMod == 'isBaseMod':
                    availableTally += 1
            return True if availableTally == 12 else False

        weaponModPerk = self.inventory.weaponMods.getWeaponModPerkFromName(weaponModPerkName)
        if weaponModPerk is None:
            return

        # proceed with toggling mod availability
        self.toggleSound.play()
        # if in available, remove it; else, add
        if weaponModPerk in self.inventory.weaponMods.available:
            self.inventory.weaponMods.available.remove(weaponModPerk)
            # update UI - if this was a base mod, update toggle all switch to reflect new status
            if not checkIfAllBaseModsAvailable():
                if self.toggleAllWeaponModsAvailableSwitch.get():
                    self.toggleAllWeaponModsAvailableSwitch.deselect()
            # update UI - if ANY mod was removed from available, this can't be true, so deselect switch
            if self.toggleAllWeaponModsUpgradedSwitch.get():
                self.toggleAllWeaponModsUpgradedSwitch.deselect()
        else:
            self.inventory.weaponMods.addToAvailable(
                weaponModPerk.applicableWeapon, weaponModPerkName)
            if len(self.inventory.weaponMods.available) >= 12:
                if checkIfAllBaseModsAvailable():
                    self.toggleAllWeaponModsAvailableSwitch.select()
            if len(self.inventory.weaponMods.available) == 61:
                self.toggleAllWeaponModsUpgradedSwitch.select()

    def toggleAllWeaponModsAvailable(self):
        """ Adds/removes all base WeaponModPerks, and selects/deselects checkboxes accordingly.  """

        self.toggleSound.play()
        allSwitchOn = self.toggleAllWeaponModsAvailableSwitch.get()

        if allSwitchOn:
            self.inventory.weaponMods.toggleAllBaseModsAvailable(True)
            # update UI - all base weapon mod checkboxes
            for each in self.weaponModsAvailableCheckboxWidgets:
                each.select()
        else:
            # clear available status for all base mods + update UI
            self.inventory.weaponMods.toggleAllBaseModsAvailable(False)
            for each in self.weaponModsAvailableCheckboxWidgets:
                each.deselect()

    def toggleAllWeaponModsUpgraded(self):
        """ Adds/removes all upgrade WeaponModPerks, and selects/deselects checkboxes accordingly.  """

        self.toggleSound.play()
        allSwitchOn = self.toggleAllWeaponModsUpgradedSwitch.get()

        if allSwitchOn:
            self.inventory.weaponMods.toggleAllModUpgradesAvailable(True)
            # update UI - all upgrade weapon mod checkboxes
            for each in self.weaponModUpgradesAvailableCheckboxWidgets:
                each.select()
        else:
            # clear available status for all mod upgrades + update UI
            self.inventory.weaponMods.toggleAllModUpgradesAvailable(False)
            for each in self.weaponModUpgradesAvailableCheckboxWidgets:
                each.deselect()

    def initRuneWidgets(self) -> None:
        """ Creates widgets for the Runes inventory module. """

        parentTab = self.runesContent
        parentTab.columnconfigure(0, weight=1)

        self.runesAvailableCheckboxWidgets = []
        self.runesUpgradedCheckboxWidgets = []
        self.runesPermEquipCheckboxWidgets = []

        self.runesHeaderLabel = ctk.CTkLabel(
            parentTab, font=self.headerFont, text='Runes')
        self.runesHeaderLabel.grid(column=0, row=3, padx=20,
                                   pady=(35, 10), columnspan=2, sticky='nw')

        self.runesSwitchFrame = ctk.CTkFrame(parentTab, fg_color='transparent')
        self.runesSwitchFrame.grid(column=0, row=4, pady=(0, 20))

        # setup toggle all switches
        self.toggleAllRunesAvailableSwitch = ctk.CTkSwitch(
            master=self.runesSwitchFrame,
            text='All Runes Unlocked',
            command=self.toggleAllRunesAvailable,
            font=self.checkboxFont,
            progress_color=RED,
            switch_height=16,
            switch_width=34)
        self.toggleAllRunesAvailableSwitch.grid(
            column=0, row=0, sticky='w', padx=(0, 0), pady=(0, 0))

        self.toggleAllRunesUpgradedSwitch = ctk.CTkSwitch(
            master=self.runesSwitchFrame,
            text='All Runes Upgraded',
            command=self.toggleAllRunesUpgraded,
            font=self.checkboxFont,
            progress_color=RED,
            switch_height=16,
            switch_width=34,
            state='disabled')
        self.toggleAllRunesUpgradedSwitch.grid(
            column=1, row=0, sticky='w', padx=(20, 0), pady=(0, 0))

        self.toggleAllRunesPermEquipSwitch = ctk.CTkSwitch(
            master=self.runesSwitchFrame,
            text='All Runes Permanently Equipped',
            command=self.toggleAllRunesPermEquip,
            font=self.checkboxFont,
            progress_color=RED,
            switch_height=16,
            switch_width=34,
            state='disabled')
        self.toggleAllRunesPermEquipSwitch.grid(
            column=2, row=0, sticky='w', padx=(20, 0), pady=(0, 0))

        # setup rune checkbox display: 4 frames, 1 per row
        allRuneFrames = []
        rowIndex = 5
        for _ in range(4):
            runeFrame = ctk.CTkFrame(parentTab, fg_color='transparent')
            runeFrame.grid(column=0, row=rowIndex, pady=(10, 10))
            allRuneFrames.append(runeFrame)
            rowIndex += 1

        # 12 runes total
        allRunes = list(RUNE_PANEL_DATA.keys())

        # create each rune's panel, with 3 per each of the 4 runeFrames
        columnIndex, rowIndex = 0, 0
        frameIndex = 0
        for rune in allRunes:
            panelPadX = (0, 0) if columnIndex == 0 else (30, 0)

            runePanel = RunePanel(
                parentApp=self,
                parentFrame=allRuneFrames[frameIndex],
                parentFrameColumn=columnIndex,
                parentFrameRow=rowIndex,
                runePerkName=rune,
                panelPadX=panelPadX)

            columnIndex += 1
            if columnIndex > 2:
                columnIndex = 0
                frameIndex += 1

    def runeAvailableCallback(self, runePerkName: str):
        """ Toggles a RunePerk's availability.  """

        self.toggleSound.play()
        runePanel = RUNE_PANEL_DATA[runePerkName]['panel']

        if runePanel:
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
                    runePanel.runeUpgradedCheckbox.configure(state='disabled')
                    runePanel.runePermEquipCheckbox.configure(state='disabled')
                    break

            if not found:
                self.inventory.runes.addToAvailable(runePerkName)
                runePanel.runeUpgradedCheckbox.configure(state='normal')
                runePanel.runePermEquipCheckbox.configure(state='normal')
                # if all are available, update UI toggle all switch to reflect that
                if len(self.inventory.runes.available) == 12:
                    self.toggleAllRunesAvailableSwitch.select()

    def runeUpgradedCallback(self, runePerkName: str):
        """ Toggles a RunePerk's Upgraded status. """

        self.toggleSound.play()
        rune = self.inventory.runes.getRunePerkFromName(runePerkName)
        if rune:
            if rune.applyUpgradesForPerk:
                rune.applyUpgradesForPerk = False
                if rune in self.inventory.runes.upgradedRunes:
                    self.inventory.runes.upgradedRunes.remove(rune)
                # clear toggleAll switch - all are no longer selected
                if self.toggleAllRunesUpgradedSwitch.get():
                    self.toggleAllRunesUpgradedSwitch.deselect()
            else:
                rune.applyUpgradesForPerk = True
                if rune not in self.inventory.runes.upgradedRunes:
                    self.inventory.runes.upgradedRunes.append(rune)
                # if all are upgraded, update UI toggle all switch to reflect that
                if len(self.inventory.runes.upgradedRunes) == 12:
                    self.toggleAllRunesUpgradedSwitch.select()

    def runePermEquipCallback(self, runePerkName: str):
        """ Toggles a RunePerk's Permanently Equipped status. """

        self.toggleSound.play()
        rune = self.inventory.runes.getRunePerkFromName(runePerkName)
        if rune:
            if rune.runePermanentEquip:
                rune.runePermanentEquip = False
                if rune in self.inventory.runes.permEquipRunes:
                    self.inventory.runes.permEquipRunes.remove(rune)
                # clear toggleAll switch - all are no longer selected
                if self.toggleAllRunesPermEquipSwitch.get():
                    self.toggleAllRunesPermEquipSwitch.deselect()
            else:
                rune.runePermanentEquip = True
                if rune not in self.inventory.runes.permEquipRunes:
                    self.inventory.runes.permEquipRunes.append(rune)
                # if all are perm equipped, update UI toggle all switch to reflect that
                if len(self.inventory.runes.permEquipRunes) == 12:
                    self.toggleAllRunesPermEquipSwitch.select()

    def toggleAllRunesAvailable(self):
        """ Adds/removes all RunePerks, and selects/deselects checkboxes + enables/disables sub-options accordingly.  """

        self.toggleSound.play()
        allSwitchOn = self.toggleAllRunesAvailableSwitch.get()

        if allSwitchOn:
            self.inventory.runes.addAllToAvailable()
            # update UI - all rune checkboxes
            for each in self.runesAvailableCheckboxWidgets:
                each.select()
            for each in self.runesUpgradedCheckboxWidgets:
                each.configure(state='normal')
            for each in self.runesPermEquipCheckboxWidgets:
                each.configure(state='normal')
            # update UI - other 'toggle all' rune switches
            self.toggleAllRunesUpgradedSwitch.configure(state='normal')
            self.toggleAllRunesPermEquipSwitch.configure(state='normal')

        else:
            # clear available status for all runes + update UI
            self.inventory.runes.available.clear()
            for each in self.runesAvailableCheckboxWidgets:
                each.deselect()
            # clear upgraded status for all runes + update UI
            self.inventory.runes.setAllAreUpgraded(False)
            for each in self.runesUpgradedCheckboxWidgets:
                each.deselect()
                each.configure(state='disabled')
            # clear perm equip status for all runes + update UI
            self.inventory.runes.setAllArePermEquip(False)
            for each in self.runesPermEquipCheckboxWidgets:
                each.deselect()
                each.configure(state='disabled')
            # update UI for sub-option toggle all switches
            self.toggleAllRunesUpgradedSwitch.deselect()
            self.toggleAllRunesUpgradedSwitch.configure(state='disabled')
            self.toggleAllRunesPermEquipSwitch.deselect()
            self.toggleAllRunesPermEquipSwitch.configure(state='disabled')

    def toggleAllRunesUpgraded(self):
        """ Toggles applyUpgradesForPerk flag for all RunePerks, and selects/deselects checkboxes + enables/disables sub-options accordingly. """

        self.toggleSound.play()
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

        self.toggleSound.play()
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

    def makeLevelInheritanceDecls(self, path):
        """ Creates decl files for each game level, with inventory inheriting from the previous level. """

        for key, value in LEVEL_INHERITANCE_MAP.items():
            fileName = f'{path}/{key}.decl;devInvLoadout'
            with open(fileName, 'w+') as file:
                file.write('{\n' + indent)
                file.write('inherit = ' + f'"devinvloadout/sp/{value}";')
                file.write('\n' + indent + 'edit = {')
                file.write('\n' + indent + '}')
                file.write('\n}')

    def verifyModContents(self):
        """ Any final validation checks of current values prior to mod generation. """

        # adjusting ammo capacity argent level won't take effect unless at least one weapon with ammo in inventory
        # since combat shotgun is received 30 sec into game, giving it slightly early to make this work
        if self.inventory.argentCellUpgrades.ammoCapacity.count > 0:
            # note: will not be added if user already added manually
            self.inventory.weapons.addToAvailable('combatShotgun')
            self.inventory.ammo.addToAvailable('shells')

    def promptUserForPath(self):
        """ Opens a dialog asking user to select a directory. Sets internal values accordingly. """

        selectedDirStr = filedialog.askdirectory(initialdir='/')

        # if 'cancel' wasn't selected
        if len(selectedDirStr) > 0:
            self.outputPathLabel.configure(text=selectedDirStr + r'/Mods')
            self.doomInstallationPath = selectedDirStr

        if self.popupMsgWindow:
            self.popupMsgWindow.destroy()

    def generateMod(self):
        """ Top-level function for generating final, usable mod output file from current app data values. """

        # perform final validation
        self.verifyModContents()

        # check for valid path; prompt user if needed
        if self.doomInstallationPath is None:
            # c:\ DOOM installation wasn't found during app init; need path
            self.errorSound.play()
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

        # play confirmation sound + show message
        self.confirmationSound.play()
        outputPathStr = topLevelPath.replace('\\', '/')
        confirmMessage: str = f'Mod generated and placed in:\n{str(outputPathStr)}'
        self.createPopupMessage(PopupType.PT_INFO, -60, 0, confirmMessage)


if __name__ == '__main__':
    App()

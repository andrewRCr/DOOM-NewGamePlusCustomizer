"""
panels.py:
- tab/panel composition classes for weapon mods and runes
- these build UI within the weapon mods and runes tab sections
"""

from CTkToolTip import CTkToolTip
import customtkinter as ctk
from functools import partial
from PIL import Image

from common import (
    WHITE, RED, RED_HIGHLIGHT, WINDOW_SIZE,
    WEAPON_MOD_PANEL_DATA, RUNE_PANEL_DATA, resource_path
)
from widgets import Checkbox


class WeaponTab():
    """ Category tab panel contents for each Weapon that has mods to display/edit. """

    def __init__(self, parentApp, weaponName: str):

        fName = WEAPON_MOD_PANEL_DATA[weaponName]['fName']

        parentWeaponTab = parentApp.weaponModsTabMenu.tab(fName)
        parentWeaponTab.columnconfigure(0, weight=1)

        self.weaponPanelFrame = ctk.CTkFrame(
            parentWeaponTab, fg_color='transparent', border_color=WHITE, border_width=0)
        self.weaponPanelFrame.grid(column=0, row=0, pady=(60, 30))

        allModsForWeapon = parentApp.inventory.weaponMods.getAllModsForWeapon(weaponName)

        columnIndex = 0
        for each in allModsForWeapon:
            if each.applicableMod == 'isBaseMod':
                WeaponModPanel(
                    parentApp=parentApp,
                    parentFrame=self.weaponPanelFrame,
                    parentFrameColumn=columnIndex,
                    parentFrameRow=0,
                    weaponModName=each.name,
                    panelPadX=(0, 80))
                columnIndex += 1

            imageSize_x = WEAPON_MOD_PANEL_DATA[weaponName]['imageSize'][0]
            imageSize_y = WEAPON_MOD_PANEL_DATA[weaponName]['imageSize'][1]

            self.weaponImage = ctk.CTkImage(light_image=Image.open(resource_path(WEAPON_MOD_PANEL_DATA[weaponName]['imagePath'])),
                                            dark_image=Image.open(resource_path(
                                                WEAPON_MOD_PANEL_DATA[weaponName]['imagePath'])),
                                            size=(int(imageSize_x * .75), int(imageSize_y * .75)))

            self.weaponImageLabel = ctk.CTkLabel(
                parentWeaponTab, image=self.weaponImage, text='')
            self.weaponImageLabel.grid(column=0, row=1, pady=(30, 0))


class WeaponTabNoMods():
    """ Category tab panel contents for each Weapon that has only non-mod upgrades to display/edit."""

    def __init__(self, parentApp, weaponName: str):

        fName = WEAPON_MOD_PANEL_DATA[weaponName]['fName']

        parentWeaponTab = parentApp.weaponModsTabMenu.tab(fName)
        parentWeaponTab.columnconfigure(0, weight=1)

        self.weaponPanelFrame = ctk.CTkFrame(
            parentWeaponTab, fg_color='transparent', border_color=WHITE, border_width=0)
        self.weaponPanelFrame.grid(column=0, row=0, pady=(60, 0))

        self.upgradesHeaderLabel = ctk.CTkLabel(
            self.weaponPanelFrame, text='Upgrades', font=parentApp.headerFont)
        self.upgradesHeaderLabel.grid(
            column=0, row=0, padx=(0, 0), pady=(0, 10), sticky='w')

        self.weaponUpgradesFrame = ctk.CTkFrame(
            self.weaponPanelFrame, fg_color='transparent', border_color=WHITE, border_width=0)
        self.weaponUpgradesFrame.grid(column=0, row=1, padx=(0, 0), sticky='w')

        allUpgrades = parentApp.inventory.weaponMods.getAllModsForWeapon(weaponName)

        rowIndex = 0
        for upgrade in allUpgrades:
            callbackFunc = partial(parentApp.weaponModCallback, upgrade.name)
            upgradeToolTipText = upgrade.description
            self.weaponModUpgradeCheckbox = Checkbox(
                parent=self.weaponUpgradesFrame,
                text=upgrade.fName,
                font=parentApp.checkboxFont,
                column=1,
                row=rowIndex,
                command=callbackFunc,
                tooltipMsg=upgradeToolTipText,
                sticky='w',
                pady=(0, 0),
                checkboxHeight=20,
                checkboxWidth=20)
            parentApp.weaponModUpgradesAvailableCheckboxWidgets.append(
                self.weaponModUpgradeCheckbox)
            rowIndex += 1

        imageSize_x = WEAPON_MOD_PANEL_DATA[weaponName]['imageSize'][0]
        imageSize_y = WEAPON_MOD_PANEL_DATA[weaponName]['imageSize'][1]

        self.weaponImage = ctk.CTkImage(
            light_image=Image.open(resource_path(
                WEAPON_MOD_PANEL_DATA[weaponName]['imagePath'])),
            dark_image=Image.open(resource_path(
                WEAPON_MOD_PANEL_DATA[weaponName]['imagePath'])),
            size=(int(imageSize_x * .75), int(imageSize_y * .75)))

        self.weaponImageLabel = ctk.CTkLabel(
            parentWeaponTab, image=self.weaponImage, text='')
        self.weaponImageLabel.grid(column=0, row=1, pady=(0, 0))


class WeaponModPanel():
    """ Panel for individual weapon mods and their upgrades, containing checkboxes for each. """

    def __init__(self, parentApp, parentFrame, parentFrameColumn, parentFrameRow, weaponModName: str, panelPadX: tuple = (0, 0), panelPadY: tuple = (0, 0)):

        self.weaponModPerk = parentApp.inventory.weaponMods.getWeaponModPerkFromName(
            weaponModName)
        if self.weaponModPerk is None:
            return

        callbackFunc = partial(parentApp.weaponModCallback, weaponModName)
        self.weaponModHeaderCheckbox = ctk.CTkCheckBox(
            master=parentFrame,
            font=parentApp.headerFont,
            text=self.weaponModPerk.fName,
            command=callbackFunc,
            fg_color=RED,
            hover_color=RED_HIGHLIGHT)
        self.weaponModHeaderCheckbox.grid(
            column=parentFrameColumn, row=parentFrameRow, padx=panelPadX, pady=(0, 10), sticky='w')
        CTkToolTip(self.weaponModHeaderCheckbox, message=self.weaponModPerk.description)
        parentApp.weaponModsAvailableCheckboxWidgets.append(self.weaponModHeaderCheckbox)

        self.weaponModUpgradesFrame = ctk.CTkFrame(
            parentFrame, fg_color='transparent', border_color=WHITE, border_width=0)
        self.weaponModUpgradesFrame.grid(
            column=parentFrameColumn, row=parentFrameRow + 1, padx=panelPadX, sticky='w')

        allModUpgrades = parentApp.inventory.weaponMods.getAllUpgradesForMod(
            weaponModName)

        rowIndex = 0
        for upgrade in allModUpgrades:
            callbackFunc = partial(parentApp.weaponModCallback, upgrade.name)
            upgradeToolTipText = upgrade.description
            self.weaponModUpgradeCheckbox = Checkbox(
                parent=self.weaponModUpgradesFrame,
                text=upgrade.fName,
                font=parentApp.checkboxFont,
                column=1,
                row=rowIndex,
                command=callbackFunc,
                tooltipMsg=upgradeToolTipText,
                sticky='w',
                pady=(0, 0),
                checkboxHeight=20,
                checkboxWidth=20)
            parentApp.weaponModUpgradesAvailableCheckboxWidgets.append(
                self.weaponModUpgradeCheckbox)
            rowIndex += 1


class RunePanel():
    """ Panel for each rune display, containing checkboxes for unlocking, upgrading, and permanently equipping. """

    def __init__(self, parentApp, parentFrame, parentFrameColumn, parentFrameRow, runePerkName: str, panelPadX: tuple = (0, 0), panelPadY: tuple = (0, 0)):

        self.runePerk = parentApp.inventory.runes.getRunePerkFromName(runePerkName)
        if self.runePerk is None:
            return

        # add to static tracking data
        RUNE_PANEL_DATA[runePerkName]['panel'] = self

        # rune: available / header
        runeAvailableCallback = partial(parentApp.runeAvailableCallback, runePerkName)
        self.runeHeaderCheckbox = ctk.CTkCheckBox(
            master=parentFrame,
            font=parentApp.subheaderFont,
            text=RUNE_PANEL_DATA[self.runePerk.name]['fName'],
            command=runeAvailableCallback,
            fg_color=RED,
            hover_color=RED_HIGHLIGHT)
        self.runeHeaderCheckbox.grid(
            column=parentFrameColumn, row=parentFrameRow, padx=panelPadX, pady=(0, 10), sticky='w')
        CTkToolTip(self.runeHeaderCheckbox, message=self.runePerk.description)
        parentApp.runesAvailableCheckboxWidgets.append(self.runeHeaderCheckbox)

        self.runeSubOptionFrame = ctk.CTkFrame(
            parentFrame, fg_color='transparent', border_color=WHITE, border_width=0)
        self.runeSubOptionFrame.grid(
            column=parentFrameColumn, row=parentFrameRow + 1, padx=panelPadX, sticky='w')

        runeImage = ctk.CTkImage(
            light_image=Image.open(resource_path(
                RUNE_PANEL_DATA[runePerkName]['imagePath'])),
            dark_image=Image.open(resource_path(
                RUNE_PANEL_DATA[runePerkName]['imagePath'])),
            size=(70, 70))
        runeImageLabel = ctk.CTkLabel(self.runeSubOptionFrame, image=runeImage, text='')
        runeImageLabel.grid(column=0, row=0, padx=(
            0, 0), pady=(0, 0), rowspan=2, sticky='nsew')

        # rune: upgraded
        runeUpgradedCallback = partial(parentApp.runeUpgradedCallback, runePerkName)
        runeUpgradedTooltipText = self.runePerk.upgradeDescription
        self.runeUpgradedCheckbox = Checkbox(
            parent=self.runeSubOptionFrame,
            text='Upgraded',
            font=parentApp.runeSubOptionFont,
            column=1,
            row=0,
            command=runeUpgradedCallback,
            tooltipMsg=runeUpgradedTooltipText,
            sticky='w',
            pady=(0, 0),
            checkboxHeight=20,
            checkboxWidth=20,
            state='disabled')
        parentApp.runesUpgradedCheckboxWidgets.append(self.runeUpgradedCheckbox)

        # rune: permanent equip
        runePermEquipCallback = partial(parentApp.runePermEquipCallback, runePerkName)
        permEquipTooltipMsg = 'Permanently equip rune without it taking up a slot.'
        self.runePermEquipCheckbox = Checkbox(
            parent=self.runeSubOptionFrame,
            text='Permanently Equipped',
            font=parentApp.runeSubOptionFont,
            column=1,
            row=1,
            command=runePermEquipCallback,
            tooltipMsg=permEquipTooltipMsg,
            sticky='w',
            pady=(0, 0),
            checkboxHeight=20,
            checkboxWidth=20,
            state='disabled')
        parentApp.runesPermEquipCheckboxWidgets.append(self.runePermEquipCheckbox)

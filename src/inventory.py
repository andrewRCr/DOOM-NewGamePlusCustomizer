"""
inventory.py: 
- abstract classes representing player inventory data
- overall Inventory consists of InventoryModules
- modules consist of Perks (capacities, suit upgrades, runes) or Items (equipment, weapons)
"""


from enum import Enum

from common import *


class Inventory():
    """ Represents an entire player starting inventory. Has method to generate decl file for modding use. """

    def __init__(self):

        # create each module
        self.argentCellUpgrades = ArgentCellUpgrades()
        self.praetorSuitUpgrades = PraetorSuitUpgrades()
        self.equipment = Equipment()
        self.weapons = Weapons()
        self.runes = Runes()

        self.modules = [self.argentCellUpgrades, self.praetorSuitUpgrades, self.equipment, self.weapons, self.runes]

    def generateDeclFile(self, path = None):
        """ """

        invItemsCount = 0
        for module in self.modules:
            # update module data
            module.createOutputDict()
            # get total inventory item count
            invItemsCount += len(module.outputDict)

        # writing to output file
        fileNameFinal = 'base.decl;devInvLoadout'
        fileNameTemp = 'loadout.txt'

        with open(fileNameTemp, 'w+') as file:
            file.write('{\n' + indent)
            file.write('edit = {\n' + doubleIndent + 'startingInventory = {')
            file.write('\n' + tripleIndent + f'num = {invItemsCount};')

            itemIndex = 0
            for module in self.modules:
                for key, value in module.outputDict.items():
                    # if itemIndex == 4: # index 4 needs to be skipped for some unknown reason
                    #     itemIndex += 1
                    file.write('\n' + tripleIndent + f'item[{itemIndex}] = ' + '{')
                    for key, value in module.outputDict[key].items():
                        file.write(''.join('\n' + quadIndent + f'{key} = {value};'))
                    file.write('\n' + tripleIndent + '}')
                    itemIndex += 1

            file.write('\n' + doubleIndent + '}')
            file.write('\n' + indent + '}')
            file.write('\n}')


class InventoryModule():
    """ Abstract base class representing a grouping of inventory items. """

    def __init__(self):

        self.moduleName = ''

    def updateOutputDict(self):
        """ Virtual method: Fills module's outputDict with required and updated data. """
        pass


class ArgentCellUpgrades(InventoryModule):
    """ Represents permanent stat increases to suit subsystem capacities provided by Argent Cells. """

    def __init__(self):

        self.moduleName = 'ArgentCellUpgrades'

        self.healthCapacity = Perk('healthCapacity', PerkType.PT_ARGENT, '"perk/zion/player/sp/environment_suit/health_capacity"', 0, True)
        self.armorCapacity = Perk('armorCapacity', PerkType.PT_ARGENT, '"perk/zion/player/sp/environment_suit/armor_capacity"', 0, True)
        self.ammoCapacity = Perk('ammoCapacity', PerkType.PT_ARGENT, '"perk/zion/player/sp/environment_suit/ammo_capacity"', 0, True)

        self.modulePerks = [self.healthCapacity, self.armorCapacity, self.ammoCapacity]
        self.outputDict = {}

    def createOutputDict(self):
        """ Fills module's outputDict with required and updated data. """

        self.outputDict['base'] = {'researchGroups' : '"main"', 'equip' : 'true'}

        for each in self.modulePerks:
            each.updatePerkData()
            if each.equip is True:
                self.outputDict[each.name] = each.perkData


class PraetorSuitUpgrades(InventoryModule):
    """ Represent permanent suit upgrades provided by Praetor Tokens. """

    def __init__(self):

        self.moduleName = 'PraetorSuitUpgrades'

        # environmental resistance
        self.environmentalResistance1 = Perk('environmentalResistance1', PerkType.PT_PRAETOR, "perk/zion/player/sp/enviroment_suit/modify_enviromental_damage_1")
        self.environmentalResistance2 = Perk('environmentalResistance2', PerkType.PT_PRAETOR, "perk/zion/player/sp/enviroment_suit/modify_enviromental_damage_2")
        self.environmentalResistance3 = Perk('environmentalResistance3', PerkType.PT_PRAETOR, "perk/zion/player/sp/enviroment_suit/modify_enviromental_damage_3")

        # area-scanning technology
        # equipment system
        # powerup effectiveness
        # dexterity

        self.modulePerks = [self.environmentalResistance1, self.environmentalResistance2, self.environmentalResistance3]
        self.outputDict = {}
        
    def createOutputDict(self):
        """ Fills module's outputDict with required and updated data. """
        
        for each in self.modulePerks:
            each.updatePerkData()
            if each.equip is True:
                self.outputDict[each.name] = each.perkData


class Runes(InventoryModule):
    """ 
    Represent demonic sigils granting unique perks, acquired via Rune Trials.
    By default, only 3 can be equipped at once, but setting the isRune flag to False
    and the equip flag to True makes the rune permanently equipped without taking up a slot.
    """

    def __init__(self):

        self.moduleName = 'Runes'

        # individual runes
        self.vacuum = Perk('vacuumRune', PerkType.PT_RUNE, "perk/zion/player/sp/enviroment_suit/increase_drop_radius", None, False, False, False, False)
        self.dazedAndConfused = Perk('dazedAndConfusedRune', PerkType.PT_RUNE, "perk/zion/player/sp/enviroment_suit/modify_enemy_stagger_duration", None, False, False, False, False)
        
        self.moduleRunes = [self.vacuum, self.dazedAndConfused]
        self.outputDict = {}

    def createOutputDict(self):
        """ Fills module's outputDict with required and updated data. """

        for each in self.moduleRunes:
            each.updatePerkData()
            if each.isRune is True or each.runePermanentEquip is True:
                self.outputDict[each.name] = each.perkData


class Equipment(InventoryModule):
    """ Represents the double-jump boots and throwable items. """

    def __init__(self):

        self.moduleName = 'Equipment'

        self.doubleJumpThrustBoots = Item('doubleJumpThrustBoots', ItemType.IT_SPECIAL, "jumpboots/base", False, False)

        self.moduleEquipment = [self.doubleJumpThrustBoots]
        self.outputDict = {}

    def createOutputDict(self):
        """ Fills module's outputDict with required and updated data. """

        for each in self.moduleEquipment:
            each.updateItemData()
            if each.available is True:
                self.outputDict[each.name] = each.itemData


class Weapons(InventoryModule):
    """ Represents weapons, their mods, and their mod upgrades. """

    def __init__(self):
        
        self.moduleName = 'Weapons'

        self.moduleWeapons = []
        self.outputDict = {}

    def createOutputDict(self):
        """ Fills module's outputDict with required and updated data. """

        for each in self.moduleWeapons:
            each.updateItemData()
            if each.available is True:
                self.outputDict[each.name] = each.itemData


class PerkType(Enum):
    """ Represents a distinct category of the Perk class. """
    PT_ARGENT = 0,
    PT_PRAETOR = 1,
    PT_WEAPON = 2,
    PT_RUNE = 3
    
    default = PT_ARGENT
    
        
class Perk():
    """ 
    Represents a bonus of some kind to be granted to the player. 
    Can be from ArgentCells, PraetorSuit, Weapon mods + their upgrades, or Runes. 
    """
    def __init__(self, name, type, path, count = None, equip = False, applyUpgradesForPerk = None, isRune = None, runePermanentEquip = None):
        """ """

        self.name = name
        self.type = type
        self.path = path
        self.count = count
        self.equip = equip
        self.applyUpgradesForPerk = applyUpgradesForPerk
        self.isRune = isRune
        self.runePermanentEquip = runePermanentEquip

    def updatePerkData(self):
        """ Applies any changes in member variables to perk's data dictionary. """

        match self.type:

            case PerkType.PT_ARGENT:
                if self.name != 'ammoCapacity':
                    self.perkData = {'perk': self.path, 'count': self.count, 'equip': str(self.equip).lower(), 'remove_after_equip': 'true'}
                elif self.name == 'ammoCapacity': # gets additional 'applyAfterLoadout' key
                    self.perkData = {'perk': self.path, 'count': self.count, 'equip': str(self.equip).lower(), 'applyAfterLoadout': 'true', 'remove_after_equip': 'true'}
            
            case PerkType.PT_PRAETOR:
                self.perkData = {'perk': self.path, 'equip': str(self.equip).lower()}

            case PerkType.PT_RUNE:
                # mod option: make rune perk permanent without taking up a rune slot
                if self.runePermanentEquip is True:
                    self.perkData = {'perk': self.path, 'applyUpgradesForPerk': str(self.applyUpgradesForPerk).lower(), 'equip': str(self.runePermanentEquip).lower()}
                # regular rune granting to inventory 
                else:
                    self.perkData = {'perk': self.path, 'applyUpgradesForPerk': str(self.applyUpgradesForPerk).lower(), 'isRune': str(self.isRune).lower()}


class ItemType(Enum):
    """ Represents a distinct category of the Item class. """
    IT_EQUIPMENT = 0,
    IT_WEAPON = 1,
    IT_AMMO = 2,
    IT_SPECIAL = 3

    default = IT_EQUIPMENT


class Item():
    """ Represents an instance of player equipment or weapons. """

    def __init__(self, name, type, path, available, equip = False, count = None, applyAfterLoadout = None):

        self.name = name
        self.type = type
        self.path = path
        self.available = available
        self.equip = equip
        self.count = count
        self.applyAfterLoadout = applyAfterLoadout

    def updateItemData(self):
        """ Applies any changes in member variables to item's data dictionary """

        if self.type is (ItemType.IT_EQUIPMENT or ItemType.IT_Weapon):
            self.itemData = {'item': self.path}
        else:
            match self.type:
                case ItemType.IT_SPECIAL:
                    self.itemData = {'item': self.path, 'equip': 'true'}
                case ItemType.IT_AMMO:
                    self.itemData = {'item': self.path, 'count': self.count, 'applyAfterLoadout': 'true'}
        
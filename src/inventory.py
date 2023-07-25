"""
inventory.py: 
- represents player starting inventory data
- overall Inventory consists of InventoryModules
- modules consist of InventoryEntries
- --- these can be Perks (capacities, suit upgrades, runes, weapon mods) 
- --- or Items (equipment, weapons, ammo)
- if these entries are added to their module's Available list, the player starts with them
- note: the typo in 'enviroment' is present in id's source, and so is here intentionally
"""

from components import *

@dataclass
class InventoryModule(metaclass = abc.ABCMeta):
    """ 
    Abstract base class representing a grouping of similar inventory entries.
    All possible entries are defined as members, with entires in the 'available' list
    being added to the player's starting inventory (some of which are added by default).
    """

    moduleName: str
    entryType: object
    available: list[InventoryEntry] = field(default_factory = list)

    def updateModuleData(self):
        """ Updates module's data dictionary attribute based on member variables. """
        
        for each in self.available:
            each.updateData()
            
    def addToModule(self, inventoryEntryName: str):
        """ Adds an entry to module's available pool, if validated. """
        
        if hasattr(self, inventoryEntryName):
            entry = getattr(self, inventoryEntryName)
            if type(entry) is self.entryType and entry not in self.available:
                self.available.append(entry)


@dataclass
class ArgentCellUpgrades(InventoryModule):
    """ Represents a collection of possible/available ArgentPerks. """

    moduleName: str = 'ArgentCellUpgrades'
    entryType: object = ArgentPerk
    
    healthCapacity = ArgentPerk('healthCapacity','"perk/zion/player/sp/enviroment_suit/health_capacity"')
    armorCapacity = ArgentPerk('armorCapacity', '"perk/zion/player/sp/enviroment_suit/armor_capacity"')
    ammoCapacity = ArgentPerk('ammoCapacity', '"perk/zion/player/sp/enviroment_suit/ammo_capacity"')

    def __post_init__(self) -> None:
        """ Adds default starting perks to available pool. """
        self.available = [self.healthCapacity, self.armorCapacity, self.ammoCapacity]
        
    
@dataclass
class PraetorSuitUpgrades(InventoryModule):
    """ Represent a collection of possible/available PraetorPerks. """

    moduleName: str = 'PraetorSuitUpgrades'
    entryType: object = PraetorPerk

    # environmental resistance
    hazardProtection = PraetorPerk(name = 'hazardProtection', 
                                   path = '"perk/zion/player/sp/enviroment_suit/modify_enviromental_damage_1"',
                                   description = 'Damage taken from explosive barrels and environmental sources is reduced.')
    selfPreservation = PraetorPerk(name = 'selfPreservation', 
                                   path = '"perk/zion/player/sp/enviroment_suit/modify_enviromental_damage_2"',
                                   description = 'Self-inflicted damage from weapons is reduced.')
    barrelsOFun = PraetorPerk(name = 'environmentalResistance3', 
                              path = '"perk/zion/player/sp/enviroment_suit/modify_enviromental_damage_3"',
                              description = 'Immunity to damage from explosive barrels.')

    # area-scanning technology
    # equipment system
    # powerup effectiveness
    # dexterity


@dataclass
class Runes(InventoryModule):
    """ Represent a collection of possible/available RunePerks. """
    
    moduleName: str = 'Runes'
    entryType: object = RunePerk
    
    #
    vacuum = RunePerk(name = 'vacuum', 
                      path = '"perk/zion/player/sp/enviroment_suit/increase_drop_radius"',
                      description = 'Increases the range for absorbing dropped items.',
                      upgradeDescription = 'Further increases the range for absorbing dropped items.')
    dazedAndConfused = RunePerk(name = 'dazedAndConfusedRune', 
                                path = '"perk/zion/player/sp/enviroment_suit/modify_enemy_stagger_duration"',
                                description = 'Increases how long demons remain in a stagger state.',
                                upgradeDescription = 'Demon staggers last even longer.')
 
 
@dataclass
class Equipment(InventoryModule):
    """ Represent a collection of possible/available EquipmentItems. """
    
    moduleName: str = 'Equipment'
    entryType: object = EquipmentItem
    
    #
    doubleJumpThrustBoots = EquipmentItem('doubleJumpThrustBoots',  "jumpboots/base", equip = True)
    fragGrenade = EquipmentItem('fragGrenade', '"throwable/zion/player/sp/frag_grenade"', equip = True)
    decoyHologram = EquipmentItem('decoyHologram', '"decoyhologram/equipment"')
    siphonGrenade = EquipmentItem('siphonGrenade', '"throwable/zion/player/sp/siphon_grenade"')
     
        
@dataclass
class Weapons(InventoryModule):
    """ Represents a collection of possible/available WeaponItems. """
    
    moduleName: str = 'Weapons'
    entryType: object = WeaponItem
    
    #
    fists = WeaponItem('fists', '"weapon/zion/player/sp/fists"')
    pistol = WeaponItem('pistol', '"weapon/zion/player/sp/pistol"', equip = True)
    combatShotgun = WeaponItem('combatShotgun', '"weapon/zion/player/sp/shotgun"')
    
    def __post_init__(self) -> None:
        """ Adds default starting armaments to available pool. """
        self.available = [self.fists, self.pistol]
    
    
@dataclass
class WeaponMods(InventoryModule):
    """ Represents a collection of possible/available WeaponModPerks. """

    moduleName: str = 'WeaponMods'
    entryType: object = WeaponModPerk
    
    # TODO: enforce weapon mods not being added by the user unless the weapon itself is as well
    # TODO: enforce masteries not being added by the user unless all preceding upgrades are as well
    
    # pistol upgrades (no mods)
    chargeEfficiency = WeaponModPerk(name = 'chargeEfficiency',
                                     path = '"perk/zion/player/sp/weapons/pistol/secondary_charge_shot_faster_charge"',
                                     description = 'Decreases charge time for a charged shot.')
    quickRecovery = WeaponModPerk(name = 'quickRecovery',
                                    path = '"perk/zion/player/sp/weapons/pistol/secondary_charge_shot_faster_discharge"',
                                    description = 'Decreases the cool-down time required after a charged shot.')
    lightWeight = WeaponModPerk(name = 'lightWeight',
                                    path = '"perk/zion/player/sp/weapons/pistol/secondary_charge_shot_no_movement_penalty"',
                                    description = 'Enables faster movement while charging.')
    increasedPowerMastery = WeaponModPerk(name = 'increasedPowerMastery',
                                    path = '"perk/zion/player/sp/weapons/pistol/secondary_charge_shot_higher_damage',
                                    description = 'Charged shots do more damage.')
    
    # chainsaw (path = '"weapon/zion/player/sp/chainsaw"')
    # combat shotgun: charged burst + upgrades
    # combat shotgun: explosive shot + upgrades
    # super shotgun upgrades (no mods)
    # heavy assault rifle: tactical scope + upgrades
    # heavy assault rifle: micro missiles + upgrades
    # plasma rifle: heat blast + upgrades
    # plasma rifle: stun bomb + upgrades
    # rocket launcher: lock-on burst + upgrades
    # rocket launcher: remote detonation + upgrades
    # gauss cannon: precision bolt + upgrades
    # gauss cannon: siege mode + upgrades
    # chaingun: gatling rotator + upgrades
    # chaingun: mobile turret + upgrades


@dataclass
class Ammo(InventoryModule):
    """ Represents a collection of possible/available AmmoItems. """
    
    moduleName: str = 'Ammo'
    entryType: object = AmmoItem
    
    #
    fuel = AmmoItem('fuel', '"ammo/zion/sharedammopool/fuel"', count = 99)
    shells = AmmoItem('shells', '"ammo/zion/sharedammopool/shells"', count = 99)


@dataclass
class Inventory():
    """ Represents an entire player starting inventory. Has method to generate decl file for modding use. """
    
    # create each module w/ defaults
    argentCellUpgrades = ArgentCellUpgrades() 
    praetorSuitUpgrades = PraetorSuitUpgrades()
    equipment = Equipment()
    weapons = Weapons()
    weaponMods = WeaponMods()
    ammo = Ammo()
    runes = Runes()
    
    modules: list[InventoryModule] = field(default_factory = list)
    
    def __post_init__(self) -> None:
        """ Adds each InventoryModule class member to modules list. """
        self.modules = [self.argentCellUpgrades, self.praetorSuitUpgrades, self.equipment, self.weapons, self.weaponMods, self.ammo, self.runes]

    def generateDeclFile(self, path = None):
        """ Generates base.decl;devInvLoadout file based on module entries, which level-specific decls inherit from. """

        invItemsCount = 1 # incl. base item
        for module in self.modules:
            # get total inventory item count
            invItemsCount += len(module.available)

        # writing to output file
        fileNameFinal = 'base.decl;devInvLoadout'
        fileNameTemp = 'loadout.txt'

        with open(fileNameTemp, 'w+') as file:
            file.write('{\n' + indent)
            file.write('edit = {\n' + doubleIndent + 'startingInventory = {')
            file.write('\n' + tripleIndent + f'num = {invItemsCount};')
            
            # add base item
            file.write('\n' + tripleIndent + f'item[0] = ' + '{')
            for key, value in BASE_ITEM.items():
                file.write(''.join('\n' + quadIndent + f'{key} = {value};'))
            file.write('\n' + tripleIndent + '}')
            itemIndex = 1
            
            # add each module's items
            for module in self.modules:
                module.updateModuleData()
                
                for eachEntry in module.available:
                    # if itemIndex == 4: # index 4 needs to be skipped for some unknown reason
                    #     itemIndex += 1
                    file.write('\n' + tripleIndent + f'item[{itemIndex}] = ' + '{')
                    
                    for key, value in eachEntry.data.items():
                        file.write(''.join('\n' + quadIndent + f'{key} = {value};'))
                            
                    file.write('\n' + tripleIndent + '}')
                    itemIndex += 1

            file.write('\n' + doubleIndent + '}')
            file.write('\n' + indent + '}')
            file.write('\n}')

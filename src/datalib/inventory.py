"""
inventory.py: 
- represents player starting inventory data
- an Inventory consists of InventoryModules
"""

from datalib.modules import *


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

    def generateDeclFile(self, path: str):
        """ Generates base.decl;devInvLoadout file based on module entries, which level-specific decls inherit from. """

        invItemsCount = 1 # incl. base item
        for module in self.modules:
            # get total inventory item count
            invItemsCount += len(module.available)

        # writing to output file
        fileNameProduction = path + r'\base.decl;devInvLoadout'
        fileNameDev = 'loadout.txt'

        with open(fileNameProduction, 'w+') as file:
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
                    file.write('\n' + tripleIndent + f'item[{itemIndex}] = ' + '{')
                    
                    for key, value in eachEntry.data.items():
                        file.write(''.join('\n' + quadIndent + f'{key} = {value};'))
                            
                    file.write('\n' + tripleIndent + '}')
                    itemIndex += 1

            file.write('\n' + doubleIndent + '}')
            file.write('\n' + indent + '}')
            file.write('\n}')

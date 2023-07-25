"""
components.py: 
- individual elements ('entries') that can be put into an InventoryModule
- hierarchy is Entry->Perk/Item->TypeofPerk/TypeofItem
"""

import abc
from dataclasses import dataclass, field
from typing import Any, Optional

from common import *


@dataclass
class InventoryEntry(metaclass = abc.ABCMeta):
    """ Base class representing a single entry into an InventoryModule. Children are InventoryPerk and InventoryItem."""

    name: str
    path: str
    data: dict = field(default_factory = dict)
    equip: Optional[bool] = None
    count: Optional[int] = None
    
    @abc.abstractmethod
    def updateData(self):
        """ Virtual method: creates relevant data dictionary. """
        pass


@dataclass
class InventoryPerk(InventoryEntry):
    """ Perk inventory entry base class. Children are ArgentPerk, PraetorPerk, RunePerk and WeaponModPerk. """
    
    description: Optional[str] = None
    applyUpgradesForPerk: Optional[bool] = None
    isRune: Optional[bool] = None
    runePermanentEquip: Optional[bool] = None
    
  
@dataclass
class ArgentPerk(InventoryPerk):
    """ Represents permanent stat increases to suit subsystem capacities provided by Argent Cells. """
    
    count: int = 0
    
    def updateData(self):
        """ """
        if self.name != 'ammoCapacity':
            self.data = {'perk': self.path, 'count': self.count, 'equip': 'true', 'remove_after_equip': 'true'}
        else: # gets additional 'applyAfterLoadout' key
            self.data = {'perk': self.path, 'count': self.count, 'equip': 'true', 'applyAfterLoadout': 'true', 'remove_after_equip': 'true'}
 

@dataclass
class PraetorPerk(InventoryPerk):
    """ Represent permanent suit upgrades provided by Praetor Tokens. """
    
    description: str = 'no description provided'
    
    def updateData(self):
        self.data = {'perk': self.path, 'equip': 'true'}
     
        
@dataclass
class RunePerk(InventoryPerk):
    """ 
    Represent demonic sigils granting unique perks, acquired via Rune Trials.
    By default, only 3 can be equipped at once, but setting the isRune flag to False
    and the equip flag to True makes the rune permanently equipped without taking up a slot.
    """
    
    applyUpgradesForPerk: bool = False
    runePermanentEquip: bool = False
    upgradeDescription: str = 'no upgrade description provided'
    
    def updateData(self):
        # mod option: make rune perk permanent without taking up a rune slot
        if self.runePermanentEquip:
            self.data = {'perk': self.path, 'applyUpgradesForPerk': str(self.applyUpgradesForPerk).lower(), 'equip': 'true'}
        else:
            self.data = {'perk': self.path, 'applyUpgradesForPerk': str(self.applyUpgradesForPerk).lower(), 'isRune': 'true'}


@dataclass
class WeaponModPerk(InventoryPerk):
    """ Represents a weapon mod and/or its upgrades. """
    
    applyUpgradesForPerk: bool = False
    equip: bool = False
    description: str = 'no description provided'
    
    def updateData(self):
        self.data = {'perk': self.path, 'applyUpgradesForPerk': str(self.applyUpgradesForPerk).lower(), 'equip': 'true'}


@dataclass
class InventoryItem(InventoryEntry):
    """ Non-perk inventory entry base class. Children are EquipmentItem, WeaponItem, and AmmoItem. """

    applyAfterLoadout: Optional[bool] = None


@dataclass
class EquipmentItem(InventoryItem):
    """ Represents double-jump thrust boots and throwables. """
    
    def updateData(self):
        if self.equip:
            self.data = {'item': self.path, 'equip': 'true'}
        else:
            self.data = {'item': self.path}

@dataclass
class WeaponItem(InventoryItem):
    """ Represents armaments: fists, chainsaw, guns. """
    
    def updateData(self):
        """ """
        if self.equip:
            self.data = {'item': self.path, 'equip': 'true'}
        else:
            self.data = {'item': self.path}
            

@dataclass
class AmmoItem(InventoryItem):
    """ Represents required item for WeaponItems to be usable: fuel, shells, bullets. """
    
    applyAfterLoadout: bool = True
    count: int = 0
    
    def updateData(self):
        """ """
        self.data = {'item': self.path, 'count': self.count, 'applyAfterLoadout': 'true'}
                    
        
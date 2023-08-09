"""
modules.py: 
- represent a grouping of inventory data
- InventoryModules consist of InventoryElements
- if these elements are added to their module's 'available' list, the player starts with them @ new game
- note: the typo in 'enviroment' is present in id's source, and so is here intentionally
"""

from datalib.elements import *


@dataclass
class InventoryModule(metaclass = abc.ABCMeta):
    """ 
    Abstract base class representing a grouping of similar inventory elements.
    All possible elements are defined as members, with elements in the 'available' list
    being added to the player's starting inventory (some of which are added by default).
    """

    # metadata
    moduleName: str
    elementType: object
    
    # elements to add to starting inventory loadout
    available: list[InventoryElement] = field(default_factory = list)

    def updateModuleData(self):
        """ Updates module's data dictionary attribute based on member variables. """
        
        for each in self.available:
            each.updateData()
            
    def addToAvailable(self, inventoryElementName: str):
        """ Adds an element to module's available pool, if validated. """
        
        if hasattr(self, inventoryElementName):
            element = getattr(self, inventoryElementName)
            if type(element) is self.elementType and element not in self.available:
                self.available.append(element)
     
    @classmethod 
    def all(cls):
        return [value for name, value in vars(cls).items()]
              
    def addAllToAvailable(self):
        """ Add all possibles elements to module's available pool, if validated. """
        
        allMembers = self.all()
        for each in allMembers:
            if type(each) is self.elementType and each not in self.available:
                self.available.append(each)


@dataclass
class ArgentCellUpgrades(InventoryModule):
    """ Represents a collection of possible/available ArgentPerks. """

    # metadata
    moduleName: str = 'ArgentCellUpgrades'
    elementType: object = ArgentPerk
    
    healthCapacity = ArgentPerk('healthCapacity','"perk/zion/player/sp/enviroment_suit/health_capacity"')
    armorCapacity = ArgentPerk('armorCapacity', '"perk/zion/player/sp/enviroment_suit/armor_capacity"')
    ammoCapacity = ArgentPerk('ammoCapacity', '"perk/zion/player/sp/enviroment_suit/ammo_capacity"')

    def __post_init__(self) -> None:
        """ Adds default starting perks to available pool. """
        self.available = [self.healthCapacity, self.armorCapacity, self.ammoCapacity]
        
    def setArgentLevel(self, category: str, level: int):
        """ Sets passed category perk's count variable to passed value, if validated. """
        
        # clamp + ensure category can be increased
        level = clamp(level, 0, 4) #max(0, min(level, 4))
        for perk in self.available:
            if perk.name == category:
                if level > 3 and not self.getCanUpgradeFurther():
                    level = 3
                perk.count = level # set
        return level # return validated level for GUI use
                
    def getCanUpgradeFurther(self) -> bool:
        """ Ensures at least one ArgentCell upgrade slot remains open for mandatory game progression. """
        
        numMaxedCapacities = 0
        for eachArgentPerk in self.available:
            if eachArgentPerk.count and eachArgentPerk.count > 3:
                numMaxedCapacities += 1
                
        return False if numMaxedCapacities > 1 else True         
        
    
@dataclass
class PraetorSuitUpgrades(InventoryModule):
    """ Represent a collection of possible/available PraetorPerks. """

    # metadata
    moduleName: str = 'PraetorSuitUpgrades'
    elementType: object = PraetorPerk

    # environmental resistance
    hazardProtection = PraetorPerk(
        name = 'hazardProtection', 
        fName = 'Hazard Protection',
        category = 'Environmental Resistance',
        path = '"perk/zion/player/sp/enviroment_suit/modify_enviromental_damage_1"',
        description = 'Damage taken from explosive barrels and environmental sources is reduced.')
    selfPreservation = PraetorPerk(
        name = 'selfPreservation',
        fName = 'Self Preservation',
        category = 'Environmental Resistance',
        path = '"perk/zion/player/sp/enviroment_suit/modify_enviromental_damage_2"',
        description = 'Self-inflicted damage from weapons is reduced.')
    barrelsOFun = PraetorPerk(
        name = 'barrelsOFun', 
        fName = 'Barrels O\' Fun',
        category = 'Environmental Resistance',
        path = '"perk/zion/player/sp/enviroment_suit/modify_enviromental_damage_3"',
        description = 'Immunity to damage from explosive barrels.')

    # area-scanning technology
    itemAwareness = PraetorPerk(
        name = 'itemAwareness', 
        fName = 'Item Awareness',
        category = 'Area-Scanning Technology',
        path = '"perk/zion/player/sp/enviroment_suit/automap_1"',
        description = 'The automap reveals exploration items in a wider radius.',
        unlockable = '"researchprojects/find_collectibles_1"')
    secretSense = PraetorPerk(
        name = 'secretSense', 
        fName = 'Secret Sense',
        category = 'Area-Scanning Technology',
        path = '"perk/zion/player/sp/enviroment_suit/automap_2"',
        description = 'The automap compass pulses when nearby a secret.')
    fullView = PraetorPerk(
        name = 'fullView', 
        fName = 'Full View',
        category = 'Area-Scanning Technology',
        path = '"perk/zion/player/sp/enviroment_suit/automap_3"',
        description = 'Exploration items are automatically displayed.')
    
    # equipment system
    quickCharge = PraetorPerk(
        name = 'quickCharge', 
        fName = 'Quick Charge',
        category = 'Equipment System',
        path = '"perk/zion/player/sp/enviroment_suit/equipment_1"',
        description = 'Equipment recharge duration is reduced.',
        unlockable = '"researchprojects/equipment_1"')
    stockUp = PraetorPerk(
        name = 'stockUp', 
        fName = 'Stock Up',
        category = 'Equipment System',
        path = '"perk/zion/player/sp/enviroment_suit/equipment_2"',
        description = 'The total number of equipment charges is increased.')
    rapidCharge = PraetorPerk(
        name = 'rapidCharge', 
        fName = 'Rapid Charge',
        category = 'Equipment System',
        path = '"perk/zion/player/sp/enviroment_suit/equipment_3"',
        description = 'Recharge duration is further reduced.')
    
    # powerup effectiveness
    powerSurge = PraetorPerk(
        name = 'powerSurge', 
        fName = 'Power Surge',
        category = 'Powerup Effectiveness',
        path = '"perk/zion/player/sp/enviroment_suit/powerup_shockwave"',
        description = 'A blast wave is unleashed when a power-up expires.')
    healingPower = PraetorPerk(
        name = 'healingPower', 
        fName = 'Healing Power',
        category = 'Powerup Effectiveness',
        path = '"perk/zion/player/sp/enviroment_suit/powerup_health"',
        description = 'Health is restored to maximum when a power-up is activated.')
    powerExtender = PraetorPerk(
        name = 'powerExtender', 
        fName = 'Power Extender',
        category = 'Powerup Effectiveness',
        path = '"perk/zion/player/sp/enviroment_suit/modify_powerup_duration"',
        description = 'Power-up durations are increased.')
    
    # dexterity
    adept = PraetorPerk(
        name = 'adept', 
        fName = 'Adept',
        category = 'Dexterity',
        path = '"perk/zion/player/sp/enviroment_suit/dexterity_increase_1"',
        description = 'Weapon changing time is reduced.')
    quickHands = PraetorPerk(
        name = 'quickHands', 
        fName = 'Quick Hands',
        category = 'Dexterity',
        path = '"perk/zion/player/sp/enviroment_suit/dexterity_increase_2"',
        description = 'Ledge grabbing speed is increased.')
    hotSwap = PraetorPerk(
        name = 'hotSwap', 
        fName = 'Hot Swap',
        category = 'Dexterity',
        path = '"perk/zion/player/sp/enviroment_suit/dexterity_increase_3"',
        description = 'Weapon modification swap time is reduced.')

@dataclass
class Runes(InventoryModule):
    """ Represent a collection of possible/available RunePerks. """
    
    # metadata
    moduleName: str = 'Runes'
    elementType: object = RunePerk
    upgradedRunes: list[RunePerk] = field(default_factory = list)
    permEquipRunes: list[RunePerk] = field(default_factory = list)
    
    def setIsUpgraded(self, runeName: str, isUpgraded: bool):
        """ Sets corresponding rune's applyUpgradesForPerk value, if validated. """
        
        rune = getattr(self, runeName)
        if isinstance(rune, RunePerk):
            rune.applyUpgradesForPerk = isUpgraded  
            
    def setAllAreUpgraded(self, areUpgraded: bool):
        """ Sets applyUpgradesForPerk flag for all runes. """
        
        allMembers = self.all()
        for each in allMembers:
            if type(each) is self.elementType and not each.applyUpgradesForPerk:
                each.applyUpgradesForPerk = areUpgraded
            
    def setIsPermanent(self, runeName: str, isPermanent: bool):
        """ Adds corresponding rune to available pool as permanently equipped (not taking up a slot), if validated. """
        
        rune = getattr(self, runeName)
        if isinstance(rune, RunePerk):
            self.addToAvailable(runeName)
            rune.runePermanentEquip = isPermanent  
    
    def setAllArePermEquip(self, arePermanent: bool):
        """ Sets runePermanentEquip flag for all runes. """
        
        allMembers = self.all()
        for each in allMembers:
            if type(each) is self.elementType and not each.runePermanentEquip:
                each.runePermanentEquip = arePermanent
           
    def getRunePerkFromName(self, runeName: str) -> RunePerk | None:
        """ Returns RunePerk object corresponding to passed name, if valid. """
        
        rune = getattr(self, runeName)
        if isinstance(rune, RunePerk):
            return rune          
    
    vacuum = RunePerk(
        name = 'vacuum', 
        path = '"perk/zion/player/sp/enviroment_suit/increase_drop_radius"',
        description = 'Increases the range for absorbing dropped items.',
        upgradeDescription = 'Further increases the range for absorbing dropped items.')
    
    dazedAndConfused = RunePerk(
        name = 'dazedAndConfused', 
        path = '"perk/zion/player/sp/enviroment_suit/modify_enemy_stagger_duration"',
        description = 'Increases how long demons remain in a stagger state.',
        upgradeDescription = 'Demon staggers last even longer.')
    
    ammoBoost = RunePerk(
        name = 'ammoBoost',
        path = '"perk/zion/player/sp/enviroment_suit/modify_ammo_drops"',
        description = 'Increases the value of ammo received from demons and items.',
        upgradeDescription = 'BFG ammo has a chance to drop from demons.')
    
    equipmentPower = RunePerk(
        name = 'equipmentPower',
        path = '"perk/zion/player/sp/enviroment_suit/activate_equipment_effectiveness"',
        description = 'Increases the effectiveness of Equipment items.',
        upgradeDescription = 'Further increases the effectiveness of Equipment items.')
    
    seekAndDestroy = RunePerk(
        name = 'seekAndDestroy',
        path = '"perk/zion/player/sp/enviroment_suit/glory_kill_dash"',
        description = 'Launch into a glory kill from much further away.',
        upgradeDescription = 'Increases the distance Seek and Destroy can be initiated.')
    
    savagery = RunePerk(
        name = 'savagery',
        path = '"perk/zion/player/sp/enviroment_suit/glory_kill_speed"',
        description = 'Perform glory kills faster.',
        upgradeDescription = 'Further increases speed of glory kills.')
    
    inFlightMobility = RunePerk(
        name = 'inFlightMobility',
        path = '"perk/zion/player/sp/enviroment_suit/double_jump_air_control"',
        description = 'Provides a significant increase in control over in-air movement after a double-jump.',
        upgradeDescription = 'Applies air-control to a single jump.')
    
    armoredOffensive = RunePerk(
        name = 'armoredOffensive',
        path = '"perk/zion/player/sp/enviroment_suit/glory_kills_award_armor"',
        description = 'Glory killing demons drop armor.',
        upgradeDescription = 'More armor drops per glory kill.')
    
    bloodFueled = RunePerk(
        name = 'bloodFueled',
        path = '"perk/zion/player/sp/enviroment_suit/speed_boost_on_glory_kill"',
        description = 'Move faster for a short time after performing a glory kill.',
        upgradeDescription = 'Extends how long you can move faster after performing a glory kill.')
    
    intimacyIsBest = RunePerk(
        name = 'intimacyIsBest',
        path = '"perk/zion/player/sp/enviroment_suit/modify_enemy_stagger_toughness"',
        description = 'Demons become more glory kill friendly due to a high damage resistance when staggered.',
        upgradeDescription = 'Demons stagger off less damage.')
    
    richGetRicher = RunePerk(
        name = 'richGetRicher',
        path = '"perk/zion/player/sp/enviroment_suit/infinite_ammo_on_health_value"',
        description = 'Firing your standard weapons will not cost ammo when you have 100 Armor or more.',
        upgradeDescription = 'Activate Rich Get Richer at 75 armor.')
    
    savingThrow = RunePerk(
        name = 'savingThrow',
        path = '"perk/zion/player/sp/enviroment_suit/activate_focus_on_death_blow"',
        description = 'Get one chance to survive a death blow and recover health. This resets on death.',
        upgradeDescription = 'Get an additional Saving Throw per life.')
 
@dataclass
class Equipment(InventoryModule):
    """ Represent a collection of possible/available EquipmentItems. """
    
    # metadata
    moduleName: str = 'Equipment'
    elementType: object = EquipmentItem
    
    doubleJumpThrustBoots = EquipmentItem(
        name = 'doubleJumpThrustBoots', 
        fName = 'Delta V Jump-Boots',
        path = '"jumpboots/base"', 
        equip = True,
        description = 'A UAC-engineered device which enables a second thruster-based mid-air jump\n' 
        + 'to be performed, greatly increasing maximum jumping distance and height.')
    fragGrenade = EquipmentItem(
        name = 'fragGrenade',
        fName = 'Frag Grenade', 
        path = '"throwable/zion/player/sp/frag_grenade"', 
        equip = True,
        description = 'While a conventional grenade based on the M67 at the core, it has been \n' 
        + 'enhanced by the UAC in several ways. Provides a five meter radius of lethal damage.')
    siphonGrenade = EquipmentItem(
        name = 'siphonGrenade', 
        fName = 'Siphon Grenade',
        path = '"throwable/zion/player/sp/siphon_grenade"',
        description = 'Functions on the basis of alternately charged Argent energy fields, creating a positive charge on the user\'s\n' 
        + 'suit and exploding with a negatively charged field. The resulting differential creates an attractive Argent field\n' 
        + 'that pulls plasma from any demons caught in the blast radius, feeding it back as energy which can heal.')
    decoyHologram = EquipmentItem(
        name = 'decoyHologram',
        fName = 'Decoy Hologram',
        path ='"decoyhologram/equipment"',
        description = 'Functions by projecting an image into a cloud of ionized argon gas.\n' 
        + 'The broad-spectrum image creates a convincing illusion which can distract enemies.')
     
        
@dataclass
class Weapons(InventoryModule):
    """ Represents a collection of possible/available WeaponItems. """
    
    def __post_init__(self) -> None:
        """ Adds default starting armaments to available pool. """
        self.available = [self.fists, self.pistol]
        
    def getAmmoTypeForWeapon(self, weaponName: str):
        """ Helper function to idenfity a weapon's corresponding ammo by names. """
        weapon = getattr(self, weaponName)
        if isinstance(weapon, WeaponItem):
            return weapon.ammoType     
    
    # metadata
    moduleName: str = 'Weapons'
    elementType: object = WeaponItem
    
    fists = WeaponItem(
        name = 'fists', 
        path = '"weapon/zion/player/sp/fists"')
    chainsaw = WeaponItem(
        name = 'chainsaw', 
        fName = 'Chainsaw',
        ammoType = 'fuel', 
        path = '"weapon/zion/player/sp/chainsaw"',
        description= 'The Chainsaw is a specialized melee weapon.\n' 
        + 'Using the Chainsaw requires fuel - the bigger the demon, the more you need.\n' 
        + 'Cutting apart a demon with the Chainsaw will always drop a surplus of ammunition.')
    pistol = WeaponItem(
        name = 'pistol',
        fName = 'Pistol', 
        path = '"weapon/zion/player/sp/pistol"', 
        equip = True,
        description = 'A small directed energy weapon based on plasma gel - called energy-matter-gel.\n' 
        + 'Four megawatts of Argent energy are compressed into a kinetic slug.\n' 
        + 'It has an unlimited ammunition supply thanks to a gravitational dynamo which is charged by the wielder\'s movements.')
    combatShotgun = WeaponItem(
        name = 'combatShotgun', 
        fName = 'Combat Shotgun',
        ammoType = 'shells',
        path = '"weapon/zion/player/sp/shotgun"',
        description = 'A pump-action shotgun with a tight spread of buckshot.')
    heavyAssaultRifle = WeaponItem(
        name = 'heavyAssaultRifle',
        fName = 'Heavy Assault Rifle',
        ammoType = 'bullets',
        path = '"weapon/zion/player/sp/heavy_rifle_heavy_ar"', 
        equipReserve = True,
        description = 'Features a dependable mechanical firing mechanism, high accuracy at long range, and an abundant supply of ammunition.')
    plasmaRifle = WeaponItem(
        name = 'plasmaRifle', 
        fName = 'Plasma Rifle',
        ammoType = 'cells',
        path = '"weapon/zion/player/sp/plasma_rifle"',
        description = 'A fully automatic rifle that fires pulses of super-heated plasma capable of dealing splash damage.')
    rocketLauncher = WeaponItem(
        name = 'rocketLauncher',
        fName = 'Rocket Launcher',
        ammoType = 'rockets',
        path = '"weapon/zion/player/sp/rocket_launcher"',
        description = 'Fires rockets that explode on impact, doing damage over a large area.')
    superShotgun = WeaponItem(
        name = 'superShotgun',
        fName = 'Super Shotgun',
        ammoType = 'shells',
        path = '"weapon/zion/player/sp/double_barrel"',
        description = 'A break-action double shotgun that fires a wide spread of buckshot.')
    gaussCannon = WeaponItem(
        name = 'gaussCannon', 
        fName = 'Gauss Cannon',
        path = '"weapon/zion/player/sp/gauss_rifle"',
        description = 'A devastatingly accurate long-range weapon with a noticeable kick that must be compensated by the operator.')
    chaingun = WeaponItem(
        name = 'chaingun', 
        fName = 'Chaingun',
        ammoType = 'bullets',
        path = '"weapon/zion/player/sp/chaingun"',
        description = 'A large drum-fed rotary machine gun with a high rate of fire.')
    bfg9000 = WeaponItem(
        name = 'bfg9000', 
        fName = 'BFG-9000', 
        ammoType = 'bfg',
        path = '"weapon/zion/player/sp/bfg"',
        description = 'The BFG-9000 is a weapon with massive power - use it to devastate your enemies.\n'
        + 'Most research regarding the BFG-9000 remains classified.\n' 
        + 'The design was first [REDACTED] by [REDACTED] and [REDACTED].')


@dataclass
class WeaponMods(InventoryModule):
    """ Represents a collection of possible/available WeaponModPerks. """

    # metadata
    moduleName: str = 'WeaponMods'
    elementType: object = WeaponModPerk
    
    def addToAvailable(self, applicableWeapon: str, modName: str):
        """ Adds an weapon mod to module's available pool, if validated."""
        if hasattr(self, modName):
            mod = getattr(self, modName)
            if mod.applicableWeapon == applicableWeapon and mod not in self.available:
                self.available.append(mod)
    
    def toggleAllBaseModsAvailable(self, areAvailable: bool):
        """ Toggles availability for all base mods. """
        
        allMembers = self.all()
        for each in allMembers:
            if isinstance(each, WeaponModPerk) and each.applicableMod == 'isBaseMod':
                if areAvailable:
                    if each not in self.available:
                        self.available.append(each)
                else:
                    if each in self.available:
                        self.available.remove(each)
                
    def toggleAllModUpgradesAvailable(self, areAvailable: bool):
        """ Toggles availability for all non-base mods (i.e., upgrades for base mods). """
        
        allMembers = self.all()
        for each in allMembers:
            if isinstance(each, WeaponModPerk) and each.applicableMod != 'isBaseMod':
                if areAvailable:
                    if each not in self.available:
                        self.available.append(each)
                else:
                    if each in self.available:
                        self.available.remove(each)
    
    def getWeaponModPerkFromName(self, modName: str) -> WeaponModPerk | None:
        """ Returns WeaponModPerk object corresponding to passed name, if valid. """
        
        weaponModPerk = getattr(self, modName)
        if isinstance(weaponModPerk, WeaponModPerk):
            return weaponModPerk
        
    def getAllModsForWeapon(self, weaponName: str):
        """ Returns all mods applicable to the passed weapon. """
        
        allModsForWeapon = []
        
        allMembers = self.all()
        for each in allMembers:
            if isinstance(each, WeaponModPerk) and each.applicableWeapon == weaponName:
                allModsForWeapon.append(each)
                
        return allModsForWeapon
        
    def getAllUpgradesForMod(self, modName: str):
        """ Returns all upgrades applicable to the passed mod. """
        
        allUpgradesForMod = []
        
        allMembers = self.all()
        for each in allMembers:
            if isinstance(each, WeaponModPerk) and each.applicableMod == modName:
                allUpgradesForMod.append(each)
                
        return allUpgradesForMod
    
    # PISTOL upgrades (no mods)
    chargeEfficiency = WeaponModPerk(
        name = 'chargeEfficiency',
        fName = 'Charge Efficiency',
        applicableWeapon = 'pistol',
        path = '"perk/zion/player/sp/weapons/pistol/secondary_charge_shot_faster_charge"',
        description = 'Decreases charge time for a charged shot.')
    quickRecovery = WeaponModPerk(
        name = 'quickRecovery',
        fName = 'Quick Recovery',
        applicableWeapon = 'pistol',
        path = '"perk/zion/player/sp/weapons/pistol/secondary_charge_shot_faster_discharge"',
        description = 'Decreases the cool-down time required after a charged shot.')
    lightWeight = WeaponModPerk(
        name = 'lightWeight',
        fName = 'Light Weight',
        applicableWeapon = 'pistol',
        path = '"perk/zion/player/sp/weapons/pistol/secondary_charge_shot_no_movement_penalty"',
        description = 'Enables faster movement while charging.')
    increasedPowerMastery = WeaponModPerk(
        name = 'increasedPowerMastery',
        fName = 'MASTERY: Increased Power',
        applicableWeapon = 'pistol',
        path = '"perk/zion/player/sp/weapons/pistol/secondary_charge_shot_higher_damage"',
        description = 'Charged shots do more damage.')
    
    # COMBAT SHOTGUN
    # combat shotgun: charged burst + upgrades
    chargedBurst = WeaponModPerk(
        name = 'chargedBurst',
        fName = 'Charged Burst',
        applicableMod = 'isBaseMod',
        applicableWeapon = 'combatShotgun',
        path = '"perk/zion/player/sp/weapons/shotgun/secondary_charge_burst"',
        description = 'An Argent-charged compression reloader fires off a volley of three shells in a quick succession.\n'
        + 'The compression reloader component used to drive this fast firing is powered by Argent energy, and requires a cool down period after use.')
    chargedBurst_speedyRecovery = WeaponModPerk(
        name = 'chargedBurst_speedyRecovery',
        fName = 'Speedy Recovery',
        applicableWeapon = 'combatShotgun',
        applicableMod = 'chargedBurst',
        path = '"perk/zion/player/sp/weapons/shotgun/secondary_charge_burst_faster_recharge"',
        description = 'Decreases recharge time of the mod.')
    chargedBurst_rapidFire = WeaponModPerk(
        name = 'chargedBurst_rapidFire',
        fName = 'Rapid Fire',
        applicableWeapon = 'combatShotgun',
        applicableMod = 'chargedBurst',
        path = '"perk/zion/player/sp/weapons/shotgun/secondary_charge_burst_faster_fire_rate"',
        description = 'Increases rate of fire of the mod.')
    chargedBurst_quickLoad = WeaponModPerk(
        name = 'chargedBurst_quickLoad',
        fName = 'Quick Load',
        applicableWeapon = 'combatShotgun',
        applicableMod = 'chargedBurst',
        path = '"perk/zion/player/sp/weapons/shotgun/secondary_charge_burst_faster_charge"',
        description = 'Decreases loading time of the mod. ')
    chargedBurst_powerShot_mastery = WeaponModPerk(
        name = 'chargedBurst_powerShot_mastery',
        fName = 'MASTERY: Power Shot',
        applicableWeapon = 'combatShotgun',
        applicableMod = 'chargedBurst',
        path = '"perk/zion/player/sp/weapons/shotgun/secondary_charge_burst_mastery"',
        description = 'Successfully hitting all three shots of a charged burst will increase the damage of the next one.\n' 
        + 'The effect does not stack.')
    
    # combat shotgun: explosive shot + upgrades
    explosiveShot = WeaponModPerk(
        name = 'explosiveShot',
        fName = 'Explosive Shot',
        applicableMod = 'isBaseMod',
        applicableWeapon = 'combatShotgun',
        path = '"perk/zion/player/sp/weapons/shotgun/pop_rocket"',
        description = 'An alternate ammunition for the combat shotgun based on octanitrocubane explosive and a glycerin fuse.\n' 
        + 'Shot embedded in the explosive is dispersed upon impact, creating an effect similar to the frag grenade,\n' 
        + 'damaging targets over a wide area. This extends the weapon\'s utility against multiple targets.')
    explosiveShot_speedyRecovery = WeaponModPerk(
        name = 'explosiveShot_speedyRecovery',
        fName = 'Speedy Recovery',
        applicableWeapon = 'combatShotgun',
        applicableMod = 'explosiveShot',
        path = '"perk/zion/player/sp/weapons/shotgun/pop_rocket_faster_recharge"',
        description = 'Decreases recharge time of the mod.')
    explosiveShot_biggerBoom = WeaponModPerk(
        name = 'explosiveShot_biggerBoom',
        fName = 'Bigger Boom',
        applicableWeapon = 'combatShotgun',
        applicableMod = 'explosiveShot',
        path = '"perk/zion/player/sp/weapons/shotgun/pop_rocket_larger_explosion"',
        description = 'Increases the area of effect.')
    explosiveShot_instantLoad = WeaponModPerk(
        name = 'explosiveShot_instantLoad',
        fName = 'Instant Load',
        applicableWeapon = 'combatShotgun',
        applicableMod = 'explosiveShot',
        path = '"perk/zion/player/sp/weapons/shotgun/pop_rocket_faster_charge"',
        description = 'Removes loading time of the mod.')
    explosiveShot_clusterStrike_mastery = WeaponModPerk(
        name = 'explosiveShot_clusterStrike_mastery',
        fName = 'MASTERY: Cluster Strike',
        applicableWeapon = 'combatShotgun',
        applicableMod = 'explosiveShot',
        path = '"perk/zion/player/sp/weapons/shotgun/pop_rocket_mastery"',
        description = 'Cluster bombs will spawn upon a direct impact on a demon providing further damage.')
    
    # SUPER SHOTGUN upgrades (no mods)
    fasterReload = WeaponModPerk(
        name = 'fasterReload',
        fName = 'Faster Reload',
        applicableWeapon = 'superShotgun',
        path = '"perk/zion/player/sp/weapons/double_barrel/default_faster_reload"',
        description = 'Decrease time to reload.')
    uraniumCoating = WeaponModPerk(
        name = 'uraniumCoating',
        fName = 'Uranium Coating',
        applicableWeapon = 'superShotgun',
        path = '"perk/zion/player/sp/weapons/double_barrel/default_bullet_penetration"',
        description = 'Shots penetrate through targets.')
    doubleTrouble_mastery = WeaponModPerk(
        name = 'doubleTrouble_mastery',
        fName = 'MASTERY: Double Trouble',
        applicableWeapon = 'superShotgun',
        path = '"perk/zion/player/sp/weapons/double_barrel/mastery"',
        description = 'Fire twice before having to reload.')
    
    # HEAVY ASSAULT RIFLE
    # heavy assault rifle: tactical scope + upgrades
    tacticalScope = WeaponModPerk(
        name = 'tacticalScope',
        fName = 'Tactical Scope',
        applicableWeapon = 'heavyAssaultRifle',
        applicableMod = 'isBaseMod',
        path = '"perk/zion/player/sp/weapons/heavy_rifle_heavy_ar/zoom"',
        description = 'The tactical scope is a telescopic sight allowing multiple levels of zoom with parallax compensation and gimbal-mounted\n'
        + 'recoil stabilization. It has a part designation of UAC-TS3. It transforms the already highly accurate heavy assault rifle into a sniper rifle.')
    tacticalScope_uraniumCoating = WeaponModPerk(
        name = 'tacticalScope_uraniumCoating',
        fName = 'Uranium Coating',
        applicableWeapon = 'heavyAssaultRifle',
        applicableMod = 'tacticalScope',
        path = '"perk/zion/player/sp/weapons/heavy_rifle_heavy_ar/zoom_bullet_penetration"',
        description = 'Shots fired with the tactical scope\'s zoom feature will pierce enemies.')
    tacticalScope_skullCracker = WeaponModPerk(
        name = 'tacticalScope_skullCracker',
        fName = 'Skull Cracker',
        applicableWeapon = 'heavyAssaultRifle',
        applicableMod = 'tacticalScope',
        path = '"perk/zion/player/sp/weapons/heavy_rifle_heavy_ar/zoom_more_headshot_damage"',
        description = 'Headshots attained in scope mode do more damage.')
    tacticalScope_lightWeight = WeaponModPerk(
        name = 'tacticalScope_lightWeight',
        fName = 'Light Weight',
        applicableWeapon = 'heavyAssaultRifle',
        applicableMod = 'tacticalScope',
        path = '"perk/zion/player/sp/weapons/heavy_rifle_heavy_ar/zoom_no_movement_penalty"',
        description = 'Increased movement speed while using the scope.')
    tacticalScope_devastatorRounds_mastery = WeaponModPerk(
        name = 'tacticalScope_devastatorRounds_mastery',
        fName = 'MASTERY: Devastator Rounds',
        applicableWeapon = 'heavyAssaultRifle',
        applicableMod = 'tacticalScope',
        path = '"perk/zion/player/sp/weapons/heavy_rifle_heavy_ar/zoom_mastery"',
        description = 'Fires powerful experimental Devastator rounds while zoomed-in.')
    
    # heavy assault rifle: micro missiles + upgrades
    microMissiles = WeaponModPerk(
        name = 'microMissiles',
        fName = 'Micro Missiles',
        applicableWeapon = 'heavyAssaultRifle',
        applicableMod = 'isBaseMod',
        path = '"perk/zion/player/sp/weapons/heavy_rifle_heavy_ar/burst_detonate"',
        description = 'The micro missile mod provides a dramatic temporary power increase, allowing the firing of up to six \n' 
        + 'explosive HMX missiles which detonate on impact. The pack of missiles attaches to the left side \n' 
        + 'of the rifle, which has a port accepting the ammo pack.')
    microMissiles_ammoEfficient = WeaponModPerk(
        name = 'microMissiles_ammoEfficient',
        fName = 'Ammo Efficient',
        applicableWeapon = 'heavyAssaultRifle',
        applicableMod = 'microMissiles',
        path = '"perk/zion/player/sp/weapons/heavy_rifle_heavy_ar/burst_detonate_lower_ammo_cost"',
        description = 'Decreased ammo usage.')
    microMissiles_advancedLoader = WeaponModPerk(
        name = 'microMissiles_advancedLoader',
        fName = 'Advanced Loader',
        applicableWeapon = 'heavyAssaultRifle',
        applicableMod = 'microMissiles',
        path = '"perk/zion/player/sp/weapons/heavy_rifle_heavy_ar/burst_detonate_faster_recharge"',
        description = 'Improved reload time.')
    microMissiles_quickLauncher = WeaponModPerk(
        name = 'microMissiles_quickLauncher',
        fName = 'Quick Launcher',
        applicableWeapon = 'heavyAssaultRifle',
        applicableMod = 'microMissiles',
        path = '"perk/zion/player/sp/weapons/heavy_rifle_heavy_ar/burst_detonate_faster_charge_time"',
        description = 'The micro missile mod can be activated instantaneously.')
    microMissiles_bottomlessMissiles_mastery = WeaponModPerk(
        name = 'microMissiles_bottomlessMissiles_mastery',
        fName = 'MASTERY: Bottomless Missiles',
        applicableWeapon = 'heavyAssaultRifle',
        applicableMod = 'microMissiles',
        path = '"perk/zion/player/sp/weapons/heavy_rifle_heavy_ar/burst_detonate_mastery"',
        description = 'Missiles can be continuously fired without a reload.')
    
    # PLASMA RIFLE
    # plasma rifle: heat blast + upgrades
    heatBlast = WeaponModPerk(
        name = 'heatBlast',
        fName = 'Heat Blast',
        applicableWeapon = 'plasmaRifle',
        applicableMod = 'isBaseMod',
        path = '"perk/zion/player/sp/weapons/plasma_rifle/secondary_aoe"',
        description = 'An attachment for the muzzle of the plasma rifle, this unit collects heat into a copper crucible,\n' 
        + 'and can release it via transfer to a diffusion chamber. The resulting wave can knock back targets\n' 
        + 'and causes damage over a small range. Normal use of the weapon will recharge this module.\n' 
        + 'The UAC recommends use of protective gear by the operator when using this device.')
    heatBlast_superHeatedRounds = WeaponModPerk(
        name = 'heatBlast_superHeatedRounds',
        fName = 'Super Heated Rounds',
        applicableWeapon = 'plasmaRifle',
        applicableMod = 'heatBlast',
        path = '"perk/zion/player/sp/weapons/plasma_rifle/secondary_aoe_faster_charge"',
        description = 'Shots build heat faster.')
    heatBlast_improvedVenting = WeaponModPerk(
        name = 'heatBlast_improvedVenting',
        fName = 'Improved Venting',
        applicableWeapon = 'plasmaRifle',
        applicableMod = 'heatBlast',
        path = '"perk/zion/player/sp/weapons/plasma_rifle/secondary_aoe_faster_recovery"',
        description = 'Decreases recovery time between heat blast shots.')
    heatBlast_expandedThreshold = WeaponModPerk(
        name = 'heatBlast_expandedThreshold',
        fName = 'Expanded Threshold',
        applicableWeapon = 'plasmaRifle',
        applicableMod = 'heatBlast',
        path = '"perk/zion/player/sp/weapons/plasma_rifle/secondary_aoe_more_damage"',
        description = 'The heat meter maximum is increased, allowing a higher range of damage.')  
    heatBlast_heatedCore_mastery = WeaponModPerk(
        name = 'heatBlast_heatedCore_mastery',
        fName = 'MASTERY: Heated Core',
        applicableWeapon = 'plasmaRifle',
        applicableMod = 'heatBlast',
        path = '"perk/zion/player/sp/weapons/plasma_rifle/secondary_aoe_mastery"',
        description = 'The heat meter is automatically charged over time, taking about 10 seconds to fully charge, and can even charge when in your inventory.')  
    
    # plasma rifle: stun bomb + upgrades
    stunBomb = WeaponModPerk(
        name = 'stunBomb',
        fName = 'Stun Bomb',
        applicableWeapon = 'plasmaRifle',
        applicableMod = 'isBaseMod',
        path = '"perk/zion/player/sp/weapons/plasma_rifle/secondary_stun"',
        description = 'A modification which combines multiple shots into a single larger projectile.\n' 
        + 'It is said to generate Birkeland currents, a phenomenon associated with intense magnetic fields,\n' 
        + 'via exceeding the "Franheiser limit," an apparently novel discovery in physics by the UAC.\n' 
        + 'It stuns targets within the discharge radius for several seconds with its electromagnetic effects.\n' 
        + 'It requires a cool-down period between firings.')
    stunBomb_quickRecharge = WeaponModPerk(
        name = 'stunBomb_quickRecharge',
        fName = 'Quick Recharge',
        applicableWeapon = 'plasmaRifle',
        applicableMod = 'stunBomb',
        path = '"perk/zion/player/sp/weapons/plasma_rifle/secondary_stun_faster_recharge"',
        description = 'Decreases cool-down time between stun bombs.')
    stunBomb_bigShock = WeaponModPerk(
        name = 'stunBomb_bigShock',
        fName = 'Big Shock',
        applicableWeapon = 'plasmaRifle',
        applicableMod = 'stunBomb',
        path = '"perk/zion/player/sp/weapons/plasma_rifle/secondary_stun_larger_radius"',
        description = 'Stun bombs have an increased area of effect.')
    stunBomb_largerStun = WeaponModPerk(
        name = 'stunBomb_largerStun',
        fName = 'Larger Stun',
        applicableWeapon = 'plasmaRifle',
        applicableMod = 'stunBomb',
        path = '"perk/zion/player/sp/weapons/plasma_rifle/secondary_stun_longer_stun"',
        description = 'The stagger induced by a stun bomb detonation lasts longer.')    
    stunBomb_chainStun_mastery = WeaponModPerk(
        name = 'stunBomb_chainStun_mastery',
        fName = 'MASTERY: Chain Stun',
        applicableWeapon = 'plasmaRifle',
        applicableMod = 'stunBomb',
        path = '"perk/zion/player/sp/weapons/plasma_rifle/secondary_stun_mastery"',
        description = 'Enemies killed while in the staggered state will explode with secondary stun bombs.')   
    
    # ROCKET LAUNCHER
    # rocket launcher: lock-on burst + upgrades
    lockOnBurst = WeaponModPerk(
        name = 'lockOnBurst',
        fName = 'Lock-On Burst',
        applicableWeapon = 'rocketLauncher',
        applicableMod = 'isBaseMod',
        path = '"perk/zion/player/sp/weapons/rocket_launcher/lock_on"',
        description = 'Though all UAC-produced rockets are fit with guidance capabilities, they are inactive by default\n' 
        + 'as a controlling guidance system is also required. This modification adds an activator for that system,\n' 
        + 'allowing the ordinary rockets to become self-guided homing missiles. This unit provides a lock-on laser\n' 
        + 'for painting the desired target, and modifies the firing characteristics of the weapon such that three rockets\n' 
        + 'will be launched in a quick series. The rockets will navigate to the desired target using built-in motors in their\n' 
        + 'fin assemblies. Lock-on burst rockets do approximately one-third as much damage as a normal rocket.')
    lockOnBurst_quickLock = WeaponModPerk(
        name = 'lockOnBurst_quickLock',
        fName = 'Quick Lock',
        applicableWeapon = 'rocketLauncher',
        applicableMod = 'lockOnBurst',
        path = '"perk/zion/player/sp/weapons/rocket_launcher/lockon_decrease_lock_time"',
        description = 'The time taken to acquire a lock-on is reduced.')
    lockOnBurst_fasterRecovery= WeaponModPerk(
        name = 'lockOnBurst_fasterRecovery',
        fName = 'Faster Recovery',
        applicableWeapon = 'rocketLauncher',
        applicableMod = 'lockOnBurst',
        path = '"perk/zion/player/sp/weapons/rocket_launcher/lockon_faster_recovery"',
        description = 'Recovery time is reduced, allowing a new lock-on to be acquired faster.')
    lockOnBurst_multiTargeting_mastery = WeaponModPerk(
        name = 'lockOnBurst_multiTargeting_mastery',
        fName = 'MASTERY: Multi-Targeting',
        applicableWeapon = 'rocketLauncher',
        applicableMod = 'lockOnBurst',
        path = '"perk/zion/player/sp/weapons/rocket_launcher/lockon_mastery"',
        description = 'Up to three targets can be locked onto simultaneously. Fired rockets will be split between the targets.')    

    # rocket launcher: remote detonation + upgrades
    remoteDetonation = WeaponModPerk(
        name = 'remoteDetonation',
        fName = 'Remote Detonation',
        applicableWeapon = 'rocketLauncher',
        applicableMod = 'isBaseMod',
        path = '"perk/zion/player/sp/weapons/rocket_launcher/detonate"',
        description = 'The remote detonator allows rockets to be exploded before impact during flight, in case the primary target\n' 
        + 'has been missed or is not in a prime location to be otherwise struck by the projectile\'s blast. It functions by covering \n' 
        + 'outgoing missiles\' fuses with a nano-fiber membrane containing a graphite weave combined with explosives.\n' 
        + 'An attached wireless receiver then overrides the missile\'s impact fuse at the weapon wielder\'s command.\n' 
        + 'Notably, there are no safety interlocks to prevent detonation at short range, so the operator must be cautious.')
    remoteDetonation_improvedWarhead = WeaponModPerk(
        name = 'remoteDetonation_improvedWarhead',
        fName = 'Improved Warhead',
        applicableWeapon = 'rocketLauncher',
        applicableMod = 'remoteDetonation',
        path = '"perk/zion/player/sp/weapons/rocket_launcher/detonate_larger_damage_radius"',
        description = 'The area-of-effect damage of remote detonated missiles is increased.')
    remoteDetonation_jaggedShrapnel = WeaponModPerk(
        name = 'remoteDetonation_jaggedShrapnel',
        fName = 'Jagged Shrapnel',
        applicableWeapon = 'rocketLauncher',
        applicableMod = 'remoteDetonation',
        path = '"perk/zion/player/sp/weapons/rocket_launcher/detonate_dot_undead"',
        description = 'Remote detonated missiles explode with shrapnel which causes bleed damage.')
    remoteDetonation_externalPayload_mastery = WeaponModPerk(
        name = 'remoteDetonation_externalPayload_mastery',
        fName = 'MASTERY: External Payload',
        applicableWeapon = 'rocketLauncher',
        applicableMod = 'remoteDetonation',
        path = '"perk/zion/player/sp/weapons/rocket_launcher/detonate_mastery"',
        description = 'Remote detonation of a missile will not cause the missile to be destroyed,\n' 
        + 'effectively allowing it to hit a target twice.')
    
    # GAUSS CANNON
    # gauss cannon: precision bolt + upgrades
    precisionBolt = WeaponModPerk(
        name = 'precisionBolt',
        fName = 'Precision Bolt',
        applicableWeapon = 'gaussCannon',
        applicableMod = 'isBaseMod',
        path = '"perk/zion/player/sp/weapons/gauss_cannon/charged_sniper"',
        description = 'The precision bolt modification adds a telescopic sight, increasing long-range accuracy.\n' 
        + 'The modification also provides the ability to accumulate additional charge while using the scope,\n' 
        + 'releasing the projectile at a higher velocity. A fully charged flechette can pierce multiple targets.')
    precisionBolt_energyEfficient = WeaponModPerk(
        name = 'precisionBolt_energyEfficient',
        fName = 'Energy Efficient',
        applicableWeapon = 'gaussCannon',
        applicableMod = 'precisionBolt',
        path = '"perk/zion/player/sp/weapons/gauss_cannon/charged_sniper_reduced_max_charge"',
        description = 'Decreases recharge time.')
    precisionBolt_lightWeight = WeaponModPerk(
        name = 'precisionBolt_lightWeight',
        fName = 'Light Weight',
        applicableWeapon = 'gaussCannon',
        applicableMod = 'precisionBolt',
        path = '"perk/zion/player/sp/weapons/gauss_cannon/charged_sniper_no_movement_penalty"',
        description = 'Increased movement speed while zoomed in.')
    precisionBolt_volatileDischarge_mastery = WeaponModPerk(
        name = 'precisionBolt_volatileDischarge_mastery',
        fName = 'MASTERY: Volatile Discharge',
        applicableWeapon = 'gaussCannon',
        applicableMod = 'precisionBolt',
        path = '"perk/zion/player/sp/weapons/gauss_cannon/charged_sniper_mastery"',
        description = 'Enemies killed with the precision bolt will explode.')
    
    # gauss cannon: siege mode + upgrades
    siegeMode = WeaponModPerk(
        name = 'siegeMode',
        fName = 'Siege Mode',
        applicableWeapon = 'gaussCannon',
        applicableMod = 'isBaseMod',
        path = '"perk/zion/player/sp/weapons/gauss_cannon/siege_mode"',
        description = 'The siege mode modification consists of an argon gas ionizer and vacuum seal to the weapon\'s launch chamber.\n' 
        + 'The ionized gas is released as plasma when the weapon is fired, adding a beam effect to the kinetic projectile.\n' 
        + 'The user must stay stationary when charging this firing mode due to the volatile gas. Aside from piercing\n' 
        + 'multiple targets, the beam will also create a blast effect upon impact.')
    siegeMode_outerBeam = WeaponModPerk(
        name = 'siegeMode_outerBeam',
        fName = 'Outer Beam',
        applicableWeapon = 'gaussCannon',
        applicableMod = 'siegeMode',
        path = '"perk/zion/player/sp/weapons/gauss_cannon/siege_mode_outer_beam"',
        description = 'Increases the area-of-effect damage for siege mode shots.')
    siegeMode_reducedCharge = WeaponModPerk(
        name = 'siegeMode_reducedCharge',
        fName = 'Reduced Charge',
        applicableWeapon = 'gaussCannon',
        applicableMod = 'siegeMode',
        path = '"perk/zion/player/sp/weapons/gauss_cannon/siege_mode_reduced_charge_time"',
        description = 'Decreases charging time.')
    siegeMode_mobileSiege_mastery = WeaponModPerk(
        name = 'siegeMode_mobileSiege_mastery',
        fName = 'MASTERY: Mobile Siege',
        applicableWeapon = 'gaussCannon',
        applicableMod = 'siegeMode',
        path = '"perk/zion/player/sp/weapons/gauss_cannon/siege_mode_mastery"',
        description = 'Enables movement while charging.')
    
    # CHAINGUN
    # chaingun: gatling rotator + upgrades
    gatlingRotator = WeaponModPerk(
        name = 'gatlingRotator',
        fName = 'Gatling Rotator',
        applicableWeapon = 'chaingun',
        applicableMod = 'isBaseMod',
        path = '"perk/zion/player/sp/weapons/chaingun/gatling"',
        description = 'This unapproved third-party modification to the chaingun overrides the release mechanism of the firing crucible,\n' 
        + 'enabling the chaingun to spin up to maximum speed without previously firing for greater efficiency. ')
    gatlingRotator_improvedTorque = WeaponModPerk(
        name = 'gatlingRotator_improvedTorque',
        fName = 'Improved Torque',
        applicableWeapon = 'chaingun',
        applicableMod = 'gatlingRotator',
        path = '"perk/zion/player/sp/weapons/chaingun/gatling_faster_spinup"',
        description = 'Decreases spin-up time.')
    gatlingRotator_uraniumCoating = WeaponModPerk(
        name = 'gatlingRotator_uraniumCoating',
        fName = 'Uranium Coating',
        applicableWeapon = 'chaingun',
        applicableMod = 'gatlingRotator',
        path = '"perk/zion/player/sp/weapons/chaingun/gatling_penetration"',
        description = 'Shots penetrate enemies.')   
    gatlingRotator_incendiaryRounds_mastery = WeaponModPerk(
        name = 'gatlingRotator_incendiaryRounds_mastery',
        fName = 'MASTERY: Incendiary Rounds',
        applicableWeapon = 'chaingun',
        applicableMod = 'gatlingRotator',
        path = '"perk/zion/player/sp/weapons/chaingun/gatling_mastery"',
        description = 'Bullets will do more damage once maximum firing rate is reached.')   
    
    # chaingun: mobile turret + upgrades
    mobileTurret = WeaponModPerk(
        name = 'mobileTurret',
        fName = 'Mobile Turret',
        applicableWeapon = 'chaingun',
        applicableMod = 'isBaseMod',
        path = '"perk/zion/player/sp/weapons/chaingun/turret"',
        description = 'This modification adds another crucible and compression piston chamber, doubling the weapon\'s\n' 
        + 'firing rate by using all three of the barrel clusters simultaneously. While more accurate and extremely \n' 
        + 'powerful, it expends ammunition at an amazing rate, slows the user down significantly, and runs the risk\n' 
        + 'of overheating the weapon if fired for too long, requiring a long cool-down period to be endured after its use.')
    mobileTurret_rapidDeployment = WeaponModPerk(
        name = 'mobileTurret_rapidDeployment',
        fName = 'Rapid Deployment',
        applicableWeapon = 'chaingun',
        applicableMod = 'mobileTurret',
        path = '"perk/zion/player/sp/weapons/chaingun/turret_faster_equip"',
        description = 'Decreases transformation time of turret.')
    mobileTurret_uraniumCoating = WeaponModPerk(
        name = 'mobileTurret_uraniumCoating',
        fName = 'Uranium Coating',
        applicableWeapon = 'chaingun',
        applicableMod = 'mobileTurret',
        path = '"perk/zion/player/sp/weapons/chaingun/turret_penetration"',
        description = 'Shots penetrate enemies.')
    mobileTurret_ultimateCooling_mastery = WeaponModPerk(
        name = 'mobileTurret_ultimateCooling_mastery',
        fName = 'MASTERY: Ultimate Cooling',
        applicableWeapon = 'chaingun',
        applicableMod = 'mobileTurret',
        path = '"perk/zion/player/sp/weapons/chaingun/turret_mastery"',
        description = 'The weapon can no longer overheat.')


@dataclass
class Ammo(InventoryModule):
    """ Represents a collection of possible/available AmmoItems. """
    
    # metadata
    moduleName: str = 'Ammo'
    elementType: object = AmmoItem
    
    fuel = AmmoItem('fuel', '"ammo/zion/sharedammopool/fuel"', count = 99)
    shells = AmmoItem('shells', '"ammo/zion/sharedammopool/shells"', count = 99)
    bullets = AmmoItem('bullets', '"ammo/zion/sharedammopool/bullets"', count = 999)
    cells = AmmoItem('cells', '"ammo/zion/sharedammopool/cells"', count = 999)
    rockets = AmmoItem('rockets', '"ammo/zion/sharedammopool/rockets"', count = 99)
    bfg = AmmoItem('bfg', '"ammo/zion/sharedammopool/bfg"', count = 99)
"""
modulles.py: 
- represent a grouping of inventory data
- modules consist of InventoryEntries
- if these entries are added to their module's Available list, the player starts with them
- note: the typo in 'enviroment' is present in id's source, and so is here intentionally
"""

from datalib.elements import *


@dataclass
class InventoryModule(metaclass = abc.ABCMeta):
    """ 
    Abstract base class representing a grouping of similar inventory entries.
    All possible entries are defined as members, with entires in the 'available' list
    being added to the player's starting inventory (some of which are added by default).
    """

    # metadata
    moduleName: str
    elementType: object
    
    # entries to add to starting inventory loadout
    available: list[InventoryElement] = field(default_factory = list)

    def updateModuleData(self):
        """ Updates module's data dictionary attribute based on member variables. """
        
        for each in self.available:
            each.updateData()
            
    def addToAvailable(self, inventoryElementName: str):
        """ Adds an entry to module's available pool, if validated. """
        
        if hasattr(self, inventoryElementName):
            element = getattr(self, inventoryElementName)
            if type(element) is self.elementType and element not in self.available:
                self.available.append(element)


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
        path = '"perk/zion/player/sp/enviroment_suit/modify_enviromental_damage_1"',
        description = 'Damage taken from explosive barrels and environmental sources is reduced.')
    selfPreservation = PraetorPerk(
        name = 'selfPreservation', 
        path = '"perk/zion/player/sp/enviroment_suit/modify_enviromental_damage_2"',
        description = 'Self-inflicted damage from weapons is reduced.')
    barrelsOFun = PraetorPerk(
        name = 'barrelsOFun', 
        path = '"perk/zion/player/sp/enviroment_suit/modify_enviromental_damage_3"',
        description = 'Immunity to damage from explosive barrels.')

    # area-scanning technology
    itemAwareness = PraetorPerk(
        name = 'itemAwareness', 
        path = '"perk/zion/player/sp/enviroment_suit/automap_1"',
        description = 'The automap reveals exploration items in a wider radius.',
        unlockable = '"researchprojects/find_collectibles_1"')
    secretSense = PraetorPerk(
        name = 'selfPreservation', 
        path = '"perk/zion/player/sp/enviroment_suit/automap_2"',
        description = 'The automap compass pulses when nearby a secret.')
    fullView = PraetorPerk(
        name = 'fullView', 
        path = '"perk/zion/player/sp/enviroment_suit/automap_3"',
        description = 'Exploration items are automatically displayed.')
    
    # equipment system
    quickCharge = PraetorPerk(
        name = 'quickCharge', 
        path = '"perk/zion/player/sp/enviroment_suit/equipment_1"',
        description = 'Equipment recharge duration is reduced.',
        unlockable = '"researchprojects/equipment_1"')
    stockUp = PraetorPerk(
        name = 'stockUp', 
        path = 'perk/zion/player/sp/enviroment_suit/equipment_2',
        description = 'The total number of equipment charges is increased.')
    rapidCharge = PraetorPerk(
        name = 'rapidCharge', 
        path = 'perk/zion/player/sp/enviroment_suit/equipment_3',
        description = 'Recharge duration is further reduced.')
    
    # powerup effectiveness
    powerSurge = PraetorPerk(
        name = 'powerSurge', 
        path = '"perk/zion/player/sp/enviroment_suit/powerup_shockwave"',
        description = 'A blast wave is unleashed when a power-up expires.')
    healingPower = PraetorPerk(
        name = 'healingPower', 
        path = '"perk/zion/player/sp/enviroment_suit/powerup_health"',
        description = 'Health is restored to maximum when a power-up is activated.')
    powerExtender = PraetorPerk(
        name = 'powerExtender', 
        path = '"perk/zion/player/sp/enviroment_suit/modify_powerup_duration"',
        description = 'Power-up durations are increased.')
    
    # dexterity
    adept = PraetorPerk(
        name = 'adept', 
        path = '"perk/zion/player/sp/enviroment_suit/dexterity_increase_1"',
        description = 'Weapon changing time is reduced.')
    quickHands = PraetorPerk(
        name = 'quickHands', 
        path = '"perk/zion/player/sp/enviroment_suit/dexterity_increase_2"',
        description = 'Ledge grabbing speed is increased.')
    hotSwap = PraetorPerk(
        name = 'hotSwap', 
        path = '"perk/zion/player/sp/enviroment_suit/dexterity_increase_3"',
        description = 'Weapon modification swap time is reduced.')

@dataclass
class Runes(InventoryModule):
    """ Represent a collection of possible/available RunePerks. """
    
    # metadata
    moduleName: str = 'Runes'
    elementType: object = RunePerk
    
    def setIsUpgraded(self, runeName: str, isUpgraded: bool):
        """ Sets corresponding rune's applyUpgradesForPerk value, if validated. """
        
        rune = getattr(self, runeName)
        if isinstance(rune, RunePerk):
            rune.applyUpgradesForPerk = isUpgraded  
            
    def setIsPermanent(self, runeName: str, isPermanent: bool):
        """ Adds corresponding rune to available pool as permanently equipped (not taking up a slot), if validated. """
        
        rune = getattr(self, runeName)
        if isinstance(rune, RunePerk):
            self.addToAvailable(runeName)
            rune.runePermanentEquip = isPermanent         
    
    vacuum = RunePerk(
        name = 'vacuum', 
        path = '"perk/zion/player/sp/enviroment_suit/increase_drop_radius"',
        description = 'Increases the range for absorbing dropped items.',
        upgradeDescription = 'Further increases the range for absorbing dropped items.')
    
    dazedAndConfused = RunePerk(
        name = 'dazedAndConfusedRune', 
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
    
    doubleJumpThrustBoots = EquipmentItem('doubleJumpThrustBoots',  "jumpboots/base", equip = True)
    fragGrenade = EquipmentItem('fragGrenade', '"throwable/zion/player/sp/frag_grenade"', equip = True)
    decoyHologram = EquipmentItem('decoyHologram', '"decoyhologram/equipment"')
    siphonGrenade = EquipmentItem('siphonGrenade', '"throwable/zion/player/sp/siphon_grenade"')
     
        
@dataclass
class Weapons(InventoryModule):
    """ Represents a collection of possible/available WeaponItems. """
    
    # metadata
    moduleName: str = 'Weapons'
    elementType: object = WeaponItem
    
    fists = WeaponItem('fists', '"weapon/zion/player/sp/fists"')
    chainsaw = WeaponItem('chainsaw', '"weapon/zion/player/sp/chainsaw"')
    pistol = WeaponItem('pistol', '"weapon/zion/player/sp/pistol"', equip = True)
    combatShotgun = WeaponItem('combatShotgun', '"weapon/zion/player/sp/shotgun"')
    heavyAssaultRifle = WeaponItem('heavyAssaultRifle', '"weapon/zion/player/sp/heavy_rifle_heavy_ar"', equipReserve = True)
    plasmaRifle = WeaponItem('plasmaRifle', '"weapon/zion/player/sp/plasma_rifle"')
    rocketLauncher = WeaponItem('rocketLauncher', '"weapon/zion/player/sp/rocket_launcher"')
    superShotgun = WeaponItem('superShotgun', '"weapon/zion/player/sp/double_barrel"')
    gaussCannon = WeaponItem('gaussCannon', "weapon/zion/player/sp/gauss_rifle")
    chaingun = WeaponItem('chaingun', '"weapon/zion/player/sp/chaingun"')
    bfg9000 = WeaponItem('bfg9000', "weapon/zion/player/sp/bfg")

    # TODO: figure out what '"summonweapon/base"' is and when/why it needs to be included; it's before the BFG is added in a full loadout decl
    #summonWeapon = WeaponItem('summonWeapon', '"summonweapon/base"')
    
    def __post_init__(self) -> None:
        """ Adds default starting armaments to available pool. """
        self.available = [self.fists, self.pistol]
    
    
@dataclass
class WeaponMods(InventoryModule):
    """ Represents a collection of possible/available WeaponModPerks. """

    # metadata
    moduleName: str = 'WeaponMods'
    elementType: object = WeaponModPerk
    
    # TODO: enforce weapon mods not being added by the user unless the weapon itself is as well (?)
    # TODO: enforce masteries not being added by the user unless all preceding upgrades are as well (?)
    
    def addToAvailable(self, applicableWeapon: str, modName: str):
        """ Adds an weapon mod to module's available pool, if validated."""
        if hasattr(self, modName):
            mod = getattr(self, modName)
            if mod.applicableWeapon == applicableWeapon and mod not in self.available:
                self.available.append(mod)
    
    # PISTOL upgrades (no mods)
    chargeEfficiency = WeaponModPerk(
        name = 'chargeEfficiency',
        applicableWeapon = 'pistol',
        path = '"perk/zion/player/sp/weapons/pistol/secondary_charge_shot_faster_charge"',
        description = 'Decreases charge time for a charged shot.')
    quickRecovery = WeaponModPerk(
        name = 'quickRecovery',
        applicableWeapon = 'pistol',
        path = '"perk/zion/player/sp/weapons/pistol/secondary_charge_shot_faster_discharge"',
        description = 'Decreases the cool-down time required after a charged shot.')
    lightWeight = WeaponModPerk(
        name = 'lightWeight',
        applicableWeapon = 'pistol',
        path = '"perk/zion/player/sp/weapons/pistol/secondary_charge_shot_no_movement_penalty"',
        description = 'Enables faster movement while charging.')
    increasedPowerMastery = WeaponModPerk(
        name = 'increasedPowerMastery',
        applicableWeapon = 'pistol',
        path = '"perk/zion/player/sp/weapons/pistol/secondary_charge_shot_higher_damage',
        description = 'Charged shots do more damage.')
    
    # COMBAT SHOTGUN
    # combat shotgun: charged burst + upgrades
    chargedBurst = WeaponModPerk(
        name = 'chargedBurst',
        applicableWeapon = 'combatShotgun',
        path = '"perk/zion/player/sp/weapons/shotgun/secondary_charge_burst"',
        description = 'An Argent-charged compression reloader fires off a volley of three shells in a quick succession. The compression reloader component used to drive this fast firing is powered by Argent energy, and requires a cool down period after use.')
    chargedBurst_speedyRecovery = WeaponModPerk(
        name = 'chargedBurst_speedyRecovery',
        applicableWeapon = 'combatShotgun',
        path = 'perk/zion/player/sp/weapons/shotgun/secondary_charge_burst_faster_recharge',
        description = 'Decreases recharge time of the mod.')
    chargedBurst_rapidFire = WeaponModPerk(
        name = 'chargedBurst_rapidFire',
        applicableWeapon = 'combatShotgun',
        path = '"perk/zion/player/sp/weapons/shotgun/secondary_charge_burst_faster_fire_rate"',
        description = 'Increases rate of fire of the mod.')
    chargedBurst_quickLoad = WeaponModPerk(
        name = 'chargedBurst_quickLoad',
        applicableWeapon = 'combatShotgun',
        path = '"perk/zion/player/sp/weapons/shotgun/secondary_charge_burst_faster_charge"',
        description = 'Decreases loading time of the mod. ')
    chargedBurst_powerShot_mastery = WeaponModPerk(
        name = 'chargedBurst_powerShot_mastery',
        applicableWeapon = 'combatShotgun',
        path = '"perk/zion/player/sp/weapons/shotgun/secondary_charge_burst_mastery"',
        description = 'Successfully hitting all three shots of a charged burst will increase the damage of the next one. The effect does not stack.')
    
    # combat shotgun: explosive shot + upgrades
    explosiveShot = WeaponModPerk(
        name = 'explosiveShot',
        applicableWeapon = 'combatShotgun',
        path = '"perk/zion/player/sp/weapons/shotgun/pop_rocket"',
        description = 'An alternate ammunition for the combat shotgun based on octanitrocubane explosive and a glycerin fuse. Shot embedded in the explosive is dispersed upon impact, creating an effect similar to the frag grenade, damaging targets over a wide area. This extends the weapon\'s utility against multiple targets.')
    explosiveShot_speedyRecovery = WeaponModPerk(
        name = 'explosiveShot_speedyRecovery',
        applicableWeapon = 'combatShotgun',
        path = '"perk/zion/player/sp/weapons/shotgun/pop_rocket_faster_recharge"',
        description = 'Decreases recharge time of the mod.')
    explosiveShot_biggerBoom = WeaponModPerk(
        name = 'explosiveShot_biggerBoom',
        applicableWeapon = 'combatShotgun',
        path = '"perk/zion/player/sp/weapons/shotgun/pop_rocket_larger_explosion"',
        description = 'Increases the area of effect.')
    explosiveShot_instantLoad = WeaponModPerk(
        name = 'explosiveShot_instantLoad',
        applicableWeapon = 'combatShotgun',
        path = '"perk/zion/player/sp/weapons/shotgun/pop_rocket_faster_charge"',
        description = 'Removes loading time of the mod.')
    explosiveShot_clusterStrike_mastery = WeaponModPerk(
        name = 'explosiveShot_clusterStrike_mastery',
        applicableWeapon = 'combatShotgun',
        path = 'perk/zion/player/sp/weapons/shotgun/pop_rocket_mastery',
        description = 'Cluster bombs will spawn upon a direct impact on a demon providing further damage.')
    
    # SUPER SHOTGUN upgrades (no mods)
    fasterReload = WeaponModPerk(
        name = 'fasterReload',
        applicableWeapon = 'superShotgun',
        path = '"perk/zion/player/sp/weapons/double_barrel/default_faster_reload"',
        description = 'Decrease time to reload.')
    uraniumCoating = WeaponModPerk(
        name = 'uraniumCoating',
        applicableWeapon = 'superShotgun',
        path = '"perk/zion/player/sp/weapons/double_barrel/default_bullet_penetration"',
        description = 'Shots penetrate through targets.')
    doubleTrouble_mastery = WeaponModPerk(
        name = 'doubleTrouble_mastery',
        applicableWeapon = 'superShotgun',
        path = '"perk/zion/player/sp/weapons/double_barrel/mastery"',
        description = 'Fire twice before having to reload.')
    
    # HEAVY ASSAULT RIFLE
    # heavy assault rifle: tactical scope + upgrades
    tacticalScope = WeaponModPerk(
        name = 'tacticalScope',
        applicableWeapon = 'heavyAssaultRifle',
        path = '"perk/zion/player/sp/weapons/heavy_rifle_heavy_ar/zoom"',
        description = '')
    tacticalScope_uraniumCoating = WeaponModPerk(
        name = 'tacticalScope_uraniumCoating',
        applicableWeapon = 'heavyAssaultRifle',
        path = '"perk/zion/player/sp/weapons/heavy_rifle_heavy_ar/zoom_bullet_penetration"',
        description = '')
    tacticalScope_skullCracker = WeaponModPerk(
        name = 'tacticalScope_skullCracker',
        applicableWeapon = 'heavyAssaultRifle',
        path = '"perk/zion/player/sp/weapons/heavy_rifle_heavy_ar/zoom_more_headshot_damage"',
        description = '')
    tacticalScope_lightWeight = WeaponModPerk(
        name = 'tacticalScope_lightWeight',
        applicableWeapon = 'heavyAssaultRifle',
        path = '"perk/zion/player/sp/weapons/heavy_rifle_heavy_ar/zoom_no_movement_penalty"',
        description = '')
    tacticalScope_devastatorRounds_mastery = WeaponModPerk(
        name = 'tacticalScope_devastatorRounds_mastery',
        applicableWeapon = 'heavyAssaultRifle',
        path = '"perk/zion/player/sp/weapons/heavy_rifle_heavy_ar/zoom_mastery"',
        description = '')
    
    # heavy assault rifle: micro missiles + upgrades
    microMissiles = WeaponModPerk(
        name = 'microMissiles',
        applicableWeapon = 'heavyAssaultRifle',
        path = '"perk/zion/player/sp/weapons/heavy_rifle_heavy_ar/burst_detonate"',
        description = '')
    microMissiles_ammoEfficient = WeaponModPerk(
        name = 'microMissiles_ammoEfficient',
        applicableWeapon = 'heavyAssaultRifle',
        path = '"perk/zion/player/sp/weapons/heavy_rifle_heavy_ar/burst_detonate_lower_ammo_cost"',
        description = '')
    microMissiles_advancedLoader = WeaponModPerk(
        name = 'microMissiles_advancedLoader',
        applicableWeapon = 'heavyAssaultRifle',
        path = '"perk/zion/player/sp/weapons/heavy_rifle_heavy_ar/burst_detonate_faster_recharge"',
        description = '')
    microMissiles_quickLauncher = WeaponModPerk(
        name = 'microMissiles_quickLauncher',
        applicableWeapon = 'heavyAssaultRifle',
        path = '"perk/zion/player/sp/weapons/heavy_rifle_heavy_ar/burst_detonate_faster_charge_time"',
        description = '')
    microMissiles_bottomlessMissles_mastery = WeaponModPerk(
        name = 'microMissiles_bottomlessMissles_mastery',
        applicableWeapon = 'heavyAssaultRifle',
        path = '"perk/zion/player/sp/weapons/heavy_rifle_heavy_ar/burst_detonate_mastery"',
        description = '')
    
    # PLASMA RIFLE
    # plasma rifle: heat blast + upgrades
    heatBlast = WeaponModPerk(
        name = 'heatBlast',
        applicableWeapon = 'plasmaRifle',
        path = '"perk/zion/player/sp/weapons/plasma_rifle/secondary_aoe"',
        description = '')
    heatBlast_superHeatedRounds = WeaponModPerk(
        name = 'heatBlast_superHeatedRounds',
        applicableWeapon = 'plasmaRifle',
        path = '"perk/zion/player/sp/weapons/plasma_rifle/secondary_aoe_faster_charge"',
        description = '')
    heatBlast_improvedVenting = WeaponModPerk(
        name = 'heatBlast_improvedVenting',
        applicableWeapon = 'plasmaRifle',
        path = '"perk/zion/player/sp/weapons/plasma_rifle/secondary_aoe_faster_recovery"',
        description = '')
    heatBlast_expandedThreshold = WeaponModPerk(
        name = 'heatBlast_expandedThreshold',
        applicableWeapon = 'plasmaRifle',
        path = '"perk/zion/player/sp/weapons/plasma_rifle/secondary_aoe_more_damage"',
        description = '')  
    heatBlast_heatedCore_mastery = WeaponModPerk(
        name = 'heatBlast_heatedCore_mastery',
        applicableWeapon = 'plasmaRifle',
        path = '"perk/zion/player/sp/weapons/plasma_rifle/secondary_aoe_mastery"',
        description = '')  
    
    # plasma rifle: stun bomb + upgrades
    stunBomb = WeaponModPerk(
        name = 'stunBomb',
        applicableWeapon = 'plasmaRifle',
        path = '"perk/zion/player/sp/weapons/plasma_rifle/secondary_stun"',
        description = '')
    stunBomb_quickRecharge = WeaponModPerk(
        name = 'stunBomb_quickRecharge',
        applicableWeapon = 'plasmaRifle',
        path = '"perk/zion/player/sp/weapons/plasma_rifle/secondary_stun_faster_recharge"',
        description = '')
    stunBomb_bigShock = WeaponModPerk(
        name = 'stunBomb_bigShock',
        applicableWeapon = 'plasmaRifle',
        path = '"perk/zion/player/sp/weapons/plasma_rifle/secondary_stun_larger_radius"',
        description = '')
    stunBomb_largerStun = WeaponModPerk(
        name = 'stunBomb_largerStun',
        applicableWeapon = 'plasmaRifle',
        path = '"perk/zion/player/sp/weapons/plasma_rifle/secondary_stun_longer_stun"',
        description = '')    
    stunBomb_chainStun_mastery = WeaponModPerk(
        name = 'stunBomb_chainStun_mastery',
        applicableWeapon = 'plasmaRifle',
        path = '"perk/zion/player/sp/weapons/plasma_rifle/secondary_stun_mastery"',
        description = '')   
    
    # ROCKET LAUNCHER
    # rocket launcher: lock-on burst + upgrades
    lockOnBurst = WeaponModPerk(
        name = 'lockOnBurst',
        applicableWeapon = 'rocketLauncher',
        path = '"perk/zion/player/sp/weapons/rocket_launcher/lock_on"',
        description = '')
    lockOnBurst_quickLock = WeaponModPerk(
        name = 'lockOnBurst_quickLock',
        applicableWeapon = 'rocketLauncher',
        path = '"perk/zion/player/sp/weapons/rocket_launcher/lockon_decrease_lock_time"',
        description = '')
    lockOnBurst_fasterRecovery= WeaponModPerk(
        name = 'lockOnBurst_fasterRecovery',
        applicableWeapon = 'rocketLauncher',
        path = '"perk/zion/player/sp/weapons/rocket_launcher/lockon_faster_recovery"',
        description = '')
    lockOnBurst_multiTargeting_mastery = WeaponModPerk(
        name = 'lockOnBurst_multiTargeting_mastery',
        applicableWeapon = 'rocketLauncher',
        path = '"perk/zion/player/sp/weapons/rocket_launcher/lockon_mastery"',
        description = '')    

    # rocket launcher: remote detonation + upgrades
    remoteDetonation = WeaponModPerk(
        name = 'remoteDetonation',
        applicableWeapon = 'rocketLauncher',
        path = '"perk/zion/player/sp/weapons/rocket_launcher/detonate"',
        description = '')
    remoteDetonation_improvedWarhead = WeaponModPerk(
        name = 'remoteDetonation_improvedWarhead',
        applicableWeapon = 'rocketLauncher',
        path = '"perk/zion/player/sp/weapons/rocket_launcher/detonate_larger_damage_radius"',
        description = '')
    remoteDetonation_jaggedShrapnel = WeaponModPerk(
        name = 'remoteDetonation_jaggedShrapnel',
        applicableWeapon = 'rocketLauncher',
        path = '"perk/zion/player/sp/weapons/rocket_launcher/detonate_dot_undead"',
        description = '')
    remoteDetonation_externalPayload_mastery = WeaponModPerk(
        name = 'remoteDetonation_externalPayload_mastery',
        applicableWeapon = 'rocketLauncher',
        path = '"perk/zion/player/sp/weapons/rocket_launcher/detonate_mastery"',
        description = '')
    
    # GAUSS CANNON
    # gauss cannon: precision bolt + upgrades
    precisionBolt = WeaponModPerk(
        name = 'precisionBolt',
        applicableWeapon = 'gaussCannon',
        path = '"perk/zion/player/sp/weapons/gauss_cannon/charged_sniper"',
        description = '')
    precisionBolt_energyEfficient = WeaponModPerk(
        name = 'precisionBolt_energyEfficient',
        applicableWeapon = 'gaussCannon',
        path = '"perk/zion/player/sp/weapons/gauss_cannon/charged_sniper_reduced_max_charge"',
        description = '')
    precisionBolt_lightWeight = WeaponModPerk(
        name = 'precisionBolt_lightWeight',
        applicableWeapon = 'gaussCannon',
        path = '"perk/zion/player/sp/weapons/gauss_cannon/charged_sniper_no_movement_penalty"',
        description = '')
    precisionBolt_volatileDischarge_mastery = WeaponModPerk(
        name = 'precisionBolt_volatileDischarge_mastery',
        applicableWeapon = 'gaussCannon',
        path = '"perk/zion/player/sp/weapons/gauss_cannon/charged_sniper_mastery"',
        description = '')
    
    # gauss cannon: siege mode + upgrades
    siegeMode = WeaponModPerk(
        name = 'siegeMode',
        applicableWeapon = 'gaussCannon',
        path = '"perk/zion/player/sp/weapons/gauss_cannon/siege_mode"',
        description = '')
    siegeMode_outerBeam = WeaponModPerk(
        name = 'siegeMode_outerBeam',
        applicableWeapon = 'gaussCannon',
        path = '"perk/zion/player/sp/weapons/gauss_cannon/siege_mode_outer_beam"',
        description = '')
    siegeMode_reducedCharge = WeaponModPerk(
        name = 'siegeMode_reducedCharge',
        applicableWeapon = 'gaussCannon',
        path = '"perk/zion/player/sp/weapons/gauss_cannon/siege_mode_reduced_charge_time";',
        description = '')
    siegeMode_mobileSiege_mastery = WeaponModPerk(
        name = 'siegeMode_mobileSiege_mastery',
        applicableWeapon = 'gaussCannon',
        path = '"perk/zion/player/sp/weapons/gauss_cannon/siege_mode_mastery"',
        description = '')
    
    # CHAINGUN
    # chaingun: gatling rotator + upgrades
    gatlingRotator = WeaponModPerk(
        name = 'gatlingRotator',
        applicableWeapon = 'chaingun',
        path = '"perk/zion/player/sp/weapons/chaingun/gatling"',
        description = '')
    gatlingRotator_improvedTorque = WeaponModPerk(
        name = 'gatlingRotator_improvedTorque',
        applicableWeapon = 'chaingun',
        path = '"perk/zion/player/sp/weapons/chaingun/gatling_faster_spinup"',
        description = '')
    gatlingRotator_uraniumCoating = WeaponModPerk(
        name = 'gatlingRotator_uraniumCoating',
        applicableWeapon = 'chaingun',
        path = '"perk/zion/player/sp/weapons/chaingun/gatling_penetration"',
        description = '')   
    gatlingRotator_incendiaryRounds_mastery = WeaponModPerk(
        name = 'gatlingRotator_incendiaryRounds_mastery',
        applicableWeapon = 'chaingun',
        path = '"perk/zion/player/sp/weapons/chaingun/gatling_mastery"',
        description = '')   
    
    # chaingun: mobile turret + upgrades
    mobileTurret = WeaponModPerk(
        name = 'mobileTurret',
        applicableWeapon = 'chaingun',
        path = '"perk/zion/player/sp/weapons/chaingun/turret"',
        description = '')
    mobileTurret_rapidDeployment = WeaponModPerk(
        name = 'mobileTurret_rapidDeployment',
        applicableWeapon = 'chaingun',
        path = '"perk/zion/player/sp/weapons/chaingun/turret_faster_equip"',
        description = '')
    mobileTurret_uraniumCoating = WeaponModPerk(
        name = 'mobileTurret_uraniumCoating',
        applicableWeapon = 'chaingun',
        path = '"perk/zion/player/sp/weapons/chaingun/turret_penetration"',
        description = '')
    mobileTurret_ultimateCooling_mastery = WeaponModPerk(
        name = 'mobileTurret_ultimateCooling_mastery',
        applicableWeapon = 'chaingun',
        path = '"perk/zion/player/sp/weapons/chaingun/turret_mastery"',
        description = '')


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
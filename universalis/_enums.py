from enum import IntEnum
from typing import ClassVar

__all__ = ("DataCenterEnum", "DataCenterToWorlds", "ItemQualityEnum", "LanguageEnum", "WorldEnum")


class LanguageEnum(IntEnum):
    en = 1
    de = 2
    ja = 3
    fr = 4


class DataCenterEnum(IntEnum):
    Unknown = 0
    Elemental = 1
    Gaia = 2
    Mana = 3
    Aether = 4
    Primal = 5
    Chaos = 6
    Light = 7
    Crystal = 8
    Materia = 9
    Meteor = 10
    Dynamis = 11
    Shadow = 12
    NA_Cloud_DC = 13
    Beta = 99
    Eorzea = 201
    Chocobo = 101
    Moogle = 102
    Fatcat = 103
    Shiba = 104
    UNK = 151


class ItemQualityEnum(IntEnum):
    """
    Enum for specifying Item Quality.

    Parameters
    -----------
    NQ = 0 |
    HQ = 1
    """

    NQ = 0
    HQ = 1


class WorldEnum(IntEnum):
    Ravana = 21
    Bismarck = 22
    Asura = 23
    Belias = 24
    Chaos = 25
    Hecatoncheir = 26
    Moomba = 27
    Pandaemonium = 28
    Shinryu = 29
    Unicorn = 30
    Yojimbo = 31
    Zeromus = 32
    Twintania = 33
    Brynhildr = 34
    Famfrit = 35
    Lich = 36
    Mateus = 37
    Shemhazai = 38
    Omega = 39
    Jenova = 40
    Zalera = 41
    Zodiark = 42
    Alexander = 43
    Anima = 44
    Carbuncle = 45
    Fenrir = 46
    Hades = 47
    Ixion = 48
    Kujata = 49
    Typhon = 50
    Ultima = 51
    Valefor = 52
    Exodus = 53
    Faerie = 54
    Lamia = 55
    Phoenix = 56
    Siren = 57
    Garuda = 58
    Ifrit = 59
    Ramuh = 60
    Titan = 61
    Diabolos = 62
    Gilgamesh = 63
    Leviathan = 64
    Midgardsormr = 65
    Odin = 66
    Shiva = 67
    Atomos = 68
    Bahamut = 69
    Chocobo = 70
    Moogle = 71
    Tonberry = 72
    Adamantoise = 73
    Coeurl = 74
    Malboro = 75
    Tiamat = 76
    Ultros = 77
    Behemoth = 78
    Cactuar = 79
    Cerberus = 80
    Goblin = 81
    Mandragora = 82
    Louisoix = 83
    UNK = 84
    Spriggan = 85
    Sephirot = 86
    Sophia = 87
    Zurvan = 88
    Aegis = 90
    Balmung = 91
    Durandal = 92
    Excalibur = 93
    Gungnir = 94
    Hyperion = 95
    Masamune = 96
    Ragnarok = 97
    Ridill = 98
    Sargatanas = 99
    Sagittarius = 400
    Phantom = 401
    Alpha = 402
    Raiden = 403
    Marilith = 404
    Seraph = 405
    Halicarnassus = 406
    Maduin = 407
    Cuchulainn = 408
    Kraken = 409
    Rafflesia = 410
    Golem = 411
    Titania = 412
    Innocence = 413
    Pixie = 414
    Tycoon = 415
    Wyvern = 416
    Lakshmi = 417
    Eden = 418
    Syldra = 419


class DataCenterToWorlds:
    Crystal: list[WorldEnum] = [  # noqa: RUF012
        WorldEnum.Balmung,
        WorldEnum.Brynhildr,
        WorldEnum.Coeurl,
        WorldEnum.Diabolos,
        WorldEnum.Goblin,
        WorldEnum.Malboro,
        WorldEnum.Mateus,
        WorldEnum.Zalera,
    ]
    Aether: list[WorldEnum] = [  # noqa: RUF012
        WorldEnum.Adamantoise,
        WorldEnum.Cactuar,
        WorldEnum.Faerie,
        WorldEnum.Gilgamesh,
        WorldEnum.Jenova,
        WorldEnum.Midgardsormr,
        WorldEnum.Sargatanas,
        WorldEnum.Siren,
    ]

    Dynamis: list[WorldEnum] = [  # noqa: RUF012
        WorldEnum.Cuchulainn,
        WorldEnum.Golem,
        WorldEnum.Halicarnassus,
        WorldEnum.Kraken,
        WorldEnum.Maduin,
        WorldEnum.Marilith,
        WorldEnum.Rafflesia,
        WorldEnum.Seraph,
    ]

    Primal: list[WorldEnum] = [  # noqa: RUF012
        WorldEnum.Behemoth,
        WorldEnum.Excalibur,
        WorldEnum.Exodus,
        WorldEnum.Famfrit,
        WorldEnum.Hyperion,
        WorldEnum.Lamia,
        WorldEnum.Leviathan,
        WorldEnum.Ultros,
    ]
    __data_centers__: ClassVar[list[str]] = ["Crystal", "Aether", "Dynamis", "Primal"]

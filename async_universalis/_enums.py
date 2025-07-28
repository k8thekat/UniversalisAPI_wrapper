"""Copyright (C) 2021-2024 Katelynn Cadwallader.

This file is part of Kuma Kuma.

Universalis API wrapper is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3, or (at your option)
any later version.

Universalis API wrapper is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public
License for more details.

You should have received a copy of the GNU General Public License
along with Universalis API wrapper; see the file COPYING.  If not, write to the Free
Software Foundation, 51 Franklin Street - Fifth Floor, Boston, MA
02110-1301, USA.
"""

from enum import IntEnum
from typing import ClassVar

__all__ = ("DataCenter", "DataCenterToWorlds", "ItemQuality", "Language", "World")


class Language(IntEnum):
    en = 1
    de = 2
    ja = 3
    fr = 4


class DataCenter(IntEnum):
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


class ItemQuality(IntEnum):
    NQ = 0
    HQ = 1


class World(IntEnum):
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
    Crystal: list[World] = [  # noqa: RUF012
        World.Balmung,
        World.Brynhildr,
        World.Coeurl,
        World.Diabolos,
        World.Goblin,
        World.Malboro,
        World.Mateus,
        World.Zalera,
    ]
    Aether: list[World] = [  # noqa: RUF012
        World.Adamantoise,
        World.Cactuar,
        World.Faerie,
        World.Gilgamesh,
        World.Jenova,
        World.Midgardsormr,
        World.Sargatanas,
        World.Siren,
    ]

    Dynamis: list[World] = [  # noqa: RUF012
        World.Cuchulainn,
        World.Golem,
        World.Halicarnassus,
        World.Kraken,
        World.Maduin,
        World.Marilith,
        World.Rafflesia,
        World.Seraph,
    ]

    Primal: list[World] = [  # noqa: RUF012
        World.Behemoth,
        World.Excalibur,
        World.Exodus,
        World.Famfrit,
        World.Hyperion,
        World.Lamia,
        World.Leviathan,
        World.Ultros,
    ]
    __data_centers__: ClassVar[list[str]] = ["Crystal", "Aether", "Dynamis", "Primal"]

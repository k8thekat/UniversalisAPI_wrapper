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

from __future__ import annotations

from typing import NotRequired, Required, TypedDict


class ListingMateria(TypedDict):
    slotID: int
    materiaID: int


class CurrentListing(TypedDict):
    """Univertsalis API Current DC/World JSON Response Keys.

    Related to :class:`UniversalisAPICurrentTyped` keys.
    """

    lastReviewTime: int
    pricePerUnit: int
    quantity: int
    stainID: NotRequired[int]
    worldName: NotRequired[str]
    worldID: NotRequired[int]
    creatorName: str
    creatorID: NotRequired[int]
    hq: bool
    isCrafted: bool
    listingID: str
    materia: list[ListingMateria]
    onMannequin: bool
    retainerCity: int
    retainerID: int
    retainerName: str
    sellerID: int
    total: int
    tax: int
    timestamp: int
    buyerName: str


class CurrentDCWorld(TypedDict):
    """Univertsalis API Current DC/World JSON Response.

    `./universalis_data/data/universalis_api_current_dc.json`
    `./universalis_data/data/universalis_api_current_world.json`
    """

    worldID: NotRequired[int]
    worldName: NotRequired[str]
    dcName: NotRequired[str]  # DC only
    itemID: int
    lastUploadTime: int
    listings: Required[list[CurrentListing]]
    recentHistory: Required[list[CurrentListing]]
    currentAveragePrice: float | int
    currentAveragePriceNQ: float | int
    currentAveragePriceHQ: float | int
    regularSaleVelocity: float | int
    nqSaleVelocity: float | int
    hqSaleVelocity: float | int
    averagePrice: float | int
    averagePriceNQ: float | int
    averagePriceHQ: float | int
    minPrice: int
    minPriceNQ: int
    minPriceHQ: int
    maxPrice: int
    maxPriceNQ: int
    maxPriceHQ: int
    stackSizeHistogram: dict[str, int]
    stackSizeHistogramNQ: dict[str, int]
    stackSizeHistogramHQ: dict[str, int]
    worldUploadTimes: dict[str, int]
    listingsCount: int
    recentHistoryCount: int
    unitsForSale: int
    unitsSold: int
    hasData: bool


class HistoryEntries(TypedDict):
    """Universalis API History.

    Related to :class:`HistoryDCWorld.entries`.
    """

    hq: bool
    pricePerUnit: int
    quantity: int
    buyerName: str
    onMannequin: bool
    timestamp: int
    worldName: NotRequired[str]
    worldID: NotRequired[int]


class HistoryDCWorld(TypedDict):
    """Universalis API History DC/World JSON Response.

    `./local_data/api_examples/universalis_api_history_dc.json`
    `./local_data/api_examples/universalis_api_history_world.json`
    """

    itemID: int
    worldID: NotRequired[int]
    lastUploadTime: int
    entries: list[HistoryEntries]
    dcName: NotRequired[str]
    stackSizeHistogram: dict[str, int]
    stackSizeHistogramNQ: dict[str, int]
    stackSizeHistogramHQ: dict[str, int]
    regularSaleVelocity: float | int
    nqSaleVelocity: float | int
    hqSaleVelocity: float | int
    worldName: NotRequired[str]


class MultiPartData(TypedDict):
    """MultiCurrentData is a representation of a bulk/multi item Universalis query.

    The key in items is the `item_id` queried.
    """

    itemIDs: list[int]
    items: dict[str, CurrentDCWorld | HistoryDCWorld]
    worldID: NotRequired[int]
    unresolvedItems: list[int]
    worldName: NotRequired[str]
    dcName: NotRequired[str]

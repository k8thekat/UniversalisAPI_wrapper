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

from typing import TYPE_CHECKING, NotRequired, Optional, Required, TypedDict

if TYPE_CHECKING:
    from ._enums import DataCenter, ItemQuality, World


class MarketBoardParams(TypedDict, total=False):
    world_or_dc: DataCenter | World
    num_listings: int
    num_history_entries: int
    item_quality: ItemQuality
    trim_item_fields: bool


class AggregatedFields(TypedDict, total=False):
    """Universalis API Aggregated DC/World Json Response fields.

    Related to :class:`UniversalisAPIAggregatedKeysTyped` keys.
    """

    price: int
    worldId: int
    tempstamp: int
    quantity: float


class AggregatedKeys(TypedDict, total=False):
    """Universalis API Aggregated DC/World JSON Response Keys.

    Related to :class:`UniversalisAPIAggregatedTyped` keys.
    """

    minListing: AggregatedFields
    recentPurchase: AggregatedFields
    averageSalePrice: AggregatedFields
    dailySaleVelocy: AggregatedFields


class Aggregated(TypedDict, total=False):
    """Universalis API Aggregated DC/World JSON Response.

    `./universalis_data/data/universalis_api_aggregated_dc.json`
    `./universalis_data/data/universalis_api_aggregated_world.json`
    """

    itemId: int
    nq: AggregatedKeys
    hq: AggregatedKeys
    worldUploadTimes: AggregatedKeys


class CurrentKeys(TypedDict, total=False):
    """Univertsalis API Current DC/World JSON Response Keys.

    Related to :class:`UniversalisAPICurrentTyped` keys.
    """

    lastReviewTime: int
    pricePerUnit: int
    quantity: int
    stainID: int
    worldName: str
    worldID: int
    creatorName: str
    creatorID: Optional[int]
    hq: bool
    isCrafted: bool
    listingID: str
    materia: list[...]  # ????
    onMannequin: bool
    retainerCity: int
    retainerID: int
    retainerName: str
    sellerID: Optional[int]
    total: int
    tax: int
    timestamp: int
    buyerName: str


class CurrentDCWorlds(TypedDict, total=False):
    """Univertsalis API Current DC/World JSON Response.

    `./universalis_data/data/universalis_api_current_dc.json`
    `./universalis_data/data/universalis_api_current_world.json`
    """

    itemID: int
    worldID: int
    lastUploadTime: int
    dcName: str  # DC only
    listings: Required[list[CurrentKeys]]
    recentHistory: Required[list[CurrentKeys]]
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
    worldName: str
    listingsCount: int
    recentHistoryCount: int
    unitsForSale: int
    unitsSold: int
    hasData: bool


class HistoryEntries(TypedDict, total=False):
    """Universalis API History.

    Related to :class:`HistoryTyped.entries`.
    """

    hq: bool
    pricePerUnit: int
    quantity: int
    buyerName: str
    onMannequin: bool
    timestamp: int
    worldName: NotRequired[str]
    worldID: NotRequired[int]


class History(TypedDict):
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


class MultiCurrentData(TypedDict):
    """MultiCurrentData is a representation of a bulk/multi item Universalis query.

    The key in items is the `item_id` queried.
    """

    items: dict[str, CurrentDCWorlds]

from __future__ import annotations

from typing import TYPE_CHECKING, NotRequired, Optional, Required, TypedDict

if TYPE_CHECKING:
    from ._enums import DataCenterEnum, ItemQualityEnum, WorldEnum


class MarketBoardParams(TypedDict, total=False):
    world_or_dc: DataCenterEnum | WorldEnum
    num_listings: int
    num_history_entries: int
    item_quality: ItemQualityEnum
    trim_item_fields: bool


class AggregatedFieldsTyped(TypedDict, total=False):
    """
    -> Universalis API Aggregated DC/World Json Response fields.\n
    Related to :class:`UniversalisAPIAggregatedKeysTyped` keys.
    """

    price: int
    worldId: int
    tempstamp: int
    quantity: float


class AggregatedKeysTyped(TypedDict, total=False):
    """
    -> Universalis API Aggregated DC/World JSON Response Keys.\n
    Related to :class:`UniversalisAPIAggregatedTyped` keys.
    """

    minListing: AggregatedFieldsTyped
    recentPurchase: AggregatedFieldsTyped
    averageSalePrice: AggregatedFieldsTyped
    dailySaleVelocy: AggregatedFieldsTyped


class AggregatedTyped(TypedDict, total=False):
    """
    -> Universalis API Aggregated DC/World JSON Response.\n
    `./universalis_data/data/universalis_api_aggregated_dc.json`
    `./universalis_data/data/universalis_api_aggregated_world.json`
    """

    itemId: int
    nq: AggregatedKeysTyped
    hq: AggregatedKeysTyped
    worldUploadTimes: AggregatedKeysTyped


class CurrentKeysTyped(TypedDict, total=False):
    """
    -> Univertsalis API Current DC/World JSON Response Keys. \n
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
    materia: list
    onMannequin: bool
    retainerCity: int
    retainerID: int
    retainerName: str
    sellerID: Optional[int]
    total: int
    tax: int
    timestamp: int
    buyerName: str


class CurrentTyped(TypedDict, total=False):
    """
    -> Univertsalis API Current DC/World JSON Response. \n
    `./universalis_data/data/universalis_api_current_dc.json`
    `./universalis_data/data/universalis_api_current_world.json`
    """

    itemID: int
    worldID: int
    lastUploadTime: int
    dcName: str  # DC only
    listings: Required[list[CurrentKeysTyped]]
    recentHistory: Required[list[CurrentKeysTyped]]
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


class HistoryEntriesTyped(TypedDict, total=False):
    """
    Universalis API History related Typed Dict.\n
    - Related to :class:`HistoryTyped.entries`.
    """

    hq: bool
    pricePerUnit: int
    quantity: int
    buyerName: str
    onMannequin: bool
    timestamp: int
    worldName: NotRequired[str]
    worldID: NotRequired[int]


class HistoryTyped(TypedDict):
    """
    -> Universalis API History DC/World JSON Response. \n
    `./local_data/api_examples/universalis_api_history_dc.json`
    `./local_data/api_examples/universalis_api_history_world.json`
    """

    itemID: int
    worldID: NotRequired[int]
    lastUploadTime: int
    entries: list[HistoryEntriesTyped]
    dcName: NotRequired[str]
    stackSizeHistogram: dict[str, int]
    stackSizeHistogramNQ: dict[str, int]
    stackSizeHistogramHQ: dict[str, int]
    regularSaleVelocity: float | int
    nqSaleVelocity: float | int
    hqSaleVelocity: float | int
    worldName: NotRequired[str]


class MultiCurrentDataTyped(TypedDict):
    """
    MultiCurrentData is a representation of a bulk/multi item Universalis query.
    - The key in items is the `item_id` query'd.

    """

    items: dict[str, CurrentTyped]

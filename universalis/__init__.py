"""
Copyright (C) 2021-2024 Katelynn Cadwallader.

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

import asyncio
import json
import logging
import pathlib
import statistics
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, ClassVar, Literal, NamedTuple, Optional

import aiohttp

from ._enums import *

if TYPE_CHECKING:
    from _types import *
    from aiohttp.client import _RequestOptions

__title__ = "Universalis API wrapper"
__author__ = "k8thekat"
__license__ = "GNU"
__version__ = "0.0.1"
__credits__ = "Universalis and Square Enix"


class VersionInfo(NamedTuple):
    Major: int
    Minor: int
    Revision: int
    releaseLevel: Literal["alpha", "beta", "pre-release", "release", "development"]


version_info: VersionInfo = VersionInfo(Major=0, Minor=0, Revision=1, releaseLevel="development")


__all__ = (
    "API_CLASS",
    "DEFAULT_DATACENTER",
    "DEFAULT_WORLD",
    "IGNORED_KEYS",
    "PRE_FORMATTED_KEYS",
    "CurrentData",
    "CurrentDataEntries",
    "HistoryData",
    "HistoryDataEntries",
    "UniversalisAPI",
)


PRE_FORMATTED_KEYS: dict[str, str] = {
    "HQ": "_hq",
    "ID": "_id",
    "NQ": "_nq",
}

IGNORED_KEYS: list[str] = []

DEFAULT_WORLD: WorldEnum = WorldEnum.Zalera
DEFAULT_DATACENTER: DataCenterEnum = DataCenterEnum.Crystal

API_CLASS: Optional[UniversalisAPI] = None


def _get_global_api() -> Optional[UniversalisAPI]:
    return API_CLASS


class UniversalisAPI:
    """
    A bare-bones wrapper for Universalis API queries.

    Attributes
    -----------
    api_call_time: :class:`datetime`
        The last time an API call was made.
    max_api_calls: :class:`int`
        The default limit is 20 API calls per second.
    base_api_url: :class:`str`
        The Universalis API url.
    session: :class:`Optional[aiohttp.ClientSession]`
        The passed in ClientSession if any, otherwise will generate a new ClientSession on first API call.

    """

    # Last time an API call was made.
    api_call_time: datetime

    # Current limit is 20 API calls per second.
    _max_api_calls: int

    # Universalis API stuff
    base_api_url: str
    logger: ClassVar[logging.Logger] = logging.getLogger(__name__)
    session: Optional[aiohttp.ClientSession]
    item_dict: dict[str, dict[str, str]]

    def __init__(self, session: Optional[aiohttp.ClientSession] = None) -> None:
        """
        Build your Universalis API wrapper.

        Parameters
        -----------
        session: :class:`Optional[aiohttp.ClientSession]`, optional
            An existing ClientSession object otherwise <UniversalisAPI> will create it's own, by default None.
        """
        # Setting it to None by default will be the best as to keep the class as light weight as possible at runtime unless needed.
        self.session = session

        # Universalis API
        self.base_api_url = "https://universalis.app/api/v2"
        self.api_call_time = datetime.now()
        self._max_api_calls = 20

        # These are the "Trimmed" API fields for Universalis Market Results.
        # These can be overwritten via properties.
        self._single_item_fields = "&fields=itemID%2Clistings.quantity%2Clistings.worldName%2Clistings.pricePerUnit%2Clistings.hq%2Clistings.total%2Clistings.tax%2Clistings.retainerName%2Clistings.creatorName%2Clistings.lastReviewTime%2ClastUploadTime"
        self._multi_item_fields = "&fields=items.itemID%2Citems.listings.quantity%2Citems.listings.worldName%2Citems.listings.pricePerUnit%2Citems.listings.hq%2Citems.listings.total%2Citems.listings.tax%2Citems.listings.retainerName%2Citems.listings.creatorName%2Citems.listings.lastReviewTime%2Citems.lastUploadTime"

        self._load_json()

        global API_CLASS
        API_CLASS = self

    # def __del__(self) -> None:
    #     try:
    #         self._ = asyncio.create_task(self.__adel__())
    #         self.logger.debug("Closed `aiohttp.ClientSession`| Session: %s", self.session)
    #     except RuntimeError:
    #         self.logger.error("Failed to close our `aiohttp.ClientSession`")

    # async def __adel__(self) -> None:
    #     if self.session is not None:
    #         await self.session.close()

    @property
    def max_api_calls(self) -> int:
        """
        The limiting value of how many API calls per second, default is 20.
        """
        return self._max_api_calls

    @max_api_calls.setter
    def max_api_calls(self, value: int) -> None:
        if isinstance(value, int):
            self._max_api_calls = value

    @property
    def single_item_fields(self) -> str:
        """
        The Universalis API fields to filter/trim when fetching results for a single item.
        """
        return self._single_item_fields

    @single_item_fields.setter
    def single_item_fields(self, value: str) -> None:
        if isinstance(value, str):
            self._single_item_fields = value

    @property
    def multi_item_fields(self) -> str:
        """
        The Universalis API fields to filter/trim when fetching results for multiple items.
        """
        return self._multi_item_fields

    @multi_item_fields.setter
    def multi_item_fields(self, value: str) -> None:
        if isinstance(value, str):
            self._multi_item_fields = value

    def _load_json(self) -> None:
        path: pathlib.Path = pathlib.Path(__file__).parent.joinpath("items.json")
        if path.exists():
            self.item_dict = json.loads(path.read_bytes())
        else:
            raise FileNotFoundError("Unable to locate our `items.json`. | Path: %s", path)

    def _get_item(self, item_id: int, lang: LanguageEnum = LanguageEnum.en) -> Optional[str]:
        res = self.item_dict.get(str(item_id))
        if res is None:
            return None
        else:
            return res[lang.name]

    async def _request(self, url: str, request_params: Optional[_RequestOptions] = None) -> Any:
        """
        A wrapper for `aiohttp.ClientSession.get`.

        Parameters
        -----------
        url: :class:`str`
            The URL to query.
        request_params: :class:`_RequestOptions`, optional
            Any additional `kwargs` to supply to `aiohttp.ClientSession.get`

        Returns
        --------
        :class:`Any`
            The JSON response if any.

        Raises
        -------
        :exc:`ConnectionError`
            If `status` != 200 or `status` == 400 or 404.
        """
        cur_time: datetime = datetime.now()
        max_diff = timedelta(milliseconds=1000 / self.max_api_calls)
        if (cur_time - self.api_call_time) < max_diff:
            sleep_time: float = (max_diff - (cur_time - self.api_call_time)).total_seconds() + 0.1
            await asyncio.sleep(delay=sleep_time)

        if self.session is None:
            self.session = aiohttp.ClientSession()

        # kwargs handler.
        if request_params is None:
            data: aiohttp.ClientResponse = await self.session.get(url=url)
        else:
            data = await self.session.get(url=url, **request_params)

        if data.status != 200:
            self.logger.error("We encountered an error in Universalis _request. Status: %s | API: %s", data.status, url)
            raise ConnectionError("We encountered an error in Universalis _request. Status: %s | API: %s", data.status, url)
        elif data.status == 400:
            self.logger.error(
                "We encountered an error in Universalis _request due to invalid Parameters. Status: %s | API: %s", data.status, url
            )
            raise ConnectionError(
                "We encountered an error in Universalis _request due to invalid Parameters. Status: %s | API: %s", data.status, url
            )
        # 404 - The world/DC or item requested is invalid. When requesting multiple items at once, an invalid item ID will not trigger this.
        # Instead, the returned list of unresolved item IDs will contain the invalid item ID or IDs.
        elif data.status == 404:
            self.logger.error(
                "We encountered an error in Universalis _request due to invalid World/DC or Item ID. Status: %s | API: %s", data.status, url
            )
            raise ConnectionError(
                "We encountered an error in Universalis _request due to invalid World/DC or Item ID. Status: %s | API: %s", data.status, url
            )

        self.api_call_time = datetime.now()
        res: Any = await data.json()
        return res

    async def get_current_data(
        self,
        item: str | int,
        *,
        world_or_dc: DataCenterEnum | WorldEnum = DEFAULT_DATACENTER,
        num_listings: int = 10,
        num_history_entries: int = 10,
        item_quality: ItemQualityEnum = ItemQualityEnum.NQ,
        trim_item_fields: bool = False,
    ) -> CurrentData:
        """
        Retrieve the current Universalis marketboard data for the provided item.

        API: https://docs.universalis.app/#current-item-price


        Parameters
        -----------
        items: :class:`list[str] | list[int] | str | int`
            Either a single Item ID or a list of Item IDs in str or int format.
        world_or_dc: :class:`DataCenterEnum | WorldEnum`, optional
            The DataCenter or World to query your results for, by default DataCenterEnum.Crystal.
            - If you specify a `<WorldEnum>`, all `<CurrentData.listings>` and `<CurrentData.recent_history>` will not have the attributes `world_name`.
            - If you specify a `<DataCenterEnum>`, all `<CurrentData.listings>` and `<CurrentData.recent_history>` will have the `world_id` and `world_name` attributes.
                - `<CurrentData>` will also have an additional attribute called `dc_name`.
        num_listings: :class:`int`, optional
            The number of listing results for the query, by default 10.
        num_history_entries: :class:`int`, optional
            The number of history results for the query, by default 10.
        item_quality: :class:`ItemQualityEnum`, optional
            The Quality of the Item to query, by default ItemQualityEnum.NQ.
        trim_item_fields: :class:`bool`, optional
            If we want to trim the result fields or not, by default True.

        Returns
        --------
        :class:`CurrentData`
            The JSON response converted into a :class:`CurrentData` object.
        """

        # Sanitize the value as a str for usage.
        if isinstance(item, int):
            item = str(item)

        api_url: str = (
            f"{self.base_api_url}/{world_or_dc.name}/{item}?listings={num_listings}&entries={num_history_entries}&hq={item_quality.value}"
        )
        # ? Suggestion
        # A fields class to handle querys.
        # If we need/want to trim fields.
        if trim_item_fields:
            api_url += self.single_item_fields

        res: CurrentTyped = await self._request(url=api_url)
        self.logger.debug("<Universalis._get_current_data>. | DC/World: %s | Item ID: %s", world_or_dc.name, item)
        self.logger.debug("<Universalis._get_current_data> URL: %s | Response:\n%s", api_url, res)
        return CurrentData(data=res)

    async def get_bulk_current_data(
        self,
        items: list[str] | list[int],
        *,
        world_or_dc: DataCenterEnum | WorldEnum = DEFAULT_DATACENTER,
        num_listings: int = 10,
        num_history_entries: int = 10,
        item_quality: ItemQualityEnum = ItemQualityEnum.NQ,
        trim_item_fields: bool = False,
    ) -> list[CurrentData]:
        """
        Retrieves a bulk item search of Universalis marketboard data.

        Parameters
        -----------
        items: :class:`list[str] | list[int]`
            A list of Item IDs in str or int format.
        world_or_dc: :class:`DataCenterEnum | WorldEnum`, optional
            The DataCenter or World to query your results for, by default DataCenterEnum.Crystal.
        num_listings: :class:`int`, optional
            The number of listing results for the query, by default 10.
        num_history_entries: :class:`int`, optional
            The number of history results for the query, by default 10.
        item_quality: :class:`ItemQualityEnum`, optional
            The Quality of the Item to query, by default ItemQualityEnum.NQ.
        trim_item_fields: :class:`bool`, optional
            If we want to trim the result fields or not, by default True.

        Returns
        --------
        :class:`list[CurrentData]`
            Returns the JSON response converted into a list of :class:`HistoryData` objects.
        """

        query: list[str] = []
        for entry in items:
            if isinstance(entry, int):
                query.append(str(entry))
            else:
                query.append(entry)

        # ? Suggestion
        # Handle lists over 100 items.
        results: list[CurrentData] = []
        for i in range(0, len(query), 100):
            api_url: str = f"{self.base_api_url}/{world_or_dc.name}/{','.join(query)}?listings={num_listings}&entries={num_history_entries}&hq={item_quality.value}"

            # If we need/want to trim fields.
            if trim_item_fields:
                api_url += self.multi_item_fields

            res: MultiCurrentDataTyped = await self._request(url=api_url)
            self.logger.debug("<Universalis._get_bulk_current_data>. | DC/World: %s | Num of Items: %s", world_or_dc.name, len(items))
            self.logger.debug("<Universalis._get_bulk_current_data> URL: %s | Response:\n%s", api_url, res)
            if res.get("items") is not None:
                results.extend([CurrentData(data=value) for value in res["items"].values()])
        return results

    async def get_history_data(
        self,
        item: str | int,
        *,
        data_center: WorldEnum | DataCenterEnum = DEFAULT_DATACENTER,
        num_listings: int = 10,
        min_price: int = 0,
        max_price: int = 2147483647,
        history: int = 604800000,
    ) -> HistoryData:
        """
        Universalis Marketboard History Data

        API: https://docs.universalis.app/#market-board-sale-history


        Parameters
        -----------
        items: :class:`Union[list[str], str]`
            The Item IDs to look up, limit of 99 entries.
        data_center: :class:` WorldEnum | DataCenterEnum`, optional
            The Datacenter to fetch the results from, by default DataCenterEnum.Crystal.
        num_listings: :class:`int`, optional
            _description_, by default 10.
        min_price: :class:`int`, optional
            _description_, by default 0.
        max_price: :class:`Union[int, None]`, optional
            The max price of the item, by default None.
        history: :class:`int`, optional
            The timestamp float value for how far to go into the history; by default 604800000.


        Returns
        --------
        :class:`HistoryData`
            The JSON response converted into a :class:`HistoryData` object.
        """
        if isinstance(item, int):
            item = str(item)

        api_url: str = f"{self.base_api_url}/history/{data_center.name}/{item}?entriesToReturn={num_listings}&statsWithin={history}&minSalePrice={min_price}&maxSalePrice={max_price}"
        res = await self._request(url=api_url)
        return HistoryData(data=res)

    async def get_suggested_price(
        self,
        item_id: int | str,
        *,
        world: WorldEnum = DEFAULT_WORLD,
        item_quality: ItemQualityEnum = ItemQualityEnum.NQ,
        num_of_listings: int = 50,
    ) -> str:
        """
        Uses current listings and recent history listings to give a "suggestive" price and stack size to sell the item.
        - *NOTE* - The information is purely based on the sample size;
        so increasing or decreasing the `num_of_listings` parameter can drastically affect the results.

        Parameters
        -----------
        item_id: :class:`int | str`
            The Item ID to look up.
        world: :class:`WorldEnum`, optional
            The Final Fantasy World name to fetch results for, by default DEFAULT_WORLD.
        item_quality: :class:`ItemQualityEnum`, optional
            The Item Quality, by default ItemQualityEnum.NQ.
        num_of_listings: :class:`int`, optional
            The number of listings and recent history listings to fetch, by default 50.

        Returns
        --------
        :class:`str`
            A string including the item name, quality, world, sample size, current highest price and lowest price,
            mean price diff for current and recent history and suggested stack sizing.
        """
        if isinstance(item_id, str):
            item_id = int(item_id)
        # Get a bulk of data to check average price/stack and other information to make a suggested price.
        res: CurrentData = await self.get_current_data(
            item=item_id,
            world_or_dc=world,
            num_listings=num_of_listings,
            num_history_entries=num_of_listings,
            item_quality=item_quality,
        )

        stacksize: int = 0
        optimal_stacksize: str = "UNK"
        for k, v in res.stack_size_histogram.items():
            if v > stacksize:
                stacksize = v
                optimal_stacksize = k

        cur_stacksize_mean: float = statistics.mode(data=[entry.quantity for entry in res.listings])
        history_stacksize_mean: float = statistics.mean(data=[entry.quantity for entry in res.recent_history])
        # Let's sort our listings by highest price first.
        # TODO - omit exaggerated values that exceed a threshold over the cost? (eg. Omit 10mill cost for a 100k item or similar)
        sorted_cur_listings: list[CurrentDataEntries] = sorted(res.listings, key=lambda x: x.price_per_unit, reverse=True)
        sorted_history_listings: list[HistoryDataEntries] = sorted(res.recent_history, key=lambda x: x.price_per_unit, reverse=True)

        # Let's get the middle price point
        cur_price_mean: float = statistics.mean(data=[entry.price_per_unit for entry in sorted_cur_listings])
        history_price_mean: float = statistics.mean(data=[entry.price_per_unit for entry in sorted_history_listings])
        # So we have the MEAN values for price and stacksize in terms of current listings and history listings.
        # Current highest price = sorted_cur_listings[0]
        # History highest price = sorted_history_listings[0]
        cur_mean_diff = int(sorted_cur_listings[0].price_per_unit - cur_price_mean)
        hist_mean_diff = int(sorted_history_listings[0].price_per_unit - history_price_mean)

        temp = []
        temp.append(
            f"Price Insight for: {self._get_item(res.item_id)} ({res.item_id}) | Item Quality: {item_quality.name} | World: {world.name} | Sample Size: {num_of_listings}"
        )
        temp.append(
            f"- Current Highest Price/Unit: {sorted_cur_listings[0].price_per_unit} | Lowest Price/Unit: {sorted_cur_listings[-1].price_per_unit}"
        )
        temp.append(
            f"- Current Mean Price/Unit: {cur_price_mean} | Price/Unit diff over Mean: {cur_mean_diff} | {(((cur_mean_diff / sorted_cur_listings[0].price_per_unit) % 2) * 100):.2f}%"
        )
        temp.append(
            f"- History Highest Price/Unit: {sorted_history_listings[0].price_per_unit} | Lowest Price/Unit: {sorted_history_listings[-1].price_per_unit}"
        )
        temp.append(
            f"- History Mean Price/Unit: {history_price_mean} | Price/Unit diff oer Mean: {hist_mean_diff} | {(((hist_mean_diff / sorted_history_listings[0].price_per_unit) % 2) * 100):.2f}%"
        )
        temp.append(
            f"- Common stack sizes (Optimal | Current Mean | History Mean): {optimal_stacksize} | {cur_stacksize_mean} | {history_stacksize_mean}"
        )
        return "\n".join(temp)

    @classmethod
    def _pep8_key_name(
        cls, key_name: str, *, ignored_keys: Optional[list[str]] = None, pre_formatted_keys: Optional[dict[str, str]] = None
    ) -> str:
        """
        Converts the provided `key_name` parameter into something that is pep8 compliant yet clear as to what it is for.
        - Adds a `_` before any uppercase char in the `key_name` and then `.lowers()` that uppercase char.

        **Note**:
            When using the parameter `pre_formatted_keys` here is an example. "I want to replace `ItemID` with `item_id`. Structure would be `{"ItemID": "item_id"}`".


        Parameters
        -----------
        key_name: :class:`str`
            The string to format.
        ignored_keys: :class:`Optional[list[str]]`
            An array of strings that if the `key_name` is in the array it will be ignored and instantly returned unformatted.
            - You may provide your own, or use the constant `IGNORED_KEYS`
        pre_formatted_keys: :class:`Optional[dict[str, str]]`
            An dictionary with keys consisting of values to compare against and the value of the keys to be the replacement string.

        Returns
        --------
        :class:`str`
            The formatted string.
        """
        if ignored_keys is None:
            ignored_keys = IGNORED_KEYS
        if pre_formatted_keys is None:
            pre_formatted_keys = PRE_FORMATTED_KEYS

        # We have keys we don't want to format/change during generation so add them to the ignored_keys list.
        if key_name in ignored_keys:
            return key_name

        # If we find a pre_formatted key structure we want, let's replace the part and then return the rest.
        for key, value in pre_formatted_keys.items():
            if key in key_name:
                key_name = key_name.replace(key, value)

        temp: str = key_name[:1].lower()
        for e in key_name[1:]:
            if e.isupper():
                temp += f"_{e.lower()}"
                continue
            temp += e
        cls.logger.debug("<UniversalisAPI.pep8_key_name> key_name: %s | Converted: %s", key_name, temp)
        return temp


class Generic:
    _logger: ClassVar[logging.Logger] = logging.getLogger(__name__)
    _repr_keys: list[str]
    _universalis: Optional[UniversalisAPI]

    world_id: Optional[int]
    world_name: Optional[str]
    dc_name: Optional[str]  # This value only exists if you look up results by "Datacenter" instead of "World"

    def __init__(self, data: Any) -> None:
        self._logger.debug("<%s.__init__()> data: %s", __class__.__name__, data)
        setattr(self, "_raw", data)
        global API_CLASS
        self._universalis = _get_global_api()

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        try:
            return f"\n\n__{self.__class__.__name__}__\n" + "\n".join([
                f"{e}: {getattr(self, e)}" for e in self._repr_keys if e.startswith("_") is False
            ])
        except AttributeError:
            return f"\n\n__{self.__class__.__name__}__\n" + "\n".join([
                f"{e}: {getattr(self, e)}" for e in sorted(self.__dict__) if e.startswith("_") is False
            ])


class GenericData(Generic):
    """
    Base class for mutual attributes and properties for Universalis data.
    """

    item_id: int
    nq_sale_velocity: float | int
    hq_sale_velocity: float | int
    regular_sale_velocity: float | int
    stack_size_histogram: dict[str, int]
    stack_size_histogram_nq: dict[str, int]
    stack_size_histogram_hq: dict[str, int]

    _last_upload_time: datetime | int

    def __getattribute__(self, name: str) -> Any:
        # Reason this is being done is some values may not exist on the class.
        if callable(name):
            return super().__getattribute__(name)

        try:
            return super().__getattribute__(name)
        except AttributeError:
            return None

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self.item_id == other.item_id

    @property
    def last_upload_time(self) -> datetime | int:
        """
        This exists on both Current Data and History Data.
        """
        return self._last_upload_time

    @last_upload_time.setter
    def last_upload_time(self, value: int) -> None:
        # This appears to be including miliseconds.. so we need to divide the value by 1000
        if isinstance(value, int):
            try:
                self._last_upload_time = datetime.fromtimestamp(timestamp=(value / 1000))
            except:
                self._last_upload_time = value


class CurrentData(GenericData):
    """
    A representation of Universalis marketboard current listings data.

    Attributes
    -----------
    item_id: :class:`int`
        The FFXIV Item ID.
    listings: :class:`list[CurrentDataEntries]`
        A list of current marketboad entries, sorted by `timestamp`.
    recent_history: :class:`list[HistoryDataEntries]`
        A list of recently sold entries with relevant data, sorted by `timestamp`.
    world_id: :class:`Optional[int]`
        The Final Fantasy 14 World ID, this will match up to the :class:`WorldEnum`.
    world_name: :class:`Optional[str]`
        The Final Fantasy 14 World name.
    nq_sale_velocity: :class:`float | int`
        The rate at which NQ of this item sells per day.
    hq_sale_velocity: :class:`float | int`
        The rate at which HQ of this item sells per day.
    regular_sale_velocity: :class:`float | int`
        The rate at which HQ + NQ of this item sells per day.
    stack_size_histogram: :class:`dict[str, int]`
        A histogram of HQ + NQ stacksize sales.
    stack_size_histogram_nq: :class:`dict[str, int]`
        A histogram of NQ stacksize sales.
    stack_size_histogram_hq: :class:`dict[str, int]`
        A histogram of HQ stacksize sales.
    last_upload_time: :class:`datetime | int`
        When the data was uploaded for the provided World, otherwise this will be the most recent value from the `world_upload_times` attribute.
    current_average_price: :class:`float | int`
        The average price accross all listings including HQ and NQ.
    current_average_price_nq: :class:`float | int`
        The average price accross all NQ listings.
    current_average_price_hq: :class:`float | int`
        The average price accross all HQ listings.
    average_price: :class:`float | int`
        The historic average price including HQ and NQ.
    average_price_nq: :class:`float | int`
        The historic average NQ price.
    average_price_hq: f:class:`loat | int`
        The historic average HQ price.
    min_price: :class:`int`
        The current listings min price including HQ and NQ.
    min_price_nq: :class:`int`
        The current listings NQ min price.
    min_price_hq: :class:`int`
        The current listings HQ min price.
    max_price: :class:`int`
        The current listings max price including HQ and NQ.
    max_price_nq: :class:`int`
        The current listings NQ max price.
    max_price_hq: :class:`int`
        The current listings HQ max price.
    world_upload_times: :class:`dict[str, int]`
        The timestamps for each World for when data was last updated.
    listings_count: :class:`int`
        The lenth or number of listings results fetched/found.
        - This value may be limited by the `num_listings` parameter when fetching data.
    recent_history_count: :class:`int`
        The lenth or number of recent_history results fetched/found.
        - This value may be limited by the `num_listings` parameter when fetching data.
    units_for_sale: :class:`int`
        Total number of units for sale.
    units_sold: :class:`int`
        The total number of unit's sold for this item.
    has_data: :class:`bool`
        If the item has data or not. (I assume this is more used for Universalis's side of data management.)
    """

    current_average_price: float | int
    current_average_price_nq: float | int
    current_average_price_hq: float | int
    average_price: float | int
    average_price_nq: float | int
    average_price_hq: float | int
    min_price: int
    min_price_nq: int
    min_price_hq: int
    max_price: int
    max_price_nq: int
    max_price_hq: int
    world_upload_times: dict[str, int]
    listings_count: int
    recent_history_count: int
    units_for_sale: int
    units_sold: int
    has_data: bool

    _listings: list[CurrentDataEntries]
    _recent_history: list[HistoryDataEntries]

    def __init__(self, data: CurrentTyped) -> None:
        super().__init__(data=data)
        for key, value in data.items():
            key = UniversalisAPI._pep8_key_name(key_name=key)
            if isinstance(value, list) and key.lower() == "listings":
                setattr(self, key, value)
            elif key.lower() in ["has_data"] and isinstance(value, int):
                setattr(self, key, bool(value))
            else:
                setattr(self, key, value)

    @property
    def listings(self) -> list[CurrentDataEntries]:
        return self._listings

    @listings.setter
    def listings(self, value: list[CurrentKeysTyped]) -> None:
        self._listings: list[CurrentDataEntries] = sorted([CurrentDataEntries(data=entry) for entry in value if isinstance(entry, dict)])

    @property
    def recent_history(self) -> list[HistoryDataEntries]:
        return self._recent_history

    @recent_history.setter
    def recent_history(self, value: list[HistoryEntriesTyped]) -> None:
        self._recent_history: list[HistoryDataEntries] = sorted([
            HistoryDataEntries(data=entry) for entry in value if isinstance(entry, dict)
        ])

    def sort_listings(self, world: Optional[WorldEnum] = None, reverse: bool = False) -> list[CurrentDataEntries]:
        """
        Sort the :class:`CurrentData.listings` by price per unit with the cheapest being first.

        Parameters
        -----------
        world: :class:`Optional[WorldEnum]`, optional
            If you want to filter out just your Final Fantasy 14 World, by default None.
        reverse: :class:`bool`, optional
            If you want the "most expensive" price per unit at the start of the array, by default True.

        Returns
        --------
        :class:`list[CurrentDataEntries]`
            A sorted list of :class:`CurrentDataEntries`.
        """
        if world is not None:
            return sorted(
                [entry for entry in self.listings if isinstance(entry.world_name, str) and entry.world_name == world.name],
                key=lambda x: x.price_per_unit,
                reverse=reverse,
            )
        return sorted(self.listings, key=lambda x: x.price_per_unit, reverse=reverse)


class CurrentDataEntries(Generic):
    """
    A representation of Universalis marketboard current listing entries data.
    - Comparing `<CurrentDataEntries>` will check quality and timestamp.

    Attributes
    -----------
    price_per_unit: :class:`int`
        The price per item.
    quantity: :class:`int`
        The quantity of items in the listing.
    stain_id: :class:`Optional[int]`
        UNK?
    world_id: :class:`Optional[int]`
        The Final Fantasy 14 World ID, this will match up to the :class:`WorldEnum`.
        - This only exists when fetching History data for a specific World.
    world_name: :class:`Optional[str]`
        The Final Fantasy 14 World name.
        - This only exists when fetching History data for a specific World.
    creator_name: :class:`str`
        The person who crafted the item, it any.
    creator_id: :class:`Optional[int]`
        The persons ID who crafted the item, it any.
    hq: :class:`bool`
        If the item is HQ or not.
    is_crafted: :class:`bool`
        If the item was crafted.
    listing_id: :class:`str`
        The Universalis listing ID.
    last_review_time: :class:`datetime | int`
        When the data was last updated for the provided listing.
    materia: :class:`list`
        If the item has any Materia melded into it.
    on_mannequin: :class:`bool`
        If the item is on a mannequin.
    retainer_city: :class:`int`
        The city the retainer is located in.
    retainer_id: :class:`int`
        The ID of the retainer.
    retainer_name: :class:`str`
        The name of the retainer.
    seller_id: :class:`Optional[int]`
        The sellers ID if any.
    total: :class:`int`
        The total cost for the item not including tax.
    tax: :class:`int`
        The total tax for the item.
    """

    price_per_unit: int
    quantity: int
    stain_id: int
    world_name: Optional[str]
    world_id: Optional[int]
    creator_name: str
    creator_id: Optional[int]
    hq: bool
    is_crafted: bool
    listing_id: str
    materia: list
    on_mannequin: bool
    retainer_city: int
    retainer_id: int
    retainer_name: str
    seller_id: Optional[int]
    total: int
    tax: int

    _last_review_time: datetime | int

    def __init__(self, data: CurrentKeysTyped) -> None:
        super().__init__(data=data)
        for key, value in data.items():
            key = UniversalisAPI._pep8_key_name(key_name=key)
            if key.lower() in ["on_mannequin", "is_crafted", "hq"] and isinstance(value, int):
                setattr(self, key, bool(value))
            else:
                setattr(self, key, value)

    @property
    def last_review_time(self) -> datetime | int:
        return self._last_review_time

    @last_review_time.setter
    def last_review_time(self, value: int) -> None:
        if isinstance(value, int):
            try:
                self._last_review_time = datetime.fromtimestamp(timestamp=value)
            except:
                self._last_review_time = value

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self.hq == other.hq  # and self.price_per_unit == other.price_per_unit

    def __lt__(self, other: object) -> bool:
        return (
            isinstance(other, self.__class__)
            and self.hq == other.hq
            and (
                isinstance(self.last_review_time, datetime)
                and isinstance(other.last_review_time, datetime)
                and self.last_review_time < other.last_review_time
            )
        )


class HistoryData(GenericData):
    """
    A representation of Universalis marketboard history data.

    Attributes
    -----------
    item_id: :class:`int`
        The Final Fantasy 14 Item ID.
    entries: :class:`list[HistoryDataEntries]`
        A list of marketboard sale history data.
    world_id: :class:`Optional[int]`
        The Final Fantasy 14 World ID, this will match up to the :class:`WorldEnum`.
        - This only exists when fetching data for a specific World.
    world_name: :class:`Optional[str]`
        The Final Fantasy 14 World name.
        - This only exists when fetching data for a specific World.
    dc_name: :class:`Optional[str]`
        The FInal Fantasy Datacenter name.
        - This only exists when fetching data for an entire Datacenter.
    nq_sale_velocity: :class:`float | int`
        The rate at which NQ of this item sells per day.
    hq_sale_velocity: :class:`float | int`
        The rate at which HQ of this item sells per day.
    regular_sale_velocity: :class:`float | int`
        The rate at which HQ + NQ of this item sells per day.
    stack_size_histogram: :class:`dict[str, int]`
        A histogram of HQ + NQ stacksize sales.
    stack_size_histogram_nq: :class:`dict[str, int]`
        A histogram of NQ stacksize sales.
    stack_size_histogram_hq: :class:`dict[str, int]`
        A histogram of HQ stacksize sales.
    last_upload_time: :class:`datetime | int`
        When the data was uploaded for the provided World.
        - Otherwise this will be the most recent value from the `world_upload_times` attribute if using Datacenter data.
    """

    _entries: list[HistoryDataEntries]

    def __init__(self, data: HistoryTyped) -> None:
        super().__init__(data=data)
        self._repr_keys = ["item_id", "world_name", "dc_name", "entries"]
        for key, value in data.items():
            key: str = UniversalisAPI._pep8_key_name(key_name=key)
            if key.lower() == "entries" and isinstance(value, list) and len(value) > 1:
                self.entries = value  # type: ignore
            else:
                setattr(self, key, value)

    @property
    def entries(self) -> list[HistoryDataEntries]:
        return sorted(self._entries)

    @entries.setter
    def entries(self, value: list[HistoryEntriesTyped]) -> None:
        self._entries = [HistoryDataEntries(data=entry) for entry in value if isinstance(entry, dict)]


class HistoryDataEntries(Generic):
    """
    A represensation of Universalis marketboard history data entries.


    Attributes
    -----------
    world_id: :class:`Optional[int]`
        The Final Fantasy 14 World ID, this will match up to the :class:`WorldEnum`.
        - This only exists when fetching History data for a Datacenter.
    world_name: :class:`Optional[str]`
        The Final Fantasy 14 World name.
        - This only exists when fetching History data for a Datacenter.
    hq: :class:`bool`
        If the item is HQ or not.
    price_per_unit: :class:`int`
        The price per item.
    quantity: :class:`int`
        The quantity of items in the listing.
    timestamp: :class:`datetime | int`
        When the listing was sold.
    buyer_name: :class:`str`
        The player who purchased the listing.
    on_mannequin: :class:`bool`
        If the item is on a mannequin.
    """

    hq: bool
    price_per_unit: int
    quantity: int
    buyer_name: str
    on_mannequin: bool
    _timestamp: datetime | int
    world_name: Optional[str]
    world_id: Optional[int]

    def __init__(self, data: HistoryEntriesTyped) -> None:
        super().__init__(data=data)
        self._repr_keys = ["hq", "quantity", "price_per_unit", "world_name", "timestamp"]
        for key, value in data.items():
            key: str = UniversalisAPI._pep8_key_name(key_name=key)
            if key.lower() in ["hq", "on_mannequin"] and isinstance(value, int):
                setattr(self, key, bool(value))
            else:
                setattr(self, key, value)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self.hq == other.hq and self.price_per_unit == other.price_per_unit

    def __lt__(self, other: object) -> bool:
        return (
            isinstance(other, self.__class__)
            and self.hq == other.hq
            and (isinstance(self.timestamp, datetime) and isinstance(other.timestamp, datetime) and self.timestamp < other.timestamp)
        )

    @property
    def timestamp(self) -> datetime | int:
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value: int) -> None:
        if isinstance(value, int):
            try:
                self._timestamp = datetime.fromtimestamp(timestamp=value)
            except:
                self._timestamp = value

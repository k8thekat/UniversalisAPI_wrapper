"""Copyright (C) 2021-2024 Katelynn Cadwallader.

This file is part of Universalis API Wrapper.

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

__title__ = "Universalis API wrapper"
__author__ = "k8thekat"
__license__ = "GNU"
__version__ = "4.0.0-dev"
__credits__ = "Universalis and Square Enix"


import datetime
import json
import logging
import pathlib
from typing import TYPE_CHECKING, Any, Literal, NamedTuple, Optional, Self, Union, Unpack

import aiohttp

from async_universalis._enums import Language

from ._enums import *
from .errors import UniversalisError

if TYPE_CHECKING:
    import types

    from aiohttp.client import _RequestOptions as AiohttpRequestOptions  # pyright: ignore[reportPrivateUsage]

    from ._types import *

    DataTypedAliase = Union[CurrentListing, CurrentDCWorld, HistoryDCWorld, HistoryEntries]


LOGGER = logging.getLogger(__name__)


class VersionInfo(NamedTuple):
    major: int
    minor: int
    revision: int
    release_level: Literal["release", "development"]


version_info: VersionInfo = VersionInfo(major=3, minor=0, revision=2, release_level="development")


__all__ = (
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

DEFAULT_DATACENTER: DataCenter = DataCenter.Crystal
DEFAULT_LANGUAGE: Language = Language.en


class UniversalisAPI:
    """A bare-bones wrapper for Universalis API queries.

    Supports context-manager style usage. `async with UniversalisAPI() as market: ...`,
    otherwise call `<UniversalisAPI>.clean_up()` if you did not provide a `aiohttp.ClientSession`.

    Attributes
    ----------
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
    api_call_time: datetime.datetime

    # Current limit is 20 API calls per second.
    _max_api_calls: int

    # Universalis API stuff
    base_api_url: str
    # Our private session object if we have to create the CLientSession
    # See `_request()`
    _session: Optional[aiohttp.ClientSession]
    session: Optional[aiohttp.ClientSession]
    item_dict: dict[str, dict[str, str]]

    # Defaults
    _language: Language
    _datacenter: DataCenter

    def __init__(self, session: Optional[aiohttp.ClientSession] = None) -> None:
        """Build your Universalis API wrapper.

        Parameters
        ----------
        session: :class:`Optional[aiohttp.ClientSession]`, optional
            An existing ClientSession object otherwise <UniversalisAPI> will create it's own, by default None.

        """
        # Setting it to None by default will be the best as to keep the class as light weight as possible at runtime unless needed.
        self.session = session
        self._session = None

        # Default search parameters.
        self.language = DEFAULT_LANGUAGE
        self.default_datacenter = DEFAULT_DATACENTER

        # Universalis API
        self.base_api_url = "https://universalis.app/api/v2"

        # These are the "Trimmed" API fields for Universalis Market Results.
        # These can be overwritten via properties.
        self._single_item_fields = (
            "&fields=itemID%2Clistings.quantity%2Clistings.worldName%2Clistings.pricePerUnit%2Clistings.hq"
            "%2Clistings.total%2Clistings.tax%2Clistings.retainerName%2Clistings.creatorName%2Clistings.lastReviewTime%2ClastUploadTime"
        )
        self._multi_item_fields = (
            "&fields=items.itemID%2Citems.listings.quantity%2Citems.listings.worldName%2Citems.listings.pricePerUnit"
            "%2Citems.listings.hq%2Citems.listings.total%2Citems.listings.tax%2Citems.listings.retainerName%2Citems.listings.creatorName%2Citems.listings.lastReviewTime%2Citems.lastUploadTime"
        )

        self._load_json()

    @property
    def single_item_fields(self) -> str:
        """The Universalis API fields to filter/trim when fetching results for a single item."""
        return self._single_item_fields

    @single_item_fields.setter
    def single_item_fields(self, value: str) -> None:
        self._single_item_fields = value

    @property
    def multi_item_fields(self) -> str:
        """The Universalis API fields to filter/trim when fetching results for multiple items."""
        return self._multi_item_fields

    @multi_item_fields.setter
    def multi_item_fields(self, value: str) -> None:
        self._multi_item_fields = value

    @property
    def language(self) -> Language:
        """Set the default language to be used when returning Final Fantasy Item names.

        Returns
        -------
        :class:`Language`
            A :class:`Language` enum.

        """
        return self._language

    @language.setter
    def language(self, value: Language) -> None:
        self._language: Language = value

    @property
    def default_datacenter(self) -> DataCenter:
        """Set the default Final Fantasy 14 DataCenter to be used when the `world_or_dc` parameter is optional.

        Returns
        -------
        :class:`DataCenter`
            A :class:`DataCenter` enum.

        """
        return self._datacenter

    @default_datacenter.setter
    def default_datacenter(self, value: DataCenter) -> None:
        self._datacenter = value

    def _load_json(self) -> None:
        path: pathlib.Path = pathlib.Path(__file__).parent.joinpath("items.json")
        if path.exists():
            self.item_dict = json.loads(path.read_bytes())
        else:
            msg = "Unable to locate our `items.json`. | Path: %s"
            raise FileNotFoundError(msg, path)

    def _get_item(self, item_id: int) -> Optional[str]:
        res = self.item_dict.get(str(item_id))
        if res is None:
            return None
        return res[self.language.name]

    async def _request(self, url: str, request_params: Optional[AiohttpRequestOptions] = None) -> Any:
        LOGGER.debug("<%s._request> | url: %s | user session: %s | req_params: %s ", __class__.__name__, url, self.session, request_params)
        # If the user supplied session is None; we create our own and set it to a private
        # attribute so we can close it later, otherwise we will use the user supplied session.
        if self.session is None:
            if self._session is None:
                session: aiohttp.ClientSession = aiohttp.ClientSession()
                self._session = session
                LOGGER.debug("<%s._request> | Creating local `aiohttp.ClientSession()` | session: %s", __class__.__name__, session)
            else:
                session = self._session
        else:
            session = self.session

        # kwargs handler.
        if request_params is None:
            data: aiohttp.ClientResponse = await session.get(url=url)
        else:
            data = await session.get(url=url, **request_params)

        LOGGER.debug("<%s._request> | Status Code: %s | Content Type: %s", __class__.__name__, data.status, data.content_type)
        if not 200 <= data.status < 300:
            raise UniversalisError(data.status, url, "generic http request")
        if data.status == 400:
            raise UniversalisError(
                data.status,
                url,
                "invalid parameters",
            )
        # 404 - The world/DC or item requested is invalid. When requesting multiple items at once, an invalid item ID will not trigger this.
        # Instead, the returned list of unresolved item IDs will contain the invalid item ID or IDs.
        if data.status == 404:
            raise UniversalisError(
                data.status,
                url,
                "invalid World/DC or Item ID",
            )

        self.api_call_time = datetime.datetime.now(datetime.UTC)
        res: Any = await data.json()
        return res

    async def get_current_data(
        self,
        item: str | int,
        *,
        world_or_dc: Optional[DataCenter | World] = None,
        num_listings: int = 10,
        num_history_entries: int = 10,
        item_quality: ItemQuality = ItemQuality.NQ,
        trim_item_fields: bool = False,
    ) -> CurrentData:
        """Retrieve the current Universalis marketboard data for the provided item.

        Retrieves the data currently shown on the market board for the requested item and world or data center.

        API: https://docs.universalis.app/#current-item-price

        .. note::
            If you want to modify the returned data fields, access `<UniversalisAPI>.single_item_fields` property and change the format.
            - See `https://docs.universalis.app/` and use their forms to generate a string with the fields you want.


        .. note::
            - If you specify a `<World>`.
                - All `<CurrentData.listings>` and `<CurrentData.recent_history>` will not have the attributes `world_name`.
            - If you specify a `<DataCenter>`.
                - All `<CurrentData.listings>` and `<CurrentData.recent_history>` will have the `world_id` and `world_name` attributes.
                - `<CurrentData>` will also have an additional attribute called `dc_name`.

        .. note::
            You can change the default DataCenter by setting the `<UniversalisAPI>.datacenter` property.


        Parameters
        ----------
        item: :class:`str| int`
            A Final Fantasy 14 item id of int or str type.
        world_or_dc: :class:`DataCenter | World`, optional
            The Final Fantasy 14 World or Datacenter to query your results for, by default `<UniversalisAPI>.datacenter`.
            - The default is a datacenter for the library, `<DataCenter>.Crystal`.
        num_listings: :class:`int`, optional
            The number of listing results for the query, by default 10.
        num_history_entries: :class:`int`, optional
            The number of history results for the query, by default 10.
        item_quality: :class:`ItemQuality`, optional
            The quality of the Item to query, by default `<ItemQuality>.NQ`.
        trim_item_fields: :class:`bool`, optional
            If we want to trim the result fields or not, by default True.

        Returns
        -------
        :class:`CurrentData`
            The JSON response converted into a :class:`CurrentData` object.

        """
        # Sanitize the value as a str for usage.
        if isinstance(item, int):
            item = str(item)
        # If no datacenter is provided; use the libs Instance default.
        if world_or_dc is None:
            world_or_dc = self.default_datacenter

        api_url: str = (
            f"{self.base_api_url}/{world_or_dc.name}/{item}?listings={num_listings}&entries={num_history_entries}&hq={item_quality.value}"
        )
        # ? Suggestion
        # A fields class to handle querys.
        # If we need/want to trim fields.
        if trim_item_fields:
            api_url += self.single_item_fields

        res: CurrentDCWorld = await self._request(url=api_url)
        LOGGER.debug("<%s._get_current_data>. | DC/World: %s | Item ID: %s", __class__.__name__, world_or_dc.name, item)
        LOGGER.debug("<%s._get_current_data> URL: %s | Response:\n%s", __class__.__name__, api_url, res)
        return CurrentData(universalis=self, data=res)

    async def get_bulk_current_data(
        self,
        items: list[str] | list[int],
        *,
        world_or_dc: Optional[DataCenter | World] = None,
        num_listings: int = 10,
        num_history_entries: int = 10,
        item_quality: ItemQuality = ItemQuality.NQ,
        trim_item_fields: bool = False,
    ) -> CurrentData | MultiPart | None:
        """Retrieve a bulk item search of Universalis marketboard data.

        Retrieves the data currently shown on the market board for the requested item and world or data center.
        Up to 100 item IDs can be comma-separated in order to retrieve data for multiple items at once.

        API: https://docs.universalis.app/#current-item-price

        .. note::
            If you want to modify the returned data fields, access `<UniversalisAPI>.multi_item_fields` property and change the format.
            - See `https://docs.universalis.app/` and use their forms to generate a string with the fields you want.

        .. note::
            - If you specify a `<World>`.
                - All `<CurrentData.listings>` and `<CurrentData.recent_history>` will not have the attributes `world_name`.
            - If you specify a `<DataCenter>`.
                - All `<CurrentData.listings>` and `<CurrentData.recent_history>` will have the `world_id` and `world_name` attributes.
                - `<CurrentData>` will also have an additional attribute called `dc_name`.


        .. note::
            You can change the default DataCenter by setting the `<UniversalisAPI>.datacenter` property.


        Parameters
        ----------
        items: :class:`list[str] | list[int]`
            A list of Final Fantasy 14 item ids of int or str type.
        world_or_dc: :class:`DataCenter | World`, optional
            The Final Fantasy 14 World or Datacenter to query your results for, by default `<UniversalisAPI>.datacenter`.
            - The default is a datacenter for the library, `<DataCenter>.Crystal`.
        num_listings: :class:`int`, optional
            The number of listing results for the query, by default 10.
        num_history_entries: :class:`int`, optional
            The number of history results for the query, by default 10.
        item_quality: :class:`ItemQuality`, optional
            The quality of the Item to query, by default `<ItemQuality>.NQ`.
        trim_item_fields: :class:`bool`, optional
            If we want to trim the result fields or not, by default True.

        Returns
        -------
        :class:`list[CurrentData] | CurrentData`
            Returns the JSON response converted into a list of :class:`CurrentData` objects.
            - Will return a single instance of :class:`CurrentData` if a single entry is found in the `items` parameter.

        Raises
        ------
        TypeError
            If the `items` parameter is of the wrong type.

        """
        if world_or_dc is None:
            world_or_dc = self.default_datacenter

        # Not sure if this is needed entirely; but in case someone passes in a wrong data structure.
        if isinstance(items, (str, int)):
            msg = "You must provide a value of type <class list[class int]> or <class list[class str]> not <%s>."
            raise TypeError(msg, type(items))

        query: list[str] = []
        for entry in items:
            if isinstance(entry, int):
                query.append(str(entry))
            else:
                query.append(entry)

        # If we are given a single entry in our list; use the `get_current_data` instead.
        # We could modify the `join` statement below; but this is far easier and provides the same results.
        if len(query) == 1:
            return await self.get_current_data(
                item=query[0],
                world_or_dc=world_or_dc,
                num_listings=num_listings,
                num_history_entries=num_history_entries,
                item_quality=item_quality,
                trim_item_fields=trim_item_fields,
            )

        # results: list[CurrentData] = []
        data: Optional[MultiPart] = None
        for idx in range(0, len(query), 100):
            api_url: str = (
                f"{self.base_api_url}/{world_or_dc.name}/{','.join(query[idx : idx + 100])}?listings={num_listings}"
                f"&entries={num_history_entries}&hq={item_quality.value}"
            )
            # If we need/want to trim fields.
            if trim_item_fields:
                api_url += self.multi_item_fields

            res: MultiPartData = await self._request(url=api_url)
            LOGGER.debug("<%s._get_bulk_current_data>. | DC/World: %s | Num of Items: %s", __class__.__name__, world_or_dc.name, len(items))
            LOGGER.debug("<%s._get_bulk_current_data>. | URL: %s | Response:\n%s", __class__.__name__, api_url, res)

            # results.extend([CurrentData(universalis=self, data=value) for value in res.get("items").values() if "listings" in value])
            data = MultiPart(
                universalis=self,
                resolved_items=[CurrentData(universalis=self, data=value) for value in res.get("items").values() if "listings" in value],
                **res,
            )
        return data

    async def get_history_data(
        self,
        item: str | int,
        *,
        world_or_dc: Optional[World | DataCenter] = None,
        num_listings: int = 10,
        min_price: int = 0,
        max_price: int = 2147483647,
        history: int = 604800000,
    ) -> HistoryData:
        """Retrieve the Universalis marketboard history data for the provided item.

        Retrieves the history data for the requested item and world or data center.

        API: https://docs.universalis.app/#market-board-sale-history

        .. note::
            If you want to modify the returned data fields, access `<UniversalisAPI>.single_item_fields` property and change the format.
            - See `https://docs.universalis.app/` and use their forms to generate a string with the fields you want.


        .. note::
            - If you specify a `<World>`.
                - All `<HistoryData.entries>` will not have the attributes `world_name`.
            - If you specify a `<DataCenter>`.
                - All  `<HistoryData.entries>` will have the `world_id` and `world_name` attributes.
                - `<HistoryData>` will also have an additional attribute called `dc_name`.

        .. note::
            You can change the default DataCenter by setting the `<UniversalisAPI>.datacenter` property.


        Parameters
        ----------
        item: :class:`str | int`
            A Final Fantasy 14 item id of int or str type.
        world_or_dc: :class:`DataCenter | World`, optional
            The Final Fantasy 14 World or Datacenter to query your results for, by default `<UniversalisAPI>.datacenter`.
            - The default is a datacenter for the library, `<DataCenter>.Crystal`.
        num_listings: :class:`int`, optional
            _description_, by default 10.
        min_price: :class:`int`, optional
            _description_, by default 0.
        max_price: :class:`Optional[int]`
            The max price of the item, by default None.
        history: :class:`int`, optional
            The timestamp float value for how far to go into the history; by default 604800000.


        Returns
        -------
        :class:`HistoryData`
            The JSON response converted into a :class:`HistoryData` object.

        """
        if isinstance(item, int):
            item = str(item)

        if world_or_dc is None:
            world_or_dc = self.default_datacenter

        api_url: str = (
            f"{self.base_api_url}/history/{world_or_dc.name}/{item}?entriesToReturn={num_listings}"
            f"&statsWithin={history}&minSalePrice={min_price}&maxSalePrice={max_price}"
        )
        res = await self._request(url=api_url)
        return HistoryData(universalis=self, data=res)

    async def get_bulk_history_data(
        self,
        items: list[str] | list[int],
        *,
        world_or_dc: Optional[World | DataCenter] = None,
        num_listings: int = 10,
        min_price: int = 0,
        max_price: int = 2147483647,
        history: int = 604800000,
    ) -> HistoryData | MultiPart | None:
        """Retrieve the Universalis marketboard history data for the provided item.

        Retrieves the history data for the requested item and world or data center.

        API: https://docs.universalis.app/#market-board-sale-history

        .. note::
            If you want to modify the returned data fields, access `<UniversalisAPI>.single_item_fields` property and change the format.
            - See `https://docs.universalis.app/` and use their forms to generate a string with the fields you want.


        .. note::
            - If you specify a `<World>`.
                - All `<HistoryData.entries>` will not have the attributes `world_name`.
            - If you specify a `<DataCenter>`.
                - All  `<HistoryData.entries>` will have the `world_id` and `world_name` attributes.
                - `<HistoryData>` will also have an additional attribute called `dc_name`.

        .. note::
            You can change the default DataCenter by setting the `<UniversalisAPI>.datacenter` property.


        Parameters
        ----------
        items: :class:`list[str] | list[int]`
            A Final Fantasy 14 item id of int or str type.
        world_or_dc: :class:`DataCenter | World`, optional
            The Final Fantasy 14 World or Datacenter to query your results for, by default `<UniversalisAPI>.datacenter`.
            - The default is a datacenter for the library, `<DataCenter>.Crystal`.
        num_listings: :class:`int`, optional
            _description_, by default 10.
        min_price: :class:`int`, optional
            _description_, by default 0.
        max_price: :class:`Optional[int]`
            The max price of the item, by default None.
        history: :class:`int`, optional
            The timestamp float value for how far to go into the history; by default 604800000.


        Returns
        -------
        :class:`list[HistoryData] | HistoryData`
            The JSON response converted into a list of :class:`HistoryData` objects.
            - Will return a single instance of :class:`HistoryData` if a single entry is found in the `items` parameter.

        Raises
        ------
        TypeError
            If the `items` parameter is of the wrong type.

        """
        # Not sure if this is needed entirely; but in case someone passes in a wrong data structure.
        if isinstance(items, (str, int)):
            msg = "You must provide a value of type <class list[class int]> or <class list[class str]> not <%s>."
            raise TypeError(msg, type(items))

        query: list[str] = []
        for entry in items:
            if isinstance(entry, int):
                query.append(str(entry))
            else:
                query.append(entry)

        if world_or_dc is None:
            world_or_dc = self.default_datacenter

        # If we are given a single entry in our list; use the `get_current_data` instead.
        # We could modify the `join` statement below; but this is far easier and provides the same results.
        # So if the `dcName` key exists, we searched by a DataCenter.
        # otherwise the `worldName` and `worldID` key will exist.
        if len(query) == 1:
            return await self.get_history_data(
                item=query[0],
                world_or_dc=world_or_dc,
                num_listings=num_listings,
                min_price=min_price,
                max_price=max_price,
                history=history,
            )

        # results: list[HistoryData] = []
        data: Optional[MultiPart] = None
        for idx in range(0, len(query), 100):
            api_url: str = (
                f"{self.base_api_url}/history/{world_or_dc.name}/{','.join(query[idx : idx + 100])}?entriesToReturn={num_listings}"
                f"&statsWithin={history}&minSalePrice={min_price}&maxSalePrice={max_price}"
            )
            res: MultiPartData = await self._request(url=api_url)
            LOGGER.debug(
                "<%s._get_bulk_current_data>. | URL: %s | DC/World: %s | Num of Items: %s | Response:\n%s",
                __class__.__name__,
                api_url,
                world_or_dc.name,
                len(items),
                res,
            )
            # results.extend(HistoryData(universalis=self, data=value) for value in res.get("items").values() if "entries" in value)
            data = MultiPart(
                universalis=self,
                resolved_items=[HistoryData(universalis=self, data=value) for value in res.get("items").values() if "entries" in value],
                **res,
            )
        return data

    @staticmethod
    def from_camel_case(
        key_name: str,
        *,
        ignored_keys: Optional[list[str]] = None,
        pre_formatted_keys: Optional[dict[str, str]] = None,
    ) -> str:
        """Resolve a camelCase string to snake_case.

        .. note::
            Adds a `_` before any uppercase char in the `key_name` and then calls `.lower()` on the remaining string.


        .. note::
            The parameter `pre_formatted_keys` the dict structure is `key` = "what to replace" and `value` = "replacement".
            - Example: `ItemID` with `item_id`. Structure would be `{"ItemID": "item_id"}`".


        Parameters
        ----------
        key_name: :class:`str`
            The string to format.
        ignored_keys: :class:`Optional[list[str]]`
            An array of strings that if the `key_name` is in the array it will be ignored and instantly returned unformatted.
            - You may provide your own, or use the constant `IGNORED_KEYS`
        pre_formatted_keys: :class:`Optional[dict[str, str]]`
            An dictionary with keys consisting of values to compare against and the value of the keys to be the replacement string.
            - You may provide your own, or use the constant `PRE_FORMATTED_KEYS`

        Returns
        -------
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
        LOGGER.debug("<%s.from_camel_case> | key_name: %s | Converted: %s", __class__.__name__, key_name, temp)
        return temp

    async def clean_up(self) -> None:
        """Cleans up any open resources."""
        LOGGER.debug("<%s._clean_up> | Closing open `aiohttp.ClientSession` %s", __class__.__name__, self._session)
        if self._session is not None:
            await self._session.close()

    async def __aexit__(  # noqa: D105
        self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[types.TracebackType],
    ) -> None:
        await self.clean_up()

    async def __aenter__(self) -> Self:  # noqa: D105
        return self


class Generic:
    _repr_keys: list[str]

    world_id: Optional[int]
    world_name: Optional[str]
    # This value only exists if you look up results by "Datacenter" instead of "World"
    dc_name: Optional[str]
    _raw: DataTypedAliase | MultiPartData

    def __init__(self, data: DataTypedAliase | MultiPartData) -> None:
        LOGGER.debug("<%s.__init__()> data: %s", __class__.__name__, data)
        self._raw = data

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
    """Base class for mutual attributes and properties for Universalis data.

    .. note::
        Inherits attributes from :class:`Generic`.

    """

    item_id: int
    name: Optional[str]
    nq_sale_velocity: float | int
    hq_sale_velocity: float | int
    regular_sale_velocity: float | int
    stack_size_histogram: dict[str, int]
    stack_size_histogram_nq: dict[str, int]
    stack_size_histogram_hq: dict[str, int]

    _last_upload_time: datetime.datetime | int

    def __hash__(self) -> int:
        return hash(self.item_id)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self.item_id == other.item_id

    @property
    def last_upload_time(self) -> datetime.datetime | int:
        """The last upload time for this endpoint."""
        return self._last_upload_time

    @last_upload_time.setter
    def last_upload_time(self, value: int) -> None:
        # This appears to be including miliseconds.. so we need to divide the value by 1000
        try:
            self._last_upload_time = datetime.datetime.fromtimestamp(
                timestamp=(value / 1000),
                tz=datetime.UTC,
            )
        except ValueError:
            self._last_upload_time = value


class CurrentData(GenericData):
    """A representation of Universalis marketboard current listings data.

    .. note::
        Inherits attributes from :class:`GenericData`.


    .. note::
        Attribute `world_id` and `world_name` only exists when data was fetched by a specified World.



    Attributes
    ----------
    item_id: :class:`int`
        The Final Fantasy 14 item ID.
    name: :class:`Optional[str]`
        The name of the Final Fantasy 14 Item based on `item_id`, if applicable.
        - This will use the language set by :class:`UniversalisAPI.language` property.
    listings: :class:`list[CurrentDataEntries]`
        A current-shown listings, sorted by `timestamp`.
    recent_history: :class:`list[HistoryDataEntries]`
        The currently-shown sales, sorted by `timestamp`.
    world_id: :class:`Optional[int]`
        The Final Fantasy 14 World ID, this will match up to the :class:`World`, if applicable.
    world_name: :class:`Optional[str]`
        The Final Fantasy 14 World name, if applicable.
    dc_name: :class:`Optional[str]`
        The Final Fantasy Datacenter name, if applicable.
    nq_sale_velocity: :class:`float | int`
        The average number of NQ sales per day, over the past seven days (or the entirety of the shown sales, whichever comes first).
        This number will tend to be the same for every item, because the number of shown sales is the same and over the same period.
        This statistic is more useful in historical queries.
    hq_sale_velocity: :class:`float | int`
        The average number of HQ sales per day, over the past seven days (or the entirety of the shown sales, whichever comes first).
        This number will tend to be the same for every item, because the number of shown sales is the same and over the same period.
        This statistic is more useful in historical queries.
    regular_sale_velocity: :class:`float | int`
        The average number of sales per day, over the past seven days (or the entirety of the shown sales, whichever comes first).
        This number will tend to be the same for every item, because the number of shown sales is the same and over the same period.
        This statistic is more useful in historical queries.
    stack_size_histogram: :class:`dict[str, int]`
        A map of quantities to listing counts, representing the number of listings of each quantity.
    stack_size_histogram_nq: :class:`dict[str, int]`
        A map of quantities to NQ listing counts, representing the number of listings of each quantity.
    stack_size_histogram_hq: :class:`dict[str, int]`
        A map of quantities to HQ listing counts, representing the number of listings of each quantity.
    last_upload_time: :class:`datetime | int`
        The last upload time for the provided endpoint,
        otherwise this will be the most recent value from the `world_upload_times` attribute.
    current_average_price: :class:`float | int`
        The average price accross all listings including HQ and NQ.
    current_average_price_nq: :class:`float | int`
        The average price accross all NQ listings.
    current_average_price_hq: :class:`float | int`
        The average price accross all HQ listings.
    average_price: :class:`float | int`
        The average sale price.
    average_price_nq: :class:`float | int`
        TThe average NQ sale price.
    average_price_hq: f:class:`loat | int`
        The average HQ sale price.
    min_price: :class:`int`
        The minimum listing price.
    min_price_nq: :class:`int`
        The minimum NQ listing price.
    min_price_hq: :class:`int`
        The minimum HQ listing price.
    max_price: :class:`int`
        The maximum listing price.
    max_price_nq: :class:`int`
        The maximum NQ listing price.
    max_price_hq: :class:`int`
        The maximum HQ listing price
    world_upload_times: :class:`dict[str, int]`
        The last upload times in milliseconds since epoch for each world in the response, if this is a DC request.
    listings_count: :class:`int`
        The number of listings retrieved for the request. When using the "listings" limit parameter, this may be
        different from the number of sale entries returned in an API response.
    recent_history_count: :class:`int`
        The number of sale entries retrieved for the request. When using the "entries" limit parameter, this may be
        different from the number of sale entries returned in an API response.
    units_for_sale: :class:`int`
        The number of items (not listings) up for sale.
    units_sold: :class:`int`
        The number of items (not sale entries) sold over the retrieved sales.
    has_data: :class:`bool`
        Whether this item has ever been updated. Useful for newly-released items.

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
    _universalis: UniversalisAPI

    def __init__(self, universalis: UniversalisAPI, data: CurrentDCWorld) -> None:
        """Build your JSON response :class:`CurrentData`.

        Represents the data from `<UniversalisAPI>.get_current_data()`.

        Parameters
        ----------
        universalis: :class:`UniversalisAPI`
            A reference to the UniversalisAPI object.
        data: :class:`CurrentDCWorlds`
            The JSON response data as a dict.

        """
        super().__init__(data=data)
        self._universalis = universalis
        self._repr_keys = [
            "world_name",
            "last_upload_time",
            "item_id",
            "regular_sale_velocity",
            "units_for_sale",
            "units_sold",
            "average_price",
            "min_price",
            "listings_count",
            "recent_history_count",
            # "listings", # !This floods any prints.
            # "recent_history", # !This floods any prints.
            "dc_name",
        ]

        # We get it early here, as the for loop won't set it to `None` if the data isn't there.
        # This is being used for `CurrentDataEntries` as fetching "world" data doesn't provide the field to `listings`.
        self.world_name = data.get("worldName", None)

        for key_, value in data.items():
            key = UniversalisAPI.from_camel_case(key_name=key_)

            if isinstance(value, list) and key.lower() == "listings":
                self.listings = value

            # This should handle price formatting.
            elif "price" in key.lower() and (isinstance(value, (int, float))):
                setattr(self, key, f"{round(value):,d}")

            elif key.lower() == "has_data" and isinstance(value, int):
                self.has_data = bool(value)

            else:
                setattr(self, key, value)
        self.name = self._universalis._get_item(self.item_id)  # type: ignore[reportPrivateUsage] # noqa: SLF001

    @property
    def listings(self) -> list[CurrentDataEntries]:
        """A current-shown listings, sorted by `timestamp`."""
        return self._listings

    @listings.setter
    def listings(self, value: list[CurrentListing]) -> None:
        self._listings: list[CurrentDataEntries] = sorted([CurrentDataEntries(data=entry, world_name=self.world_name) for entry in value])

    @property
    def recent_history(self) -> list[HistoryDataEntries]:
        """The most recent sales, sorted by `timestamp`."""
        return self._recent_history

    @recent_history.setter
    def recent_history(self, value: list[HistoryEntries]) -> None:
        self._recent_history: list[HistoryDataEntries] = sorted([HistoryDataEntries(data=entry) for entry in value])


class CurrentDataEntries(Generic):
    """A representation of Universalis marketboard current listing entries data.

    - Comparing `<CurrentDataEntries>` will check quality and timestamp.

    .. note::
        Inherits attributes from :class:`Generic`.


    .. note::
        Attribute `world_id` and `world_name` only exists when data was fetched by a specified World.


    Attributes
    ----------
    price_per_unit: :class:`int`
        The price per unit sold.
    quantity: :class:`int`
        The stack size sold.
    stain_id: :class:`Optional[int]`
        The ID of the dye on this item.
    world_id: :class:`Optional[int]`
        The Final Fantasy 14 World ID, this will match up to the :class:`World`, if applicable.
    world_name: :class:`Optional[str]`
        The Final Fantasy 14 World name, if applicable.
    creator_name: :class:`str`
        The creator's character name.
    creator_id: :class:`Optional[int]`
        A SHA256 hash of the creator's ID.
    hq: :class:`bool`
        Whether or not the item is high-quality.
    is_crafted: :class:`bool`
        Whether or not the item is crafted.
    listing_id: :class:`str`
        The ID of this listing.
    last_review_time: :class:`datetime | int`
        The time that this listing was posted.
    materia: :class:`int`
        The number of materia melded into the item.
    on_mannequin: :class:`bool`
        Whether or not the item is being sold on a mannequin.
    retainer_city: :class:`int`
        The city ID of the retainer.
    retainer_id: :class:`int`
        The retainer's ID.
    retainer_name: :class:`str`
        The retainer's name.
    seller_id: :class:`int`
        A SHA256 hash of the seller's ID.
    total: :class:`int`
        The total price for the item not including tax.
    tax: :class:`int`
        The Gil sales tax (GST) to be added to the total price during purchase.

    """

    price_per_unit: int
    quantity: int
    stain_id: Optional[int]
    world_name: Optional[str]
    world_id: Optional[int]
    creator_name: str
    creator_id: Optional[int]
    hq: bool
    is_crafted: bool
    listing_id: str
    on_mannequin: bool
    retainer_city: int
    retainer_id: int
    retainer_name: str
    seller_id: int
    total: int
    tax: int

    _last_review_time: datetime.datetime | int
    _materia: int

    def __init__(self, data: CurrentListing, *, world_name: Optional[str] = None) -> None:
        """Build your JSON response :class:`CurrentDataEntries`.

        Represents the data from property `<CurrentData>.listings`.

        Parameters
        ----------
        data: :class:`CurrentKeys`
            The JSON response data as a dict.
        world_name: :class:`Optional[str]`
            The Final Fantasy 14 World name, if applicable.

        """
        super().__init__(data=data)
        self._repr_keys = ["world_name", "price_per_unit", "quantity", "hq", "materia", "total", "tax"]

        self.world_name = world_name
        for key_, value in data.items():
            key = UniversalisAPI.from_camel_case(key_name=key_)
            if key.lower() in {"on_mannequin", "is_crafted", "hq"} and isinstance(value, int):
                setattr(self, key, bool(value))

            # This should handle price formatting.
            elif isinstance(value, (int, float)) and ("price" in key.lower() or key.lower() == "total" or key.lower() == "tax"):
                setattr(self, key, f"{round(value):,d}")

            else:
                setattr(self, key, value)

    def __hash__(self) -> int:  # noqa: D105
        return hash(self)

    @property
    def last_review_time(self) -> datetime.datetime | int:
        """The time that this listing was posted."""
        return self._last_review_time

    @last_review_time.setter
    def last_review_time(self, value: int) -> None:
        try:
            self._last_review_time = datetime.datetime.fromtimestamp(timestamp=value, tz=datetime.UTC)
        except ValueError:
            self._last_review_time = value

    @property
    def materia(self) -> int:
        """The number of Materia the item has."""
        return self._materia

    @materia.setter
    def materia(self, value: list[ListingMateria]) -> None:
        # Universalis has them as a dictionary; but the slotID and materiaID values are useless.
        # So just knowing the number of materia in the item is useful enough.
        self._materia = len(value)

    def __eq__(self, other: object) -> bool:
        """Comapres the `<object>.hq` attribute to `self`.

        Parameters
        ----------
        other: :class:`object`
            An object of instance :class:`CurrentDataEntries`.

        Returns
        -------
        :class:`bool`
            If `<CurrentDataEntries>.hq` is equal to `<object>.hq` and `<CurrentDataEntries>.listing_id` is equal to `<object>.listing_id`.

        """
        return (
            isinstance(other, self.__class__) and self.hq == other.hq and self.listing_id == other.listing_id
        )  # and self.price_per_unit == other.price_per_unit

    def __lt__(self, other: object) -> bool:
        """Comapres the `<object>.hq` attribute to `self.hq` and `<object>.last_review_time` > `self.last_review_time`.

        Parameters
        ----------
        other: :class:`object`
            An object of instance :class:`CurrentDataEntries`.

        Returns
        -------
        :class:`bool`
            If `<CurrentDataEntries>.hq` is equal to `<object>.hq`
            and `<CurrentDataEntries>.last_review_time` < `<object>.last_review_time`.

        """
        return (
            isinstance(other, self.__class__)
            and self.hq == other.hq
            and (
                isinstance(self.last_review_time, datetime.datetime)
                and isinstance(other.last_review_time, datetime.datetime)
                and self.last_review_time < other.last_review_time
            )
        )


class HistoryData(GenericData):
    """A representation of Universalis marketboard history data.

    .. note::
        Inherits attributes from :class:`GenericData`.


    .. note::
        Attribute `world_id` and `world_name` only exists when data was fetched by a specified World.


    .. note::
        Attribute `dc_name` only exists when data was fetched by a Datacenter.


    Attributes
    ----------
    item_id: :class:`int`
        The Final Fantasy 14 Item ID.
    name: :class:`Optional[str]`
        The name of the Final Fantasy 14 Item based on `item_id`, if applicable.
        - This will use the language set by :class:`UniversalisAPI.language` property.
    entries: :class:`list[HistoryDataEntries]`
        The historical sales.
    world_id: :class:`Optional[int]`
        The Final Fantasy 14 World ID, this will match up to the :class:`World`, if applicable.
    world_name: :class:`Optional[str]`
        The Final Fantasy 14 World name, if applicable.
    dc_name: :class:`Optional[str]`
        The Final Fantasy Datacenter name, if applicable.
    nq_sale_velocity: :class:`float | int`
        The average number of NQ sales per day, over the past seven days (or the entirety of the shown sales, whichever comes first).
        This number will tend to be the same for every item, because the number of shown sales is the same and over the same period.
        This statistic is more useful in historical queries.
    hq_sale_velocity: :class:`float | int`
        The average number of HQ sales per day, over the past seven days (or the entirety of the shown sales, whichever comes first).
        This number will tend to be the same for every item, because the number of shown sales is the same and over the same period.
        This statistic is more useful in historical queries.
    regular_sale_velocity: :class:`float | int`
        The average number of sales per day, over the past seven days (or the entirety of the shown sales, whichever comes first).
        This number will tend to be the same for every item, because the number of shown sales is the same and over the same period.
        This statistic is more useful in historical queries.
    stack_size_histogram: :class:`dict[str, int]`
        A map of quantities to listing counts, representing the number of listings of each quantity.
    stack_size_histogram_nq: :class:`dict[str, int]`
        A map of quantities to NQ listing counts, representing the number of listings of each quantity.
    stack_size_histogram_hq: :class:`dict[str, int]`
        A map of quantities to HQ listing counts, representing the number of listings of each quantity.
    last_upload_time: :class:`datetime | int`
        The last upload time for the provided endpoint.

    """

    _entries: list[HistoryDataEntries]
    _universalis: UniversalisAPI

    def __init__(self, universalis: UniversalisAPI, data: HistoryDCWorld) -> None:
        """Build your JSON response :class:`HistoryData`.

        Represents the data from `<UniversalisAPI>.get_current_data()`.

        Parameters
        ----------
        universalis: :class:`UniversalisAPI`
            A reference to the UniversalisAPI object.
        data: :class:`CurrentDCWorlds`
            The JSON response data as a dict.

        """
        super().__init__(data=data)
        self._universalis = universalis
        self._repr_keys = ["world_name", "dc_name", "item_id", "last_upload_time"]  # "entries" - Removed to prevent flooding the console.

        # We get it early here, as the for loop won't set it to `None` if the data isn't there.
        # This is being used for `CurrentDataEntries` as fetching "world" data doesn't provide the field to `listings`.
        self.world_name = data.get("worldName", None)

        for key_, value in data.items():
            key: str = UniversalisAPI.from_camel_case(key_name=key_)
            if key.lower() == "entries" and isinstance(value, list):
                self.entries = value
            # This should handle price formatting.
            elif isinstance(value, (int, float)) and "velocity" in key:
                setattr(self, key, f"{round(value):,d}")
            else:
                setattr(self, key, value)
        self.name = self._universalis._get_item(self.item_id)  # type: ignore[reportPrivateUsage] # noqa: SLF001

    @property
    def entries(self) -> list[HistoryDataEntries]:
        """The historical sales."""
        return sorted(self._entries)

    @entries.setter
    def entries(self, value: list[HistoryEntries]) -> None:
        self._entries = [HistoryDataEntries(data=entry, world_name=self.world_name) for entry in value]


class HistoryDataEntries(Generic):
    """A represensation of Universalis marketboard history data entries.

    - Comparing `<HistoryDataEntries>` will check quality and timestamp.

    .. note::
        Inherits attributes from :class:`Generic`.


    .. note::
        Attribute `world_id` and `world_name` only exists when data was fetched by a specified World.


    Attributes
    ----------
    world_id: :class:`Optional[int]`
        The Final Fantasy 14 World ID, this will match up to the :class:`World`, if applicable.
    world_name: :class:`Optional[str]`
        The Final Fantasy 14 World name, if applicable.
    hq: :class:`bool`
        Whether or not the item was high-quality.
    price_per_unit: :class:`int`
        The price per unit sold.
    quantity: :class:`int`
        The stack size sold
    timestamp: :class:`datetime | int`
        When the listing was sold.
    buyer_name: :class:`Optional[str]`
        The buyer's character name. This may be null.
    on_mannequin: :class:`Optional[bool]`
        Whether or not this was purchased from a mannequin. This may be null.

    """

    hq: bool
    price_per_unit: int
    quantity: int
    buyer_name: Optional[str]
    on_mannequin: Optional[bool]
    world_name: Optional[str]
    world_id: Optional[int]
    _timestamp: datetime.datetime | int

    def __init__(self, data: HistoryEntries, *, world_name: Optional[str] = None) -> None:
        """Build your JSON response :class:`HistoryDataEntries`.

        Represents the data from property `<HistoryData>.entries` and `<CurrentData>.recent_history`.

        Parameters
        ----------
        data: :class:`HistoryEntries`
            The JSON response data as a dict.
        world_name: :class:`Optional[str]`
            The Final Fantasy 14 World name, if applicable.

        """
        super().__init__(data=data)
        self._repr_keys = ["world_name", "timestamp", "quantity", "price_per_unit", "hq"]
        self.world_name = world_name

        for key_, value in data.items():
            key: str = UniversalisAPI.from_camel_case(key_name=key_)
            if key.lower() in {"hq", "on_mannequin"} and isinstance(value, int):
                setattr(self, key, bool(value))

            # This should handle price formatting.
            elif isinstance(value, (int, float)) and "price" in key:
                setattr(self, key, f"{round(value):,d}")
            else:
                setattr(self, key, value)

    def __hash__(self) -> int:  # noqa: D105
        return hash(self)

    def __eq__(self, other: object) -> bool:
        """Comapres the `<object>.hq` attribute to `self`.

        Parameters
        ----------
        other: :class:`object`
            An object of instance :class:`HistoryDataEntries`.

        Returns
        -------
        :class:`bool`
            If `<HistoryDataEntries>.hq` is equal to `<object>.hq`.

        """
        return isinstance(other, self.__class__) and self.hq == other.hq and self.price_per_unit == other.price_per_unit

    def __lt__(self, other: object) -> bool:
        """Comapres the `<object>.hq` attribute to `self.hq` and `<object>.timestamp` > `self.timestamp`.

        Parameters
        ----------
        other: :class:`object`
            An object of instance :class:`HistoryDataEntries`.

        Returns
        -------
        :class:`bool`
            If `<HistoryDataEntries>.hq` is equal to `<object>.hq`
            and `<HistoryDataEntries>.timestamp` < `<object>.timestamp`.

        """
        return (
            isinstance(other, self.__class__)
            and self.hq == other.hq
            and (
                isinstance(self.timestamp, datetime.datetime)
                and isinstance(other.timestamp, datetime.datetime)
                and self.timestamp < other.timestamp
            )
        )

    @property
    def timestamp(self) -> datetime.datetime | int:
        """When the listing was sold."""
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value: int) -> None:
        try:
            self._timestamp = datetime.datetime.fromtimestamp(timestamp=value, tz=datetime.UTC)
        except ValueError:
            self._timestamp = value


class MultiPart(Generic):
    """A represensation of a Universalis API response.

    Attributes
    ----------
    items: :class:`list[HistoryData  |  CurrentData]`
        A list of either :class:`HistoryData` or :class:`CurrentData`.
    raw_items: :class:`dict[str, CurrentDCWorld  |  HistoryDCWorld]`
        The JSON response data for each item in `<MultiPartData>.items`.
    item_ids: :class:`list[int]`
        The list of item IDs.
    unresolved_items: :class:`list[int]`
        The list of unresolved item IDs.

    """

    items: list[HistoryData | CurrentData]
    raw_items: dict[str, CurrentDCWorld | HistoryDCWorld]
    item_ids: list[int]
    unresolved_items: list[int]

    __slots__ = ["item_ids", "items", "resolved_items", "unresolved_items"]

    def __init__(self, universalis: UniversalisAPI, resolved_items: list[HistoryData | CurrentData], **data: Unpack[MultiPartData]) -> None:
        """Build your JSON response :class:`MultiPart`.

        Parameters
        ----------
        universalis: :class:`UniversalisAPI`
            A reference to the :class:`UniversalisAPI` object.
        resolved_items: :class:`list[HistoryData  |  CurrentData]`
            The data set built from `<MultiPartData>.items` as a list of either :class:`HistoryData` or :class:`CurrentData`.
        **data: :class:`MultiPartData`
            The JSON response data as a dict.

        """
        super().__init__(data=data)
        self._universalis: UniversalisAPI = universalis
        self._repr_keys = ["item_ids", "unresolved_items"]

        self.item_ids = data["itemIDs"]
        self.unresolved_items = data["unresolvedItems"]
        self.raw_items = data["items"]
        self.items = resolved_items

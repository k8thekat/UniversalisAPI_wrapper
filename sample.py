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

import aiohttp

from async_universalis import CurrentData, CurrentDataEntries, UniversalisAPI, World


async def sample() -> None:
    """Sample code."""
    item_id = 14  # Fire Cluster
    # You only need to pass in a aiohttp.ClientSession if
    # you already have one you are using elsewhere in your code base or have a Pool/etc..
    session = aiohttp.ClientSession()
    market = UniversalisAPI(session=session)

    # You are able to limit the number of listings and history results by setting
    # "num_history" or "num_listing".
    entries = 50

    # You can filter the data prior by only getting a specific Final Fantasy 14 World
    # By default it will search an entire Datacenter which can be accessed via `<UniversalisAPI>.default_datacenter`
    # Or you can pass a WorldEnum object as the `world_or_dc` parameter.
    world = World.Zalera
    cur_data: CurrentData = await market.get_current_data(
        item=item_id,
        num_history_entries=entries,
        num_listings=entries,
        world_or_dc=world,
    )

    # Maybe you want the single cheapest listing, simple call `sort_listings` and get the first entry.
    sorted_list: list[CurrentDataEntries] = sorted(cur_data.listings)
    cheapest: CurrentDataEntries = sorted_list[0]
    # Then the most expensive listing would be at the end.
    # Example: expensive: CurrentDataEntries = sorted_list[-1]
    # CurrentDataEntries has a pre-defined `__repr__()` and `__str__()`` to return useful attributes if desired.
    print(cheapest.world_name, cheapest.price_per_unit, cheapest.quantity)
    # or
    # print(cheapest)

    # You can also get the most expensive entry by setting
    # the reverse parameter to "True". Thus flipping the order of the listings.
    sorted_list = sorted(cur_data.listings, reverse=True)
    expensive: CurrentDataEntries = sorted_list[0]
    print(expensive)

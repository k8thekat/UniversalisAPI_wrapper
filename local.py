# type: ignore
# ruff: noqa
import asyncio
import logging
from logging import Logger
from time import time
from pprint import pformat, pprint
from typing import Any, TYPE_CHECKING

import argparse
import aiohttp
from argparse import Namespace
from pathlib import Path

from universalis import UniversalisAPI, HistoryData, CurrentData, DEFAULT_DATACENTER, DEFAULT_WORLD
from universalis._enums import WorldEnum

local_data_path: Path = Path(__file__).parent.joinpath("moogle_intuition")


async def local_test() -> None:
    stime = time()
    market = UniversalisAPI()
    item_id = 10373
    print(DEFAULT_DATACENTER.name, DEFAULT_WORLD.name)
    data = await market.get_current_data(item=item_id, num_listings=50, num_history_entries=50, world_or_dc=WorldEnum.Zalera)
    sort_list = data.sort_listings()
    print(sort_list[0], sort_list[-1])
    # print(data.stack_size_histogram)
    # res = await market.get_suggested_price(item_id=item_id)
    # print(res)
    _logger.info("Completed local_test() in %s seconds...", format(time() - stime, ".3f"))
    pass


async def build_test() -> None:
    """ """
    pass


async def sample() -> None:
    item_id = 14  # Fire Cluster
    # You only need to pass in a aiohttp.ClientSession if
    # you already have one you are using elsewhere in your code base or have a Pool/etc..
    session = aiohttp.ClientSession()
    universalis = UniversalisAPI(session=session)
    cur_data: CurrentData = await universalis.get_current_data(item=item_id)
    for entry in cur_data.listings:
        # Maybe you only want to buy something over X number.
        if entry.quantity >= 20:
            print(entry.world_name)
    # Maybe you want to get the data only for your world.


class Launcher(Namespace):
    item: bool
    recipe: bool
    local: bool
    build: bool
    log_level: logging.INFO


_parser = argparse.ArgumentParser()
group: argparse._MutuallyExclusiveGroup = _parser.add_mutually_exclusive_group(required=False)
_parser.add_argument(
    "-local",
    help="Run our local_test() function.",
    default=False,
    required=False,
    action="store_true",
)
_parser.add_argument(
    "-build",
    help="Run our build_test() function.",
    default=False,
    required=False,
    action="store_true",
)
group.add_argument(
    "-item",
    help="Run our item_build()",
    default=False,
    required=False,
    action="store_true",
)
group.add_argument(
    "-recipe",
    help="Run our recipe_build()",
    default=False,
    required=False,
    action="store_true",
)
_parsed_args: Launcher = _parser.parse_known_args()[0]

logging.basicConfig()
logging.getLogger().setLevel(level=logging.INFO)
_logger: Logger = logging.getLogger()
_logger.name = "Local Logging - "
file_path: Path = Path(__file__).parent

stime: float = time()

if _parsed_args.local:
    _logger.info("Running local_test()...")
    asyncio.run(local_test())
    _logger.info("Completed in %s seconds...", format(time() - stime, ".1f"))

elif _parsed_args.build:
    _logger.info("Running build_test()...")
    asyncio.run(build_test())
    _logger.info("Completed in %s seconds...", format(time() - stime, ".1f"))

elif _parsed_args.item:
    _logger.info("Running item_build()...")
    asyncio.run(item_build())
    _logger.info("Completed in %s seconds...", format(time() - stime, ".1f"))
elif _parsed_args.item:
    _logger.info("Running recipe_build()...")
    asyncio.run(recipe_build())
    _logger.info("Completed in %s seconds...", format(time() - stime, ".1f"))

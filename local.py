#type: ignore
import argparse
import asyncio
import json
import logging
from argparse import Namespace
from pathlib import Path
from time import time
from typing import Any

import aiohttp

from universalis import  CurrentData, CurrentDataEntries,  HistoryData, ItemQuality, UniversalisAPI, World

local_data_path: Path = Path(__file__).parent.joinpath("moogle_intuition")
items = [
    "4551",
    "5702",
    "5707",
    "5712",
    "5703",
    "5708",
    "5713",
    "18025",
    "18026",
    "18027",
    "25194",
    "25195",
    "25196",
    "26735",
    "26736",
    "26737",
    "33925",
    "33926",
    "33927",
    "33938",
    "33939",
    "33940",
    "41765",
    "41766",
    "41767",
    "10336",
    "12667",
    "28724",
    "25062",
    "25066",
    "24518",
    "24520",
    "24521",
    "26554",
    "21281",
    "27303",
    "27304",
    "27305",
    "16734",
    "16735",
    "15652",
    "5339",
    "14142",
    "14143",
    "14144",
    "14145",
    "14937",
    "12886",
    "12905",
    "12906",
    "12907",
    "12931",
    "12932",
    "12933",
    "12934",
    "12935",
    "12633",
    "15945",
    "16907",
    "16906",
    "17574",
    "19840",
    "19876",
    "21089",
    "21301",
    "21082",
    "22438",
    "22439",
    "22446",
    "23181",
    "24281",
    "24282",
    "31320",
    "29661",
    "29662",
    "29663",
    "29664",
    "29665",
    "29666",
    "29667",
    "29668",
    "31117",
    "31118",
    "31119",
    "31120",
    "31121",
    "31122",
    "31123",
    "31124",
    "31758",
    "31759",
    "31760",
    "31761",
    "31762",
    "31763",
    "31764",
    "31765",
    "33186",
    "33187",
    "33188",
    "33189",
    "33190",
    "33191",
    "33192",
    "33193",
    "27844",
    "27845",
    "27846",
    "27847",
    "27848",
    "28718",
    "29507",
    "29508",
    "29509",
    "29510",
    "29511",
    "31908",
    "31909",
    "31910",
    "31911",
    "31912",
    "39595",
    "36099",
    "36100",
    "36101",
    "36102",
    "36103",
    "37284",
    "38271",
    "38272",
    "38273",
    "38274",
    "38275",
    "39864",
    "39865",
    "39866",
    "39867",
    "39868",
    "16734",
    "16735",
    "15652",
    "5339",
    "14142",
    "14143",
    "14144",
    "14145",
    "14937",
    "12886",
    "12905",
    "12906",
    "12907",
    "12931",
    "12932",
    "12933",
    "12934",
    "12935",
    "12633",
    "8155",
    "8150",
    "15945",
    "16907",
    "16906",
    "17574",
    "12839",
    "19840",
    "19876",
    "21089",
    "21301",
    "21082",
    "22438",
    "22439",
    "22446",
    "23181",
    "24281",
    "24282",
    "31320",
    "33186",
    "33187",
    "33188",
    "33189",
    "33190",
    "33191",
    "33192",
    "33193",
    "27844",
    "27845",
    "27846",
    "27847",
    "27848",
    "28718",
    "29507",
    "29508",
    "29509",
    "29510",
    "29511",
    "31908",
    "31909",
    "31910",
    "31911",
    "31912",
    "10336",
    "28724",
    "12667",
    "26554",
    "21281",
    "25062",
    "25066",
    "24518",
    "24520",
    "24521",
    "27303",
    "27304",
    "27305",
    "45002",
    "5702",
    "5707",
    "5712",
    "5703",
    "5708",
    "5713",
    "18025",
    "18026",
    "18027",
    "25194",
    "25195",
    "25196",
    "26735",
    "26736",
    "26737",
    "33925",
    "33926",
    "33927",
    "33938",
    "33939",
    "33940",
    "41765",
    "41766",
    "41767",
    "38715",
    "38716",
    "38717",
    "38718",
    "38719",
    "38720",
    "38721",
    "38722",
    "38748",
    "38749",
    "38750",
    "38751",
    "38752",
    "38753",
    "38754",
    "38755",
    "39765",
    "39766",
    "39767",
    "39768",
    "39769",
    "39770",
    "39771",
    "39772",
    "41246",
    "41247",
    "41248",
    "41249",
    "41250",
    "41251",
    "41252",
    "41253",
    "29661",
    "29662",
    "29663",
    "29664",
    "29665",
    "29666",
    "29667",
    "29668",
    "31117",
    "31118",
    "31119",
    "31120",
    "31121",
    "31122",
    "31123",
    "31124",
    "31758",
    "31759",
    "31760",
    "31761",
    "31762",
    "31763",
    "31764",
    "31765",
]


async def sample() -> None:
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
    sorted_list: list[CurrentDataEntries] = cur_data.sort_listings()
    cheapest: CurrentDataEntries = sorted_list[0]
    # Then the most expensive listing would be at the end.
    # Example: expensive: CurrentDataEntries = sorted_list[-1]
    # CurrentDataEntries has a pre-defined `__repr__()` and `__str__()`` to return useful attributes if desired.
    print(cheapest.world_name, cheapest.price_per_unit, cheapest.quantity)
    # or
    # print(cheapest)

    # You can also get the most expensive entry by setting
    # the reverse parameter to "True". Thus flipping the order of the listings.
    sorted_list = cur_data.sort_listings(reverse=True)
    expensive: CurrentDataEntries = sorted_list[0]
    print(expensive)


local_data_path: Path = Path(__file__).parent.joinpath("")
response_path: Path = Path(__file__).parent.joinpath("garlandtools/_responses")
LOGGER: logging.Logger = logging.getLogger(__name__)


async def local_test() -> None:
    stime = time()
    # item_id = 10373 # magitek repair materials
    async with UniversalisAPI() as market:
        res = await market.get_current_data(item=10373)
        print(res)

    LOGGER.info("Completed local_test() in %s seconds...", format(time() - stime, ".3f"))
    return


async def build_test() -> None:
    """ """
    item_id = 10373  # Magitek Repair Materials.
    async with UniversalisAPI() as market:
        print(market.default_datacenter.name, market.language.name)
        # item_id = 46058  # Ceremonial Tunic of Healing
        cur_data = await market.get_current_data(
            item=item_id,
            num_listings=100,
            num_history_entries=100,
            item_quality=ItemQuality.NQ,
        )
        print(cur_data.listings)

        history_bulk_data: list[HistoryData] = await market.get_bulk_history_data(items=[3, 4, 5])
        print(history_bulk_data)

        sugg_data = await market.get_suggested_price(item=3)
        print(sugg_data)
        print("BULK ITEM TESTING")
        item_ids = []
        for key, entry in market.item_dict.items():
            if "materia" in entry.get("en").lower():
                item_ids.append(key)
        print(len(item_ids))
        try:
            data = await market.get_bulk_current_data(
                items=item_ids,
                num_listings=100,
                num_history_entries=100,
                item_quality=ItemQuality.NQ,
            )
        except Exception as e:
            print(e)


def ini_load(file: Path, section: str, options: list[str]) -> list[str | None]:
    """Parse an ini file.

    Parameters
    ----------
    file: :class:`Path`
        The file path.
    section: :class:`str`
        The name of the section. `[section_name]`.
    options: :class:`list[str]`
        The options to load as a list.

    Returns
    -------
        The list of options loaded in the same order.

    """
    if file.is_file():
        settings = ConfigParser(converters={"list": lambda setting: [value.strip() for value in setting.split(",")]})
        settings.read(filenames=file)
        res: list[str | None] = []
        for entry in options:
            res.append(settings.get(section=section, option=entry, fallback=None))
        return res
    raise FileNotFoundError("<%s> | Failed to load file. | Path: %s", "local.ini_load", file.as_posix())


def flatten(data: list[Any], new_list: list[Any]) -> list[Any]:
    """Flatten a list."""
    for i in data:
        if isinstance(i, list):
            flatten(i, new_list)
        else:
            new_list.append(i)
    return new_list


def write_data_to_file(
    file_name: str,
    data: bytes | dict[Any, Any] | str | list[Any],
    path: Path = Path(__file__).parent,
    *,
    mode: str = "w+",
    **kwargs: Any,
) -> None:
    """Basic file dump with json handling. If the data parameter is of type `dict`, `json.dumps()` will be used with an indent of 4.

    Parameters
    ----------
    path: :class:`Path`, optional
        The Path to write the data, default's to `Path(__file__).parent`.
    file_name: :class:`str`
        The name of the file, include the file extension.
    data: :class:`bytes | dict | str | list`
        The data to write out to the path and file_name provided.
    mode: :class:`str`, optional
        The mode to open the provided file path with using `<Path.open()>`.
    **kwargs: :class:`Any`
        Any additional kwargs to be supplied to `<json.dumps()>`, if applicable.

    """
    with path.joinpath(file_name).open(mode=mode) as file:
        LOGGER.debug("<%s.%s> | Wrote data to file %s located at: %s", __name__, "write_data_to_file", path, file_name)
        if isinstance(data, bytes):
            file.write(data.decode(encoding="utf-8"))
        elif isinstance(data, dict):
            file.write(json.dumps(data, indent=4, **kwargs))
        elif isinstance(data, list):
            if isinstance(data[0], dict):
                file.write(json.dumps(data, indent=4, **kwargs))
                return
            file.write("\n".join(data))
        else:
            file.write(data)
    LOGGER.info(
        "<%s.%s> | File write successful to path: %s ",
        __name__,
        "write_data_to_file",
        path.joinpath(file_name).as_posix(),
    )


class LogHandler:
    """Discord Multi-line code block formats:
    - https://github.com/highlightjs/highlight.js/blob/main/SUPPORTED_LANGUAGES.md

    """

    cur_log: Path
    code_formats: ClassVar[list[str]] = ["excel", "nc", "ml", " nim", " ps", " prolog", "thor"]
    default_code_format: str = "ps"

    def __init__(self, level: int = logging.INFO, local_dev: bool = True) -> None:
        self.path: Path = Path(__file__).parent.joinpath("logs")
        if self.path.exists() is False:
            self.path.mkdir()
        self.cur_log: Path = Path(__file__).parent.joinpath("logs/log.log")

        logging.basicConfig(
            level=level,
            format="%(asctime)s [%(threadName)s] [%(levelname)s]  %(message)s",
            datefmt="%m/%d/%Y %I:%M:%S %p",
            handlers=[
                logging.StreamHandler(stream=sys.stdout),
                TimedRotatingFileHandler(
                    filename=Path.as_posix(self=self.path) + "/log.log",
                    when="midnight",
                    atTime=datetime.datetime.min.time(),
                    backupCount=4,
                    encoding="utf-8",
                    utc=True,
                ),
            ],
        )


class Launcher(Namespace):
    local: bool
    build: bool
    info: bool
    debug: bool
    upgrade: Optional[bool]


_parser = argparse.ArgumentParser(description="Local arg parse for Python Package development")
_parser.add_argument("-local", help="Run our local_test() function", default=False, required=False, action="store_true")
_parser.add_argument("-build", help="Run our development_text() function", default=False, required=False, action="store_true")
# uv sync -n --upgrade-package foo
_parser.add_argument("--upgrade", help="Run `uv sync -n --upgrade-package package_name`")
# If I want to add a group, this is what I use.
# group: argparse._MutuallyExclusiveGroup = _parser.add_mutually_exclusive_group(required=False)
_parser.add_argument("-info", help="Set the logging level to `INFO`.", default=False, required=False, action="store_true")
_parser.add_argument("-debug", help="Set the logging level to `INFO`.", default=False, required=False, action="store_true")
_parsed_args: Launcher = _parser.parse_known_args()[0]

# Logging section.
LOGGER.name = "Local Logging - "
if _parsed_args.info:
    LogHandler(level=logging.INFO)
elif _parsed_args.debug:
    LogHandler(level=logging.DEBUG)


# Any specific handling of launch args.
# Update `Launcher` class with new args and type def.
stime: float = time()
if _parsed_args.upgrade:
    LOGGER.info("Running uv sync upgrade. | Package: %s", _parsed_args.upgrade)
    subprocess.run(f"uv sync -n --upgrade-package {_parsed_args.upgrade}", check=False)
    LOGGER.info("Completed in %s seconds...", format(time() - stime, ".3f"))

if _parsed_args.local:
    LOGGER.info("Running local_test()...")
    asyncio.run(local_test())
    LOGGER.info("Completed in %s seconds...", format(time() - stime, ".3f"))

if _parsed_args.build:
    LOGGER.info("Build...")
    asyncio.run(build())
    LOGGER.info("Completed in %s seconds...", format(time() - stime, ".3f"))

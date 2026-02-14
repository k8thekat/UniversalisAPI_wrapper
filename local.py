import argparse
import asyncio
import json
import logging
from logging.handlers import TimedRotatingFileHandler
import datetime
from argparse import Namespace
from pathlib import Path
from time import time
from typing import Any, ClassVar, Optional, TYPE_CHECKING
from configparser import ConfigParser
import sys
import subprocess

from async_universalis import  CurrentData, HistoryData, ItemQuality, UniversalisAPI, MultiPart, DataCenter, World, HistoryDataEntries

if TYPE_CHECKING:
    from async_universalis import DataTypedAliase, MultiPartData

local_data_path: Path = Path(__file__).parent.joinpath("local_data")
response_path: Path = Path(__file__).parent.joinpath("garlandtools/_responses")
LOGGER: logging.Logger = logging.getLogger(__name__)



# Umbra: DC = Chaos
async def local_test() -> None:
    stime = time()
    # item_id = 10373 # magitek repair materials
    # await marketboard_parse(DataCenter.Chaos)
    async with UniversalisAPI() as market:
        parse_items(market, world_or_dc=DataCenter.Chaos, stack_size= 2)
    LOGGER.info("Completed local_test() in %s seconds...", format(time() - stime, ".3f"))
    return

async def dev_test() -> None:
    pass


async def marketboard_parse(world_or_dc: DataCenter | World) -> None:
    path = Path(__file__).parent.joinpath("local_data/marketboard_hunt")
    async with UniversalisAPI() as market:
        items: list[int] = await market.get_marketable_items()
        # print(len(items))
        for indx in range(0, len(items)-1, 100):
            r_indx = indx + 100
            try:
                res: HistoryData | MultiPart | None = await market.get_bulk_history_data(items[indx:r_indx], world_or_dc, num_listings=500, history=datetime.timedelta(days=14).total_seconds() )
            except Exception as e:
                res = None
                LOGGER.error("Exception -> | Type: %s | Exc: %s", e)
                pass
           
            if res is None:
                LOGGER.warning("Failure to parse %s - %s of items", indx, r_indx)
                continue
            
            write_data_to_file(f"items_{indx}-{r_indx}{world_or_dc.name}.json", res._raw, path)
            LOGGER.info("Parsed %s -> %s items", indx, r_indx)

def parse_items(self: UniversalisAPI, world_or_dc: World | DataCenter, low_ppu: int = 500, low_velocity: int = 10, stack_size: int = 1) -> None:
    path = Path(__file__).parent.joinpath(f"local_data/marketboard_hunt/{world_or_dc.name}")
    if path.exists() is False:
        LOGGER.error("<%s.%s> | Failed to find a path related to the world_or_dc. | World or DC: %s | Path: %s", "local", "parse_items", world_or_dc, path)
        return
    files = [entry for entry in path.iterdir()]
    files = sorted(files)
    universalis = self
    data: Optional[MultiPart] = None
    for file in files:
        # print(file)
        res: MultiPartData = json.load(file.open())
        if data is None:
            data = MultiPart(
                universalis=universalis,
                resolved_items=[HistoryData(universalis=universalis, data=value) for value in res.get("items").values() if "entries" in value],
                **res,
            )
        else:
            data.items.extend([HistoryData(universalis=universalis, data=value) for value in res.get("items").values() if "entries" in value])
            data.item_ids.extend(res.get("itemIDs"))
            data.unresolved_items.extend(res["unresolvedItems"])

    if data is None:
        LOGGER.error("Data Items is None")
        return
    results: list[str] = []
    # Sort our items by sale velocity, then look at the price per unit/stack size.
    for item in sorted(data.items, key= lambda x: x.regular_sale_velocity, reverse=True):
        if item.regular_sale_velocity > 0 :
            if isinstance(item, HistoryData):
                try:
                    entry: HistoryDataEntries = item.entries[0]
                    # and item.regular_sale_velocity < entry.quantity 
                    if entry.quantity >= stack_size and item.regular_sale_velocity >= low_velocity and entry.price_per_unit >= low_ppu:
                        LOGGER.info("Item Name: %s [%s]",item.name, item.item_id)
                        LOGGER.info("Sale Velocity: %s", item.regular_sale_velocity)
                        LOGGER.info("PPU: %s | Stack Size Sold: %s", entry.price_per_unit, entry.quantity)
                        results.append(f"Item: {item.name}[{item.item_id}] || Sale Velocity: {item.regular_sale_velocity} || PPU: {entry.price_per_unit} || Stack Size: {entry.quantity}")
                except IndexError:
                    continue
    write_data_to_file(f"{world_or_dc.name}_results.md", data=results)

        



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
_parsed_args: Launcher = _parser.parse_known_args()[0] # pyright: ignore[reportAssignmentType]

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

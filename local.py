import argparse
import asyncio
import json
import logging
from logging.handlers import TimedRotatingFileHandler
import datetime
from argparse import Namespace
from pathlib import Path
from time import time
from typing import Any, ClassVar, Optional
from configparser import ConfigParser
import sys
import subprocess

from async_universalis import  CurrentData, HistoryData, ItemQuality, UniversalisAPI, MultiPart, DataCenter, World

local_data_path: Path = Path(__file__).parent.joinpath("local_data")
response_path: Path = Path(__file__).parent.joinpath("garlandtools/_responses")
LOGGER: logging.Logger = logging.getLogger(__name__)


async def local_test() -> None:
    stime = time()
    # item_id = 10373 # magitek repair materials
    items = [1, 10373]
    async with UniversalisAPI() as market:
        res: CurrentData | MultiPart | None = await market.get_bulk_current_data(items, world_or_dc=World.Zalera)
        if isinstance(res, CurrentData):
            "Current Data response."
            print(res.listings)
        elif isinstance(res, MultiPart):
            print("Unresolved", res.unresolved_items)
            print()
            print(res)
            print()
            print(res.resolved_items[0])
            print()
            if isinstance(res.resolved_items[0], CurrentData):
                print(res.resolved_items[0].listings[0])
        else:
            print("Failed", type(res))

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

# Version - 6.0.0-dev - [9801aac](https://github.com/k8thekat/UniversalisAPI_wrapper/commit/9801aac)
## Additional endpoints added!
- Added new endpoints `get_aggregated_data()`, `get_marketable_items()` and `get_market_tax_rates()`.
- Updated docstrings and attribute docs for better info via Intellisense/Linters.
- Updated number of entries for history results from `10` to `25`.
- Added functionality to update the `items.json` file for `item_id` lookups. See `get_update_items()` and `write_data_to_file()`.
- Reorganized some functions.

# Version - 5.0.1-dev - [ad0683b](https://github.com/k8thekat/UniversalisAPI_wrapper/commit/ad0683b)
## Minor fixes for endpoints.
- Changed parameter type for `item_quality` from Enum to Literal strings.
	- Updated logic in `get_current_data()` to handle changes.
- Added minor formatting to the `__repr__()` func all object's use. Formatting the "price" values.

# Version - 5.0.0-dev - [f569ea1](https://github.com/k8thekat/UniversalisAPI_wrapper/commit/f569ea1)
## Minor Update
- Changed from `ItemQuality` to a Literal for getting current marketboard functions.
- Added a `get_worlds` to the DataCenterToWorlds enum.

# Version - 4.1.0-dev - [45a28dc](https://github.com/k8thekat/UniversalisAPI_wrapper/commit/45a28dc)
## Minor fixes
- Added default values for `world_name` and `dc_name` for CurrentDataEntries` and `HistoryDataEntries`.
- Updated documentation.

# Version - 4.0.2-dev - [b07cf6e](https://github.com/k8thekat/UniversalisAPI_wrapper/commit/b07cf6e)
## Reverted formatting on price values.
- Realized doing math on strings.. :cry:

## ISSUES
- Fixed data return on `MultiPart` as it was overwriting the object not returning full results.

# Version - 4.0.1-dev - [28136d2](https://github.com/k8thekat/UniversalisAPI_wrapper/commit/28136d2)
##Changelog generation code formatting typo.


# Version - 4.0.0-dev - [9cd794b](https://github.com/k8thekat/UniversalisAPI_wrapper/commit/9cd794b)
## Development Release: Updated data structure for bulk searching.
- Bulk Item searching was keyed into the resulting items not allowing users to access `unresolved_items`.
	- Added a new data structure. `MultiPart` which houses the entire response.
- Added formatting to currency's and counts.
- Moved sample code to a separate file.
- Updated attributes that are printed via __str__() and __repr__() for `HistoryData` and `CurrentData`.

## # Issues
- Fixed path issue in `settings.json` for Numpy template.

# Version - 3.0.2-dev - [091437d](https://github.com/k8thekat/UniversalisAPI_wrapper/commit/091437d)
## Manifest path issue.
- Missing package files.

# Version - 3.0.1-dev - [a19bc92](https://github.com/k8thekat/UniversalisAPI_wrapper/commit/a19bc92)
## Fixed package data.
- Forgot to update directory.

# Version - 3.0.0-dev - [f7aa97a](https://github.com/k8thekat/UniversalisAPI_wrapper/commit/f7aa97a)
## Pypi release
- Changed project naming to `async_universalis`.
- Updated relevant files.

# Version - 2.0.2-dev - [8c8641a](https://github.com/k8thekat/UniversalisAPI_wrapper/commit/8c8641a)
## Failure to build.
- Fixed typo in pyproject.toml.
- Cleaned up changelog.

# Version - 2.0.1 - [5719619](https://github.com/k8thekat/UniversalisAPI_wrapper/commit/5719619)
## Overall
Merge branch 'development' of https://github.com/k8thekat/UniversalisAPI_wrapper into development
- Changed `init repo` flag to False.


# Version - 2.0.0 - [7094191](https://github.com/k8thekat/UniversalisAPI_wrapper/commit/7094191)
## v2.0.0 - Remove sort listings and suggested pricing.
- Removed two functions as they were out of scope for the library.
- Updated readme to reflect code changes.
- Added logic checks inside bulk search functions to handle single entry lists(if it occurs).
- Added `world_name` attribute to `CurrentDataEntries` and `HistoryDataEntries` when you search by World, as by default they are not included.
- Fixed  typo's in the docstring for UniversalisAPI class.
- Fixed a logic error in the query loops. (oops).
- Updated `MANIFEST.in` to incluide `items.json`.
- Added a `name` attribute to `HistoryData` and `CurrentData`.
- Updated the `TODO.md`.
- Attempting to include `data` files.
- Version bump.
- Fixed error in `pyproject.toml` in an attempt to include a `json` structure needed.
- Added a `MANIFEST` file.
- Fixed some formatting on `debug` logger statements.
- Updated the docstring on `from_camel_case()`.
- Updated legal notice names as they were incorrect.
- Removed un-used TypedDict.
- Added py.typed file.
- Switched to using `uv` instead of manually managing the package.
- Updated `.gitignore`.
- Updated `README.md` with a better example.
- Removed `reqs.txt`
- Removed functionality related to "rate limiting" as it wasn't needed.
- Changed naming of some data response structures and keys.
- Added `get_bulk_history_data()` function.
- Defined keys to be returned when `__repr__()` is called on our listing, history and entry objects.
- Fixed init attributes and naming for `default_datacenter` oops..
- Added debug/warning logger statements to `_request` function.
- Added a few more rules to `[tool.ruff.lint]` to be ignored. Mostly notifications for TODOs.
- Re-organized dunder methods.
- Added a DataTypeAliases for interacting with `_raw` attribute.
- Set up properties to set default language and datacenter when getting results.
- Set up Context manager dunder methods for UniversalisAPI.
- Set up function for closing our local aiohttp.ClientSession.
- Updated the typed dict for bulk data results.
Following ruff and pyright standards
Thanks for the feedback @AbrstractUmbra"
Signed-off-by: Alex Nørgaard <umbra@abstractumbra.dev>
- Basic functionality built for getting `current` and `history` marketboard data.
- Support for `bulk` item searching for `current` data.
- Support for suggested pricing.
- Item lookup to reference item id to an name with minimal language support.

# Version - 0.0.0 [000000]
- Init of repo.
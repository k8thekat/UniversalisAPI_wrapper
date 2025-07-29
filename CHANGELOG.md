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
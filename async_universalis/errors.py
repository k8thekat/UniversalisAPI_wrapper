"""Copyright (C) 2021-2024 Katelynn Cadwallader.

This file is part of Universalis API wrapper.

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

import logging

__all__ = ("UniversalisError",)

LOGGER = logging.getLogger("universalis.errors")


class UniversalisError(Exception):  # noqa: D101
    def __init__(self, status_code: int, url: str, error_reason: str) -> None:  # noqa: D107
        message = "We encountered an error during a request to Universalis in %s. Current URL: %r | Status Code: %s"
        super().__init__(message, error_reason, url, status_code)
        LOGGER.error(message, error_reason, url, status_code)

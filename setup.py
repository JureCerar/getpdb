#!/usr/bin/env python3
# 
# Copyright (C) 2023-2024 Jure Cerar
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from setuptools import setup

try:
    from getpdb import __version__
except:
    print("Could not import package version")
    __version__ = "0.0.0"

setup(
    name="getpdb",
    version = __version__,
    description = "Retrieves molecular structure data from online databases.",
    author="Jure Cerar",
    url="https://github.com/JureCerar/getpdb",
    install_requires=["requests"],
    entry_points={
        "console_scripts": [
            "getpdb = getpdb:main",
        ]
    },
)
# GetPDB

Python script that retrives molecular structure data from online databases (if possible).

Script check following databases:

- [RCSB Protein Data Bank](https://www.rcsb.org/)
- [PubChem](https://pubchem.ncbi.nlm.nih.gov/)
- [AlphaFold Protein Structure Database](https://alphafold.ebi.ac.uk/)

## Installation

Type the following in command line:

```bash
git clone https://github.com/JureCerar/getpdb.git
cd ./getpdb
pip install .
```

## Usage

```text
usage: getpdb [-h] [-V] [-v] [-o TYPE] [-d DIR] code [code ...]

Retrives molecular structure data from online databases (if possible)

positional arguments:
  code               unique stucture identifiers (PDB, CID, UniProt, ...)

options:
  -h, --help         show this help message and exit
  -V, --version      show version information and exit
  -v, --verbose      provide verbose output
  -o TYPE            output file type (supported file types depend on host)
  -d DIR, --dir DIR  path to a directory that will store the files

examples:
  getpdb 1lyz
  getpdb P00698 -o cif
  getpdb 1lyz 2lyz 3lyz -d ./output
```

## Notes

__IMPORTANT:__ This script is not meant for large batch queries (downloads) and should be limited to less than 5 requests per second (otherwise you will be temporarily blocked by server - Error 429). If you have a large data set that you need to compute with, see documentation for that particular database, as there are likely more efficient ways to approach such bulk queries. 

Also take a look at other similar github projects:

- [Wang-Lin-boop/GetPDB](https://github.com/Wang-Lin-boop/GetPDB)
- [gessha/getpdb](https://github.com/gessha/getpdb)
- [xgaia/getPDB](https://github.com/xgaia/getPDB)

## License

This program is licensed under the __GNU General Public License v3.0__

Copyright (C) 2023 [Jure Cerar](https://github.com/JureCerar)

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see http://www.gnu.org/licenses/.

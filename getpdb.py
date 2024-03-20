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

import argparse
import logging
import requests
import gzip
import os
import warnings

__author__ = "Jure Cerar"
__date__ = "20 Mar 2024"
__version__ = "0.2.0"

""" Retrieves molecular structure data from online databases (if possible) """

# Default file type settings
FILE_DEFAULT_SMALL = "sdf"
FILE_DEFAULT_LARGE = "cif"

# Supported databases and file types
DATABASE_HOSTS = {
    "rcsb": ["pdb", "cif", "bcif", "xml"],
    "rcsb-ligand": ["cif", "sdf", "mol2"],
    "pubchem": ["sdf", "json", "xml", "asnt"],
    "alphafold": ["cif", "bcif", "pdb"],
}


class CustomFormatter(logging.Formatter):
    """ Custom color logging formatter """
    format = "[%(asctime)s] %(filename)s:%(lineno)d:%(levelname)s: %(message)s"
    FORMATS = {
        logging.DEBUG: format,
        logging.INFO: format,
        logging.WARNING: "\x1b[33;20m" + format + "\x1b[0m",
        logging.ERROR: "\x1b[31;20m" + format + "\x1b[0m",
        logging.CRITICAL: "\x1b[31;1m" + format + "\x1b[0m",
    }
    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def _getpdb(code, type, host, verify=True) -> list:
    """ Get code from host. Returns file as a list of data """
    if host.lower() == "rcsb":
        # See: https://www.rcsb.org/docs/programmatic-access/file-download-services
        url = f"https://files.rcsb.org/download/{code.upper()}.{type.lower()}.gz"
        logging.info(f"Fetching from '{url}'")
        response = requests.get(url, verify=verify)
        response.raise_for_status()
        data = gzip.decompress(response.content).decode("ascii").split("\n")

    elif host.lower() == "rcsb-ligand":
        # See: https://www.rcsb.org/docs/programmatic-access/file-download-services
        # NOTE: SDF and MOL2 files have two flavors:
        # "model" (crystal structure) of "ideal" (relaxed structure)
        if type.lower() in ("sdf", "mol2"):
            url = f"https://files.rcsb.org/ligands/download/{code.upper()}_ideal.{type.lower()}"
        else:
            url = f"https://files.rcsb.org/ligands/download/{code.upper()}.{type.lower()}"
        logging.info(f"Fetching from '{url}'")
        response = requests.get(url, verify=verify)
        response.raise_for_status()
        data = response.text.split("\n")
    
    elif host.lower() == "pubchem":
        # See: https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/CID/{code}/record/{type.upper()}?record_type=3d"
        logging.info(f"Fetching from '{url}'")
        response = requests.get(url, verify=verify)
        response.raise_for_status()
        data = response.text.split("\n")

    elif host.lower() == "alphafold":
        # See: https://alphafold.ebi.ac.uk/api-docs
        url = f"https://alphafold.ebi.ac.uk/api/prediction/{code.upper()}"
        logging.info(f"Fetching from '{url}'")
        response = requests.get(url, verify=verify)
        response.raise_for_status()
        meta = response.json()[0]
        if type.lower() == "cif":
            url = meta["cifUrl"]
        elif type.lower() == "bcif":
            url = meta["bcifUrl"]
        elif type.lower() == "pdb":
            url = meta["pdbUrl"]
        else:
            raise Exception(f"Invalid file type '{type}'")
        logging.info(f"Fetching from '{url}'")
        response = requests.get(url, verify=verify)
        response.raise_for_status()
        data = response.text.split("\n")
    
    else:
        raise Exception(f"Unknown host '{host}'")
    
    return data


def getpdb(code, type=None, path=None, verify=True):
    """
    DESCRIPTION
        Retrieves molecular structure data from online databases (if possible). 
    USAGE
        getpdb code [ type [, hosts [, path ]]]
    ARGUMENTS
        code = str: A unique structure identifier (PDB, CID, UniProt, ...)
        type = str: File format to fetch. See notes for more info. {default: None}
        path = str: File output directory. 'None' for current dir. {default: None}
        verify = bool: Enable/disable SSL verification when making requests. {default: True}
    NOTES
        Supported file types depend on server. See DATABASE_HOSTS.

        Requires a direct connection to the internet and thus may
        not work behind certain types of network firewalls.
    """

    # Set up defaults
    if not type:
        if len(code) < 4:
            type = FILE_DEFAULT_SMALL
        else:
            type = FILE_DEFAULT_LARGE 
    
    # TODO: Add chain fetch support

    # Fetch data from hosts
    data = list()
    for host in DATABASE_HOSTS.keys():
        # Check if host supports file type
        if type.lower() not in DATABASE_HOSTS.get(host):
            logging.warning(f"Host '{host}' does not support '{type}' type")
            continue           

        try:
            data = _getpdb(code, type, host, verify)
            break
        except Exception as error:
            logging.warning(error)
    
    # Error if no fetch was successful
    if not data:
        logging.error(f"Could not fetch '{code}.{type}'")
        return
    
    # Create file name
    output = f"{code}.{type.lower()}"
    if path:
        output = os.path.join(path, output)
    
    # Write to output file
    logging.info(f"Writing output to '{output}'")
    try:
        if path:
            os.makedirs(path, exist_ok=True)
        handle = open(output, "w")
        for line in data:
            print(line, file=handle)
    except Exception as error:
        logging.error(error)
        return
    
    logging.info("Finished")

    return


def main():   
    # Define command line arguments
    parser = argparse.ArgumentParser(
        description="Retrieves molecular structure data from online databases (if possible)",
        epilog="examples:\n  getpdb 1lyz\n  getpdb P00698 -o cif\n  getpdb 1lyz 2lyz 3lyz -d ./output",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "-V", "--version", action="version",
        version=f"%(prog)s {__version__}",
        help="show version information and exit"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="provide verbose output"
    )
    parser.add_argument(
        "code", nargs="+",
        help="unique structure identifiers (PDB, CID, UniProt, ...)"
    )
    parser.add_argument(
        "-o", dest="type", default=None,
        help="output file type (supported file types depend on host)"
    )
    parser.add_argument(
        "-d", "--dir", default=None,
        help="path to a directory that will store the files"
    )
    parser.add_argument(
        "--no-ssl-verify", dest="verify", action='store_true',
        help="disable SSL verification when making requests"
    )
    args = parser.parse_args()
    
    # Set up logging (i'm a geek)
    fmt = logging.StreamHandler()
    fmt.setFormatter(CustomFormatter())
    log = logging.getLogger()
    log.addHandler(fmt)
    log.setLevel(logging.ERROR)
    if args.verbose:
        log.setLevel(logging.INFO)

    # Ignore warnings
    warnings.filterwarnings("ignore")

    # Lets do this
    for code in args.code:
        getpdb(code, args.type, args.dir, args.verify)
        
    return

if __name__ == "__main__":
    main()
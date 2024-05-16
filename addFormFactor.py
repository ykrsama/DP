#!/usr/bin/env python3

from argparse import ArgumentParser
from pathlib import Path
from distutils.dir_util import copy_tree


COLOUR= {
    "FAIL": '\033[91m',
    'OKGREEN': '\033[92m',
    'OKBLUE': '\033[94m',
    'WARNING': '\033[93m',
    'BOLD': '\033[1m',
    'RESET': '\033[0m',
}


def get_args():
    parser = ArgumentParser(description='Add Form Factor to UFO')
    parser.add_argument('UFO', nargs='?', type=Path, help='Original UFO Model')
    parser.add_argument('-f', '--formfactor', type=str, required=True, help='Form Factor Name')

    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()
    ufo_dir = args.UFO
    ff_name = args.formfactor
    ff_dir = Path(f"FormFactors/{ff_name}")
    # Check if UFO directory exists
    if not ufo_dir:
        print(f'{COLOUR["FAIL"]}UFO directory not provided')
        exit(1)
    if not ufo_dir.exists():
        print(f'{COLOUR["FAIL"]}UFO {ufo_file} does not exist')
        exit(1)
    # Check if form factor directory exists
    if not ff_dir.exists():
        print(f'{COLOUR["FAIL"]}Form Factor {ff_dir} does not exist')
        exit(1)
    # Check if Fortran directory already exists in UFO
    fortran_dir = ufo_dir / "Fortran"
    if fortran_dir.exists():
        print(f'{COLOUR["FAIL"]}Fortran directory already exists in UFO')
        exit(1)

    # Copy Fortran/ form factor files to UFO directory
    copy_tree(str(ff_dir / "Fortran"), str(fortran_dir))

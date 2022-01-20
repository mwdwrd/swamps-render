#!/usr/bin/env python3
"""

"""

__author__ = "Matty Woodward"
__version__ = "1.0.0"
__license__ = "MIT"

import utils
import os
import sys
from pathlib import Path
import logging as log
import voxelize

sys.path.append(os.path.realpath('..'))
dirname = os.path.dirname(__file__)

INPUT_PATH = os.path.join(dirname, "../input/")
OUTPUT_PATH = os.path.join(dirname, "../output/")

def setup_path(artwork):
    output_path = OUTPUT_PATH + str(artwork)
    Path(output_path).mkdir(parents=True, exist_ok=True)
    print("Paths for {} Setup".format(artwork))

def main():
    params = utils.setup_parameters()
    artwork = str(params.artwork)

    setup_path(artwork)
    voxelize.create(artwork)

if __name__ == "__main__":
    main()

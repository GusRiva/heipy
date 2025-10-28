# PYTHON FOR HEIEDITIONS

## Installation

Erstmal ein _Virtual Environment_ unter `venv` anlegen und dann: 
``` 
source venv/bin/activate
```

Dann heipy installieren. Im Verzeichnis `pip install .` oder auf dem Eltern-Verzeichnis `pip install ./heipy`

Oder aus dem pypy Package (Zukunftsmusik)

## heipipe: Das heiEDITIONS-Pipeline Modul

from heipy.heipipe.steps import *

## Synopse

Das Modul für die Synopse ist `heipy.synopse`. Es hat zwei Funktionen: _transform_synopse_ und _create_synopse_. Importiere es so:

`from src.heipy.synopse import transform_synopse, create_synopse`

oder 

`from heipy.synopse import transform_synopse, create_synopse`

__create_synopse__: Creates a synoptic map in the abbreviated syntax (collection of `<link>`) from a list of input TEI-XML files and writes the result to an output file. Has two parameters:

input (list): A list of file paths to the input XML files.

output (str): The file path to the output file where the synopse will be written.

__transform_synopse__: Transforms an abbreviated synoptic map (collection of `<link>`) to an expanded synoptic map (collection of `<linkGrp>`). Has two parameters:

input (str): The path to the input TEI XML file.

output (str): The path where the transformed XML file will be saved.


## CLI options
usage: all.py [-h] [--semantic] [--synoptic] [--sourcedoc] [--debug [OPTION ...]] [text_files ...]

Shared argument parser for my scripts

positional arguments:
  text_files            List of input files

options:
  -h, --help            show this help message and exit
  --semantic, -sem      Semantic pipeline
  --synoptic, -syn      Synoptic pipeline
  --sourcedoc, -sou     SourceDoc pipeline
  --debug [OPTION ...]  Enable debug options. Use without arguments for all options.
                        Available options:
                            • time    - Show execution time for functions.
                            • serial  - Serialize the result of each step into a file to be stored in the tmp directory.

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

## correspSearch
### Short description of the service

The correspSearch portal aggregates metadata on correspondences (letters, postcards, etc.) and thus allows for project- and 
institution-independent research (both via API and web interface).

For that the correspondence's metadata must be collected in the _Correspondence Metadata Interchange Format_ (see below) and made 
available under a URL. After registration with correspSearch, the URL will be regularly harvested, so that current data 
is available on the portal; changes to the metadata are possible at any time.

For heiEditions, the URL is currently:
https://digi.ub.uni-heidelberg.de/editionService/cmif/{name_of_the_edition_as_in_Exist}

For example:
https://digi.ub.uni-heidelberg.de/editionService/cmif/WilamowitzMoellendorff

### Correspondence Metadata Interchange Format (CMIF)
#### Short description
CMIF is a restrictive TEI-XML dialect that underlies the correspSearch portal and is developed by the Special Interest Group Correspondence of the TEI.
* Documentation: https://correspsearch.net/de/dokumentation.html
* Issues: https://github.com/TEI-Correspondence-SIG/CMIF/issues

#### Open Points on CMIF
* Issue opened: @cert is included in examples and schema, but not listed on the CMIF website; currently only value "low" is allowed 
* Why can't publisher contain an idno? -> maybe open an issue?
* In the documentation, "URL" is used as the type value of idno, but in the schema, it's "url" -> adjust in script if updated
* The Geonames ID is obligatory if any ID is to be used for places. Places without id are included in the export but will be mentioned in `cmif.py`'s output. 

### Integration
Use edition WilamowitzMoellendorff as an example for the integration steps: 
* include a file `cmif_export.py` in the `pipelines` directory. This file must contain the list of files to be used for the export:
```python
from heipy.cmif import create_cmif_export
import sys

files = [] # include files here
project_name = sys.argv[1]
output_path = sys.argv[2]
edition_doi = "https://..." # hc:editionWebsiteIdentifier
edition_title = "..."
edition_citation = "..." # hc:RecommendedBibliographicReferenceForEditionWebsite

create_cmif_export(files, project_name, output_path, edition_doi, edition_title, edition_citation)
```
* adjust the control file (e.g. bin/control.sh) to call cmif_export.py and upload the generated CMIF file to exist:
```commandline
    echo "Starting CMIF export"
    outputPath= # e.g.: "converted/cmif/"
    python pipelines/cmif_export.py "$existdir" "$outputPath"
    heipy/bin/existUpload.sh "${outputPath}CMIF_Export.xml" "${existdir}/cmif"
```
* optional: verify the correspondence metadata in the generated file via CMIF check: https://correspsearch.net/de/cmif-check.html
* send an email with the URL to correspsearch@bbaw.de for registration (neccessary only once)



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

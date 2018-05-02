===================
Specdal Info Script
===================

Usage
=====
::

    usage: specdal_info [-h] [--raw] [--list_measure_types]
                        [--list_metadata_fields] [--measure_type MEASURE_TYPE]
                        [--metadata [FIELD [FIELD ...]]] [-n N] [-d]
                        FILE [FILE ...]


Command Line Arguments
======================
    positional arguments:
      ``FILE``                  input directory containing input files

    optional arguments:
      ``-h, --help``            show this help message and exit

      ``--raw``                 output raw dataframe and metadata and exit

      ``--list_measure_types``  list measurement types and exit

      ``--list_metadata_fields``
                            list metadata fields and exit

      ``--measure_type MEASURE_TYPE``
                            type of measurement to read

      ``--metadata [FIELD [FIELD ...]]``
                            specify metadata fields to display
                            
      ``-n N, --N N``           number of spectra to display from head and tail

      ``-d, --debug``


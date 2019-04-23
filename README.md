# Overview
poreception is aimed at helping researchers filter their nanopore data.

poreception is compatible only with Python 3. Run poreception with the following command

```
$ python poreception.py
```

The startup window will prompt you for a HDF5 file with a format produced by `fast_five_converter.py` (see below for details).

poreception will run slowly with large data sets, but it's purpose is to help researchers filter these datasets down to smaller groups. As the data sets are filtered to be smaller, it should run more quickly.

Please submit any issues you find (I expect many) and see TODO.md for things currently being worked on.

### Fast five converter
We ran into an issue with Python 3 and Mac OS that caused pickling to fail with files larger than 2GB. `fast_five_converter.py` is a quick workaround to allow some productivity while we work on a larger solution. `fast_five_converter.py` uses Python 3. Run the command

```
$ python fast_five_converter.py
```
And you will be prompted with a window asking for a pandas dataframe of peptide metadata, a corresponding numpy array of raw data information, and a name for the HDF5 file you wish to create.

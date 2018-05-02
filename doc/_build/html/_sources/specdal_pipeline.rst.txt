=======================
Specdal Pipeline Script
=======================

Specdal provides a command line script ``specdal_pipeline`` for batch
processing of spectral data files in a directory. A typical input to
``specdal_pipeline`` is a directory containing spectral files
(i.e. .asd files), which will be converted into .csv files and figures
of spectra. User can provide arguments to customize the processing
operations (i.e. jump correction, groupby) and output (i.e. .csv file
of group means). This page describes the usage and provides examples.

Usage
=====
::

    usage: specdal_pipeline [-h] [--proximal_reference PATH] [-o PATH]
                            [-op PREFIX] [-of] [-od] [-oi] [-i {slinear,cubic}]
                            [-is SPC] [-s {mean,median,min,max}] [-j {additive}]
                            [-js WVL [WVL ...]] [-jr REF] [-g] [-gs S]
                            [-gi [I [I ...]]] [-gmean] [-gmedian] [-gstd]
                            [-fstd wl0 wl1 n_std [wl0 wl1 n_std ...]]
                            [-fthresh wl0 wl1 LO HI [wl0 wl1 LO HI ...]] [-fwhite]
                            [-fg method] [-fo set] [-yl ymin ymax] [-q] [-f]
                            INPUT_PATH

Command Line Arguments
======================
    
    positional arguments:
      ``INPUT_PATH``            directory containing input files
    
    optional arguments:
      ``-h, --help``            show this help message and exit

      ``--proximal_reference PATH``
                            directory containing proximal reference spectral files

      ``-o PATH, --output_dir PATH``
                            directory to store the csv files and figures

      ``-op PREFIX, --prefix PREFIX``
                            option to specify prefix for output dataset files

      ``-of, --omit_figures``   option to omit output png figures

      ``-od, --omit_data``      option to omit output csv files

      ``-oi, --omit_individual``
                            option to omit output of individual csv file for each spectrum file

      ``-i {slinear,cubic}, --interpolate {slinear,cubic}``
                            specify the interpolation method.
                            method descriptions can be found on scipy docs:
                            https://docs.scipy.org/doc/scipy-0.19.1/reference/generated/scipy.interpolate.interp1d.html

      ``-is SPC, --interpolate_spacing SPC``
                            specify desired spacing for interpolation in nanometers

      ``-s {mean,median,min,max}, --stitch {mean,median,min,max}``
                            specify overlap stitching method;
                            not necessary if data at detector edges does not overlap

      ``-j {additive}, --jump_correct {additive}``
                            specify jump correction method;

      ``-js WVL [WVL ...], --jump_correct_splices WVL [WVL ...]``
                            wavelengths of jump locations

      ``-jr REF, --jump_correct_reference REF``
                            specify the reference detector (e.g. VNIR is 1, SWIR1 is 2)

      ``-g, --group_by``        create groups using filenames``

      ``-gs S, --group_by_separator S``
                            specify filename separator character to define groups

      ``-gi [I [I ...]], --group_by_indices [I [I ...]]``
                            specify the indices of the split filenames to define a group

      ``-gmean, --group_mean``  calculate group means and append to group figures

      ``-gmedian, --group_median``
                            calculate group median and append to group figures

      ``-gstd, --group_std``    calculate group standard deviation and append to group figures

      ``-fstd wl0 wl1 n_std [wl0 wl1 n_std ...], --filter_std wl0 wl1 n_std [wl0 wl1 n_std ...]``
                            Remove spectra from dataset with a pct_reflect over n_std
                            away from the mean between wavelengths wl0 and wl1.
                            Can specify multiple sets of wavenumber ranges and thresholds

      ``-fthresh wl0 wl1 LO HI [wl0 wl1 LO HI ...], --filter_threshold wl0 wl1 LO HI [wl0 wl1 LO HI ...]``
                            Remove spectra from the dataset with a pct_reflect outside
                            (LO,HI)in the wavenumber range wl0 wl1. Can specify multiple
                            sets of wavenumber ranges and thresholds

      ``-fwhite, --filter_white``
                            Remove white reference spectra from dataset

      ``-fg method, --filter_group method``
                            How to combine the wavelengths selected by --filter_group.

      ``-fo set, --filter_on set``
                            What subset of the data to apply filter on (collection, group or both)

      ``-yl ymin ymax, --ylim ymin ymax``
                            Force the y axis of plots to display between ymin and ymax

      ``-q, --quiet``

      ``-f, --force``           if output path exists, remove previous output and run
    
Examples
========
For a description of all command line arguments: ``specdal_pipeline --help``.

To produce an individual plot and textfile for every spectrum file 
in directory ``/path/to/spectra/`` and store the results in ``specdal_output/``:
``specdal_pipeline  -o specdal_output /path/to/spectra/``

To only output whole-dataset images and files:
``specdal_pipeline  -oi -o specdal_output /path/to/spectra/``

To only output images, with no data files:
``specdal_pipeline  -od -o specdal_output /path/to/spectra/``


To group input files by the first 3 underscore-separated components 
of their filename (such that ``foo_bar_baz_001.asd`` and 
``foo_bar_baz_002.asd`` will appear in one group, and
``foo_bar_qux_001.asd`` in another):
``specdal_pipeline -g -gi 0 1 2 -- /path/to/spectra/``

To also output the mean and median of every group of spectra:
``specdal_pipeline -g -gi 0 1 2  -gmean -gmedian /path/to/spectra/``

To remove all white reference spectra from the output dataset (leaves input files intact):
``specdal_pipeline --filter_white /path/to/spectra/``

Filtering (WIP)
===============
specdal_pipeline also provides the option to automatically filter spectra out of
the dataset. This feature is not fully tested and may cause issues.

To remove all  spectra
with a 750-1200 nm reflectance that is greater than 1 standard deviation from the mean,
or with a 500-600 nm reflectance that is greater than 2 standard devations from the mean:

``specdal_pipeline --filter_std 750 1200 1 500 600 2  -- /path/to/spectra/``

To perform the filtering above, and then group the remaining spectra by filename:

``specdal_pipeline --filter_std 750 1200 1 500 600 2 
-g -gi 0 1 2 /path/to/spectra/``

To group the spectra by filename, and then perform filtering on each group:

``specdal_pipeline --filter_std 750 1200 1 500 600 2 
-g -gi 0 1 2  --filter_on group /path/to/spectra/``


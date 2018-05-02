#via https://stackoverflow.com/a/1057534
from os.path import dirname, basename, isfile 
from os.path import abspath, expanduser, splitext, join, split
import glob
from .asd import read_asd
from .sed import read_sed
from .sig import read_sig
from .pico import read_pico

modules = glob.glob(dirname(__file__)+"/*.py")
__all__ = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]

SUPPORTED_READERS = {
        '.asd':read_asd, 
        '.sig':read_sig,
        '.sed':read_sed,
        '.pico':read_pico,
        '.light':read_pico,
        '.dark':read_pico,
}

def read(filepath, read_data=True, read_metadata=True, verbose=False):
    """Calls a reader function based on the extension of the passed filename.
        .asd: read_asd
        .sig: read_sig
        .sed: read_sed
        .pico: read_pico
    """
    ext = splitext(filepath)[1]
    assert ext in SUPPORTED_READERS
    reader = SUPPORTED_READERS[ext]
    return reader(abspath(expanduser(filepath)), read_data,
                  read_metadata, verbose)


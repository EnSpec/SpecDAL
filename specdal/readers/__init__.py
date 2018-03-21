#via https://stackoverflow.com/a/1057534
from os.path import dirname, basename, isfile 
from os.path import abspath, expanduser, splitext, join, split
import glob
modules = glob.glob(dirname(__file__)+"/*.py")
__all__ = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]

from . import *
SUPPORTED_READERS = {
        '.asd':asd.read_asd, 
        '.sig':sig.read_sig,
        '.sed':sed.read_sed,
        '.pico':pico.read_pico,
        '.light':pico.read_pico,
        '.dark':pico.read_pico,
}
def read(filepath, read_data=True, read_metadata=True, verbose=False):
    """
    Calls the appropriate reader based on file extension
    """
    ext = splitext(filepath)[1]
    assert ext in SUPPORTED_READERS
    reader = SUPPORTED_READERS[ext]
    return reader(abspath(expanduser(filepath)), read_data,
                  read_metadata, verbose)

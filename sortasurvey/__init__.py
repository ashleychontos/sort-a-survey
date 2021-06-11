import os

from .observing import *
from .pipeline import *
from .sample import *
from .survey import *
from .utils import *

__all__ = ['cli', 'observing', 'pipeline', 'sample', 'survey', 'utils']

__version__ = '1.0.2'

_ROOT = os.path.abspath(os.getcwd())
INPDIR = os.path.join(_ROOT, 'info')
OUTDIR = os.path.join(_ROOT, 'results')
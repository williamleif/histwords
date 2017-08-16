import sys
import os

tpath = os.path.dirname(os.path.realpath(__file__))
VIZ_DIR=tpath

tpath = os.path.abspath(os.path.join(tpath, "../"))
ROOT_DIR=tpath

sys.path.append(tpath)

from common import *

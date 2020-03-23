from .tree import Paper, Tree
from .timeline import TimelinePlot, TimelineTest

import os
import sys
from matplotlib import pyplot as plt
# Set the current working directory as one directory up
# i.e. where the `main.py` file is located.
os.chdir(os.path.dirname(sys.argv[0]))
# os.chdir('..')

plt.rcParams.update(plt.rcParamsDefault)
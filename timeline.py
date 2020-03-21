# Python program showing Graphical output of a paper tree
# Variables of interest: year of publicaation for timeline
# and the number of citations on the y-axis.
# OPTIONAL: the zise of the markers indicates the degree of the 
# node, equal to the number of references linked to it.

# Links between nodes are rendered using the numpy
# representation of tanh() function 
from typing import List, Set, Dict, Tuple, Optional
import numpy as np 
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

import os
import sys
# Set the current working directory as where the file is located
os.chdir(os.path.dirname(sys.argv[0]))
exec(open('./light_mode.py').read())

class TimelinePlot:

    # Define the format of the links and custom types of data structures
    _Pair_ = Tuple[List[float], List[float]]
    _LinkCollection_ = List[_Pair_]

    def __init__(self, links_collection: _LinkCollection_ = None) -> None:
        # red for numpy.tanh() 
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        self.links_collection = links_collection

    @staticmethod
    def make_link_function(x_nodes: List[float], y_nodes: List[float]) -> Tuple[Line2D, Line2D]:
        in_array  = np.linspace(-np.pi, np.pi, 120)
        out_array = (np.tanh(in_array) + 1)/2 * (y_nodes[1] - y_nodes[0]) + y_nodes[0]
        in_array  = (in_array/np.pi + 1)/2 * (x_nodes[1] - x_nodes[0]) + x_nodes[0]    
        line_object = Line2D(in_array, out_array, color = 'grey', marker = None, alpha = 0.5, linewidth = 1)
        markers = Line2D(x_nodes, y_nodes, color = 'grey', linewidth = 0, marker = 'o', alpha = 0.5, markersize = 2)
        return  line_object, markers

    def plot_nodes(self, x_nodes: List[float], y_nodes: List[float]) -> None:
        line, markers = self.make_link_function(x_nodes, y_nodes)
        self.ax.add_line(line)
        self.ax.add_line(markers)

    def plot_pair(self, pair: _Pair_) -> None:
        self.plot_nodes(*pair)

    def plot_pair_collection(self, pairs):
        for pair in pairs:
            self.plot_pair(pair)

    def make_plot(self) -> None:
        self.plot_pair_collection(self.links_collection)
        self.ax.set_title("Test with numpy.tanh()") 
        self.ax.set_xlabel("Year of publication") 
        self.ax.set_ylabel("Number of citations")
        self.ax.set_ylim(np.min(self.links_collection), np.max(self.links_collection))
        self.ax.set_xlim(np.min(self.links_collection), np.max(self.links_collection))
        self.ax.set_aspect('equal')

def make_pair_collection() -> TimelinePlot._LinkCollection_:
        collection = []
        x_anchors = np.linspace(0, 10, 110)
        y_anchors = np.linspace(3, 10, 20)

        for x_anchor in x_anchors:
            for y_anchor in y_anchors:
                pair = ([x_anchor, x_anchor + np.random.uniform(0,5)], [y_anchor, y_anchor + np.random.uniform(-5,5)])
                collection.append(pair)

        return collection

if __name__ == '__main__':  
    
    collection = make_pair_collection()
    timeline = TimelinePlot(links_collection = collection)
    timeline.make_plot()
    plt.show()

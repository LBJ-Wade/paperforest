# Python program showing Graphical output of a paper tree
# Variables of interest: year of publicaation for timeline
# and the number of citations on the y-axis.
# OPTIONAL: the zise of the markers indicates the degree of the 
# node, equal to the number of references linked to it.

# Links between nodes are rendered using the numpy
# representation of tanh() function 
from typing import List, Set, Dict, Tuple, Optional
import os
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from operator import itemgetter

from .tree import Tree

class TimelinePlot:

    # Define the format of the links and custom types of data structures
    _Pair_ = Tuple[List[float], List[float]]
    _LinkCollection_ = List[_Pair_]

    def __init__(self, links_collection: _LinkCollection_ = None) -> None:
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        self.links_collection = links_collection

    @staticmethod
    def make_link_function(x_nodes: List[float], y_nodes: List[float]) -> Tuple[Line2D, Line2D]:
        in_array  = np.linspace(-np.pi, np.pi, 120)
        out_array = (np.tanh(in_array) + 1)/2 * (y_nodes[1] - y_nodes[0]) + y_nodes[0]
        in_array  = (in_array/np.pi + 1)/2 * (x_nodes[1] - x_nodes[0]) + x_nodes[0]    
        line_object = Line2D(in_array, out_array, color = 'grey', marker = None, alpha = 0.3, linewidth = 0.5)
        markers = Line2D(x_nodes, y_nodes, color = 'grey', linewidth = 0, marker = 'o', alpha = 0.8, markersize = 1)
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

        plot_lims = np.array([
            [min(min(self.links_collection, key=itemgetter(0))[0])-5,
             max(max(self.links_collection, key=itemgetter(0))[0])+5],
            [1,
             max(max(self.links_collection, key=itemgetter(1))[1])*1.5]
        ])
        print(plot_lims)


        self.plot_pair_collection(self.links_collection)
        self.ax.set_title(f"{self.start_paper.get_first_author().split(',')[0]} et al. ({self.start_paper.get_year()})")
        self.ax.set_xlabel("Year of publication") 
        self.ax.set_ylabel("Number of citations")
        self.ax.set_yscale('log')
        self.ax.set_xlim(plot_lims[0])
        self.ax.set_ylim(plot_lims[1])
        # self.ax.set_aspect('equal')


    def set_mode(self, mode: str) -> None:
        plt.style.use(mode)

    @classmethod
    def from_graph(cls, graph: nx.Graph):

        collection = []
        print("Collection of links:\n-----------------------------")

        for edge in graph.edges:
            node_0 = graph.nodes(data=True)[edge[0]]
            node_1 = graph.nodes(data=True)[edge[1]]
            pair = ([node_0['data']['year'], node_1['data']['year']],
                    [node_0['data']['citation_count'], node_1['data']['citation_count']])
            print(pair)
            collection.append(pair)

        return cls(links_collection = collection)

    @classmethod
    def from_tree(cls, tree: Tree):
        graph = tree.read()
        timeline = cls.from_graph(graph)

        # Also capture the start paper as class attribute
        setattr(timeline, 'start_paper', tree.start_paper)

        return timeline

    def save(self) -> None:
        plt.savefig('plottimeline_'+ self.start_paper.bibcode.replace('.', '') + '.png', dpi = 400)
        print(f"TimelinePlot saved in {os.getcwd()} as "
              f"{'plottimeline_'+ self.start_paper.bibcode.replace('.', '') + '.png'}.")



class TimelineTest:

    @staticmethod
    def make_pair_collection() -> TimelinePlot._LinkCollection_:
            collection = []
            x_anchors = np.linspace(0, 10, 110)
            y_anchors = np.linspace(3, 10, 20)

            for x_anchor in x_anchors:
                for y_anchor in y_anchors:
                    pair = ([x_anchor, x_anchor + np.random.uniform(0,5)], [y_anchor, y_anchor + np.random.uniform(-5,5)])
                    collection.append(pair)

            return collection

    def main(self):
        collection = self.make_pair_collection()
        timeline = TimelinePlot(links_collection=collection)
        timeline.set_mode('dark_background')
        timeline.make_plot()
        plt.show()

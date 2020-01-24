import ads
import math
import networkx as nx
import matplotlib.pyplot as plt
from random import random

class Paper:

    def __init__(self, bibcode: str = None):

        if not bibcode:
            raise('Bibcode not specified for this paper.')
        else:
            self.bibcode = bibcode

            # print('References not specified - importing data from NASA/ADS...')
            search = ads.SearchQuery(bibcode=bibcode, fl=['bibcode', 'citation_count',
                                                          'reference', 'first_author',
                                                          'year'])
            for article_found in search:
                self.references = article_found.reference

    def print_info(self):
        print('Bibcode: ', self.bibcode)
        print('References number:', len(self.references))


class Tree(nx.Graph):

    def __init__(self, start_paper = None):

        self.graph = nx.Graph()
        self.start_paper = start_paper

    def __del__(self):

        search_cost = ads.RateLimits('SearchQuery').limits
        print('Remaining daily available searches:  ({}/{})  {} %'.format(search_cost['remaining'], search_cost[
            'limit'], 100*int(search_cost['remaining']) / int(search_cost['limit'])))

    def _add_node(self, node):
        self.graph.add_node(node)

    def _add_edge(self, edge):
        self.graph.add_edge(edge)

    def _add_block(self, top_node, bottom_nodes: list):

        if top_node not in self.graph:
            self._add_node(top_node)

        for bottom_node in bottom_nodes:
            self._add_node(bottom_node)

            if not self.graph.has_edge(bottom_node, top_node):
                self.graph.add_edge(bottom_node, top_node)

    def _add_layer(self, top_node_list, label = None):

        # Associate a label to the particular layer, e.g. tree depth
        if not label == None:
            setattr(Tree._add_layer, 'label', label)

        # Gather all layer references here for recursion
        _all_bottom_nodes = []

        for top_node in top_node_list:

            top_paper = Paper(bibcode = top_node)
            self._add_block(top_paper.bibcode, top_paper.references)
            _all_bottom_nodes.extend(top_paper.references)

        print('{} total references found in this layer.'.format(len(_all_bottom_nodes)))
        return _all_bottom_nodes


    def build_reference_tree(self, depth = None):

        assert depth > -1 and depth < 201, '[Error] The tree depth must be 0 <= depth <= 200.'

        if depth == 0:
            print('[Warning] depth == 0 implies only the input paper in the graph.')
            self.graph.add_node(self.start_paper)

        elif depth == 1:
            print('[Warning] depth == 1 implies only the input paper and its references in the graph.')
            self._add_layer([self.start_paper], label='1')

        else:

            for layer_degree in range(depth + 1):

                print('Initialising layer {}...'.format(layer_degree))

                if layer_degree == 0:
                    _all_bottom_nodes = self._add_layer([self.start_paper], label = '{}'.format(layer_degree))

                else:
                    _all_bottom_nodes = self._add_layer(_all_bottom_nodes, label = '{}'.format(layer_degree))

    def quick_plot(self):

        nx.draw(self.graph, with_labels=True)

    @staticmethod
    def hierarchy_pos(G, root=None, width=1., vert_gap = 0.2, vert_loc = 0, xcenter = 0.5):

        '''
        From Joel's answer at https://stackoverflow.com/a/29597209/2966723.
        Licensed under Creative Commons Attribution-Share Alike

        If the graph is a tree this will return the positions to plot this in a
        hierarchical layout.

        G: the graph (must be a tree)

        root: the root node of current branch
        - if the tree is directed and this is not given,
          the root will be found and used
        - if the tree is directed and this is given, then
          the positions will be just for the descendants of this node.
        - if the tree is undirected and not given,
          then a random choice will be used.

        width: horizontal space allocated for this branch - avoids overlap with other branches

        vert_gap: gap between levels of hierarchy

        vert_loc: vertical location of root

        xcenter: horizontal location of root
        '''
        if not nx.is_tree(G):
            raise TypeError('cannot use hierarchy_pos on a graph that is not a tree')

        if root is None:
            if isinstance(G, nx.DiGraph):
                root = next(iter(nx.topological_sort(G)))  #allows back compatibility with nx version 1.11
            else:
                root = random.choice(list(G.nodes))

        def _hierarchy_pos(G, root, width=1., vert_gap = 0.2, vert_loc = 0, xcenter = 0.5, pos = None, parent = None):
            '''
            see hierarchy_pos docstring for most arguments

            pos: a dict saying where all nodes go if they have been assigned
            parent: parent of this branch. - only affects it if non-directed

            '''

            if pos is None:
                pos = {root:(xcenter,vert_loc)}
            else:
                pos[root] = (xcenter, vert_loc)
            children = list(G.neighbors(root))
            if not isinstance(G, nx.DiGraph) and parent is not None:
                children.remove(parent)
            if len(children)!=0:
                dx = width/len(children)
                nextx = xcenter - width/2 - dx/2
                for child in children:
                    nextx += dx
                    pos = _hierarchy_pos(G,child, width = dx, vert_gap = vert_gap,
                                        vert_loc = vert_loc-vert_gap, xcenter=nextx,
                                        pos=pos, parent = root)
            return pos


        return _hierarchy_pos(G, root, width, vert_gap, vert_loc, xcenter)

    def radial_plot(self):
        pos = self.hierarchy_pos(self.graph, self.start_paper, width=2 * math.pi, xcenter=0)
        new_pos = {u: (r * math.cos(theta), r * math.sin(theta)) for u, (theta, r) in pos.items()}
        nx.draw(self.graph, pos=new_pos, node_size=50)
        nx.draw(self.graph, pos=new_pos, nodelist=[self.start_paper], node_color='blue', node_size=200, with_labels=True,
                font_weight='bold')

    def hierarchy_plot(self):
        pos = self.hierarchy_pos(self.graph, self.start_paper)
        nx.draw(self.graph, pos=pos, with_labels=True, font_weight='bold')





def main():
    ads.config.token = 'your_API_token'

    article_bib = '2019JCAP...06..001B'

    tree = Tree(start_paper = article_bib)
    tree.build_reference_tree(depth = 2)
    tree.hierarchy_plot()
    plt.show()



if __name__ == '__main__':
    main()
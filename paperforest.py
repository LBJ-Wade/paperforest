import ads
import math
import networkx as nx
import matplotlib.pyplot as plt
from random import random

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

def plot_radial_graph(G, first_item):
    pos = hierarchy_pos(G, first_item, width = 2*math.pi, xcenter=0)
    new_pos = {u:(r*math.cos(theta),r*math.sin(theta)) for u, (theta, r) in pos.items()}
    nx.draw(G, pos=new_pos, node_size = 50)
    nx.draw(G, pos=new_pos, nodelist = [first_item], node_color = 'blue', node_size = 200, with_labels=True, font_weight='bold')

def plot_hierarchy_graph(G, first_item):
    pos = hierarchy_pos(G, first_item)    
    nx.draw(G, pos=pos, with_labels=True, font_weight='bold')

def _add_layer(top_nodes: list, graph: nx.classes.graph.Graph):
 """
        Builds one single level tree for this paper.

        :param top_nodes:
            The paper top_nodes (generally the refs from previous papers).

        :type top_nodes:
            list(str)

        :param graph:
            The graph to push the data onto.

        :type graph:
            nx.classes.graph.Graph

        :returns:
            The merged list of references for the current articles.
    """
    
    ref_nodes_MASTER = []
    search = ads.SearchQuery(bibcode=top_nodes)

    for top_node in search:

        # Add the node to the graph if does not exist
        if top_node.bibcode not in graph:
            graph.add_node(top_node.bibcode)

        # Extract ref_nodes and link them to top_nodes
        ref_nodes = top_node.reference
        edges = [(top_node.bibcode, ref_node) for ref_node in ref_nodes]

        # Update the graph
        graph.add_nodes_from(ref_nodes)
        graph.add_edges_from(edges)
        
        # Append all ref_nodes to returned array
        ref_nodes_MASTER.append(ref_nodes)
    
    return ref_nodes_MASTER

def build_reference_tree(start: str, graph: nx.classes.graph.Graph, depth: int = 0):
    """
        Builds a reference tree for this paper.

        :param start:
            The paper bibcode to start from.

        :type start:
            str

        :param graph:
            The graph to push the data onto.

        :type graph:
            nx.classes.graph.Graph

        :param depth:
            The number of levels to fetch in the reference tree.

        :type depth:
            int


        :returns:
            The networkx graph as a list of references to the current article, with pre-loaded
            references down by ``depth``.
    """

    print('Level 0')
    refs_0 = _add_layer([start], graph)
    edges_0 = [(start, ref) for ref in refs_0]

    if depth > 0:
        for i in range(1, depth+1):            
            print('Level {}'.format(i))
            refs_1 = _add_layer(refs_0, graph)

            # Update the input for _add_layer method
            refs_0 = refs_1
    
    return graph
    

def main():
    ads.config.token = '73GO3Lmt6NRR59aoLzs9to6CsJX2thnB6Kg4bVNt'

    article_bib = ' 2019JCAP...06..001B '

    graph = nx.DiGraph()
    graph = build_reference_tree(article_bib, graph, depth=3)
    plot_hierarchy_graph(graph, article_bib)
    plt.show()

if __name__ == '__main__':
    main()
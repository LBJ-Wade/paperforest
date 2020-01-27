import paperforest as pf

import os
import ads
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

def main():

    # Import your ADS token
    ads.config.token = 'yourToken'

    # Specify the paper to start from
    article_bib = '1985ApJS...57...77S'

    # Create tree and save as NetworkX graph if not existent
    if not os.path.isfile('./' + article_bib + '.gpickle'):
        tree = pf.Tree(start_paper = article_bib)
        tree.build_reference_tree(depth = 2)
        tree.save(article_bib)

    # Pickle-back the graph
    G = nx.read_gpickle(article_bib + '.gpickle')

    # Plot the graph
    pos = nx.spring_layout(G)
    nx.draw_networkx_nodes(G, pos, node_size=3, node_color='orange')
    nx.draw_networkx_edges(G, pos, alpha=0.3, edge_color='lime')
    plt.axis('off')
    plt.savefig('graph_' + article_bib + '.png', dpi = 300)


    # Plot the degree distribution
    plt.clf()
    degree_sequence = sorted([d for n, d in G.degree()], reverse=True)  # degree sequence
    bins = np.logspace(0, 3, 20)
    plt.hist(degree_sequence, bins=bins, color='b')
    plt.title("Degree Histogram")
    plt.ylabel("Count")
    plt.xlabel("Degree")
    plt.xscale('log')
    plt.yscale('log')
    plt.savefig('degree_distribution_' + article_bib + '.png', dpi = 250)


if __name__ == '__main__':
    main()
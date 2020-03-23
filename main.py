import paperforest as pf

import os
import ads
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt


if __name__ == '__main__':

    # Import your ADS token
    ads.config.token = ''

    # Specify the paper to start from
    paper = pf.Paper(bibcode='2018MNRAS.479.4028B')
    tree  = pf.Tree(start_paper=paper, depth=1)

    # Create tree and save as NetworkX graph if not existent
    if not tree.exists():
        tree.build_reference_tree()
        tree.save()

    # Create a Timeline plot (year of publications VS num of citations)
    timeline = pf.TimelinePlot.from_tree(tree)
    timeline.make_plot()
    timeline.save()
    plt.clf()

    plt.close()

    # Plot the degree distribution
    degree_sequence = sorted([d for n, d in tree.read().degree()], reverse=True)  # degree sequence
    bins = np.logspace(0, 3, 20)
    plt.hist(degree_sequence, bins=bins, color='b')
    plt.title("Degree Histogram")
    plt.ylabel("Count")
    plt.xlabel("Degree")
    plt.xscale('log')
    plt.yscale('log')
    plt.savefig('degree_distribution_' + paper.bibcode.replace('.', '') + '.png', dpi=400)



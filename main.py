import paperforest as pf

import os
import ads
import networkx as nx
import matplotlib.pyplot as plt

def main():

    # Import your ADS token
    ads.config.token = 'enter-your-token-here'

    # Specify the paper to start from
    article_bib = '1985ApJS...57...77S'

    # Create tree and save as NetworkX graph if not existent
    if not os.path.isfile('./' + article_bib + '.gpickle'):
        tree = pf.Tree(start_paper = article_bib)
        tree.build_reference_tree(depth = 1)
        tree.save(article_bib)

    # Pickle-back the graph and plot it
    G = nx.read_gpickle(article_bib + '.gpickle')
    layout = nx.spring_layout(G, iterations=50)
    nx.draw(G, layout,
            with_labels=True, node_color='orange',
            node_size=400, edge_color='black', linewidths=1,
            font_size=7)

    plt.axis('off')
    plt.savefig(article_bib + '.png', dpi = 300)
    plt.show()


if __name__ == '__main__':
    main()
import ads
import os
import networkx as nx
from typing import List, Set, Dict, Tuple, Optional
from matplotlib import pyplot as plt


class Paper:

    requirements = ['bibcode', 'citation_count', 'reference', 'first_author', 'year']

    def __init__(self, bibcode: str = None):

        assert bibcode is not None, "Bibcode not specified for this paper."
        self.bibcode = bibcode

        try:            
            search = ads.SearchQuery(bibcode = bibcode, fl = self.requirements)

        except:
            setattr(Paper, 'reference', [])
            setattr(Paper, 'reference_count', 0)
            setattr(Paper, 'citation_count', 0)
            setattr(Paper, 'first_author', '')
            setattr(Paper, 'year', 0)

        else:
            for article_found in search:
                setattr(Paper, 'reference', article_found.reference)
                setattr(Paper, 'citation_count', article_found.citation_count)
                setattr(Paper, 'first_author', article_found.first_author)
                setattr(Paper, 'year', int(article_found.year))

        # The ADS API returns `none` if no references exist: may cause errors
        if self.reference is None:
            self.reference = []
            setattr(Paper, 'reference_count', len(self.reference))
    
    def __str__(self):
            return f"\tPaper {self.bibcode}\t|\t{self.first_author:<20} ({self.year:<4})   |   References: " \
                f"{len(self.reference):<5}   |   Citations: {self.citation_count:<5}"

    def get_bibcode(self):
        return self.bibcode
    
    def get_reference(self):
        return self.reference
    
    def get_citation_count(self):
        return self.citation_count

    def get_first_author(self):
        return self.first_author
    
    def get_year(self):
        return self.year

    def get_info(self):
        return {
            'bibcode'        : self.bibcode,
            'citation_count' : self.citation_count,
            'reference'      : self.reference,
            'first_author'   : self.first_author,
            'year'           : self.year
        }


class Tree(nx.Graph):

    def __init__(self, start_paper: Paper = None, depth: int = 1):
        self.graph = nx.Graph()
        self.start_paper = start_paper
        self.depth = depth
        print("Start paper:\n", str(self.start_paper), "\n")

    def __del__(self):
        search_cost = ads.RateLimits('SearchQuery').limits
        print('Remaining daily available searches:  ({}/{})  {} %'.format(search_cost['remaining'], 
                search_cost['limit'], 100*int(search_cost['remaining']) / int(search_cost['limit'])))

    def __str__(self):
        return f"Nodes:\n{self.graph.nodes(data=True)}\n\nEdges:\n{self.graph.edges(data=True)}"
            
    def _add_node(self, paper: Paper):
        self.graph.add_node(paper.bibcode, data = paper.get_info())

    def _add_edge(self, bottom_paper: Paper, top_paper: Paper):
        self.graph.add_edge(bottom_paper.bibcode, top_paper.bibcode)

    def _add_block(self, top_node : Paper):

        if top_node.bibcode not in self.graph:
            self._add_node(top_node)

        reference_list = []

        for bottom_bib in top_node.reference:
            assert bottom_bib is not None and type(bottom_bib) is str
            bottom_node = Paper(bibcode=bottom_bib)
            print(str(bottom_node))
            self._add_node(bottom_node)
            reference_list.append(bottom_node)

            if not self.graph.has_edge(bottom_node.bibcode, top_node.bibcode):
                self._add_edge(bottom_node, top_node)
            del bottom_node

        return reference_list

    def _add_layer(self, top_node_list : List[Paper], label : int = None):

        # Gather all layer references here for recursion
        _all_bottom_nodes = []
        for top_node in top_node_list:
            _bottom_nodes = self._add_block(top_node)

            if label < self.depth +1:
                _all_bottom_nodes.extend(_bottom_nodes)

        print(f"Layer {label} has {len(_all_bottom_nodes)} references in total.\n")
        return _all_bottom_nodes


    def build_reference_tree(self):

        if self.depth == 0:
            print('[Warning] depth == 0 implies only the input paper in the graph.')
            self.graph.add_node(self.start_paper)

        elif self.depth == 1:
            print('[Warning] depth == 1 implies only the input paper and its references in the graph.')
            self._add_layer([self.start_paper], label = 1)

        else:
            _all_refs = []
            for layer_degree in range(self.depth):
                print('Initialising layer {}...'.format(layer_degree))
                if layer_degree == 0:
                    _all_refs = self._add_layer([self.start_paper], label = layer_degree)
                else:
                    _top_input = _all_refs
                    _all_refs = self._add_layer(_top_input, label = layer_degree)

    def save(self) -> None:
        nx.write_gpickle(self.graph, self.start_paper.bibcode.replace('.', '') + '.gpickle')
        print(f"Tree saved in {os.getcwd()} as {self.start_paper.bibcode.replace('.', '') + '.gpickle'}.")

    def exists(self) -> bool:
        return os.path.isfile(self.start_paper.bibcode.replace('.', '') + '.gpickle')

    def read(self) -> nx.Graph:
        if self.exists():
            return nx.read_gpickle(self.start_paper.bibcode.replace('.', '') + '.gpickle')
        else:
            raise FileNotFoundError

    def clear(self) -> None:
        if self.exists():
            os.remove(self.start_paper.bibcode.replace('.', '') + '.gpickle')


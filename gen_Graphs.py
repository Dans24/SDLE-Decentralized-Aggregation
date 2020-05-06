import networkx as nx
import random


def random_graph(n):
    graph = nx.Graph()
    graph.add_nodes_from(range(n))
    while not nx.is_connected(graph):
        a = random.randrange(n)
        b = random.randrange(n)
        if a != b and not graph.has_edge(a, b):
            graph.add_edge(a, b)
    return graph


def preferential_graph(n):
    graph = nx.Graph()
    graph.add_nodes_from(range(n))
    array = list(range(n))
    while not nx.is_connected(graph):
        a = random.randrange(n)
        b = random.choice(array)
        if a != b and not graph.has_edge(a, b):
            graph.add_edge(a, b)
            array.extend([a, b])
    return graph

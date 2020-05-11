import networkx as nx
import random
import math


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


def twod_graph(n, ray):
    graph = nx.Graph()
    graph.add_nodes_from(range(n))
    positions = []
    for _ in range(n):
        positions.append([random.randrange(n),random.randrange(n)])
    for a in range(n):
        connected = False
        while not connected:
            if not hasNeighbours(graph, ray, positions, a):
                positions[a] = [random.randrange(n),random.randrange(n)]
                continue
            connected = True
    return graph

def hasNeighbours(graph, ray, positions, a):
    result = False
    for b in range(10):
        if a != b and not graph.has_edge(a, b):
            distance = math.sqrt(((positions[a][0]-positions[b][0])**2)+((positions[a][1]-positions[b][1])**2))
            if distance <= ray:
                graph.add_edge(a, b)
                result = True
    return result


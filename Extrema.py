import discrete_event_simulator, gen_Graphs
import random
import statistics
import logging
import logging.config
import pylab

from Simulator_Statistics import Simulator_Analyzer


class ExtremaNode(discrete_event_simulator.Node):
    def __init__(self, node, neighbours, K: int, T: int, drop_chance = 0.0, r: int = 1):
        self.node = node
        self.neighbours = neighbours
        self.K = K
        self.T = T
        self.r = r
        self.drop_chance = drop_chance
        
    def start(self):
        self.nonews = 0
        self.converged = False
        self.x = []
        for _ in range(self.K):
            self.x.append(self.r * random.expovariate(1))
        
        msgs = ([], [])
        for neighbour in self.neighbours:
            if random.random() > self.drop_chance:
                msgs[0].append(discrete_event_simulator.Message(self.node, neighbour, self.x))
        return msgs

    def handle_message(self, message: discrete_event_simulator.Message, time: int):
        changed = False
        for i in range(self.K):
            if message.body[i] < self.x[i]:
                self.x[i] = message.body[i]
                changed = True
        if changed:
            self.nonews = 0
        else:
            self.nonews += 1
        if self.nonews >= self.T:
            if self.converged:
                N = (self.K - 1) / sum(self.x) # unbiased estimator of N with exponential distribution
                variance = (N**2) / (self.K - 2)
                # print("Nodes: " , N, " Variance: ", variance)
            self.converged = True
        else:
            msgs = ([], [])
            for neighbour in self.neighbours:
                if random.random() > self.drop_chance:
                    msgs[0].append(discrete_event_simulator.Message(self.node, neighbour, self.x))
            return msgs
        return [], []

    def handle_event(self, event, time: int):
        return None
    
class UnstableNetworkSimulator(discrete_event_simulator.Simulator):
    def __init__(self, nodes, distances, max_dist = 0, timeout = 0, network_change_time = 1, debug = False):
        super().__init__(nodes, distances)
        self.max_dist = max_dist
        self.timeout = timeout
        self.network_change_time = network_change_time
        self.debug = debug

    def handle_simulator_event(self, event):
        if self.debug:
            print("Update network")
        graph = gen_Graphs.random_graph(len(self.nodes))
        for node in graph.nodes:
            self.nodes[node].neighbours = list(graph.neighbors(node))
            for neighbour in self.nodes[node].neighbours:
                self.distances[node][neighbour] = random.randrange(1, self.max_dist + 2)
                if self.debug:
                    print(str(node) + " -> " + str(neighbour) + " = " + str(self.distances[node][neighbour]))
            self.distances[node][node] = self.timeout
        return [(random.randrange(1, self.network_change_time + 2), discrete_event_simulator.SimulatorEvent(True))]

def simulatorGenerator(n, K, T, max_dist = 0, timeout = 0, fanout = None, debug = False):
    graph = gen_Graphs.random_graph(n)
    dists = [[0 for _ in range(n)] for _ in range(n)] # fill matrix with zeroes
    nodes = []
    for node in graph.nodes:
        neighbours = list(graph.neighbors(node))
        graph_node = ExtremaNode(node, neighbours, K, T, 0.0)
        nodes.append(graph_node)
    simulator = UnstableNetworkSimulator(nodes, dists, max_dist=max_dist, timeout=timeout, network_change_time=1, debug=True)
    simulator.start()
    return simulator


analyser = Simulator_Analyzer()
range_n = range(5, 10)
simulators = []
for n in range_n:
    simulators.append(simulatorGenerator(n, 15, 15, max_dist=20))

analyser.analyze_variable("Number of Nodes", range_n, simulators, 5, title="Extrema Propagation with Termination")

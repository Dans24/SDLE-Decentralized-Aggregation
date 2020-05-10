import discrete_event_simulator, gen_Graphs
import random
import statistics

class ExtremaNode(discrete_event_simulator.Node):
    def __init__(self, node, neighbours, K: int, T: int, drop_chance=0.0):
        self.node = node
        self.neighbours = neighbours
        self.K = K
        self.T = T
        self.drop_chance = drop_chance
        
    def start(self):
        self.nonews = 0
        self.converged = False
        self.x = []
        for _ in range(self.K):
            self.x.append(random.expovariate(1))
        
        msgs = []
        for neighbour in self.neighbours:
            if random.random() > self.drop_chance:
                msgs.append(discrete_event_simulator.Message(self.node, neighbour, self.x))
        return msgs

    def handle_message(self, message: discrete_event_simulator.Message):
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
            return []
        else:
            msgs = []
            for neighbour in self.neighbours:
                if random.random() > self.drop_chance:
                    msgs.append(discrete_event_simulator.Message(self.node, neighbour, self.x))
            return msgs

    def handle_event(self, event):	
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
                #if self.debug:
                    # print(str(node) + " -> " + str(neighbour) + " = " + str(self.distances[node][neighbour]))
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

def floods(n_iter):
    n = 1000
    K = 1
    T = 1000
    times = []
    n_messages = []
    for _ in range(n_iter):
        simulator = simulatorGenerator(n, K, T)
        num_events = len(simulator.get_message_events())
        print(num_events)
        last_event = simulator.get_events()[num_events - 1]
        (last_time, _) = last_event
        n_messages.append(num_events)
        times.append(last_time)
    print("Tempo mínimo: " + str(min(times)))
    print("Tempo médio: " + str(statistics.mean(times)))
    print("Tempo máximo: " + str(max(times)))
    print()
    print("Numero mensagens minimo: " + str(min(n_messages)))
    print("Numero mensagens médio: " + str(statistics.mean(n_messages)))
    print("Numero mensagens máximo: " + str(max(n_messages)))


floods(20)
print("Fim!!")

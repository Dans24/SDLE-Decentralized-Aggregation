import discrete_event_simulator, gen_Graphs
import random
import statistics

class ExtremaNode(discrete_event_simulator.Node):
    def __init__(self, node, neighbours, K: int, T: int, drop_chance = 0.0, r = 1, timeout = 1):
        self.node = node
        self.neighbours = neighbours
        self.K = K
        self.T = T
        self.r = r
        self.drop_chance = drop_chance
        self.timeout = timeout
        self.timeout_time = 0
        
    def start(self):
        # TODO: Começar em apenas 1?
        self.nonews = 0
        self.converged = False
        self.x = []
        for _ in range(self.K):
            self.x.append(self.r * random.expovariate(1))
        return (self.broadcast_messages(self.x), self.set_timeout(0, None))

    def handle_message(self, message: discrete_event_simulator.Message, time):
        self.time = time
        changed = False
        for i in range(self.K):
            if message.body[i] < self.x[i]:
                self.x[i] = message.body[i]
                changed = True
        if changed:
            self.nonews = 0
        else:
            self.nonews += 1
        # TODO: basear o T em relação ao número de vizinhos?
        if self.nonews >= self.T:
            # TODO: Os nodos convergidos não estão a convergir, fazer o teste só para 1?
            if not self.converged:
                N = (self.K - 1) / sum(self.x) # unbiased estimator of N with exponential distribution
                variance = (N**2) / (self.K - 2)
                print("Node ", self.node, " :: Result: " , N, " ± ", (variance**(1/2)) * 3)
                # TODO: guardar os valores de N
            self.converged = True
            msgs = self.broadcast_messages(self.x)
            return ([], [])
        # TODO: enviar mensagens apenas quando existe alteração?
        else:
            if time >= self.timeout_time and not self.converged:
                timeout_event = self.set_timeout(time, None)
            else:
                timeout_event = []
            msgs = self.broadcast_messages(self.x)
            return (msgs, timeout_event)

    def handle_event(self, event: discrete_event_simulator.SelfEvent, time):
        if self.converged:
            return ([], [])
        if time >= self.timeout_time:
            print("TIMEOUT " + str(self.node))
            msgs = self.broadcast_messages(self.x)
            timeout_event = self.set_timeout(time, None)
            return (msgs, timeout_event)
        else:
            print("FAKE TIMEOUT " + str(self.node))
            return ([], self.set_timeout(time, None))

    def broadcast_messages(self, body):
        msgs = []
        for neighbour in self.neighbours:
            if random.random() > self.drop_chance:
                msgs.append(discrete_event_simulator.Message(self.node, neighbour, body))
        return msgs

    def set_timeout(self, time, body):
        self.timeout_time = time + self.timeout
        return [(self.timeout, discrete_event_simulator.SelfEvent(self.node, body))]
    
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
        graph_node = ExtremaNode(node, neighbours, K, T, drop_chance = 0.0, timeout=max_dist)
        nodes.append(graph_node)
    simulator = UnstableNetworkSimulator(nodes, dists, max_dist=max_dist, timeout=timeout, network_change_time=10, debug=True)
    simulator.start()
    return simulator

def floods(n_iter):
    n = 10
    K = 100
    T = 20
    times = []
    n_messages = []
    for _ in range(n_iter):
        simulator = simulatorGenerator(n, K, T, max_dist=20)
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

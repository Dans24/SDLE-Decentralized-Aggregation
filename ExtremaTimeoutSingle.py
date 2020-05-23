import discrete_event_simulator, gen_Graphs
import random
import statistics
from Simulator_Statistics import Simulator_Analyzer

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
        self.converged = False
        self.nonews = 0
        self.x = []
        for _ in range(self.K):
            self.x.append(self.r * random.expovariate(1))
        return (self.broadcast_messages(self.x), self.set_timeout(0, None))

    def handle_message(self, message: discrete_event_simulator.Message, time):
        self.time = time
        if self.converged: # Já sabe que o sistema convergiu por isso não precisa de enviar mensagem para todos
            return (self.direct_message(message.src, "CONVERGED"), [])
        if message.body == "CONVERGED": # Acaba de saber que o sistema convergiu e avisa a todos
            print(message.to, "CONVERGED")
            self.converged = True
            msgs = self.broadcast_messages("CONVERGED")
            return (msgs, [])
        # atualiza o corpo
        for i in range(self.K):
            self.x[i] = message.body[i]
        # TODO: basear o T em relação ao número de vizinhos?
        if time >= self.timeout_time:
            timeout_event = self.set_timeout(time, None)
        else:
            timeout_event = []
        msgs = self.broadcast_messages(self.x)
        print(time, message.to)
        return (msgs, timeout_event)

    def handle_event(self, event: discrete_event_simulator.SelfEvent, time):
        if time < self.timeout_time: # Existe um timeout posterior, por isso, este deixa de ter efeito
            print("FAKE TIMEOUT " + str(self.node))
            return ([], self.set_timeout(time, None))
        print("TIMEOUT " + str(self.node))
        msgs = self.broadcast_messages(self.x)
        timeout_event = self.set_timeout(time, None)
        return (msgs, timeout_event)

    def broadcast_messages(self, body):
        msgs = []
        for neighbour in self.neighbours:
            if random.random() > self.drop_chance:
                msgs.append(discrete_event_simulator.Message(self.node, neighbour, body))
        return msgs

    def direct_message(self, to, body):
        if to in self.neighbours: # É vizinho, pode mandar a mensagem
            return [discrete_event_simulator.Message(self.node, to, body)]
        else: # Não é vizinho, não pode mandar a mensagem
            return []

    def set_timeout(self, time, body):
        self.timeout_time = time + self.timeout
        return [(self.timeout, discrete_event_simulator.SelfEvent(self.node, body))]

class ExtremaNodeQuery(ExtremaNode):
    def __init__(self, node, neighbours, K: int, T: int, emit, drop_chance = 0.0, r = 1, timeout = 1):
        super().__init__(node, neighbours, K, T, drop_chance, r, timeout)
        self.emit = emit

    def start(self):
        return super().start()
    
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
        print(self.nonews)
        if self.nonews >= self.T:
            N = (self.K - 1) / sum(self.x) # unbiased estimator of N with exponential distribution
            # variance = (N**2) / (self.K - 2)
            self.emit(time, N)
            return None
        # TODO: enviar mensagens apenas quando existe alteração?
        else:
            if time >= self.timeout_time and not self.converged:
                timeout_event = self.set_timeout(time, None)
            else:
                timeout_event = []
            msgs = self.broadcast_messages(self.x)
            return (msgs, timeout_event)
        
    
    
class UnstableNetworkSimulator(discrete_event_simulator.Simulator):
    def __init__(self, nodes, distances, max_dist = 1, timeout = 0, network_change_time = 1, debug = False):
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
                self.distances[node][neighbour] = random.randrange(1, self.max_dist + 1)
                #if self.debug:
                    # print(str(node) + " -> " + str(neighbour) + " = " + str(self.distances[node][neighbour]))
            self.distances[node][node] = self.timeout
        return [(random.randrange(1, self.network_change_time + 1), discrete_event_simulator.SimulatorEvent(True))]

def simulatorGenerator(n, K, T, max_dist = 0, timeout = 0, fanout = None, debug = False):
    graph = gen_Graphs.random_graph(n)
    dists = [[0 for _ in range(n)] for _ in range(n)] # fill matrix with zeroes
    nodes = []
    first = True
    for node in graph.nodes:
        neighbours = list(graph.neighbors(node))
        if first:
            print(neighbours)
            graph_node = ExtremaNodeQuery(node, neighbours, K, T, lambda time, n : print(">>>", time, n), drop_chance = 0.0, timeout=max_dist)
            first = False
        else:
            graph_node = ExtremaNode(node, neighbours, K, T, drop_chance = 0.0, timeout=max_dist)
        nodes.append(graph_node)
    simulator = UnstableNetworkSimulator(nodes, dists, max_dist=max_dist, timeout=timeout, network_change_time=10, debug=True)
    simulator.start()
    return simulator

def floods(n_iter):
    n = 10
    K = 10000
    T = 100
    times = []
    n_messages = []
    for _ in range(n_iter):
        simulator = simulatorGenerator(n, K, T, max_dist=1)
        num_events = len(simulator.get_message_events())
        print("Num eventos :", num_events)
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


analyser = Simulator_Analyzer()
range_n = range(5, 10)
simulators = []
for n in range_n:
    simulators.append(simulatorGenerator(n, 15, 15, max_dist=20))

analyser.analyze_variable("Number of Nodes3", range_n, simulators, 5, title="Extrema Propagation Timeout Single Start")

print("Fim!!")
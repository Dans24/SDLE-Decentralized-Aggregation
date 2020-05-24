import discrete_event_simulator, gen_Graphs
import random
import statistics
from Simulator_Statistics import Simulator_Analyzer

"""
Semelhante ao ExtremaTimeout mas apenas um dos nodos é que faz as queries.
"""

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
        # atualiza o corpo
        for i in range(self.K):
            if message.body[i] < self.x[i]:
                self.x[i] = message.body[i]
        # TODO: basear o T em relação ao número de vizinhos?
        if time >= self.timeout_time:
            timeout_event = self.set_timeout(time, None)
        else:
            timeout_event = []
        msgs = self.broadcast_messages(self.x)
        return (msgs, timeout_event)

    def handle_event(self, event: discrete_event_simulator.SelfEvent, time):
        if time < self.timeout_time: # Existe um timeout posterior, por isso, este deixa de ter efeito
            #print("FAKE TIMEOUT " + str(self.node))
            return ([], self.set_timeout(time, None))
        #print("TIMEOUT " + str(self.node))
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
    def __init__(self, node, neighbours, K: int, T: int, answer, drop_chance = 0.0, r = 1, timeout = 1):
        super().__init__(node, neighbours, K, T, drop_chance, r, timeout)
        self.answer = answer

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
        #print("No news:", self.nonews)
        if self.nonews >= self.T:
            self.N = (self.K - 1) / sum(self.x) # unbiased estimator of N with exponential distribution
            # variance = (N**2) / (self.K - 2)
            return None
        # TODO: enviar mensagens apenas quando existe alteração?
        else:
            if time >= self.timeout_time and not self.converged:
                timeout_event = self.set_timeout(time, None)
            else:
                timeout_event = []
            msgs = self.broadcast_messages(self.x)
            return (msgs, timeout_event)
        
    def result(self):
        return (abs(self.N - self.answer) / self.answer) * 100



class ExtremaNodeQueryT(ExtremaNodeQuery):
    def handle_message(self, message: discrete_event_simulator.Message, time):
        self.time = time
        changed = False
        for i in range(self.K):
            if message.body[i] < self.x[i]:
                self.x[i] = message.body[i]
                changed = True
        if changed:
            self.T = self.nonews if self.nonews > self.T else self.T
            self.nonews = 0
        else:
            self.nonews += 1
        has_correct_answer = True
        answer = self.calculateAnswer()
        for i in range(self.K):
            if self.x[i] > answer[i]:
                has_correct_answer = False
                break
        if has_correct_answer:
            return None
        # TODO: enviar mensagens apenas quando existe alteração?
        else:
            if time >= self.timeout_time and not self.converged:
                timeout_event = self.set_timeout(time, None)
            else:
                timeout_event = []
            msgs = self.broadcast_messages(self.x)
            return (msgs, timeout_event)

    def result(self):
        return self.T

    def calculateAnswer(self):
        if self.answer[0] == False:
            answer = [float("inf") for _ in range(self.K)]
            for node in self.answer[1]:
                for i in range(self.K):
                    answer[i] = answer[i] if node.x[i] > answer[i] else node.x[i]
            self.answer = (True, answer)
            return answer
        else:
            return self.answer[1]
        
    
    
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

def simulatorGenerator(n, K, T, max_dist = 0, timeout = 0, fanout = None, debug = False, drop_chance = 0.0):
    graph = gen_Graphs.random_graph(n)
    dists = [[0 for _ in range(n)] for _ in range(n)] # fill matrix with zeroes
    nodes = []
    first = True
    for node in graph.nodes:
        neighbours = list(graph.neighbors(node))
        if first:
            graph_node = ExtremaNodeQuery(node, neighbours, K, T, n, drop_chance = drop_chance, timeout=max_dist)
            first = False
        else:
            graph_node = ExtremaNode(node, neighbours, K, T, drop_chance = 0.0, timeout=max_dist)
        nodes.append(graph_node)
    simulator = UnstableNetworkSimulator(nodes, dists, max_dist=max_dist, timeout=timeout, network_change_time=10)
    simulator.start()
    return simulator

def simulatorGeneratorT(n, K, max_dist = 0, timeout = 0, fanout = None, debug = False, drop_chance = 0.0):
    graph = gen_Graphs.random_graph(n)
    dists = [[0 for _ in range(n)] for _ in range(n)] # fill matrix with zeroes
    nodes = []
    first = True
    for node in graph.nodes:
        neighbours = list(graph.neighbors(node))
        if first:
            graph_node = ExtremaNodeQueryT(node, neighbours, K, 0, (False, nodes), drop_chance = 0.0, timeout=max_dist)
            first = False
        else:
            graph_node = ExtremaNode(node, neighbours, K, None, drop_chance = drop_chance, timeout=max_dist)
        nodes.append(graph_node)
    simulator = UnstableNetworkSimulator(nodes, dists, max_dist=max_dist, timeout=timeout, network_change_time=10)
    return simulator

def floods(n_iter):
    n = 10
    K = 1
    T = 100
    times = []
    n_messages = []
    for _ in range(n_iter):
        simulator = simulatorGeneratorT(n, K, max_dist=1, debug=True)
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

range_n = range(10, 101, 10)
simulators = []
iters = 25
print("A carregar simuladores...")
for n in range_n:
    round = []
    for m in range(iters):
        round.append(simulatorGenerator(n, 100, 50, max_dist=20, drop_chance = 0.2))
    simulators.append(round)
    print("Ronda carregada:", n)
print("Simuladores carregados...")
analyser.analyze_variable("Número de nodos", range_n, simulators, 100, title="Extrema Propagation Timeout Single Start K=100 T=50 Drop=20%", results_name="Erro %")

print("A carregar simuladores...")
simulators = []
for n in range_n:
    round = []
    for m in range(iters):
        round.append(simulatorGeneratorT(n, 100, max_dist=20, drop_chance=0.2))
    simulators.append(round)
    print("Ronda carregada:", n)
print("Simuladores carregados...")
analyser.analyze_variable("Número de nodos", range_n, simulators, 100, title="Extrema Propagation Timeout Single Start K=100 Drop=20%", results_name="T")

print("Fim!!")
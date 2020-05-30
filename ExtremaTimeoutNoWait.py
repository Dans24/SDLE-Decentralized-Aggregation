import discrete_event_simulator, gen_Graphs
import random
import statistics
import threading
from multiprocessing.pool import ThreadPool
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
    def __init__(self, node, neighbours, K: int, T: int, answer, drop_chance = 0.0, r = 1, timeout = 1, single = True):
        super().__init__(node, neighbours, K, T, drop_chance, r, timeout)
        self.answer = answer
        self.single = single

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
            self.no_news = 0
        else:
            self.no_news += 1
        # TODO: basear o T em relação ao número de vizinhos?
        #print("No news:", self.nonews)
        if self.no_news >= self.T:
            if not self.converged:
                self.converged
                self.N = (self.K - 1) / sum(self.x) # unbiased estimator of N with exponential distribution
            # variance = (N**2) / (self.K - 2)
            if self.single:
                return None
        # TODO: enviar mensagens apenas quando existe alteração?
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
            self.nodes[node].neighbours = list(graph.neighbours(node))
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
    return simulator

def simulatorGeneratorAll(n, K, T, max_dist = 0, timeout = 0, fanout = None, debug = False, drop_chance = 0.0):
    graph = gen_Graphs.random_graph(n)
    dists = [[0 for _ in range(n)] for _ in range(n)] # fill matrix with zeroes
    nodes = []
    for node in graph.nodes:
        neighbours = list(graph.neighbours(node))
        graph_node = ExtremaNodeQuery(node, neighbours, K, T, n, drop_chance = drop_chance, timeout=max_dist, single=False)
        nodes.append(graph_node)
    simulator = UnstableNetworkSimulator(nodes, dists, max_dist=max_dist, timeout=timeout, network_change_time=10)
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


def simulatorGeneratorArgs(*args):
    return simulatorGenerator(args[0][0], args[0][1], args[0][2],  max_dist=args[1].get("max_dist"), drop_chance=args[1].get("drop_chance"))

def simulatorGeneratorAllArgs(*args):
    return simulatorGeneratorAll(args[0][0], args[0][1], args[0][2],  max_dist=args[1].get("max_dist"), drop_chance=args[1].get("drop_chance"))

def simulatorGeneratorTArgs(*args):
    return simulatorGeneratorT(args[0][0], args[0][1], max_dist=args[1].get("max_dist"), drop_chance=args[1].get("drop_chance"))

analyser = Simulator_Analyzer()
range_n = range(10, 201, 20)
'''
simulators = []
iters = 25
print("A carregar simuladores...")
"""
def fill(simulators, i, n, iters):
    round = []
    print("A começar", n)
    for m in range(iters):
        round.append(simulatorGenerator(n, 100, 50, max_dist=20, drop_chance = 0.2))
    simulators[i] = round
    print("Terminou ", n)

threads = []
pool = ThreadPool(len(range_n))
for n in range_n:
    simulators.append(None)
    pool.apply_async(fill, args=(simulators, len(simulators) - 1, n, iters,))

pool.close()
pool.join()
print()
"""
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
'''
kwargs = []
for n in range_n:
    args = (n, 100, 25)
    kwarg = {"max_dist": 20, "drop_chance": 0.2}
    kwargs.append((args, kwarg))
analyser.analyze_gen_variable("Número de nodos", range_n, simulatorGeneratorArgs, kwargs, 100,  title="Extrema Propagation No Wait K=100 T=25 Drop=20%", results_name="Erro relativo (%)")
analyser.analyze_gen_variable("Número de nodos", range_n, simulatorGeneratorTArgs, kwargs, 100,  title="Extrema Propagation No Wait K=100 Drop=20%", results_name="T")

print("Fim!!")
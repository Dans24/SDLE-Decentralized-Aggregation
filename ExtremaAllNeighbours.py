import discrete_event_simulator, gen_Graphs
import random
import statistics

from Simulator_Statistics import Simulator_Analyzer

"""
    Semelhante ao ExtremaTimeout mas espera pela mensagens de todos os vizinhos para enviar o seu x
"""
class ExtremaNode(discrete_event_simulator.Node):
    def __init__(self, node, neighbours, K: int, T: int, drop_chance = 0.0, r = 1, timeout = 1, answer = None):
        self.node = node
        self.neighbours = neighbours
        self.K = K
        self.T = T
        self.r = r
        self.drop_chance = drop_chance
        self.timeout = timeout
        self.timeout_time = 0
        self.gotFrom = []
        self.converged = False
        self.debug = False
        self.answer = answer
        
    def start(self):
        self.nonews = 0
        self.x = []
        for _ in range(self.K):
            self.x.append(self.r * random.expovariate(1))
        return (self.broadcast_messages(self.x), self.set_timeout(0, None))

    def result(self):
        return 0

    def handle_message(self, message: discrete_event_simulator.Message, time):
        self.time = time
        oldx = False
        for i in range(self.K):
            if message.body[i] < self.x[i]:
                self.x[i] = message.body[i]
                oldx = True
        if oldx:
            self.nonews = 0
            self.gotFrom.clear()
        else:
            if message.src not in self.gotFrom:
                self.gotFrom.append(message.src)
            if len(self.gotFrom) == len(self.neighbours):
                self.nonews += 1
                self.gotFrom.clear()

        if self.nonews >= self.T:
            if not self.converged:
                self.N = (self.K - 1) / sum(self.x)
                self.converged = True
        if time >= self.timeout_time and not self.converged:
            timeout_event = self.set_timeout(time, None)
        else:
            timeout_event = []
        msgs = self.missingN_messages(self.x)
        if self.debug:
            for msg in msgs:
                print("src: " + str(msg.src) + " to: " + str(msg.to))
        return (msgs, timeout_event)

    def handle_event(self, event: discrete_event_simulator.SelfEvent, time):
        if self.converged:
            return ([], [])
        if time >= self.timeout_time:
            if self.debug:
                print("TIMEOUT " + str(self.node))
            msgs = self.broadcast_messages(self.x)
            timeout_event = self.set_timeout(time, None)
            return (msgs, timeout_event)
        else:
            if self.debug:
                print("TIMEOUT2 " + str(self.node))
            return ([], self.set_timeout(time, None))

    def broadcast_messages(self, body):
        msgs = []
        for neighbour in self.neighbours:
            if random.random() > self.drop_chance:
                msgs.append(discrete_event_simulator.Message(self.node, neighbour, body))
        return msgs
    
    def missingN_messages(self, body):
        msgs = []
        for neighbour in self.neighbours:
            if neighbour not in self.gotFrom:
                msgs.append(discrete_event_simulator.Message(self.node, neighbour, body))
        return msgs
    
    def set_timeout(self, time, body):
        self.timeout_time = time + self.timeout
        return [(self.timeout, discrete_event_simulator.SelfEvent(self.node, body))]

    def result(self):
        return (abs(self.N - self.answer) / self.answer) * 100 if self.answer else None

class ExtremaNodeT(ExtremaNode):
    def handle_message(self, message: discrete_event_simulator.Message, time):
        self.time = time
        oldx = False
        for i in range(self.K):
            if message.body[i] < self.x[i]:
                self.x[i] = message.body[i]
                oldx = True
        if oldx:
            self.nonews = 0
            self.gotFrom.clear()
        else:
            if message.src not in self.gotFrom:
                self.gotFrom.append(message.src)
            if len(self.gotFrom) == len(self.neighbours):
                self.nonews += 1
                self.gotFrom.clear()

        has_correct_answer = True
        answer = self.calculateAnswer()
        for i in range(self.K):
            if self.x[i] > answer[i]:
                has_correct_answer = False
                break
        if has_correct_answer:
            return None
        if time >= self.timeout_time and not self.converged:
            timeout_event = self.set_timeout(time, None)
        else:
            timeout_event = []
        msgs = self.missingN_messages(self.x)
        if self.debug:
            for msg in msgs:
                print("src: " + str(msg.src) + " to: " + str(msg.to))
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
        return []

def simulatorGenerator(n, K, T, max_dist = 0, timeout = float("inf"), fanout = None, network_change_time = float("inf"), debug = False):
    graph = gen_Graphs.random_graph(n)
    dists = [[0 for _ in range(n)] for _ in range(n)] # fill matrix with zeroes
    nodes = []
    for node in graph.nodes:
        neighbours = list(graph.neighbors(node))
        graph_node = ExtremaNode(node, neighbours, K, T, drop_chance = 0.0, timeout=timeout, answer = n)
        nodes.append(graph_node)
    simulator = UnstableNetworkSimulator(nodes, dists, max_dist=max_dist, timeout=timeout, network_change_time=network_change_time, debug=False)
    return simulator

def simulatorGeneratorT(n, K, max_dist = 0, timeout = float("inf"), fanout = None, network_change_time = float("inf"), debug = False):
    graph = gen_Graphs.random_graph(n)
    dists = [[0 for _ in range(n)] for _ in range(n)] # fill matrix with zeroes
    nodes = []
    for node in graph.nodes:
        neighbours = list(graph.neighbors(node))
        graph_node = ExtremaNodeT(node, neighbours, K, drop_chance = 0.0, timeout=timeout, answer = (False, nodes))
        nodes.append(graph_node)
    simulator = UnstableNetworkSimulator(nodes, dists, max_dist=max_dist, timeout=timeout, network_change_time=network_change_time, debug=False)
    return simulator

def simulatorGeneratorArgs(*args):
    return simulatorGenerator(args[0][0], args[0][1], args[0][2], max_dist=args[1].get("max_dist"), network_change_time=args[1].get("network_change_time"), timeout=args[1].get("timeout"))
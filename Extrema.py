import discrete_event_simulator, gen_Graphs
import random
import statistics

class ExtremaNode(discrete_event_simulator.Node):
    def __init__(self, node, neighbours, K: int, T: int, fanout=None, drop_chance=0.0):
        self.node = node
        self.neighbours = neighbours
        self.fanout = fanout if fanout != None else len(self.neighbours)
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
        for neighbour in random.sample(self.neighbours, self.fanout):
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
            # Make show the number of nodes
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
    

def simulatorGenerator(n, K, T, max_dist = 0, fanout = None):
    rootId = random.randrange(n)
    graph = gen_Graphs.random_graph(n)
    neighbours = graph.neighbors(rootId)
    dists = [[0 for _ in range(n)] for _ in range(n)] # fill matrix with zeroes
    nodes = []
    for node in graph.nodes:
        for neighbour in graph.nodes:
            dists[node][neighbour] = random.randrange(1, max_dist + 2)
        dists[node][node] = 0
        neighbours = list(graph.neighbors(node))
        graph_node = ExtremaNode(node, neighbours, K, T, None, 0.0)
        nodes.append(graph_node)
    simulator = discrete_event_simulator.Simulator(nodes, dists)
    simulator.start()
    return simulator


def floods(n_iter):
    n = 10
    times = []
    n_messages = []
    for _ in range(n_iter):
        simulator = simulatorGenerator(n, 3, 1)
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

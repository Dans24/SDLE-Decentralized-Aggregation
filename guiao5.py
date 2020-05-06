import discrete_event_simulator, gen_Graphs
import random
import statistics

class GraphNode(discrete_event_simulator.Node):
    def __init__(self, node, neighbours, fanout=None):
        self.node = node
        self.neighbours = neighbours
        self.fanout = fanout
        self.has = False
        
    def handle_message(self, message):
        self.has = True
        msgs = []
        for neighbour in self.neighbours:
            msgs.append(discrete_event_simulator.Message(self.node, neighbour, "FLOOD"))
        return msgs

class RootNode(GraphNode):
    def __init__(self, node, neighbours, fanout=None):
        super().__init__(node, neighbours, fanout)

    def start(self):
        msgs = []
        for neighbour in self.neighbours:
            msgs.append(discrete_event_simulator.Message(self.node, neighbour, "FLOOD"))
        return msgs

    def __str__(self):
        sb = ""
        for neighbour in self.neighbours:
            sb += str(neighbour) + "; "
        return "ROOT: " + str(self.node) + "-> neighbours: " + sb

def simulatorGenerator(n, max_dist = 0, fanout = None):
    rootId = random.randrange(n)
    graph = gen_Graphs.random_graph(n)
    neighbours = graph.neighbors(rootId)
    root = RootNode(rootId, neighbours, fanout)
    nodes = [root]
    dists = [[0 for _ in range(n)] for _ in range(n)] # fill matrix with zeroes
    for node in graph.nodes:
        for neighbour in graph.nodes:
            dists[node][neighbour] = random.randrange(max_dist) + 1
        dists[node][node] = 0
        neighbours = graph.neighbors(node)
        if rootId != node:
            graph_node = GraphNode(node, neighbours, fanout)
            nodes.append(graph_node)
    simulator = discrete_event_simulator.Simulator(nodes, dists)
    simulator.start()
    return simulator


def floods(n_iter):
    n = 10
    times = []
    n_messages = []
    for _ in range(n_iter):
        simulator = simulatorGenerator(n, 1)
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
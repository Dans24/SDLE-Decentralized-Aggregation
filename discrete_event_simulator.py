import queue

class Node:	
    # function - callback for handler	
    # start - callback for initialization	
    def start(self):	
        # return a list of events : [(message: Message)]	
        return []	

    # message : Message	
    def handle_message(self, message):	
        # return a list of events : [(message: Message)]	
        return []	

    # return (delay:int, event: Event) or None
    def handle_event(self, event):	
        return None


class Message:
    def __init__(self, src, to, body):
        self.src = src
        self.to = to
        self.body = body

    def __str__(self):
        return self.src.__str__() + " -> " + self.to.__str__() + "; body: " + self.body.__str__()

    def __lt__(self, other):
        return self.body < other.body


class Event:
    def __init__(self, src, body):
        self.src = src
        self.body = body

    def __str__(self):
        return "event: " + str(self.src) + "; body: " + str(self.body)

    def __lt__(self, other):
        return self.body < other.body


class SimulatorEvent:
    def __init__(self, state):
        self.status = state


class StartSimulationEvent (SimulatorEvent):
    def __init__(self):
        super().__init__(None)


class Simulator:
    # distances : [src][to] = dst
    # events : [(delay), message: Message]
    # nodes : [Node]
    def __init__(self, nodes, distances):
        self.nodes = nodes
        self.distances = distances
        self.events = queue.PriorityQueue()
        self.current_time = 0
        self.event_history = []

    # return [(delay, event: Event)]
    def handle_simulator_event(self, event):
        return []

    # msg: Message
    def put_message(self, msg):
        delay = self.distances[msg.src][msg.to]
        self.events.put((delay, msg))

    def put_event(self, event):
        (delay, new_event) = event
        self.events.put((self.current_time + delay, new_event))

    # events = event
    def put_messages(self, events):
        for event in events:
            self.put_message(event)

    def start(self):
        self.handle_simulator_event(StartSimulationEvent())
        for i in self.nodes:
            self.put_messages(i.start())

        while not self.events.empty():
            (time, event) = self.events.get()
            print(self.current_time, time, str(event))
            if isinstance(event, SimulatorEvent): # simulator handle SimulatorEvent
                simulator_events = self.handle_simulator_event(event)
                if simulator_events:
                    continue
                if self.events.empty():
                    break # There is only simulator's event, should stop the simulation
                for new_event in simulator_events:
                    self.put_event(new_event)
                continue # SimulatorEvent don't update current_time
            self.event_history.append((time, event))
            self.current_time = time	
            if isinstance(event, Message):
                new_events = self.nodes[event.to].handle_message(event)
                self.put_messages(new_events)
            elif isinstance(event, Event):
                local_event = self.nodes[event.src].handle_event(event)
                if local_event is not None:
                    self.put_event(local_event)
            else:
                raise NotImplementedError()

    def get_message_events(self):
        return [(time, ev) for (time, ev) in self.event_history if isinstance(ev, Message)]

    def get_events(self):
        return self.event_history

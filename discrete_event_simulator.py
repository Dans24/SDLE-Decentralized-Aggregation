import queue
import string
from typing import List, Tuple, Optional


class Event:
    def __init__(self, body):
        self.body = body

    def __str__(self):
        return "Event: " + str(self.body)

    def __lt__(self, other):
        return True

class Message(Event):
    def __init__(self, src: int, to: int, body):
        super().__init__(body)
        self.src = src
        self.to = to

    def __str__(self):
        return "Message: " + str(self.src) + " -> " + str(self.to) + " :: " + str(self.body)

class SelfEvent(Event):
    def __init__(self, origin: int, body):
        super().__init__(body)
        self.origin = origin
        self.body = body

    def __str__(self):
        return "Self Event: " + str(self.origin) + " :: " + str(self.body)


class SimulatorEvent(Event):
    def __init__(self, body):
        super().__init__(body)


class StartSimulationEvent (SimulatorEvent):
    def __init__(self):
        super().__init__(None)

class Node:	
    # function - callback for handler	
    # start - callback for initialization	
    def start(self) -> List[Message]:
        # return a list of events : [(message: Message)]	
        return []

    # message : Message	
    def handle_message(self, message: Message, time: int = 0) -> Tuple[List[Message], List[Tuple[int, SelfEvent]]]:	
        return ([], [])

    def handle_event(self, event: Event, time: int = 0) -> Tuple[List[Message], List[Tuple[int, SelfEvent]]]:
        return ([], [])

    def result(self):
        return None

class Simulator:
    # distances : [src][to] = dst
    # events : [(delay), message: Message]
    # nodes : [Node]
    def __init__(self, nodes: List[Node], distances: List[List[int]]):
        self.nodes = nodes
        self.distances = distances
        self.events = queue.PriorityQueue()
        self.current_time = 0
        self.event_history = []

    # return [(delay, event: Event)]
    def handle_simulator_event(self, event: Event) -> List[Tuple[int, Event]]:
        return []

    # msg: Message
    def put_message(self, msg: Message):
        delay = self.distances[msg.src][msg.to]
        self.put_event((delay, msg))

    def put_event(self, event: Tuple[int, Event]):
        (delay, new_event) = event
        # print("Added new event", self.current_time + delay, str(new_event))
        self.events.put((self.current_time + delay, new_event))

    # events = event
    def put_messages(self, messages: List[Message]):
        for message in messages:
            self.put_message(message)
            
    def result(self):
        getResult = lambda node : node.result()
        hasResult = lambda result : result != None
        results = list(filter(hasResult, map(getResult, self.nodes)))
        if len(results) > 0:
            return (min(results), sum(results) / len(results), max(results))
        else:
            return None

    def start(self, debug = False):
        simulator_events = self.handle_simulator_event(StartSimulationEvent())
        for new_event in simulator_events:
            self.put_event(new_event)
        
        for i in self.nodes:
            (new_messages, new_self_events) = i.start()
            self.put_messages(new_messages)
            for self_event in new_self_events:
                self.put_event(self_event)

        while not (self.isConverged() or self.events.empty()):
            (time, event) = self.events.get()
            if time > self.current_time:
                if debug:
                    print(time)
            self.current_time = time
            if debug:
                print(time, str(event))
            if isinstance(event, SimulatorEvent): # simulator handle SimulatorEvent
                simulator_events = self.handle_simulator_event(event)
                if self.events.empty():
                    break # There is only simulator's event, should stop the simulation
                for new_event in simulator_events:
                    self.put_event(new_event)
                continue # SimulatorEvent don't update current_time
            self.event_history.append((time, event))
            if isinstance(event, Message):
                new_events = self.nodes[event.to].handle_message(event, time)
            elif isinstance(event, SelfEvent):
                new_events = self.nodes[event.origin].handle_event(event, time)
            else:
                raise NotImplementedError()
            if new_events == None:
                break
            (new_messages, new_self_events) = new_events
            self.put_messages(new_messages)
            for self_event in new_self_events:
                self.put_event(self_event)


    def isConverged(self):
        convergence = True
        for node in self.nodes:
            if not node.converged:
                convergence = False
                break
        return convergence

    def get_message_events(self) -> List[Tuple[int, Event]]:
        return [(time, ev) for (time, ev) in self.event_history if isinstance(ev, Message)]

    def get_events(self) -> List[Tuple[int, Event]]:
        return self.event_history

    def get_logger_file(self) -> string:
        return None

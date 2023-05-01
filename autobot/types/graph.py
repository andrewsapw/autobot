import networkx as nx
from aiogram import Dispatcher

from autobot.types.state import State
from autobot.types.transition import Transition


class Graph(nx.DiGraph):
    def __init__(self, incoming_graph_data=None, **attr):
        super().__init__(incoming_graph_data, **attr)
        self.dispatcher = Dispatcher()
        

    def find_state(self, state_name: str) -> State | None:
        matched_states = [i for i in self.nodes if i.name == state_name]
        if not matched_states:
            return None
        
        return matched_states[0]

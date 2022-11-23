import networkx as nx
from aiogram import Bot, Dispatcher

from autobot.settings import BOT_TOKEN
from autobot.types.condition import *
from autobot.types.graph import *
from autobot.types.graph import State


class Graph(nx.DiGraph):
    def __init__(self, incoming_graph_data=None, **attr):
        super().__init__(incoming_graph_data, **attr)

        self.bot = None
        self.dispatcher = Dispatcher()

    def add_node(self, state: State):
        state.register(self.dispatcher)
        super().add_node(state.name, data=state)

    def update_state_data(self, state: State):
        self.nodes[state.name]["data"] = state

    def add_edge(self, transition: Transition):
        if not self.has_node(transition.from_state.name):
            self.add_node(transition.from_state)

        if not self.has_node(transition.to_state.name):
            self.add_node(transition.to_state)

        to_state: State = self.nodes[transition.to_state.name]["data"]
        to_state.add_in_state(transition.from_state)
        self.update_state_data(to_state)

        transition.register(self, dispatcher=self.dispatcher)
        super().add_edge(
            transition.from_state.name, transition.to_state.name, data=transition
        )

    def run(self):
        self.bot = Bot(token=BOT_TOKEN)
        self.dispatcher.run_polling(self.bot)


G = Graph()

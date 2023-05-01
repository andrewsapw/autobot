import networkx as nx
from aiogram import Bot, Dispatcher

from autobot.settings import BOT_TOKEN
from autobot.types.conditions.condition import *
from autobot.types.graph import *
from autobot.types.graph import State


class Graph(nx.DiGraph):
    def __init__(self, incoming_graph_data=None, **attr):
        super().__init__(incoming_graph_data, **attr)

        self.bot = None
        self.dispatcher = Dispatcher()

    def add_node(self, state: State):
        super().add_node(state)

    def add_edge(self, transition: Transition):
        if not self.has_node(transition.from_state):
            self.add_node(transition.from_state)

        if not self.has_node(transition.to_state):
            self.add_node(transition.to_state)

        super().add_edge(transition.from_state, transition.to_state, data=transition)

    def run(self):
        self.bot = Bot(token=BOT_TOKEN)
        self.dispatcher.run_polling(self.bot)


G = Graph()

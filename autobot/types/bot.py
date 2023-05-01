from typing import Optional
from aiogram.filters.state import StateFilter

from networkx import DiGraph
from aiogram import Bot, Dispatcher
from aiogram.client.session.base import BaseSession

from autobot.types import State, Transition
from autobot.types.callback import Callback
from autobot.types.conditions import (
    ConditionBase,
    MessageCondition,
    CallbackCondition,
    AlwaysCondition,
    ElseCondition,
)
from autobot.utils.callback import construct_callback
from autobot.types.handler import construct_handler


class AutoBot:
    def __init__(
        self, states: dict[str, State], edges: dict[tuple[str, str], Transition]
    ) -> None:
        self.dispatcher = Dispatcher()
        self.graph = DiGraph()
        self.states = states
        self.edges = edges

        self.init_graph()
        self.build_routes()

    def find_state(self, state_name: str):
        return self.states[state_name]

    def get_state_handler(self, state: State):
        return self.graph.nodes[state]["handler"]

    def init_graph(self):
        # init states
        for _, state in self.states.items():
            self.graph.add_node(state)

        # init edges
        for _, edge in self.edges.items():
            from_state = self.find_state(edge.from_state)
            to_state = self.find_state(edge.to_state)

            self.graph.add_edge(from_state, to_state, conditions=edge.conditions)

        # init callbacks
        for node in self.graph.nodes:
            prev_nodes = list(self.graph.predecessors(node))
            handler = construct_handler(node, prev_states=prev_nodes)
            self.graph.nodes[node]["handler"] = handler

    def _register_route(
        self, from_state: State, to_state: State, conditions: list[ConditionBase]
    ):
        state_filter = StateFilter(from_state.name)
        handlers = []
        for c in conditions:
            if isinstance(c, (CallbackCondition, MessageCondition)):
                c.register(
                    dispatcher=self.dispatcher,
                    handler=self.get_state_handler(to_state),
                )
            elif isinstance(c, ElseCondition):
                target = c.to_state
                target_handler = self.graph.nodes[target]["handler"]
                c.register(
                    dispatcher=self.dispatcher,
                    handler=self.get_state_handler(target),
                )
            elif isinstance(c, AlwaysCondition):
                target = c.to_state
                target_handler = self.graph.nodes[target]["handler"]
                self.graph.nodes[from_state]["handler"].add_callback(target_handler)
                c.register(
                    dispatcher=self.dispatcher,
                    handler=self.get_state_handler(target),
                )
                
            # if isinstance(c, (MessageCondition, CallbackCondition)):

    def build_routes(self):
        for node in self.graph.nodes:
            state_filter = StateFilter(node.name)

            predecessors = list(self.graph.predecessors(node))  # previous nodes
            successors = list(self.graph.successors(node))  # next nodes

            handler = construct_handler(state=node, prev_states=predecessors)
            for p in predecessors:
                edge = self.graph.edges[p, node]
                conditions = edge["conditions"]

                self._register_route(from_state=p, to_state=node, conditions=conditions)

            for s in successors:
                edge = self.graph.edges[node, s]
                conditions = edge["conditions"]

                self._register_route(from_state=node, to_state=s, conditions=conditions)

        for from_state, to_state, data in self.graph.edges(data=True):  # type: ignore
            conditions: list[ConditionBase] = data["conditions"]  # type: ignore
            self._register_route(
                from_state=from_state, to_state=to_state, conditions=conditions
            )
            self.dispatcher.message.register(construct_handler(state=from_state))

    # def add_state(self, state: State):
    #     # check if already exists
    #     if state in self.states:
    #         return

    #     self.states.append(state)

    # def add_edge(self, edge: Transition):
    #     if edge in self.transitions:
    #         return

    #     self.states.append(edge)

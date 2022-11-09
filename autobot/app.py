import networkx as nx
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Filter, StateFilter
from aiogram.handlers import BaseHandler, CallbackQueryHandler, MessageHandler

from autobot.core.generator import register_command
from autobot.logger import logger
from autobot.types.condition import *
from autobot.types.condition import (
    AlwaysCondition,
    CallbackCondition,
    ConditionBase,
    MessageCondition,
)
from autobot.types.graph import *
from autobot.types.graph import State

from .settings import BOT_TOKEN


class Graph(nx.DiGraph):
    def __init__(self, incoming_graph_data=None, **attr):
        super().__init__(incoming_graph_data, **attr)

        self.bot = None
        self.dispatcher = Dispatcher()

    def add_node(self, state: State):
        super().add_node(state.name, data=state)

    def add_edge(self, transition: Transition):
        if not self.has_node(transition.from_state.name):
            self.add_node(transition.from_state)

        if not self.has_node(transition.to_state.name):
            self.add_node(transition.to_state)

        super().add_edge(
            transition.from_state.name, transition.to_state.name, data=transition
        )

    def construct_transitions(
        self,
        conditions: list[ConditionBase],
        from_state_name: str,
        to_state_name: str,
    ) -> list[BaseHandler]:
        from_state = G.nodes[from_state_name]["data"]
        to_state = G.nodes[to_state_name]["data"]

        message_filters: list[Filter] = []
        callback_filters: list[Filter] = []

        state_filter = StateFilter(from_state.name)
        for condition in conditions:
            if isinstance(condition, MessageCondition):
                self.dispatcher.message.register(
                    to_state.handle, state_filter, condition.check()
                )
                logger.debug(
                    f"Register message transition from {from_state_name} to {to_state_name} on data {condition.text}"
                )
            elif isinstance(condition, CallbackCondition):
                self.dispatcher.callback_query.register(
                    to_state.handle, state_filter, condition.check()
                )
                logger.debug(
                    f"Register message transition from {from_state_name} to {to_state_name} on data {condition.data}"
                )
            elif isinstance(condition, ElseCondition):
                target = condition.target
                target_node = self.nodes[target]["data"]

                self.dispatcher.callback_query.register(
                    target_node.handle, state_filter, condition.check()
                )
                self.dispatcher.message.register(
                    target_node.handle, state_filter, condition.check()
                )
                logger.debug(
                    f"Register else transition from {from_state_name} to {target}"
                )
            elif isinstance(condition, AlwaysCondition):
                target = condition.target
                target_callback = self.nodes[target]["data"].handle

                from_state.post_call = target_callback
                G.nodes[from_state_name]["data"] = from_state

                self.dispatcher.callback_query.register(
                    target_callback, state_filter, condition.check()
                )
                self.dispatcher.message.register(
                    target_callback, state_filter, condition.check()
                )
                logger.debug(
                    f"Register ALWAYS transition from {from_state_name} to {target}"
                )
            else:
                raise TypeError(f"Condition of type {type(condition)} is not supported")

        logger.debug(f"Register back button to {from_state}")
        self.dispatcher.callback_query.register(
            from_state.callback, StateFilter(to_state.name), F.data == from_state.name
        )

        handlers = []
        if message_filters:
            handlers.append(MessageHandler(callback=callback, filters=message_filters))  # type: ignore

        if callback_filters:
            handlers.append(CallbackQueryHandler(callback=callback, filters=callback_filters))  # type: ignore

        return handlers

    def init_in_edges(self, node: str):
        in_edges = self.in_edges(node, data=True)
        if not in_edges:
            return

        for from_node, to_node, edge_data in in_edges:
            if edge_data is None:
                raise ValueError("Edge data can't be None")

            node_data: dict[str, State] = self.nodes[node]

            transition: Transition = edge_data["data"]
            handlers = self.construct_transitions(
                conditions=transition.conditions,
                from_state_name=transition.from_state.name,
                to_state_name=transition.to_state.name,
            )

    def init_routes(self):
        self.dispatcher = Dispatcher()  # reset dispatcher

        # init states
        node_data: dict[str, State]
        node: str
        for node, node_data in self.nodes(data=True):  # type: ignore
            state = node_data["data"]
            if state.command is not None:
                register_command(
                    dispatcher=self.dispatcher,
                    command=state.command,
                    callback=state.handle,
                )

            self.init_in_edges(node=node)

    def run(self):
        self.init_routes()
        self.bot = Bot(token=BOT_TOKEN)
        self.dispatcher.run_polling(self.bot)


G = Graph()

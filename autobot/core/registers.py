from autobot.logger import logger
from autobot.types import Graph, State
from aiogram import Dispatcher
from aiogram.filters.state import StateFilter
from aiogram import F
from aiogram.filters import Command

from autobot.types.conditions import *
from autobot.types.graph import *
from autobot.types.graph import State

from autobot.types.callback import Callback
from autobot.utils.callback import construct_callback


def init_routes(edge: Transition, graph: Graph):
    from_state = edge.from_state
    to_state = edge.to_state

    dispatcher = graph.dispatcher
    state_filter = StateFilter(from_state.name)
    for condition in edge.conditions:
        if isinstance(condition, (ElseCondition, AlwaysCondition)):
            target = condition.to_state
            target_callback: Callback = graph.nodes[target]["callback"]

            if isinstance(condition, AlwaysCondition):
                target_callback = graph.nodes[target]["callback"]
                graph.nodes[from_state]["callback"].add_callback(target_callback)

        elif isinstance(condition, ConditionBase):
            callback: Callback = graph.nodes[to_state]["callback"]
            condition.register(
                dispatcher=dispatcher,
                state_filter=state_filter,
                callback=callback.handle,
            )
        else:
            raise TypeError(f"Condition type {type(condition)} is not supported")

    print(from_state)
    # register possible back button
    dispatcher.callback_query.register(
        graph.nodes[from_state]["callback"].handle,
        StateFilter(to_state.name),
        F.data == from_state.name,
    )


def register_edge(edge: Transition, graph: Graph):
    """Register transition in graph structure

    Args:
        G (nx.DiGraph): _description_
        dispatcher (Dispatcher): _description_

    Raises:
        TypeError: condition type is not supported
    """
    from_state = edge.from_state
    to_state = edge.to_state

    dispatcher = graph.dispatcher
    state_filter = StateFilter(from_state.name)
    for condition in edge.conditions:
        if isinstance(condition, (ElseCondition, AlwaysCondition)):
            target = condition.to_state
            target_callback: Callback = graph.nodes[target]["callback"]

            condition.register(
                dispatcher=dispatcher,
                state_filter=state_filter,
                callback=target_callback.handle,
            )
            if isinstance(condition, AlwaysCondition):
                target_callback = graph.nodes[target]["callback"]
                graph.nodes[from_state]["post_call"] = target_callback

        elif isinstance(condition, ConditionBase):
            callback: Callback = graph.nodes[to_state]["callback"]
            condition.register(
                dispatcher=dispatcher,
                state_filter=state_filter,
                callback=callback.handle,
            )
        else:
            raise TypeError(f"Condition type {type(condition)} is not supported")

    print(from_state)
    # register possible back button
    dispatcher.callback_query.register(
        graph.nodes[from_state]["callback"].handle,
        StateFilter(to_state.name),
        F.data == from_state.name,
    )


def register_command(dispatcher: Dispatcher, command: str, callback: Callback):
    """Register command trigger"""
    logger.debug(f"Register command {command}")
    dispatcher.message.register(callback.handle, Command(command))


def register_state(state: State, graph: Graph):
    """Register state. Initializes command trigger.

    Args:
        dispatcher (Dispatcher): aiogram dispatcher
    """

    in_edges = graph.in_edges(state)
    if in_edges:
        prev_states = [i[1] for i in in_edges]
    else:
        prev_states = []

    callback_fun = construct_callback(
        state=state,
        prev_states=prev_states,
    )

    callback = Callback()
    callback.add_callback(callback_fun)

    dispatcher = graph.dispatcher
    if state.command is not None:
        register_command(
            dispatcher=dispatcher, command=state.command, callback=callback
        )

    graph.nodes[state]["callback"] = callback
    return callback

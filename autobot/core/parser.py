import pathlib
from pprint import pprint

import networkx as nx
import yaml

from autobot.types.condition import CallbackCondition, ConditionBase, MessageCondition
from autobot.types.graph import Graph, State, Transition
from autobot.core.generator import (
    construct_callback,
    construct_transitions,
    register_command,
)
from autobot import dispatcher


def parse_conditions(conditions_dict: dict) -> list[ConditionBase]:
    conds = []
    for text in conditions_dict.get("message", []):
        conds.append(MessageCondition(text=text))

    for callback_query in conditions_dict.get("callback", []):
        conds.append(CallbackCondition(data=callback_query))

    return conds


def parse_config(config_path: str | pathlib.Path) -> nx.DiGraph:
    g = nx.DiGraph()

    with open(config_path, "rb") as f:
        config_data = yaml.load(f, Loader=yaml.SafeLoader)

    pprint(config_data)

    states = config_data["states"]
    transitions = config_data["transitions"]

    for state_name, state_data in states.items():
        state = State(
            name=state_name,
            text=state_data.get("text", None),
            reply_markup=None,
            command=state_data.get("command", None),
            add_back_button=state_data.get("add_back_button", False),
        )

        callback = construct_callback(
            send_text=state.text,
            reply_markup=state.reply_markup,
            node_state=state.name,
            back_button=state.add_back_button,
        )
        g.add_node(state.name, callback=callback, command=state.command, back_button=state.add_back_button)

        if state.command is not None:
            register_command(
                dispatcher=dispatcher, command=state.command, callback=callback
            )

    transitions_formatted = {}
    for transition_name, transition_data in transitions.items():
        from_state = transition_data["from"]
        if from_state not in g.nodes:
            raise ValueError(f"State {from_state} not found in existing states :(")

        to_state = transition_data["to"]
        if to_state not in g.nodes:
            raise ValueError(f"State {to_state} not found in existing states :(")

        conditions = parse_conditions(transition_data["conditions"])

        callback = g.nodes[to_state]["callback"]
        handlers = construct_transitions(
            dispatcher=dispatcher,
            conditions=conditions,
            callback=callback,
            from_state=from_state,
            back_button=g.nodes[from_state]["back_button"]
        )
        g.add_edge(from_state, to_state, handlers=handlers)

    return g


def parse_graph(g: nx.DiGraph) -> None:
    for node, data in g.nodes(data=True):
        edges: list[tuple] = g.in_edges(node)  # type: ignore
        if not edges:
            continue

        for from_node, to_node in edges:
            print(from_node, to_node)


if __name__ == "__main__":
    g = parse_config("/home/svist/projects/autobot/examples/configs/simple.yaml")
    parse_graph(g)

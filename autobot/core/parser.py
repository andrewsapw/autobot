import pathlib

import networkx as nx
import yaml

from autobot.app import Graph
from autobot.types.condition import (
    AlwaysCondition,
    CallbackCondition,
    ConditionBase,
    MessageCondition,
    ElseCondition,
)
from autobot.types.graph import State, Transition
from autobot.utils.callback import construct_callback


def parse_conditions(transitions: dict) -> list[ConditionBase]:
    conditions_dict = transitions["conditions"]
    conds = []
    for text in conditions_dict.get("message", []):
        conds.append(MessageCondition(text=text))

    for callback_query in conditions_dict.get("callback", []):
        conds.append(CallbackCondition(data=callback_query))

    else_state = conditions_dict.get("else", None)
    if else_state is not None:
        conds.append(ElseCondition(target=else_state))

    always = "always" in conditions_dict
    if always:
        conds.append(AlwaysCondition(target=transitions["to"]))

    return conds


def parse_config(G: Graph, config_path: str | pathlib.Path) -> Graph:
    with open(config_path, "rb") as f:
        config_data = yaml.load(f, Loader=yaml.SafeLoader)

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
        G.add_node(state)

    for transition_name, transition_data in transitions.items():
        from_state = transition_data["from"]

        if from_state not in G.nodes:
            raise ValueError(f"State {from_state} not found in existing states")

        to_state = transition_data["to"]
        if to_state not in G.nodes:
            raise ValueError(f"State {to_state} not found in existing states")

        conditions = parse_conditions(transition_data)
        transition = Transition(
            from_state=G.nodes[from_state]["data"],
            to_state=G.nodes[to_state]["data"],
            conditions=conditions,
        )
        G.add_edge(transition)

    return G


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

import pathlib

import networkx as nx
import yaml
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from autobot.app import Graph
from autobot.types.condition import (
    AlwaysCondition,
    CallbackCondition,
    ConditionBase,
    ElseCondition,
    MessageCondition,
)
from autobot.types.graph import State, Transition


def parse_conditions(transitions: dict) -> list[ConditionBase]:
    conditions_dict = transitions["conditions"]
    conds = []
    for text in conditions_dict.get("message", []):
        conds.append(MessageCondition(text=text))

    for callback_query in conditions_dict.get("data", []):
        conds.append(CallbackCondition(data=callback_query))

    else_state = conditions_dict.get("else", None)
    if else_state is not None:
        conds.append(ElseCondition(target=else_state))

    always = "always" in conditions_dict
    if always:
        conds.append(AlwaysCondition(target=transitions["to"]))

    return conds


def parse_inline_buttons(inline_buttons: list):
    inline_buttons_formatted = []
    for row in inline_buttons:
        row_formatted = []
        row_buttons = row["row"]
        for btn in row_buttons:
            row_formatted.append(InlineKeyboardButton.parse_obj(btn))

        inline_buttons_formatted.append(row_formatted)

    return InlineKeyboardMarkup(inline_keyboard=inline_buttons_formatted)


def parse_config(G: Graph, config_path: str | pathlib.Path) -> Graph:
    """Core function for config parser.
    Translates config to graph structure (using networkx)
    """

    # read config
    with open(config_path, "rb") as f:
        config_data = yaml.load(f, Loader=yaml.SafeLoader)

    # extract states and transition data
    states = config_data["states"]
    transitions = config_data.get("transitions", [])
    if transitions is None:
        raise ValueError(
            "Transitions can't be empty. If you want to "
            "make one-state bot - then just remove `transitions` statement from config"
        )

    # process state
    for state_name, state_data in states.items():
        # parse inline buttons
        inline_buttons = state_data.get("inline_buttons", None)
        if inline_buttons is not None:
            reply_markup = parse_inline_buttons(inline_buttons)
        else:
            reply_markup = None

        # pydantic for validation of state fields
        state = State(
            name=state_name,
            text=state_data.get("text", None),
            reply_markup=reply_markup,
            command=state_data.get("command", None),
            add_back_button=state_data.get("add_back_button", False),
        )

        G.add_node(state)

    # process edges (transitions)
    for transition_data in transitions:
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
    from autobot.app import G

    g = parse_config(G, "/home/svist/projects/autobot/examples/configs/simple.yaml")
    parse_graph(g)

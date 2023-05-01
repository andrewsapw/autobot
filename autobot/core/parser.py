import pathlib
from typing import Iterable

import networkx as nx
import yaml
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from autobot.types import Graph, State, Transition
from autobot.types.conditions import (
    AlwaysCondition,
    CallbackCondition,
    ConditionBase,
    ElseCondition,
    MessageCondition,
)


def parse_transitions(
    transitions: dict, states: dict[str, State]
) -> list[ConditionBase]:
    """Parsing transitions from dict to ConditionBase based classes

    Args:
        transitions (dict): transitions parsed from YAML config

    Returns:
        list[ConditionBase]: parsed conditions
    """
    conditions_dict = transitions["conditions"]
    conditions: list[ConditionBase] = []

    from_state = states[transitions["from"]]
    to_state = states[transitions["to"]]
    always = "always" in conditions_dict
    if always:
        conditions.append(AlwaysCondition(from_state=from_state, to_state=to_state))
        return conditions

    for text in conditions_dict.get("message", []):
        conditions.append(
            MessageCondition(from_state=from_state, to_state=to_state, text=text)
        )

    for callback_query in conditions_dict.get("data", []):
        conditions.append(
            CallbackCondition(
                from_state=from_state, to_state=to_state, data=callback_query
            )
        )

    else_state = conditions_dict.get("else", None)
    if else_state is not None:
        else_state = states[else_state]
        conditions.append(ElseCondition(from_state=from_state, to_state=else_state))

    return conditions


def parse_inline_buttons(inline_buttons: list) -> InlineKeyboardMarkup:
    """Inline buttons parsing to aiogram InlineKeyboardButton type

    Args:
        inline_buttons (list): array of inline buttons from YAML config

    Returns:
        InlineKeyboardMarkup: aiogram buttons markup
    """
    inline_buttons_formatted = []
    for row in inline_buttons:
        row_formatted = []
        row_buttons = row["row"]
        for btn in row_buttons:
            row_formatted.append(InlineKeyboardButton.parse_obj(btn))

        inline_buttons_formatted.append(row_formatted)

    return InlineKeyboardMarkup(inline_keyboard=inline_buttons_formatted)


def parse_config(config_path: str | pathlib.Path) -> tuple[dict, dict]:
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

    states_formatted = {}  # state name to state data
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
            back_button=state_data.get("add_back_button", False),
        )
        states_formatted[state.name] = state

    transitions_formatted = {}  # edge name to edge data
    # process edges (transitions)
    for transition_data in transitions:
        from_state_name = transition_data["from"]
        to_state_name = transition_data["to"]

        conditions = parse_transitions(transition_data, states=states_formatted)
        transition = Transition(
            from_state=from_state_name,
            to_state=to_state_name,
            conditions=conditions,
        )
        transitions_formatted[(transition.from_state, transition.to_state)] = transition

    return states_formatted, transitions_formatted


def parse_graph(g: nx.DiGraph) -> None:
    for node, data in g.nodes(data=True):
        edges: list[tuple] = g.in_edges(node)  # type: ignore
        if not edges:
            continue

        for from_node, to_node in edges:
            print(from_node, to_node)

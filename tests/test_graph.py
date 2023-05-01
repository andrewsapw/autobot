import pytest

from autobot.app import G, Graph
from autobot.core import parser
from autobot.types.conditions.condition import MessageCondition
from autobot.types.graph import State, Transition


@pytest.fixture
def random_state_generator():
    def func(n: int):
        for i in range(n):
            yield State(name=f"state_{i}", text="state {i} text", reply_markup=None)

    return func


def test_add_node(random_state_generator):
    for state in random_state_generator(100):
        G.add_node(state=state)

        assert G.has_node(state.name)
        state_added = G.nodes[state.name]


def test_non_existing_node():
    with pytest.raises(KeyError):
        G.nodes["not_existing_node"]


def test_add_edge():
    state1 = State(name="state1", text="state1 text", reply_markup=None)
    state2 = State(name="state2", text="state2 text", reply_markup=None)
    conditions = [MessageCondition(text=str(i)) for i in range(10)]

    edge = Transition(
        from_state=state1,
        to_state=state2,
        conditions=conditions,
    )
    G.add_node(state1)
    G.add_edge(edge)
    assert G.has_edge(edge.from_state.name, edge.to_state.name)

    added_edge_data = G.get_edge_data(edge.from_state.name, edge.to_state.name)

    assert added_edge_data is not None
    added_edge: Transition = added_edge_data["data"]

    assert isinstance(added_edge, Transition)


def test_routes_init():
    g: Graph = parser.parse_config(G, "examples/configs/simple.yaml")

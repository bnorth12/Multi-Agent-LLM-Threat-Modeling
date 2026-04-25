"""
Unit tests for orchestrator.py (LangGraph state graph integration)
"""
import pytest
from src.threat_modeler.orchestrator import StateGraph, build_default_state_graph

def test_state_graph_add_and_run():
    sg = StateGraph()
    called = []
    def node_a(state):
        called.append('a')
        state['a'] = True
        return state
    def node_b(state):
        called.append('b')
        state['b'] = True
        return state
    sg.add_node('a', node_a)
    sg.add_node('b', node_b)
    sg.add_edge('a', 'b')
    result = sg.run('a', {})
    assert result['a'] is True
    assert result['b'] is True
    assert called == ['a', 'b']

def test_build_default_state_graph():
    sg = build_default_state_graph()
    assert 'input_normalizer' in sg.nodes
    assert 'context_builder' in sg.nodes
    assert 'context_builder' in sg.edges['input_normalizer']

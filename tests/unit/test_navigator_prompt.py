import pytest
from app.langchain_graph.navigator import NavigatorGraph


def test_prompt_template_contains_fields():
    template = NavigatorGraph._template
    assert "{task_text}" in template
    assert "{initiatives}" in template

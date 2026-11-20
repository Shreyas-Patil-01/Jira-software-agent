
from langgraph.graph import StateGraph, START, END

from graph.state import JiraAgentState
from agents.jira_fetcher import jira_fetcher_agent


def build_jira_graph():

    workflow = StateGraph(JiraAgentState)

    # Register agent
    workflow.add_node(
        "jira_fetcher",
        jira_fetcher_agent
    )

    # Define execution flow
    workflow.add_edge(START, "jira_fetcher")
    workflow.add_edge("jira_fetcher", END)

    # Compile graph
    return workflow.compile()


from typing import TypedDict, Any


class JiraAgentState(TypedDict, total=False):

    # Input
    assignee_account_id: str

    # Jira data
    tickets: list[dict[str, Any]]
    total_tickets: int

    # Execution information
    status: str
    error: str

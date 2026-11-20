
from tools.jira_client import JiraClient


def jira_fetcher_agent(state):

    print("\n[JIRA FETCHER AGENT] Starting...")

    try:

        account_id = state.get("assignee_account_id")

        if not account_id:
            raise ValueError("Assignee account ID is required.")

        jira = JiraClient()

        # Step 1: Fetch assigned tickets
        issues = jira.get_assigned_issues(account_id)

        print(f"\nFound {len(issues)} Jira tickets.")

        # Step 2: Fetch complete details
        tickets = []

        for issue in issues:

            ticket_data = jira.fetch_ticket_details(issue)

            tickets.append(ticket_data)

        print("\n[JIRA FETCHER AGENT] Completed successfully.")

        return {
            "tickets": tickets,
            "total_tickets": len(tickets),
            "status": "completed",
            "error": ""
        }

    except Exception as error:

        print(f"\n[JIRA FETCHER AGENT] Error: {error}")

        return {
            "tickets": [],
            "total_tickets": 0,
            "status": "failed",
            "error": str(error)
        }

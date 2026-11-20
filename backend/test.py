
import json

from pathlib import Path

from tools.jira_client import JiraClient
from graph.workflow import build_jira_graph


BASE_DIR = Path(__file__).resolve().parent


def main():

    print("\n" + "=" * 60)
    print("          JIRA AI AGENT - TICKET FETCHER")
    print("=" * 60)

    # Get Jira assignee
    assignee = input(
        "\nEnter Jira Assignee Account ID (or type 'me'): "
    ).strip()

    if not assignee:
        print("Assignee cannot be empty.")
        return

    try:

        jira = JiraClient()

        if assignee.lower() == "me":
            account_id = jira._get("/rest/api/3/myself")["accountId"]
        else:
            account_id = assignee

        print(f"\nAssignee Account ID: {account_id}")

        # Build LangGraph
        app = build_jira_graph()

        # Initial state
        initial_state = {
            "assignee_account_id": account_id,
            "tickets": [],
            "total_tickets": 0,
            "status": "started",
            "error": ""
        }

        # Execute graph
        print("\nExecuting LangGraph workflow...")

        result = app.invoke(initial_state)

        if result["status"] != "completed":
            print("\nAgent failed:", result["error"])
            return

        # Save results
        output_dir = BASE_DIR / "output"
        output_dir.mkdir(exist_ok=True)

        output_file = output_dir / "jira_tickets.json"

        with open(output_file, "w", encoding="utf-8") as file:

            json.dump(
                result["tickets"],
                file,
                indent=4,
                ensure_ascii=False
            )

        print("\n" + "=" * 60)
        print("              EXECUTION COMPLETED")
        print("=" * 60)

        print(f"Total tickets fetched: {result['total_tickets']}")
        print(f"JSON output: {output_file}")

        print("\nTickets:")

        for ticket in result["tickets"]:

            print(
                f"{ticket['key']} - "
                f"{ticket['fields'].get('summary', 'No summary')}"
            )

    except Exception as error:

        print(f"\nExecution Error: {error}")


if __name__ == "__main__":
    main()

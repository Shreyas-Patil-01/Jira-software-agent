
import os
import re
import requests

from pathlib import Path
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = BASE_DIR.parent

load_dotenv(PROJECT_DIR / ".env")


class JiraClient:

    def __init__(self):

        self.base_url = os.getenv("JIRA_BASE_URL", "").rstrip("/")
        self.email = os.getenv("JIRA_EMAIL")
        self.api_token = os.getenv("JIRA_API_TOKEN")

        if not all([self.base_url, self.email, self.api_token]):
            raise ValueError("Jira configuration missing in .env")

        self.session = requests.Session()
        self.session.auth = HTTPBasicAuth(self.email, self.api_token)
        self.session.headers.update({
            "Accept": "application/json"
        })

        self.download_attachments = (
            os.getenv("JIRA_DOWNLOAD_ATTACHMENTS", "true").lower()
            == "true"
        )

        self.output_dir = BASE_DIR / "output" / "attachments"

    def _get(self, endpoint, params=None):

        url = f"{self.base_url}{endpoint}"

        response = self.session.get(
            url,
            params=params,
            timeout=60
        )

        response.raise_for_status()
        return response.json()

    def _post(self, endpoint, payload):

        url = f"{self.base_url}{endpoint}"

        response = self.session.post(
            url,
            json=payload,
            timeout=60
        )

        response.raise_for_status()
        return response.json()

    def get_assigned_issues(self, account_id):

        jql = f'assignee = "{account_id}" ORDER BY updated DESC'

        all_issues = []
        next_page_token = None

        print("\nFetching assigned Jira tickets...")

        while True:

            payload = {
                "jql": jql,
                "maxResults": 100,
                "fields": ["*all"],
                "expand": "names,renderedFields"
            }

            if next_page_token:
                payload["nextPageToken"] = next_page_token

            result = self._post(
                "/rest/api/3/search/jql",
                payload
            )

            issues = result.get("issues", [])
            all_issues.extend(issues)

            print(f"Fetched {len(all_issues)} tickets so far...")

            next_page_token = result.get("nextPageToken")

            if not next_page_token:
                break

        return all_issues

    def get_all_comments(self, issue_key):

        comments = []
        start_at = 0

        while True:

            result = self._get(
                f"/rest/api/3/issue/{issue_key}/comment",
                params={
                    "startAt": start_at,
                    "maxResults": 100
                }
            )

            page_comments = result.get("comments", [])
            comments.extend(page_comments)

            start_at += len(page_comments)

            if not page_comments or start_at >= result.get("total", 0):
                break

        return comments

    def get_all_worklogs(self, issue_key):

        worklogs = []
        start_at = 0

        while True:

            result = self._get(
                f"/rest/api/3/issue/{issue_key}/worklog",
                params={
                    "startAt": start_at,
                    "maxResults": 100
                }
            )

            page_worklogs = result.get("worklogs", [])
            worklogs.extend(page_worklogs)

            start_at += len(page_worklogs)

            if not page_worklogs or start_at >= result.get("total", 0):
                break

        return worklogs

    def download_attachment(self, attachment, issue_key):

        filename = Path(attachment["filename"]).name
        attachment_id = attachment["id"]

        safe_issue_key = re.sub(r"[^A-Za-z0-9_-]", "_", issue_key)

        destination = (
            self.output_dir
            / safe_issue_key
            / f"{attachment_id}_{filename}"
        )

        destination.parent.mkdir(parents=True, exist_ok=True)

        response = self.session.get(
            attachment["content"],
            stream=True,
            timeout=120
        )

        response.raise_for_status()

        with open(destination, "wb") as file:

            for chunk in response.iter_content(chunk_size=8192):

                if chunk:
                    file.write(chunk)

        return str(destination.relative_to(BASE_DIR))

    def fetch_ticket_details(self, issue):

        issue_key = issue["key"]
        fields = issue.get("fields", {})

        print(f"Processing {issue_key}...")

        # Retrieve complete comments and worklogs
        comments = self.get_all_comments(issue_key)
        worklogs = self.get_all_worklogs(issue_key)

        # Attachment metadata
        attachments = fields.get("attachment", []) or []

        attachment_results = []

        for attachment in attachments:

            attachment_info = {
                "id": attachment.get("id"),
                "filename": attachment.get("filename"),
                "mimeType": attachment.get("mimeType"),
                "size": attachment.get("size"),
                "created": attachment.get("created"),
                "author": attachment.get("author"),
                "content_url": attachment.get("content"),
                "downloaded": False,
                "local_path": None
            }

            if self.download_attachments:

                try:
                    local_path = self.download_attachment(
                        attachment,
                        issue_key
                    )

                    attachment_info["downloaded"] = True
                    attachment_info["local_path"] = local_path

                except requests.RequestException as error:
                    attachment_info["download_error"] = str(error)

            attachment_results.append(attachment_info)

        return {
            "id": issue.get("id"),
            "key": issue_key,
            "self": issue.get("self"),
            "fields": fields,
            "comments": comments,
            "worklogs": worklogs,
            "attachments": attachment_results
        }

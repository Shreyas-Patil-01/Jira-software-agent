import requests
from requests.auth import HTTPBasicAuth

JIRA_BASE_URL = "https://shreyaspatil.atlassian.net"
JIRA_EMAIL = "pythonwithscience@gmail.com"
JIRA_API_TOKEN = "ATATT3xFfGF0DnTW1E7tD-g34USLnkEuarhCYyjrPME6z24px5knL5wzba7J6o1VM-sy1TxjPE3rmjCQkcFFbV6Med2N_NPEIomiDAycEQVDO89p2MWW2wetDiJ0OgGW35oXgUPEQsIQZZiQliq_bQGFvrtAkXPkNmHpGICWjVpX4wzgslX3mY8=12DCEF8B"


import requests
from requests.auth import HTTPBasicAuth
import json

url = f"{JIRA_BASE_URL}/rest/api/3/search/jql"

params = {
    "jql": "assignee=currentUser()",
    "maxResults": 100,
    "fields": "summary,status,assignee"
}

response = requests.get(
    url,
    params=params,
    auth=HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN),
    headers={"Accept": "application/json"}
)

print(json.dumps(response.json(), indent=2))
print("Status:", response.status_code)
print("Response:")
print(response.text)
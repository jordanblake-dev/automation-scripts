import requests
import os

# Define the GitHub repository and workflow details
owner = "jordanblake-dev"
repo = "automation-scripts"
workflow_id = "auto_commit_generated_code.yml"
ref = "main"  # Branch to run the workflow on

# Get the GitHub token from environment variables
github_token = os.getenv("GITHUB_TOKEN")

# Define the API endpoint
url = f"https://api.github.com/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches"

# Define the payload
payload = {
    "ref": ref
}

# Define the headers
headers = {
    "Authorization": f"Bearer {github_token}",
    "Accept": "application/vnd.github.v3+json"
}

# Trigger the workflow
response = requests.post(url, json=payload, headers=headers)

if response.status_code == 204:
    print("Workflow triggered successfully!")
else:
    print(f"Failed to trigger workflow: {response.status_code}")
    print(response.json())


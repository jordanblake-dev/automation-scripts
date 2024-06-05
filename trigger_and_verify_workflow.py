import requests
import os
import time
import zipfile
import openai
from pathlib import Path

# Define the GitHub repository and workflow details
owner = "jordanblake-dev"
repo = "automation-scripts"
workflow_id = "auto_commit_generated_code.yml"
ref = "main"  # Branch to run the workflow on

# Get the GitHub token and OpenAI API key from environment variables
github_token = os.getenv("GITHUB_TOKEN")
openai_api_key = os.getenv("OPENAI_API_KEY")

if not github_token or not openai_api_key:
    raise EnvironmentError("Required environment variables GITHUB_TOKEN or OPENAI_API_KEY are not set.")

# Initialize OpenAI
openai.api_key = openai_api_key

# Function to trigger the workflow
def trigger_workflow():
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches"
    payload = {"ref": ref}
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 204:
        print("Workflow triggered successfully!")
        return True
    else:
        print(f"Failed to trigger workflow: {response.status_code}")
        print(response.json())
        return False

# Function to get the latest workflow run
def get_latest_workflow_run():
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs"
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        runs = response.json().get("workflow_runs", [])
        if runs:
            return runs[0]
    else:
        print(f"Failed to get latest workflow run: {response.status_code}")
        print(response.json())
    return None

# Function to monitor the workflow run
def monitor_workflow_run(run_id):
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}"
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    max_retries = 30  # Maximum retries for monitoring the workflow run
    for _ in range(max_retries):
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            run = response.json()
            status = run.get("status")
            conclusion = run.get("conclusion")
            print(f"Workflow run status: {status}")
            if status == "completed":
                return conclusion == "success", run
            time.sleep(10)
        else:
            print(f"Failed to get workflow run status: {response.status_code}")
            print(response.json())
            break
    return False, None

# Function to get workflow run logs
def get_workflow_run_logs(run_id):
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}/logs"
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        with open("workflow_run_logs.zip", "wb") as f:
            f.write(response.content)
        print("Workflow run logs downloaded successfully!")
        return True
    else:
        print(f"Failed to get workflow run logs: {response.status_code}")
        print(response.json())
        return False

# Function to extract and display errors from logs
def extract_and_display_errors():
    with zipfile.ZipFile("workflow_run_logs.zip", "r") as zip_ref:
        zip_ref.extractall("logs")
    log_files = [f for f in os.listdir("logs") if f.endswith(".txt")]
    errors = []
    for log_file in log_files:
        with open(os.path.join("logs", log_file), "r") as f:
            lines = f.readlines()
            for line in lines:
                if "error" in line.lower() or "failed" in line.lower():
                    errors.append(line.strip())
    for error in errors:
        print(error)
    return errors

# Function to update the script with new logic based on OpenAI feedback
def update_script_with_openai_feedback(errors):
    # Create a prompt with errors to send to OpenAI
    prompt = "The following errors were encountered in the script:\n"
    for error in errors:
        prompt += f"- {error}\n"
    prompt += "\nPlease suggest how to fix these errors in the script."
    
    # Send the prompt to OpenAI with retry logic
    for attempt in range(3):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300
            )
            suggestions = response.choices[0].message["content"].strip()
            break
        except openai.error.APIError as e:
            if attempt < 2:  # Retry up to 3 times
                print(f"OpenAI API error: {e}. Retrying in 5 seconds...")
                time.sleep(5)
            else:
                print("Failed to get suggestions from OpenAI after multiple attempts.")
                return False
    
    # Implement the suggested changes (this part is commented out for safety)
    # print("OpenAI suggested the following changes:")
    # print(suggestions)
    # print("Please review the suggestions and implement them manually.")
    
    return True

# Main function
def main():
    if trigger_workflow():
        print("Waiting for the workflow run to start...")
        time.sleep(10)
        latest_run = get_latest_workflow_run()
        if latest_run:
            run_id = latest_run["id"]
            print(f"Monitoring workflow run {run_id}...")
            success, run_info = monitor_workflow_run(run_id)
            if success:
                print("Workflow completed successfully!")
                return
            else:
                print("Workflow failed.")
                if get_workflow_run_logs(run_id):
                    # Extract and display errors from logs
                    errors = extract_and_display_errors()
                    print("Error details:")
                    print(run_info)
                    # Update the script based on errors using OpenAI feedback
                    if not update_script_with_openai_feedback(errors):
                        print("Failed to update the script with OpenAI feedback.")
                else:
                    print("Failed to download workflow logs.")
        else:
            print("No workflow runs found.")
    else:
        print("Failed to trigger the workflow.")

if __name__ == "__main__":
    main()


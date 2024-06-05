import os
import openai
from github import Github
import subprocess
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

# Function to send email notifications
def send_email(subject, body, to_email):
    # ... (same as your provided function)

# Authenticate with OpenAI and GitHub
openai.api_key = os.getenv('OPENAI_API_KEY')
github_token = os.getenv('MY_GITHUB_TOKEN')
g = Github(github_token)

# Define repository and branch details
repo_name = "jordanblake-dev/automation-scripts"
branch_name = "new-feature-branch"
file_name = "generated_code.py"

# Function to generate code using GPT-4
def generate_code(prompt):
    # ... (same as your provided function)

# Generate code
code_prompt = "Write a Python function to calculate the Fibonacci sequence."
generated_code = generate_code(code_prompt)

# Function to execute a subprocess command
def run_command(command):
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, command, result.stdout, result.stderr)
    return result.stdout

try:
    # Configure Git to use the token
    run_command(["git", "config", "--global", "credential.helper", "store"])

    # Clone the repository
    repo_path = os.path.join(os.getcwd(), repo_name.split('/')[-1])
    run_command(["git", "clone", f"https://github.com/{repo_name}.git", repo_path])

    # Change to the repository directory
    os.chdir(repo_path)

    # Create a new branch
    run_command(["git", "checkout", "-b", branch_name])

    # Write the generated code to a file
    with open(file_name, "w") as f:
        f.write(generated_code)

    # Add, commit, and push the changes
    run_command(["git", "add", file_name])
    run_command(["git", "commit", "-m", "Add generated Fibonacci sequence function"])
    run_command(["git", "push", "--set-upstream", "origin", branch_name])

    # Create a pull request
    repo = g.get_repo(repo_name)
    pr = repo.create_pull(title="Add generated Fibonacci sequence function", body="This PR adds a new function to calculate the Fibonacci sequence.", head=branch_name, base="main")

    # Send email notification
    subject = "New Pull Request Created"
    body = f"A new pull request has been created:\n\nTitle: {pr.title}\nURL: {pr.html_url}"
    send_email(subject, body, "jordan.blake.ai@gmail.com")

except Exception as e:
    print(f"An error occurred: {e}")
    # Handle errors appropriately (e.g., send an error email notification)

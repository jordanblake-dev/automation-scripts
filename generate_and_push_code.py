import os
import openai
from github import Github
import subprocess
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

# Function to send email notifications
def send_email(subject, body, to_email):
    from_email = os.getenv('BOT_EMAIL')
    password = os.getenv('BOT_EMAIL_PASSWORD')

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, password)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")

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
    response = openai.Completion.create(
        engine="text-davinci-004",
        prompt=prompt,
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.7,
    )
    return response.choices[0].text.strip()

# Generate code
code_prompt = "Write a Python function to calculate the Fibonacci sequence."
generated_code = generate_code(code_prompt)

# Clone the repository
subprocess.run(["git", "clone", f"https://{github_token}@github.com/{repo_name}.git"])
os.chdir(repo_name.split('/')[-1])

# Create a new branch
subprocess.run(["git", "checkout", "-b", branch_name])

# Write the generated code to a file
with open(file_name, "w") as f:
    f.write(generated_code)

# Add, commit, and push the changes
subprocess.run(["git", "add", file_name])
subprocess.run(["git", "commit", "-m", "Add generated Fibonacci sequence function"])
subprocess.run(["git", "push", "--set-upstream", "origin", branch_name])

# Create a pull request
repo = g.get_repo(repo_name)
pr = repo.create_pull(title="Add generated Fibonacci sequence function", body="This PR adds a new function to calculate the Fibonacci sequence.", head=branch_name, base="main")

# Send email notification
subject = "New Pull Request Created"
body = f"A new pull request has been created:\n\nTitle: {pr.title}\nURL: {pr.html_url}"
send_email(subject, body, "jordan.blake.ai@gmail.com")


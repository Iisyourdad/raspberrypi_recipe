import os

# Get commit message from the user
commit_msg = input("Enter commit message: ")

# Stage all changes
os.system("git add .")

# Commit with the provided message
os.system(f'git commit -m "{commit_msg}"')

# Pull remote changes (rebasing local commits on top)
os.system("git pull --rebase origin main")

# Push to the remote repository (assuming branch "main")
os.system("git push -u origin main")

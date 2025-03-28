import os


def print_tree(startpath):
    for root, dirs, files in os.walk(startpath):
        # Skip the .venv and .git directories
        if '.venv' in root or '.git' in root:
            continue

        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 4 * (level + 1)
        for file in files:
            print(f"{subindent}{file}")


# Print the tree of the current directory, excluding .venv and .git
print_tree(os.getcwd())

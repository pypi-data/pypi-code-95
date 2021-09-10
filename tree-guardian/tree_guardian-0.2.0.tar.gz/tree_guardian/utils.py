
def get_gitignored():
    with open('.gitignore') as gitignore:
        return set(line.strip() for line in gitignore.readlines() if line.strip() and not line.startswith('#'))

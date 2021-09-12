template = '''from taskr import taskr

DEFAULT = "all"

def build() -> bool:
    """
    Builds a wheel
    """
    cmd = "python setup.py -q bdist_wheel;"
    cmd += "echo 'Artifact:'; ls dist/"
    return taskr.run(cmd)


# Remove build artifacts, cache, etc.
def clean() -> bool:
    cmd = "rm -rf ./dist/ ./build/ ./__pycache__ ./*.egg*/"
    return taskr.run(cmd)


# Run tests
def test() -> bool:
    return taskr.run("python -m pytest tests/ -vv")


# Run black
def fmt() -> bool:
    return taskr.run("python -m black .")


# Sort imports
def sort() -> bool:
    return taskr.run("python -m isort --atomic .")


# Checks types
def mypy() -> bool:
    return taskr.run("python -m mypy")


# Check flake8
def flake() -> bool:
    return taskr.run("python -m flake8"])


# Runs all static analysis tools
def all() -> bool:
    return taskr.run_conditional(fmt, mypy, sort, flake, test)

'''

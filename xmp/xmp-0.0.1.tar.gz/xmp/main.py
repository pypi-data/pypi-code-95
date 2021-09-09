import argparse
import subprocess
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile


def handle(filepath: Path):
    if not filepath.exists():
        raise FileNotFoundError(f"{filepath} is not found")

    lines = filepath.read_text()
    py = []
    is_script = False

    for line in lines.split("\n"):
        if line == "```" and is_script:
            is_script = False

        if is_script:
            py.append(line)

        if line == "```py":
            is_script = True

    tmp = filepath.with_suffix(".xmp")

    with tmp.open(mode="w") as f:
        f.write("\n".join(py))

    subprocess.run(f"python {tmp}", shell=True)

    tmp.unlink()


def main():
    parser = argparse.ArgumentParser("Execute Python code in Markdown code block.")
    parser.add_argument("filepath", type=Path, help="Markdown filepath")
    args = parser.parse_args()

    try:
        handle(**args.__dict__)
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

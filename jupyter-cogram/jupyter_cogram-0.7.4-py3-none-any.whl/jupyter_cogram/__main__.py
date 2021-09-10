import argparse
import sys
from typing import Text


def install_token(token: Text) -> None:
    from pathlib import Path

    config_location = Path().home() / ".ipython/nbextensions/jupyter-cogram"
    token_file_name = "cogram_auth_token"

    loc = config_location.absolute()

    if not loc.is_dir():
        loc.mkdir(parents=True)

    p = loc / token_file_name

    p.write_text(token)

    print(f"Successfully stored API token at '{p}' 🎉")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Set your Cogram API token")
    parser.add_argument(
        "-t",
        "--token",
        help="Your Cogram API token",
        required=True,
    )

    token = parser.parse_args().token

    if not token:
        print(
            "⚠️  Could not find token! The full command is\n"
            "python3 -m jupyter_cogram --token YOUR_TOKEN"
        )
        sys.exit(1)

    # noinspection PyBroadException
    try:
        install_token(token)
    except Exception as e:
        print("⚠️  Could not install token:\n{e}")

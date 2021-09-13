# Copyright 2020 Karlsruhe Institute of Technology
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import json
import os
import sys
import tempfile

import click
from flask import current_app

from kadi.cli.main import kadi
from kadi.cli.utils import check_env
from kadi.cli.utils import danger
from kadi.cli.utils import echo
from kadi.cli.utils import run_command
from kadi.cli.utils import success
from kadi.cli.utils import warning
from kadi.plugins import run_hook


@kadi.group()
def i18n():
    """Utility commands for managing translations."""


def _pybabel_extract(translations_path):
    cwd = os.getcwd()
    # Change to the application root path so all extracted strings will be shown as
    # being relative to that path.
    os.chdir(current_app.root_path)

    babel_cfg = os.path.join(translations_path, "babel.cfg")
    messages_pot = os.path.join(translations_path, "messages.pot")

    cmd = [
        "pybabel",
        "extract",
        "-F",
        babel_cfg,
        "-k",
        "lazy_gettext",
        "-k",
        "_l",
        "-o",
        messages_pot,
        "--copyright-holder",
        "Karlsruhe Institute of Technology",
        "--project",
        "Kadi4Mat",
        ".",
    ]
    run_command(cmd)

    os.chdir(cwd)


def _get_translations_path(plugin):
    if plugin is not None:
        plugin = current_app.plugin_manager.get_plugin(plugin)
        if plugin is not None:
            if hasattr(plugin, "kadi_get_translations_paths"):
                return plugin.kadi_get_translations_paths()

            danger("The given plugin does not specify a translations path.")
        else:
            danger("No plugin with that name could be found.")

        sys.exit(1)

    return current_app.config["BACKEND_TRANSLATIONS_PATH"]


@i18n.command()
@click.argument("lang")
@click.option("--plugin", help="The name of a plugin to use instead.")
@click.option("--i-am-sure", is_flag=True)
@check_env
def init(lang, plugin, i_am_sure):
    """Add a new language to the backend translations."""
    if not i_am_sure:
        warning(
            f"This might replace existing translations for language '{lang}'. If you"
            " are sure you want to do this, use the flag --i-am-sure."
        )
        sys.exit(1)

    translations_path = _get_translations_path(plugin)
    messages_pot = os.path.join(translations_path, "messages.pot")
    cmd = ["pybabel", "init", "-i", messages_pot, "-d", translations_path, "-l", lang]

    _pybabel_extract(translations_path)
    run_command(cmd)

    success("Initialization completed successfully.")


@i18n.command()
@click.option("--plugin", help="The name of a plugin to use instead.")
@check_env
def update(plugin):
    """Update all existing backend translations."""
    translations_path = _get_translations_path(plugin)
    messages_pot = os.path.join(translations_path, "messages.pot")
    cmd = ["pybabel", "update", "-N", "-i", messages_pot, "-d", translations_path]

    _pybabel_extract(translations_path)
    run_command(cmd)

    success("Update completed successfully.")


@i18n.command()
@check_env
def compile():
    """Compile all existing backend translations, including plugins."""
    translations_paths = [current_app.config["BACKEND_TRANSLATIONS_PATH"]] + run_hook(
        "kadi_get_translations_paths"
    )

    for path in translations_paths:
        cmd = ["pybabel", "compile", "-d", path]
        run_command(cmd)

    success("Compilation completed successfully.")


def _sync(key, value, old_translation, new_translation):
    if isinstance(value, dict):
        _new_translation = new_translation[key] = {}

        # If an old translation exists with the key (and is also a dictionary), then use
        # it for the subsequent checks of the nested keys.
        if key in old_translation and isinstance(old_translation[key], dict):
            _old_translation = old_translation[key]
        else:
            _old_translation = {}

        for _key, _value in value.items():
            _sync(_key, _value, _old_translation, _new_translation)
    else:
        if key in old_translation:
            new_translation[key] = old_translation[key]
        else:
            new_translation[key] = f"NOT_TRANSLATED [{value}]"


def _get_missing_entries(old_translation, new_translation):
    missing_entries = {}

    for key, value in old_translation.items():
        # Exclude old missing entries.
        if key == "_old":
            continue

        if key not in new_translation:
            missing_entries[key] = value
        elif isinstance(value, dict):
            results = _get_missing_entries(old_translation[key], new_translation[key])
            if results:
                missing_entries[key] = results

    return missing_entries


def _merge_missing_entries(old_entries, new_entries):
    merged_entries = {}

    for key in set(list(old_entries.keys()) + list(new_entries.keys())):
        if key in old_entries:
            merged_entries[key] = old_entries[key]

        if key in new_entries:
            if key not in merged_entries:
                merged_entries[key] = new_entries[key]
            else:
                # If the key already existed in the old entries, check if both entries
                # are dictionaries, in which case we continue recursively.
                if isinstance(old_entries[key], dict) and isinstance(
                    new_entries[key], dict
                ):
                    merged_entries[key] = _merge_missing_entries(
                        old_entries[key], new_entries[key]
                    )
                # Otherwise, the new entries are just taken instead.
                else:
                    merged_entries[key] = new_entries[key]

    return merged_entries


@i18n.command()
@check_env
def sync():
    """Synchronize all frontend translation keys based on the default locale."""
    translations_path = current_app.config["FRONTEND_TRANSLATIONS_PATH"]
    default_locale = current_app.config["LOCALE_DEFAULT"]

    default_locale_path = os.path.join(translations_path, f"{default_locale}.json")
    with open(default_locale_path, encoding="utf-8") as f:
        primary_translation = json.load(f)

    for locale in current_app.config["LOCALES"]:
        current_locale_path = os.path.join(translations_path, f"{locale}.json")

        if locale == default_locale:
            # Only sort the keys for the default locale.
            new_translation = primary_translation
        else:
            with open(current_locale_path, encoding="utf-8") as f:
                old_translation = json.load(f)

            new_translation = {}
            for key, value in primary_translation.items():
                _sync(key, value, old_translation, new_translation)

            # List any missing entries separately instead of removing them, in case they
            # were just moved to another key.
            missing_entries = _get_missing_entries(old_translation, new_translation)
            missing_entries = _merge_missing_entries(
                old_translation.get("_old", {}), missing_entries
            )

            if missing_entries:
                new_translation["_old"] = missing_entries

        # Create a new file in the same directory with the new translations, then
        # replace the old one.
        # pylint: disable=consider-using-with
        tmp_file = tempfile.NamedTemporaryFile(
            mode="w", dir=translations_path, delete=False
        )

        try:
            json_data = json.dumps(
                new_translation, ensure_ascii=False, indent=2, sort_keys=True
            )

            tmp_file.write(f"{json_data}\n")
            tmp_file.close()

            os.rename(tmp_file.name, current_locale_path)

            if locale != default_locale:
                echo(f"Synchronized '{current_locale_path}'.")

        except Exception as e:
            danger(str(e))

            try:
                os.remove(tmp_file.name)
            except FileNotFoundError:
                pass

            sys.exit(1)

    success("Synchronization completed successfully.")

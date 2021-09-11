import argparse
import importlib.util
import os
import shutil

import click
import tomli
from rich import print

import labo.config as conf
import labo.template as tmpl


@click.group()
@click.pass_context
@click.option("--config")
def cli(ctx, config):
    ctx.ensure_object(dict)
    g_conf = conf.load_global_config(config)
    if g_conf is None:
        click.echo("No config file found", err=True)
    ctx.obj["config"] = g_conf


@click.command()
@click.pass_context
def ls(ctx):
    click.echo("List of templates...")
    g_conf = ctx.obj["config"]
    contents = os.listdir(g_conf["template_dir"])
    for c in contents:
        if os.path.isdir(os.path.join(g_conf["template_dir"], c)):
            print(f"- {c}")


@click.command()
@click.pass_context
@click.argument("template")
def help(ctx, template):
    g_conf = ctx.obj["config"]
    p = os.path.join(g_conf["template_dir"], template)
    if os.path.isdir(p):
        conf_p = os.path.join(p, "config.toml")
        with open(conf_p, "r") as f:
            templ_conf = tomli.load(f)

        print(f"Name: {template}")
        if "help" in templ_conf:
            print(templ_conf["help"])

        if "options" in templ_conf:
            print(f"Options: {' '.join(templ_conf['options'])}")

        if "variables" in templ_conf:
            print(f"Variables: {' '.join(templ_conf['variables'].keys())}")

        if "instantiate" in templ_conf:
            print(f"Templates: {' '.join(templ_conf['instantiate'])}")

        if "copy" in templ_conf:
            print(f"Copies: {' '.join(templ_conf['copy'])}")

        if "copy" in templ_conf:
            print(f"Links: {' '.join(templ_conf['link'])}")
    else:
        print(f"Template '{template}' not found")


@click.command(
    context_settings=dict(ignore_unknown_options=True, allow_extra_args=True)
)
@click.option("--prompt/--no-prompt", default=True)
@click.pass_context
@click.argument("template")
@click.argument("name")
def new(ctx, prompt, template, name):
    g_conf = ctx.obj["config"]
    p = os.path.join(g_conf["template_dir"], template)
    if os.path.isdir(p):
        conf_p = os.path.join(p, "config.toml")
        with open(conf_p, "r") as f:
            templ_conf = tomli.load(f)

        # Parse template-specific options (if any)
        options = {}
        if "options" in templ_conf:
            parser = argparse.ArgumentParser()
            for opt in templ_conf["options"]:
                parser.add_argument(f"--{opt}")
            kwargs, _ = parser.parse_known_args(ctx.args)
            options = vars(kwargs)

        # Load custom hooks if they exist
        hooks = None
        if os.path.isfile(os.path.join(p, "hooks.py")):
            print("Loading hooks...")
            spec = importlib.util.spec_from_file_location(
                "hooks", os.path.join(p, "hooks.py")
            )
            hooks = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(hooks)

        # Get all variables
        variables = {}
        if "variables" in templ_conf:
            click.echo("Instantiating template variables...")
            for k in templ_conf["variables"].keys():
                if prompt:
                    variables[k] = click.prompt(
                        templ_conf["variables"][k]["prompt"],
                        default=templ_conf["variables"][k]["default"],
                    )
                else:
                    variables[k] = templ_conf["variables"][k]["default"]

        # Create dir based on name
        new_path = os.path.abspath(os.path.join(".", name))
        os.mkdir(new_path)

        if hooks and hasattr(hooks, "pre_template_hook"):
            print("Running pre-template hook")
            vrs = hooks.pre_template_hook(os.getcwd(), new_path, options, variables)
            variables = {**variables, **vrs}

        # Instantiate templates
        if "instantiate" in templ_conf:
            print("Instantiating templates...")
            for t_name in templ_conf["instantiate"]:
                name, ext = os.path.splitext(t_name)
                document = ""
                if ext == ".tex":
                    document = tmpl.render_latex_template(p, t_name, variables)
                elif name == "Makefile":
                    document = tmpl.render_makefile_template(p, t_name, variables)
                with open(os.path.join(new_path, t_name), "w") as f:
                    f.write(document)

        # Copy the files that need to be copied
        if "copy" in templ_conf:
            print("Copying files...")
            for name in templ_conf["copy"]:
                shutil.copy(os.path.join(p, name), os.path.join(new_path, name))

        # Link files that need to be linked
        if "link" in templ_conf:
            print("Linking files...")
            for name in templ_conf["link"]:
                os.link(os.path.join(p, name), os.path.join(new_path, name))

        print(f"Created new LaTeX project: {new_path}")

    else:
        click.echo(f"Invalid template: {template}")


cli.add_command(ls)
cli.add_command(help)
cli.add_command(new)

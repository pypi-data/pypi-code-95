#!/usr/bin/env python3
import pop.hub


def start():
    hub = pop.hub.Hub()
    hub.pop.sub.add(dyne_name="{{cookiecutter.clean_name}}")
    hub["{{cookiecutter.clean_name}}"].init.cli()

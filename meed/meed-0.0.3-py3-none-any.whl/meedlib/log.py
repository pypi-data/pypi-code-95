import argparse
from csv import DictWriter
from datetime import datetime
from sys import exit
from typing import *

import PySimpleGUI as sg

from .config import MeedConfig, MeedConfigNotExists
from .terminal import fatal_error
from .command import Command


class MeedLog:
    def __init__(self, config: MeedConfig):
        self.config = config
        sg.theme(self.config["Theme"])

        layout = self.radio_style()
        if self.config["Style"] == "Slider":
            layout = self.slider_style()
        elif self.config["Style"] == "Button":
            layout = self.button_style()

        self.window = sg.Window("Meed", layout)

        stats = self.extract_submit_event()
        now = datetime.now()
        stats["DateTime"] = now.strftime("%d-%m-%Y_%H:%M:%S")
        stats["Profile"] = self.config.profile_name
        self.write_to_csv(stats)

        self.window.close()
        return

    def write_to_csv(self, row: dict) -> None:
        headers = ["Profile", "DateTime", *self.config["Stats"]]
        with open(self.config["Output_File"], "a+", newline="") as file:
            csv_writer = DictWriter(file, fieldnames=headers)
            # Write headers if new file
            if file.tell() == 0:
                csv_writer.writeheader()
            csv_writer.writerow(row)

    def radio_style(self) -> list:
        layout = []
        for stat_group, stat in enumerate(self.config["Stats"]):
            layout.append([sg.Text(stat)])
            row = [
                sg.Radio(text=str(i), group_id=stat_group, key=f"{stat}_{i}")
                for i in range(1, self.config["Depth"] + 1)
            ]
            layout.append(row)
        layout.append([sg.Submit(), sg.Cancel()])
        return layout

    def slider_style(self) -> list:
        layout = []
        for stat_group, stat in enumerate(self.config["Stats"]):
            layout.append([sg.Text(stat)])
            layout.append([sg.Slider(range=(1, 10), orientation="horizontal")])
        layout.append([sg.Submit(), sg.Cancel()])
        return layout

    def button_style(self) -> list:
        layout = []
        for stat_group, stat in enumerate(self.config["Stats"]):
            layout.append([sg.Text(stat)])
            row = [
                sg.Button(
                    button_text=str(i),
                    button_type=sg.BUTTON_TYPE_REALTIME,
                    key=f"{stat}_{i}",
                )
                for i in range(1, self.config["Depth"] + 1)
            ]
            layout.append(row)
        layout.append([sg.Submit(), sg.Cancel()])
        return layout

    def extract_submit_event(self) -> Optional[dict]:
        while True:
            event, values = self.window.read()
            if event == "Submit":
                params = {}
                for key, val in values.items():
                    if val:
                        stat, stat_val = key.split("_")
                        params[stat] = stat_val
                if set(params.keys()) == set(self.config["Stats"]):
                    return params
                else:
                    sg.popup_error("Please select values for every stat", title="Error")
            elif event in [sg.WIN_CLOSED, "Cancel"]:
                self.window.close()
                exit()


class Log(Command):
    def __init__(self, parser):
        Command.__init__(self, parser)

    def main(self, args: argparse.Namespace):
        if args.log:
            try:
                config = MeedConfig(args.log)
                MeedLog(config)
            except MeedConfigNotExists:
                fatal_error(MeedConfigNotExists.MESSAGE)

    def create(self):
        self.parser.add_argument(
            "log",
            nargs="?",
            help="Name of the meed log profile. Use --new option to setup a profile",
        )


if __name__ == "__main__":
    Log(argparse.ArgumentParser()).parse()

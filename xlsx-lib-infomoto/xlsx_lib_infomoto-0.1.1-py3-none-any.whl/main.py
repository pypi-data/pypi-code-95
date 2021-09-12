import os
import random
from typing import Optional

from domain.motorcycle_model.motorcycle_model import MotorcycleModel
from domain.motorcycle_model.motorcycle_model_workbook import MotorcycleModelWorkbook
import glob


def create_motorcycle_model(filename: str, directory: Optional[str] = None):
    motorcycle_model: MotorcycleModel = MotorcycleModelWorkbook(
        filename=filename,
        directory=directory
    ).motorcycle_model


def create_all_models() -> list[MotorcycleModel]:
    filenames: list[str] = glob.glob("./files/*.xlsx", recursive=True)

    models: list[MotorcycleModel] = list()
    # TODO: Create directory name

    directory_name: str = f"./json/{random.randint(0, 999)}"

    try:
        os.mkdir(directory_name)
    except OSError:
        print("caca")

    for filename in filenames:
        create_motorcycle_model(
            filename=filename,
            directory=directory_name,
        )

    return models


if __name__ == "__main__":
    # create_motorcycle_model("files/FICHA T MAX 560 2020.xlsx")
    # create_motorcycle_model("files/FICHA MONSTER 796.xlsx")
    # create_motorcycle_model("files/FICHA PEGASO 650 ´93 ´00.xlsx")
    # create_motorcycle_model("files/FICHA XVS 950 STAR ´14.xlsx")
    # create_motorcycle_model("files/FICHA FORZA 125 ´15 .xlsx")
    # create_motorcycle_model("files/FICHA ATLANTIC 125 200 ´02.xlsx")
    create_all_models()

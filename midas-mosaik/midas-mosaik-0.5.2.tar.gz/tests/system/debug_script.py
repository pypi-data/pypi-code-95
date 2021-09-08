import midas
from midas.cli.cli import init_logger
from midas.util.runtime_config import RuntimeConfig


def main():

    RuntimeConfig().load()
    init_logger(2)
    midas.run(
        "my_second_midas",
        params={
            "mosaikdb_params": {"filename": "debug.hdf5"},
            "with_db": True,
        },
    )
    # midas.run(
    #     scenario_name="demo", config="src/midas/adapter/mango/blackstart.yml"
    # )
    # cli(["run", "-n", "midasmv"])
    # cli(["-vv", "download", "-w", "-f", "-k"])


if __name__ == "__main__":
    main()

from omniblack.model import Model
from pathlib import Path

model = Model('@omniblack/vulcan')

__all__ = ('model', )


async def load_model():
    await model.structs.load_model_dir(Path(__file__).parent/'model')

def start_load():
    model.start_load(load_model())

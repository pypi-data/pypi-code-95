try:
    import torch
    import torchvision
    import torchaudio
    import ignite
except ModuleNotFoundError:
    raise ImportError(
        'Please install torch>=1.9.0, torchaudio>=0.9.0.'
        ' torchvision>=0.10.0, pytorch-ignite>=0.4.6 '
        'to support module "geyser_lava.task.torch"'
    )
